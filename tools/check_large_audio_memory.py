"""Isolated resident-memory regression check for a 160 MiB audio workflow."""
import json
import resource
import tempfile
from pathlib import Path

from PySide6.QtMultimedia import QAudioFormat
from soundsausage.audio import wav_header,read_wav,write_wav
from soundsausage.document import Document
from soundsausage.capture import Take
from soundsausage import storage
from soundsausage.session import Session
from soundsausage.project import save_project,load_project
from soundsausage.recovery import Recovery
from soundsausage.playback import EncodedAudio
from soundsausage.peaks import piece_peaks

baseline=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
stages={}
def mark(name):
    stages[name]=round((resource.getrusage(resource.RUSAGE_SELF).ru_maxrss-baseline)/1024,1)

with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'large.wav'
    frames=20*1024*1024
    header=wav_header(frames,2,48000,'float32')
    with path.open('wb') as output:
        output.write(header);output.truncate(len(header)+frames*8)
    audio=read_wav(path);mark('open')
    doc=Document(audio.samples,48000);mark('document')
    doc.apply('normalize',target=.98,remove_dc=True);mark('normalize')
    piece_peaks(doc._pieces,doc.frames,2,1000);mark('waveform')
    write_wav(path,doc.view(),48000,'float32');mark('save')
    session=Session(48000,1);session.import_audio([(doc.view(),48000,'Long')]);mark('import')
    session.render();mark('render')
    project=Path(folder)/'large.celp';save_project(session,project);mark('project-save')
    reopened=load_project(project);mark('project-open')
    recovery=Recovery();recovery.checkpoint(doc,session);mark('recovery');recovery.close()
    fmt=QAudioFormat();fmt.setSampleRate(48000);fmt.setChannelCount(2);fmt.setSampleFormat(QAudioFormat.SampleFormat.Float)
    output=EncodedAudio(doc.view(),48000,fmt)
    for start in range(0,len(output),65536):
        part=output[start:min(start+65536,len(output))]
    mark('playback-encode')
    take=Take(48000,2,'Memory check input')
    source=doc.view()
    for a in range(0,len(source),storage.BLOCK_FRAMES):
        take.append(source[a:a+storage.BLOCK_FRAMES])
    take.finish();mark('recording-file')
    recorded=Document(take.samples,take.rate)
    mark('recording-apply');take.discard()
    assert recorded.frames==frames
print(json.dumps({'decoded_mib':160,'baseline_mib':round(baseline/1024,1),'extra_resident_mib':stages}))
if max(stages.values())>80:
    raise SystemExit('Resident audio memory grew beyond the bounded-workflow allowance of 80 MiB.')
