"""Compare a SES render and PCM16 stereo VM mix without alignment or gain changes."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import wave

import numpy as np

from soundsausage.audio import read_wav, write_wav
from soundsausage.legacy import load_legacy_project


def file_record(path):
    path = Path(path)
    return dict(path=str(path), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def tail_record(samples):
    return dict(frames=len(samples), silent=bool(np.all(samples == 0)),
                peak_per_channel=np.max(np.abs(samples), axis=0).tolist() if len(samples) else [0.0, 0.0])


def pcm16_metrics(actual, reference):
    difference = (np.frombuffer(actual, dtype="<i2").astype(np.int32)
                  - np.frombuffer(reference, dtype="<i2").astype(np.int32)).reshape(-1, 2)
    return dict(exact_shared_audio_bytes=actual == reference,
                maximum_error_lsb_per_channel=np.max(np.abs(difference), axis=0).tolist(),
                rms_error_lsb_per_channel=np.sqrt(np.mean(difference.astype(np.float64) ** 2, axis=0)).tolist(),
                differing_samples_per_channel=np.count_nonzero(difference, axis=0).tolist())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    session = load_legacy_project(args.session)
    reference = read_wav(args.reference)
    actual = session.render()
    if reference.encoding != "pcm16" or reference.samples.shape[1] != 2:
        parser.error("The VM reference must be stereo PCM16 WAV.")
    if reference.sample_rate != session.sample_rate:
        parser.error("Samplerates differ; this tool does not resample.")
    shared = min(len(actual), len(reference.samples))
    if not shared:
        parser.error("At least one shared audio frame is required.")
    difference = reference.samples[:shared].astype(np.float64) - actual[:shared]
    equal_length = len(actual) == len(reference.samples)
    shared_equal = bool(np.array_equal(reference.samples[:shared], actual[:shared]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Compare encoded audio independently of our own WAV decoder, excluding headers.
    with wave.open(str(args.reference), "rb") as stream:
        reference_pcm = stream.readframes(shared)
    with tempfile.TemporaryDirectory(dir=args.out.parent) as folder:
        exported = Path(folder) / "native-mix.wav"
        write_wav(exported, actual, session.sample_rate, "pcm16")
        with wave.open(str(exported), "rb") as stream:
            standard_bytes = stream.readframes(shared)
            standard_pcm = pcm16_metrics(standard_bytes, reference_pcm)
        write_wav(exported, actual, session.sample_rate, "pcm16", pcm16_symmetric=True)
        with wave.open(str(exported), "rb") as stream:
            session_bytes = stream.readframes(shared)
            session_pcm = pcm16_metrics(session_bytes, reference_pcm)
    clips = [clip for track in session.tracks for clip in track.clips]
    boundaries = sorted({0, shared, *(frame for clip in clips for frame in (clip.start, clip.end)
                                     if 0 <= frame <= shared)})
    segments = [dict(start_frame=lo, end_frame_exclusive=hi,
                     active_sources=[session.media[clip.media_id].name for clip in clips
                                     if clip.start < hi and clip.end > lo],
                     native_peak_per_channel=np.max(np.abs(actual[lo:hi]), axis=0).tolist(),
                     reference_peak_per_channel=np.max(np.abs(reference.samples[lo:hi]), axis=0).tolist(),
                     session_pcm16_export=pcm16_metrics(session_bytes[lo * 4:hi * 4], reference_pcm[lo * 4:hi * 4]),
                     standard_pcm16_export=pcm16_metrics(standard_bytes[lo * 4:hi * 4], reference_pcm[lo * 4:hi * 4]))
                for lo, hi in zip(boundaries, boundaries[1:])]
    report = dict(
        session=file_record(args.session), reference=file_record(args.reference),
        sources=[file_record(args.session.parent / item.name) for item in session.media.values()],
        sample_rate=session.sample_rate, channels=2, reference_encoding=reference.encoding,
        native_frames=len(actual), reference_frames=len(reference.samples), shared_frames=shared,
        reference_minus_native_frames=len(reference.samples) - len(actual),
        reference_minus_native_seconds=(len(reference.samples) - len(actual)) / session.sample_rate,
        equal_length=equal_length, exact_shared_samples=shared_equal,
        exact_full_samples=equal_length and shared_equal,
        exact_shared_pcm16_bytes=session_pcm["exact_shared_audio_bytes"],
        session_pcm16_export=dict(limits=[-32767, 32767], **session_pcm),
        standard_pcm16_export=dict(limits=[-32768, 32767], **standard_pcm),
        raw_float_comparison="Unclipped render against quantized reference; nonzero errors can be due to PCM conversion.",
        segments=segments,
        maximum_absolute_error_per_channel=np.max(np.abs(difference), axis=0).tolist(),
        rms_error_per_channel=np.sqrt(np.mean(difference * difference, axis=0)).tolist(),
        differing_samples_per_channel=np.count_nonzero(difference, axis=0).tolist(),
        reference_tail=tail_record(reference.samples[shared:]), native_tail=tail_record(actual[shared:]),
        comparison="Frame zero aligned; no shift, resampling, gain adjustment or tolerance.",
        coverage="This supplied mix and encoding only; intermediate pan positions, other gains, fades and effects remain untested.",
    )
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    args.out.write_text(output)
    print(output, end="")


if __name__ == "__main__":
    main()
