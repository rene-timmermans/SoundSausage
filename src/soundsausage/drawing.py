"""Sparse, analytical waveform strokes; audio is allocated only on confirmation."""
import math


class DrawingStroke:
    def __init__(self, document, channel, visible_frames, width):
        self.document = document
        self.channel = channel
        # One group per two logical pixels; cap its audio extent, not the gesture.
        self.stride = min(document.sample_rate, max(1, math.ceil(2 * visible_frames / width)))
        self.size = self.stride
        self.groups = {}
        self.last = None

    def add(self, frame, value):
        frame = max(0, min(self.document.frames - 1, int(frame)))
        value = max(-1.0, min(1.0, float(value)))
        previous = self.last or (frame, value)
        a, b = sorted((previous, (frame, value)))
        first = a[0] // self.stride * self.stride
        last = b[0] // self.stride * self.stride
        for start in range(first, last + 1, self.stride):
            end = min(self.document.frames, start + self.size)
            def at(position):
                if a[0] == b[0]:
                    return value
                fraction = max(0.0, min(1.0, (position-a[0])/(b[0]-a[0])))
                return a[1] + (b[1]-a[1])*fraction
            self.groups[start] = (end, at(start), at(end-1))
        self.last = frame, value

    def patches(self):
        return tuple((start, *self.groups[start]) for start in sorted(self.groups))
