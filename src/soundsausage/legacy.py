"""Read-only inspection and import of a limited legacy SES format.

Field meanings are inferred from the six user-generated reference sessions.
Unsupported envelopes, flags and chunks are rejected rather than flattened.
"""
from dataclasses import replace
import hashlib
import math
import ntpath
from pathlib import Path
import struct

from .audio import AudioError, MAX_AUDIO_BYTES, read_wav
from .session import Session, Track, SessionClip, identifier, number


class MissingMediaError(AudioError):
    def __init__(self, names):
        self.names = names
        super().__init__("Locate the WAV files used by this session: " + ", ".join(names))


def _counted(payload, label):
    if len(payload) < 4:
        raise AudioError(f"The SES {label} chunk is truncated.")
    count = struct.unpack_from("<I", payload)[0]
    if count > 4096 or len(payload) != 4 + count * 72:
        raise AudioError(f"The SES {label} record layout is unsupported.")
    return count


def inspect_ses(path):
    path = Path(path)
    if path.stat().st_size > 8 * 1024 * 1024:
        raise AudioError("This SES inspector supports at most 8 MiB of project metadata.")
    data = path.read_bytes()
    if len(data) < 12 or data[:8] != b"COOLNESS" or struct.unpack_from("<I", data, 8)[0] != len(data) - 12:
        raise AudioError("This is not a supported SES session, or its length is invalid.")
    chunks, payloads, warnings = [], {}, []
    cursor = 12
    while cursor < len(data):
        special = data[cursor:cursor + 8] == b"LISTFILE"
        tag_size = 8 if special else 4
        if cursor + tag_size + 4 > len(data):
            raise AudioError("The SES chunk header is truncated.")
        kind = data[cursor:cursor + tag_size].decode("ascii", "replace")
        declared = struct.unpack_from("<I", data, cursor + tag_size)[0]
        begin = cursor + tag_size + 4
        actual = declared
        recovered = False
        if kind == "trks" and (declared > len(data) - begin) and data[begin + 4:begin + 12] == b"LISTFILE":
            # The user's empty reference has negative/uninitialized length and
            # count words. Only recover that exact, otherwise empty layout.
            header = payloads.get("hdr ", b"")
            if len(header) == 40 and struct.unpack_from("<I", header, 8)[0] == 0:
                actual = 4
                recovered = True
                warnings.append("Empty SES track-length/count fields are invalid; no track records were present.")
        if actual > len(data) - begin or kind in payloads:
            raise AudioError("The SES has an invalid chunk length or duplicate chunk.")
        payloads[kind] = data[begin:begin + actual]
        chunks.append(dict(kind=kind, offset=cursor, payload_offset=begin,
                           declared_size=declared, actual_size=actual, recovered_empty=recovered))
        cursor = begin + actual  # These SES chunks do not have RIFF's even-byte padding.
    required = {"hdr ", "vers", "stat", "trks", "LISTFILE", "blk ", "envp", "cues"}
    if not required <= set(payloads):
        raise AudioError("The SES is missing a required chunk.")
    header = payloads["hdr "]
    if len(header) != 40:
        raise AudioError("Unsupported SES header layout.")
    rate, unknown, count_hint, bits, flags, left, right, offset = struct.unpack("<IIIHHddd", header)
    version = payloads["vers"].split(b"\0", 1)[0].decode("cp1252", "replace")
    recovered = any(item["recovered_empty"] for item in chunks)
    tracks = []
    if not recovered:
        for index in range(_counted(payloads["trks"], "track")):
            p = 4 + index * 72
            row = payloads["trks"][p:p + 72]
            l, r, properties = struct.unpack_from("<ddI", row)
            name = row[20:32].split(b"\0", 1)[0].decode("cp1252", "replace") or f"Track {index + 1}"
            tracks.append(dict(index=index, left=l, right=r, flags=properties, name=name,
                               tail=list(struct.unpack_from("<4i", row, 56))))
    files, cursor = [], 0
    file_data = payloads["LISTFILE"]
    while cursor < len(file_data):
        if cursor + 8 > len(file_data) or file_data[cursor:cursor + 4] != b"wav ":
            raise AudioError("Unsupported SES media-list entry.")
        length = struct.unpack_from("<I", file_data, cursor + 4)[0]
        start = cursor + 8
        if length < 9 or start + length > len(file_data):
            raise AudioError("The SES media path is truncated.")
        key, properties = struct.unpack_from("<II", file_data, start)
        raw = file_data[start + 8:start + length]
        if not raw.endswith(b"\0"):
            raise AudioError("The SES media path is not terminated.")
        stored = raw[:-1].decode("cp1252", "replace")
        files.append(dict(id=key, flags=properties, path=stored, basename=ntpath.basename(stored)))
        cursor = start + length
    blocks = []
    for index in range(_counted(payloads["blk "], "clip")):
        p = 4 + index * 72
        row = payloads["blk "][p:p + 72]
        l, r, properties = struct.unpack_from("<ddI", row)
        position, frames, track, source_start, source_id, clip_id, a, b, c, d = struct.unpack_from("<10I", row, 32)
        blocks.append(dict(index=index, left=l, right=r, flags=properties, start=position,
            frames=frames, track=track, source_start=source_start, source_id=source_id,
            clip_id=clip_id, tail=[a, b, c, d]))
    env = payloads["envp"]
    if len(env) < 4:
        raise AudioError("The SES envelope chunk is truncated.")
    envelope_count = struct.unpack_from("<I", env)[0]
    if envelope_count > 4096:
        raise AudioError("Too many SES envelopes.")
    envelopes, cursor = [], 4
    for _ in range(envelope_count):
        if cursor + 16 > len(env):
            raise AudioError("The SES envelope header is truncated.")
        header_size, block, volumes, pans = struct.unpack_from("<4I", env, cursor)
        if header_size != 16 or volumes + pans > 8192 or cursor + 16 + (volumes + pans) * 24 > len(env):
            raise AudioError("Unsupported SES envelope layout.")
        cursor += 16
        points = []
        for _ in range(volumes + pans):
            frame, point_flags, value, curve = struct.unpack_from("<IIdd", env, cursor)
            points.append(dict(frame=frame, flags=point_flags, value=value, curve=curve))
            cursor += 24
        envelopes.append(dict(block=block, volume=points[:volumes], pan=points[volumes:]))
    if cursor != len(env):
        raise AudioError("Unexpected trailing SES envelope data.")
    cues = payloads["cues"]
    if len(cues) < 4:
        raise AudioError("Truncated SES cue data.")
    if recovered and (files or blocks or envelopes or struct.unpack_from("<I", cues)[0]):
        raise AudioError("Cannot recover track metadata in a nonempty SES.")
    return dict(path=str(path.resolve()), sha256=hashlib.sha256(data).hexdigest(), size=len(data),
        version=version, sample_rate=rate, sample_bits=bits, header_flags=flags,
        header_unknown=unknown, header_count_hint=count_hint, header_left=left, header_right=right,
        header_offset=offset, chunks=chunks, tracks=tracks, files=files, blocks=blocks,
        envelopes=envelopes, cue_count=struct.unpack_from("<I", cues)[0], cue_bytes=len(cues),
        warnings=warnings)


def _gain_pan(left, right):
    left = number(left, 0, 100, "Legacy left gain")
    right = number(right, 0, 100, "Legacy right gain")
    gain = max(left, right)
    if gain == 0:
        return 0.0, 0.0
    pan = 1 - left / gain if right >= left else right / gain - 1
    return gain, pan


def load_legacy_project(path, dsp=None, media_dirs=()):
    report = inspect_ses(path)
    kinds = {chunk["kind"] for chunk in report["chunks"]}
    if kinds != {"hdr ", "vers", "stat", "trks", "LISTFILE", "blk ", "envp", "cues"}:
        raise AudioError("This SES contains chunks the limited importer does not support.")
    if report["version"] != "Cool Edit Pro 1.0" or report["sample_bits"] != 16 or report["header_flags"] != 1:
        raise AudioError("This importer supports the tested legacy SES layout with 16-bit source audio.")
    if report["header_left"] != 1 or report["header_right"] != 1 or report["header_offset"] != 0:
        raise AudioError("Non-default SES master settings are not supported yet.")
    if len(report["tracks"]) > 32 or len(report["files"]) > 128:
        raise AudioError("This SES exceeds the track or media limits.")
    if report["cue_count"] or report["cue_bytes"] != 4:
        raise AudioError("SES cue import is not implemented yet.")
    by_envelope = {}
    for entry in report["envelopes"]:
        if entry["block"] in by_envelope:
            raise AudioError("Duplicate SES envelope reference.")
        by_envelope[entry["block"]] = entry
        for points, expected in ((entry["volume"], 1.0), (entry["pan"], 0.5)):
            if not points or any(p["value"] != expected or p["flags"] != 0 or p["curve"] != 0 for p in points):
                raise AudioError("SES volume/pan automation has not been validated for import yet.")
    if set(by_envelope) != set(range(len(report["blocks"]))):
        raise AudioError("The SES clip/envelope references are incomplete.")
    roots = [Path(path).resolve().parent, *(Path(folder).resolve() for folder in media_dirs)]
    located, missing = {}, []
    for record in report["files"]:
        basename = record["basename"]
        if not basename or basename in (".", "..") or Path(basename).suffix.lower() != ".wav" or record["flags"] != 17:
            raise AudioError("Unsupported SES source-file description.")
        candidate = next((root / basename for root in roots if (root / basename).is_file()), None)
        if candidate is None:
            missing.append(basename)
        if record["id"] in located:
            raise AudioError("Duplicate SES media identifier.")
        located[record["id"]] = candidate
    if missing:
        raise MissingMediaError(missing)
    session = Session(report["sample_rate"], max(1, len(report["tracks"])), dsp=dsp, adopt_first_rate=False)
    bank, media_map, total = {}, {}, 0
    for record in report["files"]:
        audio = read_wav(located[record["id"]])
        if audio.sample_rate != session.sample_rate:
            raise AudioError("The SES source audio has a different sample rate.")
        total += audio.samples.nbytes
        if total > MAX_AUDIO_BYTES:
            raise AudioError("The SES source audio exceeds the supported address space.")
        item = session._prepare_media(audio.samples, audio.sample_rate, record["basename"], audio.metadata)
        bank[item.id] = item
        media_map[record["id"]] = item.id
    session._media = bank
    tracks = list(session.tracks)
    for index, record in enumerate(report["tracks"]):
        if record["flags"] != 0 or record["tail"] != [1, 1, 1, -1]:
            raise AudioError("This SES has track flags or routing the limited importer does not understand.")
        gain, pan = _gain_pan(record["left"], record["right"])
        tracks[index] = replace(tracks[index], name=record["name"], gain=gain, pan=pan)
    for record in report["blocks"]:
        if record["flags"] != 0 or record["tail"] != [0, 1, 0, 0xffffffff]:
            raise AudioError("This SES has clip flags the limited importer does not understand.")
        if record["track"] >= len(report["tracks"]) or record["source_id"] not in media_map:
            raise AudioError("Invalid SES clip track or source reference.")
        source = bank[media_map[record["source_id"]]]
        gain, pan = _gain_pan(record["left"], record["right"])
        clip = SessionClip(identifier(), source.id, source.name, record["start"], record["source_start"],
                           record["source_start"] + record["frames"], gain=gain, pan=pan)
        session._validate_clip(clip)
        index = record["track"]
        tracks[index] = replace(tracks[index], clips=(*tracks[index].clips, clip))
    session._tracks = tuple(tracks)
    session.selected_track = tracks[0].id
    session.path = None  # Never save over the original .ses.
    session.display_name = Path(path).name + " (import)"
    session.legacy_report = report
    session.mark_saved()
    return session
