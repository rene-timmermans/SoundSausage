"""Immutable source-frame automation curves, independent of timeline placement."""
from bisect import bisect_right
import math

from .audio import AudioError


MAX_ENVELOPE_POINTS = 512
KINDS = {"volume": (0.0, 2.0, 1.0), "pan": (-1.0, 1.0, 0.0)}


def validate_points(points, kind, source_frames):
    if kind not in KINDS or not isinstance(points, (tuple, list)) or len(points) > MAX_ENVELOPE_POINTS:
        raise AudioError("An envelope supports at most 512 points.")
    low, high, _ = KINDS[kind]
    result, previous = [], -1
    for point in points:
        if not isinstance(point, (tuple, list)) or len(point) != 2:
            raise AudioError("Each envelope point needs a source frame and a value.")
        frame, value = point
        if type(frame) is not int or not previous < frame < source_frames:
            raise AudioError("Envelope frames must be unique, ordered and inside the source audio.")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
            raise AudioError(f"Envelope values must be between {low:g} and {high:g}.")
        result.append((frame, float(value)))
        previous = frame
    return tuple(result)


def value_at(points, frame, neutral):
    if not points:
        return neutral
    index = bisect_right(points, (frame, math.inf))
    if index == 0:
        return points[0][1]
    if index == len(points):
        return points[-1][1]
    a, b = points[index - 1], points[index]
    return a[1] + (b[1] - a[1]) * ((frame - a[0]) / (b[0] - a[0]))


def remap_points(points, begin, end, new_frames, neutral):
    """Keep the visible curve's shape when edited audio replaces a clip's source."""
    if not points:
        return ()
    first = value_at(points, begin, neutral)
    if new_frames == 1 or end - begin == 1:
        return ((0, first),) if new_frames == 1 else ((0, first), (new_frames - 1, first))
    samples = [(begin, first), *(p for p in points if begin < p[0] < end - 1),
               (end - 1, value_at(points, end - 1, neutral))]
    mapped = {round((frame - begin) * (new_frames - 1) / (end - begin - 1)): value for frame, value in samples}
    mapped[0], mapped[new_frames - 1] = first, samples[-1][1]
    if len(mapped) > MAX_ENVELOPE_POINTS:
        keys = sorted(mapped)
        if mapped[keys[0]] == mapped[keys[1]]:
            del mapped[keys[0]]
        keys = sorted(mapped)
        if len(mapped) > MAX_ENVELOPE_POINTS and mapped[keys[-1]] == mapped[keys[-2]]:
            del mapped[keys[-1]]
    return tuple(sorted(mapped.items()))
