"""WAV metadata kept with audio; cue and sampler positions follow edits."""
import struct
from . import id3_metadata

MAX_METADATA_BYTES = 16 * 1024 * 1024
CORE_CHUNKS = {b'fmt ', b'data', b'fact', b'ds64', b'JUNK', b'PAD '}


def remap(chunks, position, *, time_reference=None):
    result = []
    cue_ids = None
    for kind, raw in chunks:
        if kind == b'cue ' and len(raw) >= 4:
            count, = struct.unpack_from('<I', raw)
            if len(raw) != 4 + count * 24:
                continue
            cues = []
            cue_ids = set()
            for i in range(count):
                values = list(struct.unpack_from('<II4sIII', raw, 4 + i * 24))
                mapped = position(values[5])
                if mapped is not None and 0 <= mapped < 2**32:
                    cue_ids.add(values[0])
                    values[1] = values[5] = int(mapped)
                    cues.append(struct.pack('<II4sIII', *values))
            raw = struct.pack('<I', len(cues)) + b''.join(cues)
        elif kind == b'smpl' and len(raw) >= 36:
            count, = struct.unpack_from('<I', raw, 28)
            if 36 + count * 24 > len(raw):
                continue
            loops = []
            for i in range(count):
                values = list(struct.unpack_from('<6I', raw, 36 + i * 24))
                a, b = position(values[2]), position(values[3])
                if a is not None and b is not None and max(a, b) < 2**32:
                    values[2:4] = sorted((int(a), int(b)))
                    loops.append(struct.pack('<6I', *values))
            header = bytearray(raw[:36]); struct.pack_into('<I', header, 28, len(loops))
            raw = bytes(header) + b''.join(loops) + raw[36 + count * 24:]
        elif kind == b'bext' and len(raw) >= 346 and time_reference is not None:
            raw = bytearray(raw)
            reference, = struct.unpack_from('<Q', raw, 338)
            struct.pack_into('<Q', raw, 338, max(0, min(2**64-1, int(time_reference(reference)))))
            raw = bytes(raw)
        result.append((kind, raw))
    if cue_ids is not None:
        filtered = []
        for kind, raw in result:
            if kind == b'LIST' and raw[:4] == b'adtl':
                items = []; offset = 4
                while offset + 8 <= len(raw):
                    tag, length = struct.unpack_from('<4sI', raw, offset)
                    end = offset + 8 + length + (length & 1)
                    if end > len(raw):
                        break
                    if tag not in (b'labl', b'note', b'ltxt') or (length >= 4 and struct.unpack_from('<I', raw, offset + 8)[0] in cue_ids):
                        items.append(raw[offset:end])
                    offset = end
                raw = b'adtl' + b''.join(items)
            filtered.append((kind, raw))
        result = filtered
    return tuple(result)


def replace(chunks, start, end, frames, *, sample_rate=None):
    if frames == end - start:
        return chunks
    def position(p):
        if p < start:
            return p
        if p >= end:
            return p + frames - (end - start)
        return None
    result = remap(chunks, position)
    return id3_metadata.timeline(result, 'replace', start, end, frames, sample_rate) if sample_rate else result


def crop(chunks, start, end, *, sample_rate=None):
    result = remap(chunks, lambda p: p - start if start <= p < end else None,
                   time_reference=lambda ref: ref + start)
    if sample_rate:
        result = id3_metadata.timeline(result, 'crop', start, end, 0, sample_rate)
        result = id3_metadata.audio_changed(result, end-start, sample_rate)
    return result


def resample(chunks, old_rate, new_rate, target_frames=None):
    scale = lambda p: (p * new_rate + old_rate // 2) // old_rate
    position = lambda p: min(max(0,target_frames-1),scale(p)) if target_frames is not None else scale(p)
    result = remap(chunks, position, time_reference=scale)
    # smpl's nanoseconds per sample must describe the new rate too.
    output = []
    for kind, raw in result:
        if kind == b'smpl' and len(raw) >= 36:
            raw = bytearray(raw); struct.pack_into('<I', raw, 8, round(1e9 / new_rate)); raw = bytes(raw)
        output.append((kind, raw))
    return tuple(output)


def insert_markers(destination, source, start, *, sample_rate=None):
    """Paste cue points/labels with fresh identifiers; retain destination file tags."""
    existing=[]
    output=[]
    for kind,raw in destination:
        if kind==b'cue ' and len(raw)>=4:
            count,=struct.unpack_from('<I',raw)
            if len(raw)==4+24*count:
                existing.extend(raw[4+i*24:28+i*24] for i in range(count))
        else:
            output.append((kind,raw))
    identifiers={struct.unpack_from('<I',raw)[0] for raw in existing}
    next_id=max(identifiers,default=-1)+1
    mapping={}
    for kind,raw in source:
        if kind!=b'cue ' or len(raw)<4:continue
        count,=struct.unpack_from('<I',raw)
        if len(raw)!=4+24*count:continue
        for i in range(count):
            values=list(struct.unpack_from('<II4sIII',raw,4+i*24))
            if next_id>=2**32 or values[5]+start>=2**32:continue
            mapping[values[0]]=next_id
            values[0]=next_id;next_id+=1
            values[1]=values[5]=values[5]+start
            existing.append(struct.pack('<II4sIII',*values))
    if existing:
        output.append((b'cue ',struct.pack('<I',len(existing))+b''.join(existing)))
    for kind,raw in source:
        if kind!=b'LIST' or raw[:4]!=b'adtl':continue
        chunks=[];offset=4
        while offset+8<=len(raw):
            tag,length=struct.unpack_from('<4sI',raw,offset)
            end=offset+8+length+(length&1)
            if end>len(raw):break
            if tag in (b'labl',b'note',b'ltxt') and length>=4:
                identifier,=struct.unpack_from('<I',raw,offset+8)
                if identifier in mapping:
                    chunk=bytearray(raw[offset:end]);struct.pack_into('<I',chunk,8,mapping[identifier]);chunks.append(bytes(chunk))
            offset=end
        if chunks:output.append((b'LIST',b'adtl'+b''.join(chunks)))
    result = tuple(output)
    return id3_metadata.paste_chapters(result, source, start, sample_rate) if sample_rate else result
