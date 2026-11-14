"""Frame-positioned WAV cues and ID3 chapters; editing never changes audio samples.

RIFF cue/adtl: IBM/Microsoft Multimedia Programming Interface and Data Specs 1.0.
ID3 chapter addendum: https://id3.org/id3v2-chapters-1.0
"""
from dataclasses import dataclass
import struct
import unicodedata

from .errors import AudioError
from . import id3_metadata
from .metadata import MAX_METADATA_BYTES

MAX_MARKERS = 4096
UNSET = object()


@dataclass(frozen=True)
class Marker:
    key: str
    start: int
    end: object
    name: str
    kind: str


def _items(raw):
    offset = 4
    while offset < len(raw):
        if offset+8 > len(raw): raise AudioError('Invalid marker information.')
        tag, length = struct.unpack_from('<4sI', raw, offset)
        stop = offset+8+length+(length&1)
        if stop > len(raw): raise AudioError('Invalid marker information.')
        yield tag, raw[offset+8:offset+8+length], raw[offset:stop]
        offset = stop


def _chunk(tag, data):
    return struct.pack('<4sI',tag,len(data))+data+(b'\0' if len(data)&1 else b'')


def _codec(chunks):
    page=next((struct.unpack_from('<H',raw)[0] for kind,raw in chunks if kind==b'CSET' and len(raw)>=2),None)
    return ('utf-8' if page==65001 else 'cp'+str(page)) if page else None


def _decode(raw, chunks):
    raw=raw.split(b'\0',1)[0]
    for encoding in dict.fromkeys((_codec(chunks),'utf-8','cp1252')):
        if encoding is None:continue
        try:return raw.decode(encoding)
        except (UnicodeError,LookupError):pass
    return raw.decode('utf-8','replace')


def _cues(chunks):
    records=[];seen=set()
    for kind,raw in chunks:
        if kind!=b'cue ':continue
        if len(raw)<4:raise AudioError('Invalid marker information.')
        count,=struct.unpack_from('<I',raw)
        if len(raw)!=4+24*count:raise AudioError('Invalid marker information.')
        for i in range(count):
            values=struct.unpack_from('<II4sIII',raw,4+24*i)
            if values[0] in seen or values[2]!=b'data' or values[3] or values[4]:
                raise AudioError('These cue points cannot be edited safely.')
            records.append(values);seen.add(values[0])
            if len(records)>MAX_MARKERS:raise AudioError('There are too many markers to edit.')
    return records


def read(chunks, rate):
    labels={};result=[]
    try:
        for kind,raw in chunks:
            if kind==b'LIST' and raw[:4]==b'adtl':
                for tag,data,_ in _items(raw):
                    if tag==b'labl' and len(data)>=4:
                        labels.setdefault(struct.unpack_from('<I',data)[0],_decode(data[4:],chunks))
        for identifier,_,_,_,_,frame in _cues(chunks):
            result.append(Marker('cue:'+str(identifier),frame,None,labels.get(identifier,''),'Marker'))
    except AudioError:
        # Opaque or noncanonical cue metadata remains untouched in the file.
        pass
    for index,(kind,raw) in enumerate(chunks):
        if kind.lower()!=b'id3 ':continue
        tags=id3_metadata.load(raw)
        if tags is None:continue
        for chapter in tags.getall('CHAP'):
            if chapter.start_time==id3_metadata.UNKNOWN:continue
            title=chapter.sub_frames.get('TIT2')
            name=str(title.text[0]) if title is not None and title.text else ''
            end=None if chapter.end_time==id3_metadata.UNKNOWN else round(chapter.end_time*rate/1000)
            result.append(Marker('chapter:'+str(index)+':'+chapter.element_id,
                                 round(chapter.start_time*rate/1000),end,name,'Chapter'))
            if len(result)>=MAX_MARKERS:break
        if len(result)>=MAX_MARKERS:break
    return tuple(sorted(result,key=lambda m:(m.start,m.key)))


def for_model(model):
    cached=getattr(model,'_marker_cache',None)
    if cached is None or cached[0] is not model.metadata or cached[1]!=model.sample_rate:
        cached=(model.metadata,model.sample_rate,read(model.metadata,model.sample_rate))
        model._marker_cache=cached
    return cached[2]


def _checked(chunks):
    chunks=tuple(chunks)
    if sum(len(raw) for _,raw in chunks)>MAX_METADATA_BYTES:raise AudioError('Marker information is too large.')
    return chunks


def _name(value):
    if not isinstance(value,str) or len(value)>256 or any(unicodedata.category(c)=='Cc' for c in value):
        raise AudioError('Marker names may contain at most 256 characters and no control characters.')
    return value.strip()


def _position(value,frames):
    if type(value) is not int or not 0<=value<frames:raise AudioError('The marker must be inside the audio.')
    return value


def _rewrite_cues(chunks,records,target,name=UNSET,remove=False):
    result=[];written=False
    for kind,raw in chunks:
        if kind==b'cue ':
            if not written and records:
                result.append((kind,struct.pack('<I',len(records))+b''.join(struct.pack('<II4sIII',*v) for v in records)))
            written=True
        elif kind==b'LIST' and raw[:4]==b'adtl':
            parts=[]
            for tag,data,original in _items(raw):
                match=tag in (b'labl',b'note',b'ltxt') and len(data)>=4 and struct.unpack_from('<I',data)[0]==target
                if match and (remove or (tag==b'labl' and name is not UNSET)):continue
                parts.append(original)
            if parts:result.append((kind,b'adtl'+b''.join(parts)))
        else:result.append((kind,raw))
    if not written and records:
        result.append((b'cue ',struct.pack('<I',len(records))+b''.join(struct.pack('<II4sIII',*v) for v in records)))
    if name is not UNSET and name and not remove:
        try:encoded=name.encode(_codec(chunks) or 'utf-8')
        except (UnicodeError,LookupError) as error:
            raise AudioError('This marker name cannot be stored in the existing WAV character set.') from error
        result.append((b'LIST',b'adtl'+_chunk(b'labl',struct.pack('<I',target)+encoded+b'\0')))
    return _checked(result)


def add(chunks,rate,frames,start,name=''):
    _position(start,frames);name=_name(name)
    if len(read(chunks,rate))>=MAX_MARKERS:raise AudioError('There are too many markers to edit.')
    if start>=2**32:raise AudioError('WAV cue positions must fit in 32 bits. Choose an earlier position.')
    records=_cues(chunks);used={v[0] for v in records};identifier=0
    while identifier in used:identifier+=1
    records.append((identifier,start,b'data',0,0,start))
    return _rewrite_cues(chunks,records,identifier,name), 'cue:'+str(identifier)


def edit(chunks,rate,frames,key,*,start=UNSET,end=UNSET,name=UNSET,remove=False):
    if name is not UNSET:name=_name(name)
    marker=next((m for m in read(chunks,rate) if m.key==key),None)
    if marker is None:raise AudioError('That marker is no longer available.')
    if start is not UNSET:_position(start,frames)
    if end is not UNSET and end is not None and (type(end) is not int or not 0<=end<=frames):
        raise AudioError('Invalid chapter position.')
    if start==marker.start:start=UNSET
    if end==marker.end:end=UNSET
    if name==marker.name:name=UNSET
    if not remove and start is UNSET and end is UNSET and name is UNSET:return chunks
    if marker.kind=='Marker':
        if end is not UNSET:raise AudioError('Only chapter markers have an end position.')
        records=_cues(chunks);target=int(key.split(':')[1]);new=[]
        for values in records:
            if values[0]==target:
                if remove:continue
                if start is not UNSET:
                    if start>=2**32:raise AudioError('WAV cue positions must fit in 32 bits. Choose an earlier position.')
                    values=(values[0],start,*values[2:5],start)
            new.append(values)
        return _rewrite_cues(chunks,new,target,name,remove)
    _,index,identifier=key.split(':',2);index=int(index)
    tags=id3_metadata.load(chunks[index][1],strict=True)
    chapter=tags.get('CHAP:'+identifier)
    if chapter is None:raise AudioError('That marker is no longer available.')
    if remove:
        tags.delall(chapter.HashKey);id3_metadata.clean_toc(tags)
    else:
        if start is not UNSET or end is not UNSET:
            a=chapter.start_time if start is UNSET else round(start*1000/rate)
            b=chapter.end_time if end is UNSET else id3_metadata.UNKNOWN if end is None else round(end*1000/rate)
            if b!=id3_metadata.UNKNOWN and b<=a:
                raise AudioError('The chapter end must follow its start and stay inside the audio.')
            if a>=id3_metadata.UNKNOWN or (end is not UNSET and end is not None and b>=id3_metadata.UNKNOWN):
                raise AudioError('Invalid chapter position.')
            if (a,b)!=(chapter.start_time,chapter.end_time):
                chapter.start_time,chapter.end_time=a,b
                chapter.start_offset=chapter.end_offset=id3_metadata.UNKNOWN
            elif name is UNSET:
                return chunks  # CHAP positions have millisecond precision.
        if name is not UNSET:
            from mutagen.id3 import TIT2
            chapter.sub_frames.delall('TIT2')
            if name:chapter.sub_frames.add(TIT2(encoding=3,text=[name]))
        id3_metadata.clean_toc(tags)
    result=list(chunks);result[index]=(chunks[index][0],id3_metadata.dump(tags))
    return _checked(result)


def move(chunks,rate,frames,key,start):
    marker=next((m for m in read(chunks,rate) if m.key==key),None)
    if marker is None:raise AudioError('That marker is no longer available.')
    settings=dict(start=start)
    if marker.kind=='Chapter' and marker.end is not None:
        duration=marker.end-marker.start
        settings['start']=max(0,min(start,frames-duration))
        settings['end']=settings['start']+duration
    return edit(chunks,rate,frames,key,**settings)


def export_cues(chunks,rate,frames,tags):
    """Translate point cues to millisecond chapters, preserving original ID3 nodes."""
    if rate is None or frames is None:return set()
    try:records=_cues(chunks)
    except AudioError:return set()
    if any(v[5]>=frames for v in records):return set()
    handled={i for i,(kind,_) in enumerate(chunks) if kind==b'cue '}
    if not records:return handled
    from mutagen.id3 import CHAP, TIT2, CTOC
    names={m.key:m.name for m in read(chunks,rate) if m.kind=='Marker'}
    used={c.element_id for name in ('CHAP','CTOC') for c in tags.getall(name)}
    def fresh(base):
        candidate=base;counter=0
        while candidate in used:counter+=1;candidate=base+'-'+str(counter)
        used.add(candidate);return candidate
    duration=max(1,min(id3_metadata.UNKNOWN-1,round(frames*1000/rate)))
    ordered=sorted(records,key=lambda v:(v[5],v[0]))
    starts=[min(duration-1,round(v[5]*1000/rate)) for v in ordered]
    for index,record in enumerate(ordered):
        start=starts[index];end=next((p for p in starts[index+1:] if p>start),duration)
        name=names.get('cue:'+str(record[0]),'')
        tags.add(CHAP(element_id=fresh('ss-cue-'+str(record[0])),start_time=start,end_time=end,
                      start_offset=id3_metadata.UNKNOWN,end_offset=id3_metadata.UNKNOWN,
                      sub_frames=[TIT2(encoding=3,text=[name])] if name else []))
    id3_metadata.clean_toc(tags)
    nodes={c.element_id for name in ('CHAP','CTOC') for c in tags.getall(name)}
    references={name for toc in tags.getall('CTOC') for name in toc.child_element_ids}
    roots=sorted(nodes-references)
    for toc in tags.getall('CTOC'):toc.flags&=~2
    while len(roots)>255:
        groups=[]
        for start in range(0,len(roots),255):
            key=fresh('ss-markers-group');tags.add(CTOC(element_id=key,flags=0,child_element_ids=roots[start:start+255]));groups.append(key)
        roots=groups
    if roots:tags.add(CTOC(element_id=fresh('ss-markers'),flags=2,child_element_ids=roots))
    cue_ids={v[0] for v in records}
    for index,(kind,raw) in enumerate(chunks):
        if kind==b'LIST' and raw[:4]==b'adtl':
            try:
                items=list(_items(raw))
                if all(tag==b'labl' and len(data)>=4 and struct.unpack_from('<I',data)[0] in cue_ids for tag,data,_ in items):handled.add(index)
            except AudioError:pass
    return handled
