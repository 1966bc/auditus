#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Levels of a recording: duration, peak, RMS, clipping.

    python3 levels.py recording.wav

Reads 16 or 32 bit WAV, mono or stereo; one line per channel.
Recording target: peak around -12 dBFS, no clipped samples.
"""

import sys
import wave

import numpy as np


def read(path):
    with wave.open(path) as w:
        width, nch, sr = w.getsampwidth(), w.getnchannels(), w.getframerate()
        raw = w.readframes(w.getnframes())
    dtype = {2: np.int16, 4: np.int32}.get(width)
    if dtype is None:
        sys.exit(f"{path}: {8 * width}-bit samples are not supported")
    x = np.frombuffer(raw, dtype=dtype).reshape(-1, nch) / float(2 ** (8 * width - 1))
    return x, sr


def db(v):
    return 20 * np.log10(max(v, 1e-12))


def main(path):
    x, sr = read(path)
    print(f"{path}: {len(x) / sr:.1f} s, {sr} Hz, {x.shape[1]} channels")
    for ch in range(x.shape[1]):
        s = x[:, ch]
        peak = np.abs(s).max()
        rms = np.sqrt(np.mean(s ** 2))
        clipped = int((np.abs(s) > 0.999).sum())
        print(f"  channel {ch + 1}: peak {db(peak):6.1f} dBFS, RMS {db(rms):6.1f} dBFS, "
              f"clipped {clipped}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
