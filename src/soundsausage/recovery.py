"""Atomic recovery journals over private immutable buffers, never original files."""
import base64
from dataclasses import asdict
import json
import os
from pathlib import Path
import time

import numpy as np

from . import storage, peaks
from .audio import AudioError, validate_audio
from .document import Document
from .session import Session, Media, Track, SessionClip, text, number, integer, MAX_TRACKS, MAX_MEDIA, MAX_CLIPS
from .envelopes import validate_points
from .operations import operation

MAX_JOURNAL_BYTES=64*1024*1024
_pins={}


def _metadata(chunks):
    return [[kind.decode('latin1'),base64.b64encode(raw).decode('ascii')] for kind,raw in chunks]


def _decode_metadata(value):
    if not isinstance(value,list):
        raise AudioError('Invalid recovery metadata.')
    result=[]
    for kind,encoded in value:
        raw=base64.b64decode(encoded,validate=True)
        kind=kind.encode('latin1')
        if len(kind)!=4 or len(raw)>16*1024*1024:
            raise AudioError('Invalid recovery metadata.')
        result.append((kind,raw))
    return tuple(result)


def _publish_pins():
    storage.pin_paths({path for paths in _pins.values() for path in paths})


class Recovery:
    def __init__(self):
        self.owner=storage.Workspace()
        self.path=self.owner.path/'recovery.json'
        self._last_key=None

    def checkpoint(self,document,session,mode='waveform',editing_clip_id=None):
        key=(id(document),document.revision,document.dirty,document.selection,document.cursor,
             str(document.path),id(session),session.revision,session.dirty,session.selection,session.cursor,
             str(session.path),mode,editing_clip_id)
        if key==self._last_key:
            return
        if not document.dirty and not session.dirty:
            self.clear();self._last_key=key;return
        roots=[];paths=set()
        def buffer(samples):
            if not len(samples):return None
            root,record=storage.persist_array(samples)
            roots.append(root);paths.add(storage.lease_of(root).path)
            return record
        with operation():  # Journaling follows a committed edit and cannot cancel that edit.
            doc=dict(pieces=[buffer(piece) for piece in document._pieces],rate=document.sample_rate,
                     channels=document.channels,encoding=document.encoding,path=str(document.path) if document.path else None,
                     selection=list(document.selection),cursor=document.cursor,dirty=document.dirty,
                     metadata=_metadata(document.metadata),extra_chunks=list(document.extra_chunks),
                     name=getattr(document,'display_name',None),last_effect=document.last_effect)
            active={clip.media_id for track in session.tracks for clip in track.clips}
            media=[dict(id=item.id,name=item.name,buffer=buffer(item.samples),metadata=_metadata(item.metadata))
                   for key,item in session.media.items() if key in active]
            multitrack=dict(rate=session.sample_rate,tracks=[asdict(track) for track in session.tracks],media=media,
                            selection=list(session.selection),cursor=session.cursor,selected_clip=session.selected_clip,
                            selected_track=session.selected_track,dirty=session.dirty,path=str(session.path) if session.path else None,
                            adopt_first_rate=session.adopt_first_rate)
            record=dict(format='soundsausage-recovery',version=1,time=time.time(),document=doc,session=multitrack,
                        mode=mode,editing_clip_id=editing_clip_id)
            encoded=json.dumps(record,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')
            if len(encoded)>MAX_JOURNAL_BYTES:
                raise AudioError('Recovery information exceeds the supported journal size.')
            temporary=self.path.with_suffix('.tmp')
            try:
                with temporary.open('wb') as output:
                    output.write(encoded);output.flush();os.fsync(output.fileno())
                os.replace(temporary,self.path)
                directory=os.open(self.path.parent,os.O_RDONLY)
                try:os.fsync(directory)
                finally:os.close(directory)
            finally:
                temporary.unlink(missing_ok=True)
            _pins[str(self.path)]=paths
            _publish_pins()
        self._last_key=key

    def clear(self):
        self.path.unlink(missing_ok=True)
        _pins.pop(str(self.path),None);_publish_pins()
        self._last_key=None

    def close(self):
        self.clear();self.owner.close()


def candidates():
    """Keep the journal lock until restore/discard/later has been decided."""
    result=[]
    root=storage.cache_root()
    if not root.exists():return result
    for path in sorted(root.glob('*/recovery.json'),key=lambda p:p.stat().st_mtime,reverse=True):
        if str(path.parent.resolve()) in storage._workspaces:
            continue
        try:
            owner=storage.Workspace(root,existing=path.parent)
        except (AudioError,OSError):
            continue
        result.append(owner)
    return result


def restore(owner,dsp=None):
    path=owner.path/'recovery.json'
    if path.stat().st_size>MAX_JOURNAL_BYTES:
        raise AudioError('The recovery journal is too large.')
    try:
        record=json.loads(path.read_text('utf-8'))
        if record.get('format')!='soundsausage-recovery' or record.get('version')!=1:
            raise AudioError('Unsupported recovery journal.')
        descriptors=list(record['document']['pieces'])+[item['buffer'] for item in record['session']['media']]
        protected={(storage.cache_root()/item['file']).resolve() for item in descriptors}
        if any(not value.is_relative_to(storage.cache_root().resolve()) for value in protected):
            raise AudioError('Invalid recovery buffer path.')
        _pins[str(path)]=protected;_publish_pins()
        opened={}
        def buffer(value,channels=None):
            filename=value['file']
            shape=value['shape']
            key=(filename,tuple(shape))
            if key not in opened:
                root=storage.open_buffer(storage.cache_root()/filename,shape)
                validate_audio(root,44100);peaks.prepare(root)
                opened[key]=root
            root=opened[key]
            offset=integer(value['offset'],'Buffer offset')
            frames=integer(value['frames'],'Buffer frames',1)
            width=root.shape[1]
            if offset%width or offset//width+frames>len(root) or (channels and width!=channels):
                raise AudioError('Invalid recovery buffer range.')
            return root[offset//width:offset//width+frames]
        item=record['document']
        document=Document(sample_rate=integer(item['rate'],'Sample rate',1000,384000),
                          channels=integer(item['channels'],'Channels',1,2),encoding=item['encoding'],dsp=dsp)
        if item['encoding'] not in ('pcm8','pcm16','pcm24','pcm32','float32'):
            raise AudioError('Invalid recovery encoding.')
        document._pieces=tuple(buffer(value,document.channels) for value in item['pieces'])
        document.metadata=_decode_metadata(item['metadata'])
        document.extra_chunks=tuple(item['extra_chunks'])
        document.path=Path(item['path']) if item['path'] else None
        document.select(*item['selection']);document.cursor=integer(item['cursor'],'Cursor',0,document.frames)
        document.last_effect=item.get('last_effect')
        if item.get('name'):document.display_name=text(item['name'])
        if item['dirty']:document._saved_state_id=-1
        document.revision=1
        item=record['session']
        session=Session(integer(item['rate'],'Sample rate',1000,384000),1,dsp=document.dsp,adopt_first_rate=item['adopt_first_rate'])
        if not 1<=len(item['tracks'])<=MAX_TRACKS or len(item['media'])>MAX_MEDIA:
            raise AudioError('Invalid recovery track/media count.')
        from .project import _id
        for entry in item['media']:
            key=_id(entry['id'])
            if key in session._media:raise AudioError('Duplicate recovery media.')
            session._media[key]=Media(key,text(entry['name']),buffer(entry['buffer']),session.sample_rate,_decode_metadata(entry['metadata']))
        tracks=[];track_ids=set();clip_ids=set()
        for entry in item['tracks']:
            key=_id(entry['id'])
            if key in track_ids:raise AudioError('Duplicate recovery track.')
            track_ids.add(key);clips=[]
            for values in entry['clips']:
                if len(clip_ids)>=MAX_CLIPS:raise AudioError('Too many recovery clips.')
                values=dict(values)
                for kind in ('volume','pan'):
                    values[kind+'_envelope']=validate_points(values[kind+'_envelope'],kind,len(session._media[values['media_id']].samples))
                clip=SessionClip(**values)
                _id(clip.id)
                if clip.id in clip_ids:raise AudioError('Duplicate recovery clip.')
                clip_ids.add(clip.id);session._validate_clip(clip);clips.append(clip)
            if type(entry['muted']) is not bool or type(entry['solo']) is not bool:
                raise AudioError('Invalid recovery mute/solo.')
            tracks.append(Track(key,text(entry['name']),tuple(clips),number(entry['gain'],0,100,'Gain'),number(entry['pan'],-1,1,'Pan'),entry['muted'],entry['solo']))
        session._tracks=tuple(tracks)
        session.selected_track=item['selected_track'] if item['selected_track'] in track_ids else tracks[0].id
        session.selected_clip=item['selected_clip'] if item['selected_clip'] in clip_ids else None
        session.select(*item['selection']);session.cursor=integer(item['cursor'],'Cursor',0,session.sample_rate*86400)
        session.path=Path(item['path']) if item['path'] else None
        if item['dirty']:session._saved_state_id=-1
        session.revision=1
        mode=record['mode'] if record['mode'] in ('waveform','multitrack') else 'waveform'
        editing=record.get('editing_clip_id')
        editing=editing if editing in clip_ids else None
        # Protect old buffers until a replacement journal has been committed.
        _pins[str(path)]={storage.lease_of(root).path for root in opened.values()}
        _publish_pins()
        return document,session,mode,editing
    except (KeyError,TypeError,ValueError,UnicodeError,OverflowError) as error:
        if isinstance(error,AudioError):raise
        raise AudioError('The recovery information is invalid or damaged.') from error


def discard(owner):
    path=owner.path/'recovery.json'
    path.unlink(missing_ok=True)
    _pins.pop(str(path),None);_publish_pins()
    owner.close()


def collect_orphans():
    """Only unlocked workspaces without a journal or referenced buffers are cleaned."""
    root=storage.cache_root()
    if not root.exists():return
    keep=set()
    for path in root.glob('*/recovery.json'):
        try:
            if path.stat().st_size>MAX_JOURNAL_BYTES:continue
            value=json.loads(path.read_text('utf-8'))
            for item in value.get('document',{}).get('pieces',[]):
                keep.add((root/item['file']).resolve())
            for item in value.get('session',{}).get('media',[]):
                keep.add((root/item['buffer']['file']).resolve())
        except (OSError,KeyError,TypeError,ValueError):
            # Damaged journals are retained for explicit handling, not guessed away.
            return
    for folder in root.iterdir():
        if not folder.is_dir() or str(folder.resolve()) in storage._workspaces:continue
        try:owner=storage.Workspace(root,existing=folder)
        except (AudioError,OSError):continue
        try:
            if not (folder/'recovery.json').exists():
                for path in folder.glob('*.buffer'):
                    if path.resolve() not in keep:path.unlink(missing_ok=True)
                if not any(folder.glob('*.buffer')):
                    (folder/'recovery.tmp').unlink(missing_ok=True)
                    (folder/'.lock').unlink(missing_ok=True)
                    try:folder.rmdir()
                    except OSError:pass
        finally:owner.close()
