"""Versioned, self-contained .celp projects: JSON plus embedded float32 WAV audio."""
from dataclasses import asdict, replace
import io
import json
import os
from pathlib import Path
import re
import stat
import struct
import tempfile
import zipfile

import numpy as np

from .audio import AudioError, MAX_AUDIO_BYTES, read_wav
from .session import Session, Track, SessionClip, MAX_TRACKS, MAX_CLIPS, MAX_MEDIA, integer, text, number
from .envelopes import validate_points


PROJECT_FORMAT = "cooledit-linux-project"
PROJECT_VERSION = 2
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
_IDENTIFIER = re.compile(r"^[0-9a-f]{32}$")


def _id(value):
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise AudioError("The project contains an invalid identifier.")
    return value


def _float_wav(samples, rate):
    channels = samples.shape[1]
    payload = samples.astype("<f4", copy=False).tobytes()
    fmt = struct.pack("<HHIIHH", 3, channels, rate, rate * channels * 4, channels * 4, 32)
    body = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt
    body += b"fact" + struct.pack("<II", 4, len(samples))
    body += b"data" + struct.pack("<I", len(payload)) + payload
    return b"RIFF" + struct.pack("<I", len(body)) + body


def save_project(session, path):
    path = Path(path)
    active = {clip.media_id for track in session.tracks for clip in track.clips}
    media = [session.media[key] for key in sorted(active)]
    manifest = dict(format=PROJECT_FORMAT, version=PROJECT_VERSION, sample_rate=session.sample_rate,
        tracks=[asdict(track) for track in session.tracks],
        media=[dict(id=item.id, name=item.name, frames=len(item.samples), channels=item.samples.shape[1],
                    file=f"media/{item.id}.wav") for item in media])
    encoded = json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8")
    if len(encoded) > MAX_MANIFEST_BYTES:
        raise AudioError("The project description is too large.")
    previous_mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix="." + path.name + ".", suffix=".tmp", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3) as archive:
            archive.writestr("project.json", encoded)
            for item in media:
                archive.writestr(f"media/{item.id}.wav", _float_wav(item.samples, session.sample_rate))
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.chmod(temporary, previous_mode)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    session.path = path.resolve()
    session.mark_saved()


def _reject_constant(value):
    raise AudioError(f"The project contains a non-finite number: {value}.")


def _load_project(path, dsp):
    with zipfile.ZipFile(path, "r") as archive:
        members = archive.infolist()
        names = [item.filename for item in members]
        if len(names) != len(set(names)) or len(names) > MAX_MEDIA + 1 or "project.json" not in names:
            raise AudioError("The project archive has missing or duplicate entries.")
        if any(item.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED) or item.flag_bits & 1 for item in members):
            raise AudioError("The project archive uses an unsupported compression or encryption method.")
        if archive.getinfo("project.json").file_size > MAX_MANIFEST_BYTES:
            raise AudioError("The project description is too large.")
        if sum(item.file_size for item in members) > MAX_AUDIO_BYTES + MAX_MANIFEST_BYTES + MAX_MEDIA * 128:
            raise AudioError("The project exceeds the prototype's source-audio limit.")
        manifest = json.loads(archive.read("project.json").decode("utf-8"), parse_constant=_reject_constant)
        if not isinstance(manifest, dict) or manifest.get("format") != PROJECT_FORMAT:
            raise AudioError("This is not a SoundSausage project.")
        if type(manifest.get("version")) is not int or manifest["version"] not in (1, PROJECT_VERSION):
            raise AudioError("This project version is not supported.")
        rate = integer(manifest.get("sample_rate"), "Sample rate", 1000, 384000)
        tracks_data, media_data = manifest.get("tracks"), manifest.get("media")
        if not isinstance(tracks_data, list) or not 1 <= len(tracks_data) <= MAX_TRACKS:
            raise AudioError("Invalid track list.")
        if not isinstance(media_data, list) or len(media_data) > MAX_MEDIA:
            raise AudioError("Invalid media list.")
        session = Session(rate, 1, dsp=dsp, adopt_first_rate=False)
        bank, expected_names, total = {}, {"project.json"}, 0
        for record in media_data:
            if not isinstance(record, dict):
                raise AudioError("Invalid media record.")
            key = _id(record.get("id"))
            if key in bank:
                raise AudioError("Duplicate media identifier.")
            filename = f"media/{key}.wav"
            if record.get("file") != filename or filename not in names:
                raise AudioError("The project refers to missing or invalid embedded audio.")
            expected_names.add(filename)
            frames = integer(record.get("frames"), "Media frames", 1, MAX_AUDIO_BYTES // 4)
            channels = integer(record.get("channels"), "Media channels", 1, 2)
            total += frames * channels * 4
            if total > MAX_AUDIO_BYTES or archive.getinfo(filename).file_size != frames * channels * 4 + 56:
                raise AudioError("The embedded audio size does not match the project description.")
            audio = read_wav(io.BytesIO(archive.read(filename)))
            if audio.encoding != "float32" or audio.sample_rate != rate or audio.samples.shape != (frames, channels):
                raise AudioError("The embedded audio format does not match the session.")
            item = session._prepare_media(audio.samples, rate, text(record.get("name")))
            bank[key] = replace(item, id=key)
        if set(names) != expected_names:
            raise AudioError("The project contains unexpected archive entries.")
        session._media = bank
        tracks, track_ids, clip_ids = [], set(), set()
        for record in tracks_data:
            if not isinstance(record, dict):
                raise AudioError("Invalid track record.")
            key = _id(record.get("id"))
            if key in track_ids:
                raise AudioError("Duplicate track identifier.")
            track_ids.add(key)
            gain = number(record.get("gain"), 0, 100, "Track volume")
            pan = number(record.get("pan"), -1, 1, "Track pan")
            if type(record.get("muted")) is not bool or type(record.get("solo")) is not bool:
                raise AudioError("Invalid track mute/solo settings.")
            clips_data = record.get("clips")
            if not isinstance(clips_data, list) or len(clip_ids) + len(clips_data) > MAX_CLIPS:
                raise AudioError("Invalid or oversized clip list.")
            clips = []
            for entry in clips_data:
                if not isinstance(entry, dict):
                    raise AudioError("Invalid clip record.")
                entry = dict(entry)
                if manifest["version"] == 1:
                    if "volume_envelope" in entry or "pan_envelope" in entry:
                        raise AudioError("Project version 1 cannot contain envelope fields.")
                else:
                    for kind in ("volume", "pan"):
                        source_id = entry.get("media_id")
                        if source_id not in bank:
                            raise AudioError("A clip refers to missing audio.")
                        envelope_key = kind + "_envelope"
                        if envelope_key not in entry:
                            raise AudioError("The project is missing an envelope field.")
                        entry[envelope_key] = validate_points(entry[envelope_key], kind, len(bank[source_id].samples))
                clip = SessionClip(**entry)
                _id(clip.id)
                _id(clip.media_id)
                if clip.id in clip_ids:
                    raise AudioError("Duplicate clip identifier.")
                clip_ids.add(clip.id)
                session._validate_clip(clip)
                clips.append(clip)
            tracks.append(Track(key, text(record.get("name")), tuple(clips), gain, pan, record["muted"], record["solo"]))
        session._tracks = tuple(tracks)
        session.selected_track = tracks[0].id
        session.selected_clip = None
        session.path = Path(path).resolve()
        session.mark_saved()
        return session


def load_project(path, dsp=None):
    try:
        return _load_project(path, dsp)
    except AudioError:
        raise
    except (zipfile.BadZipFile, KeyError, TypeError, ValueError, UnicodeError, EOFError, struct.error) as error:
        raise AudioError(f"The project is invalid or damaged: {error}") from error
