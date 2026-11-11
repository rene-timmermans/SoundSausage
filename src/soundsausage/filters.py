"""Validated EQ designs; normalized coefficients shared by audio and response plot.

Biquad equations: Robert Bristow-Johnson, W3C Audio EQ Cookbook,
https://www.w3.org/TR/audio-eq-cookbook/ (shelves use monotonic slope S=1).
"""
import math

import numpy as np

GRAPHIC_CENTRES = (31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000)
EFFECTS = ("graphic_eq", "parametric_eq", "filter")


def number(value, low, high, label):
    if isinstance(value, (bool, str)):
        raise ValueError(f"Invalid {label}.")
    try:
        value = float(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError(f"Invalid {label}.") from error
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{label} must be between {low:g} and {high:g}.")
    return value


def frequency_limit(sample_rate):
    return number(sample_rate, 1000, 768000, "Sample rate") * .499


def biquad(kind, frequency, sample_rate, gain_db=0, q=1 / math.sqrt(2)):
    frequency = number(frequency, 1, frequency_limit(sample_rate), "Frequency (Hz)")
    gain_db = number(gain_db, -24, 24, "Gain (dB)")
    q = number(q, .1, 50, "Q")
    w = 2 * math.pi * frequency / sample_rate
    c, s = math.cos(w), math.sin(w)
    alpha = s / (2*q)
    a = 10 ** (gain_db / 40)
    if kind in ("bell", "low_shelf", "high_shelf") and gain_db == 0:
        return (1., 0., 0., 0., 0.)
    if kind == "bell":
        b0, b1, b2 = 1+alpha*a, -2*c, 1-alpha*a
        a0, a1, a2 = 1+alpha/a, -2*c, 1-alpha/a
    elif kind in ("low_shelf", "high_shelf"):
        t = math.sqrt(2*a)*s
        if kind == "low_shelf":
            b0, b1, b2 = a*((a+1)-(a-1)*c+t), 2*a*((a-1)-(a+1)*c), a*((a+1)-(a-1)*c-t)
            a0, a1, a2 = (a+1)+(a-1)*c+t, -2*((a-1)+(a+1)*c), (a+1)+(a-1)*c-t
        else:
            b0, b1, b2 = a*((a+1)+(a-1)*c+t), -2*a*((a-1)+(a+1)*c), a*((a+1)+(a-1)*c-t)
            a0, a1, a2 = (a+1)-(a-1)*c+t, 2*((a-1)-(a+1)*c), (a+1)-(a-1)*c-t
    else:
        a0, a1, a2 = 1+alpha, -2*c, 1-alpha
        if kind == "low_pass":
            b0, b1, b2 = (1-c)/2, 1-c, (1-c)/2
        elif kind == "high_pass":
            b0, b1, b2 = (1+c)/2, -(1+c), (1+c)/2
        elif kind == "band_pass":
            b0, b1, b2 = alpha, 0, -alpha
        elif kind == "notch":
            b0, b1, b2 = 1, -2*c, 1
        else:
            raise ValueError("Unknown filter type.")
    return (b0/a0, b1/a0, b2/a0, a1/a0, a2/a0)


def design(name, sample_rate, **settings):
    """Return a bounded cascade and output multiplier, with no audio allocation.

    Graphic bands above the usable frequency limit are deliberately omitted.
    Parametric frequencies are explicit: out-of-range enabled bands are errors.
    """
    maximum = frequency_limit(sample_rate)
    options = dict(settings)
    output = number(options.pop("output_db", 0), -24, 24, "Output gain (dB)")
    stages = []
    if name == "graphic_eq":
        gains = options.pop("gains", (0,) * 10)
        if not isinstance(gains, (tuple, list)) or len(gains) != 10:
            raise ValueError("Graphic EQ needs ten band gains.")
        for frequency, gain in zip(GRAPHIC_CENTRES, gains):
            gain = number(gain, -24, 24, "Band gain (dB)")
            if frequency <= maximum and gain != 0:
                # One octave between half-gain points (analogue Q definition).
                stages.append(biquad("bell", frequency, sample_rate, gain, math.sqrt(2)))
    elif name == "parametric_eq":
        bands = options.pop("bands", ())
        if not isinstance(bands, (tuple, list)) or len(bands) > 16:
            raise ValueError("Parametric EQ supports up to sixteen bands.")
        for band in bands:
            if not isinstance(band, dict) or set(band) - {"enabled", "kind", "frequency", "gain_db", "q"}:
                raise ValueError("Invalid parametric band.")
            enabled = band.get("enabled", True)
            if not isinstance(enabled, bool):
                raise ValueError("Invalid band enable switch.")
            if not enabled:
                continue
            kind = band.get("kind", "bell")
            if kind not in ("bell", "low_shelf", "high_shelf"):
                raise ValueError("Invalid parametric band type.")
            stages.append(biquad(kind, band.get("frequency", 1000), sample_rate,
                                 band.get("gain_db", 0), band.get("q", 1)))
    elif name == "filter":
        kind = options.pop("kind", "high_pass")
        frequency = options.pop("frequency", 80)
        q = options.pop("q", 1)
        slope = options.pop("slope", 24)
        if type(slope) is not int or slope not in (12, 24, 36, 48):
            raise ValueError("Filter slope must be 12, 24, 36 or 48 dB/octave.")
        if kind in ("low_pass", "high_pass"):
            order = slope // 6
            for k in range(order // 2):
                butterworth_q = 1 / (2 * math.cos((2*k+1) * math.pi / (2*order)))
                stages.append(biquad(kind, frequency, sample_rate, q=butterworth_q))
        elif kind in ("band_pass", "notch"):
            stages.append(biquad(kind, frequency, sample_rate, q=q))
        else:
            raise ValueError("Unknown filter type.")
    else:
        raise ValueError("Unknown EQ effect.")
    if options:
        raise ValueError("Unknown EQ settings: " + ", ".join(sorted(options)))
    coefficients = np.asarray(stages, np.float64).reshape(-1, 5)
    return np.ascontiguousarray(coefficients), 10 ** (output / 20)


def response(coefficients, gain, frequencies, sample_rate):
    z = np.exp(-2j * np.pi * np.asarray(frequencies) / sample_rate)
    h = np.full(z.shape, complex(gain))
    for b0, b1, b2, a1, a2 in coefficients:
        h *= (b0 + b1*z + b2*z*z) / (1 + a1*z + a2*z*z)
    return 20 * np.log10(np.maximum(np.abs(h), 1e-12))
