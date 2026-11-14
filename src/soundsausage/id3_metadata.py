"""ID3 chapter timelines and explicitly recognised audio-dependent information."""
from io import BytesIO
import struct

from .errors import AudioError
from .operations import progress


UNKNOWN = 0xffffffff
DEPENDENT = frozenset(('ASPI', 'AENC', 'ETCO', 'EQU2', 'MLLT', 'POSS', 'SEEK',
    'SYLT', 'SYTC', 'RVA2', 'RVAD', 'SIGN', 'TSIZ', 'TENC', 'TSSE', 'TDEN', 'TDTG'))
INFO_FIELDS = {b'INAM': 'TIT2', b'IART': 'TPE1', b'IPRD': 'TALB', b'IGNR': 'TCON',
               b'ICRD': 'TDRC', b'ITRK': 'TRCK', b'ICOP': 'TCOP', b'ICMT': 'COMM'}


def load(raw, *, strict=False):
    try:
        from mutagen.id3 import ID3
        from mutagen import MutagenError
    except ImportError:
        if strict:
            raise AudioError('MP3 support requires FFmpeg and Mutagen. Install the application dependencies.')
        return None
    try:
        return ID3(BytesIO(raw))
    except (MutagenError, ValueError):
        if strict:
            raise AudioError('Invalid MP3 metadata.')
        # Unreadable embedded WAV tags remain opaque; they cannot be exported as ID3.
        return None


def dump(tags):
    from .metadata import MAX_METADATA_BYTES
    output = BytesIO()
    tags.save(output, v2_version=4, padding=lambda _: 0)
    raw = output.getvalue()
    if len(raw) > MAX_METADATA_BYTES:
        raise AudioError('MP3 metadata exceeds the supported 16 MiB size.')
    return raw


def modify(chunks, operation):
    result = []
    for kind, raw in chunks:
        if kind.lower() == b'id3 ':
            progress(0, 1, 'Updating file information')
            tags = load(raw)
            if tags is not None:
                operation(tags)
                raw = dump(tags)
            progress(1, 1, 'Updating file information')
        result.append((kind, raw))
    from .metadata import MAX_METADATA_BYTES
    if sum(len(raw) for _, raw in result) > MAX_METADATA_BYTES:
        raise AudioError('MP3 metadata exceeds the supported 16 MiB size.')
    return tuple(result)


def clean_toc(tags):
    chapters = {c.element_id: c.start_time for c in tags.getall('CHAP')}
    tables = {}
    for table in tags.getall('CTOC'):
        if table.element_id in chapters:
            tags.delall(table.HashKey)
        else:
            tables[table.element_id] = table
    times = dict(chapters)
    status = {}
    # Iterative post-order traversal: linear work, no dangling references or cycles.
    for root in tables:
        if status.get(root):
            continue
        status[root] = 1
        stack = [(root, iter(list(tables[root].child_element_ids)))]
        while stack:
            name, iterator = stack[-1]
            child = next(iterator, None)
            if child is not None:
                if child in tables:
                    if status.get(child) == 1:
                        tables[name].child_element_ids = [c for c in tables[name].child_element_ids if c != child]
                    elif not status.get(child):
                        status[child] = 1
                        stack.append((child, iter(list(tables[child].child_element_ids))))
                continue
            table = tables[name]
            children = list(dict.fromkeys(c for c in table.child_element_ids if c in times))
            if not children:
                tags.delall(table.HashKey)
            else:
                if table.flags & 1:
                    children.sort(key=lambda c: times[c])
                table.child_element_ids = children
                times[name] = min(times[c] for c in children)
            status[name] = 2
            stack.pop()


def _set_chapter(tags, chapter, a, b):
    a, b = max(0, round(a)), min(UNKNOWN-1, round(b))
    if b <= a or a >= UNKNOWN:
        tags.delall(chapter.HashKey)
        return
    chapter.start_time, chapter.end_time = a, b
    chapter.start_offset = chapter.end_offset = UNKNOWN


def timeline(chunks, mode, start, end, frames, rate):
    """Map half-open chapter ranges; WAV sample-index mapping is kept separate."""
    scale = 1000 / rate
    left, right, inserted = start*scale, end*scale, frames*scale
    def change(tags):
        for chapter in list(tags.getall('CHAP')):
            a, b = chapter.start_time, chapter.end_time
            if a == UNKNOWN or b <= a:
                tags.delall(chapter.HashKey)
                continue
            if mode == 'crop':
                a, b = max(a, left)-left, min(b, right)-left
            elif mode == 'reverse':
                if left <= a and b <= right:
                    a, b = left+right-b, left+right-a
                elif a < right and b > left and not (a <= left and b >= right):
                    # A partly reversed chapter would describe disjoint audio.
                    tags.delall(chapter.HashKey)
                    continue
            else:
                def position(p, is_end):
                    if p < left or (is_end and p == left):
                        return p
                    if p >= right:
                        return p + inserted-(right-left)
                    if mode == 'stretch':
                        return left + (p-left)*inserted/(right-left)
                    return left + (inserted if is_end else 0)
                a, b = position(a, False), position(b, True)
            _set_chapter(tags, chapter, a, b)
        clean_toc(tags)
    return modify(chunks, change)


def sanitise(tags, frames, rate):
    """Drop stale measurements/timestamps and refresh duration before audio changes."""
    from mutagen.id3 import TLEN
    pending, seen = [tags], set()
    while pending:
        level = pending.pop()
        if id(level) in seen:
            continue
        seen.add(id(level))
        for name in DEPENDENT:
            level.delall(name)
        for frame in list(level.values()):
            name = getattr(frame, 'desc', '').strip().casefold().replace(' ', '_').replace('-', '_')
            if frame.FrameID in ('TXXX', 'COMM') and (
                    name.startswith(('replaygain_', 'r128_', 'mp3gain_', 'accuraterip_')) or
                    name in ('itunnorm', 'itunsmpb', 'acoustid_fingerprint', 'chromaprint_fingerprint')):
                level.delall(frame.HashKey)
            subframes = getattr(frame, 'sub_frames', None)
            if subframes is not None:
                pending.append(subframes)
    duration = round(frames*1000/rate)
    tags.add(TLEN(encoding=3, text=[str(duration)]))
    for chapter in list(tags.getall('CHAP')):
        _set_chapter(tags, chapter, chapter.start_time, min(chapter.end_time, duration))
    clean_toc(tags)


def audio_changed(chunks, frames, rate):
    return modify(chunks, lambda tags: sanitise(tags, frames, rate))


def musical_change(chunks, *, tempo=False, pitch=False):
    def change(tags):
        if tempo:
            tags.delall('TBPM')
        if pitch:
            tags.delall('TKEY')
        for frame in list(tags.getall('TXXX')):
            name = frame.desc.strip().casefold().replace(' ', '_')
            if (tempo and name in ('bpm', 'tempo')) or (pitch and name in ('key', 'initial_key', 'initialkey')):
                tags.delall(frame.HashKey)
    return modify(chunks, change)


def paste_chapters(destination, source, start, rate):
    """Import chapter names and hierarchy with fresh IDs; keep destination file tags."""
    if not any(kind.lower() == b'id3 ' for kind, _ in source):
        return destination
    from mutagen.id3 import ID3, CTOC
    source_tags = next((load(raw) for kind, raw in source if kind.lower() == b'id3 '), None)
    if source_tags is None or not source_tags.getall('CHAP'):
        return destination
    destination_raw = next((raw for kind, raw in destination if kind.lower() == b'id3 '), None)
    tags = load(destination_raw) if destination_raw is not None else ID3()
    if tags is None:
        return destination
    clean_toc(source_tags)
    used = {c.element_id for name in ('CHAP', 'CTOC') for c in tags.getall(name)}
    counter = 0
    def fresh():
        nonlocal counter
        while True:
            name = 'ss-paste-'+str(counter); counter += 1
            if name not in used:
                used.add(name)
                return name
    elements = [c for name in ('CHAP', 'CTOC') for c in source_tags.getall(name)]
    mapping = {c.element_id: fresh() for c in elements}
    shift = start*1000/rate
    for element in elements:
        element.element_id = mapping[element.element_id]
        if element.FrameID == 'CHAP':
            element.start_time = min(UNKNOWN-1, round(element.start_time+shift))
            element.end_time = min(UNKNOWN-1, round(element.end_time+shift))
            element.start_offset = element.end_offset = UNKNOWN
        else:
            element.child_element_ids = [mapping[c] for c in element.child_element_ids if c in mapping]
        tags.add(element)
    clean_toc(tags)
    nodes = {c.element_id: c for name in ('CHAP', 'CTOC') for c in tags.getall(name)}
    referenced = {c for table in tags.getall('CTOC') for c in table.child_element_ids}
    roots = [name for name in nodes if name not in referenced]
    for table in tags.getall('CTOC'):
        table.flags &= ~2
    while len(roots) > 255:
        grouped = []
        for offset in range(0, len(roots), 255):
            name = fresh()
            tags.add(CTOC(element_id=name, flags=1, child_element_ids=roots[offset:offset+255]))
            grouped.append(name)
        roots = grouped
    if len(roots) == 1 and roots[0] in nodes and nodes[roots[0]].FrameID == 'CTOC':
        nodes[roots[0]].flags |= 2
    elif roots:
        tags.add(CTOC(element_id=fresh(), flags=3, child_element_ids=roots))
    clean_toc(tags)
    result = tuple((kind, raw) for kind, raw in destination if kind.lower() != b'id3 ')
    return result + ((b'id3 ', dump(tags)),)


def info_items(raw):
    """Parse bounded RIFF INFO subchunks; return an explicit malformed marker."""
    offset = 4
    while offset < len(raw):
        if offset+8 > len(raw):
            yield None, None
            return
        name, length = struct.unpack_from('<4sI', raw, offset)
        stop = offset+8+length
        if stop > len(raw) or stop+(length & 1) > len(raw):
            yield None, None
            return
        value = raw[offset+8:stop].rstrip(b'\0')
        try:
            text = value.decode('utf-8')
        except UnicodeDecodeError:
            text = value.decode('cp1252', 'replace')
        yield name, text
        offset = stop+(length & 1)


def export_tags(chunks, *, sample_rate=None, frames=None):
    """Map known INFO fields; report every omitted field, including conflicts."""
    from mutagen import id3
    raw = next((raw for kind, raw in chunks if kind.lower() == b'id3 '), None)
    tags = load(raw, strict=True) if raw is not None else id3.ID3()
    omitted = set()
    from .markers import export_cues
    handled=export_cues(chunks,sample_rate,frames,tags)
    id3_count = 0
    for index,(kind, raw) in enumerate(chunks):
        if index in handled:continue
        if kind.lower() == b'id3 ':
            id3_count += 1
            if id3_count > 1:
                omitted.add('ID3/'+str(id3_count))
            continue
        if kind != b'LIST' or raw[:4] != b'INFO':
            omitted.add(kind.decode('ascii', 'replace'))
            continue
        for name, text in info_items(raw):
            if name == b'ISFT':
                # File-encoder information is refreshed from the new MP3 encoder.
                continue
            target = INFO_FIELDS.get(name)
            if target is None:
                omitted.add('LIST/INFO'+('/'+name.decode('ascii','replace') if name else ''))
                continue
            existing = tags.getall(target)
            if existing:
                if not any(text in map(str, getattr(frame, 'text', ())) for frame in existing):
                    omitted.add('LIST/INFO/'+name.decode('ascii','replace'))
            elif target == 'COMM':
                tags.add(id3.COMM(encoding=3, lang='eng', desc='', text=[text]))
            else:
                try:
                    frame = getattr(id3, target)(encoding=3, text=[text])
                    if text and (not frame.text or not str(frame.text[0])):
                        omitted.add('LIST/INFO/'+name.decode('ascii','replace'))
                    else:
                        tags.add(frame)
                except ValueError:
                    omitted.add('LIST/INFO/'+name.decode('ascii','replace'))
    return tags, omitted
