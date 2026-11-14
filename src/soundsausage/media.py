"""Bounded, cancelable MP3 conversion with atomic saves and retained ID3 tags."""
from contextlib import contextmanager
from io import BytesIO
import os
from pathlib import Path
import selectors
import shutil
import stat
import subprocess
import tempfile

from .audio import AudioError, AudioFile, read_wav, write_wav, validate_audio
from . import storage, id3_metadata
from .metadata import MAX_METADATA_BYTES
from .operations import _current, operation, progress


MP3_ENCODINGS={f'mp3_{rate}':rate for rate in (128,192,256,320)}
AUDIO_FILTER='Audio files (*.wav *.WAV *.mp3 *.MP3);;WAV audio (*.wav *.WAV);;MP3 audio (*.mp3 *.MP3);;All files (*)'


def _id3_api():
    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3,ID3NoHeaderError,TLEN
        from mutagen import MutagenError
    except ImportError as error:
        raise AudioError('MP3 support requires FFmpeg and Mutagen. Install the application dependencies.') from error
    return MP3,ID3,ID3NoHeaderError,TLEN,MutagenError


@contextmanager
def _stage(label):
    parent=_current.get()
    with operation((lambda done,total,_:parent.update(done,total,label)) if parent else None):
        yield


def _ffmpeg(arguments,seconds,label):
    executable=shutil.which('ffmpeg')
    if executable is None:
        raise AudioError('MP3 support requires FFmpeg and Mutagen. Install the application dependencies.')
    total=max(1,round(seconds*1000000));done=0;pending=b'';errors=[]
    progress(0,total,label)
    command=[executable,'-nostdin','-hide_banner','-loglevel','error','-nostats',
             '-progress','pipe:1','-y',*arguments]
    process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0)
    try:
        os.set_blocking(process.stdout.fileno(),False)
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout,selectors.EVENT_READ)
            while selector.get_map() or process.poll() is None:
                for key,_ in selector.select(.05):
                    block=os.read(key.fd,65536)
                    if not block:
                        selector.unregister(key.fileobj);continue
                    pending+=block
                    lines=pending.split(b'\n');pending=lines.pop()[-16384:]
                    for raw in lines:
                        line=raw.decode('utf-8','replace').strip()
                        if line.startswith('out_time_us='):
                            try:done=max(done,min(total-1,int(line.split('=',1)[1])))
                            except ValueError:pass
                        elif line and '=' not in line:
                            errors.append(line[-1024:]);errors=errors[-8:]
                progress(done,total,label)
        if process.wait()!=0:
            detail='\n'.join(errors) or pending.decode('utf-8','replace')[-2048:]
            raise AudioError('MP3 conversion failed: {0}'.format(detail.strip() or 'FFmpeg'))
        progress(total,total,label)
    finally:
        if process.poll() is None:
            process.terminate()
            try:process.wait(timeout=2)
            except subprocess.TimeoutExpired:process.kill();process.wait()
        process.stdout.close()


def _tag_bytes(tags):
    if tags is None:return b''
    output=BytesIO();tags.save(output,v2_version=4,padding=lambda _:0)
    result=output.getvalue()
    if len(result)>MAX_METADATA_BYTES:raise AudioError('MP3 metadata exceeds the supported 16 MiB size.')
    return result


def read_mp3(path):
    MP3,_,_,_,MutagenError=_id3_api();path=Path(path).resolve()
    with path.open('rb') as source:
        header=source.read(10)
        if header[:3]==b'ID3':
            if len(header)!=10 or any(value&128 for value in header[6:]):raise AudioError('Invalid MP3 metadata.')
            size=sum(value<<(7*(3-index)) for index,value in enumerate(header[6:]))
            if size+20>MAX_METADATA_BYTES:raise AudioError('MP3 metadata exceeds the supported 16 MiB size.')
    try:
        info=MP3(path)
        if info.info.layer!=3 or info.info.channels not in (1,2):raise AudioError('SoundSausage supports mono and stereo MP3 audio.')
        tags=_tag_bytes(info.tags)
        bitrate=min(MP3_ENCODINGS.values(),key=lambda rate:abs(rate*1000-info.info.bitrate))
        with tempfile.TemporaryDirectory(prefix='mp3-read-',dir=storage.workspace().path) as folder:
            decoded=Path(folder)/'decoded.wav'
            _ffmpeg(['-xerror','-protocol_whitelist','file,pipe','-f','mp3','-i',str(path),
                     '-map','0:a:0','-vn','-sn','-dn','-c:a','pcm_f32le','-f','wav','-rf64','auto',str(decoded)],
                    info.info.length,'MP3 openen')
            with _stage('MP3 openen'):audio=read_wav(decoded)
        chunks=tuple((kind,raw) for kind,raw in audio.metadata if kind.lower()!=b'id3 ')
        if tags:chunks+=((b'id3 ',tags),)
        if sum(len(raw) for _,raw in chunks)>MAX_METADATA_BYTES:raise AudioError('MP3 metadata exceeds the supported 16 MiB size.')
        return AudioFile(audio.samples,audio.sample_rate,f'mp3_{bitrate}',tuple(kind.decode('ascii','replace') for kind,_ in chunks),chunks)
    except MutagenError as error:raise AudioError('Invalid or incomplete MP3 file.') from error


def write_mp3(path,samples,sample_rate,encoding='mp3_192',*,metadata=()):
    if encoding not in MP3_ENCODINGS:raise AudioError('Choose a supported MP3 bitrate.')
    validate_audio(samples,sample_rate)
    if not len(samples):raise AudioError('MP3 export requires some audio.')
    if len(samples)*1000<sample_rate*2:
        raise AudioError('MP3 export needs at least 2 ms of audio. Use WAV for shorter selections.')
    _,ID3,ID3NoHeaderError,TLEN,MutagenError=_id3_api()
    tags, _ = id3_metadata.export_tags(metadata,sample_rate=sample_rate,frames=len(samples))
    id3_metadata.sanitise(tags, len(samples), sample_rate)
    path=Path(path);temporary=None
    mode=stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    try:
        with tempfile.TemporaryDirectory(prefix='mp3-write-',dir=storage.workspace().path) as folder:
            source=Path(folder)/'source.wav';encoded=Path(folder)/'encoded.mp3'
            with _stage('MP3 voorbereiden'):write_wav(source,samples,sample_rate,'float32')
            rate=min((32000,44100,48000),key=lambda value:abs(value-sample_rate))
            _ffmpeg(['-xerror','-protocol_whitelist','file,pipe','-i',str(source),'-map','0:a:0',
                     '-vn','-sn','-dn','-map_metadata','0','-c:a','libmp3lame','-b:a',f'{MP3_ENCODINGS[encoding]}k',
                     '-ar',str(rate),'-id3v2_version','4','-write_id3v1','0','-f','mp3',str(encoded)],
                    len(samples)/sample_rate,'MP3 opslaan')
            try:generated=ID3(encoded);offset=generated.size
            except ID3NoHeaderError:generated=ID3();offset=0
            for frame in generated.getall('TSSE'):
                tags.add(frame)
            tags.add(TLEN(encoding=3,text=[str(round(len(samples)*1000/sample_rate))]))
            tag_bytes=_tag_bytes(tags)
            size=encoded.stat().st_size-offset
            with encoded.open('rb') as input_file,tempfile.NamedTemporaryFile(prefix='.'+path.name+'.',suffix='.tmp',dir=path.parent,delete=False) as output:
                temporary=Path(output.name);output.write(tag_bytes);input_file.seek(offset);done=0
                while block:=input_file.read(65536):
                    output.write(block);done+=len(block);progress(done,max(1,size),'MP3 opslaan')
                output.flush();os.fsync(output.fileno())
            progress(size,max(1,size),'MP3 opslaan');os.chmod(temporary,mode);os.replace(temporary,path);temporary=None
    except MutagenError as error:raise AudioError('Invalid MP3 metadata.') from error
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)


def write_audio(path,samples,sample_rate,encoding='pcm16',**kwargs):
    if encoding in MP3_ENCODINGS:
        kwargs.pop('pcm16_symmetric',None)
        return write_mp3(path,samples,sample_rate,encoding,**kwargs)
    return write_wav(path,samples,sample_rate,encoding,**kwargs)
