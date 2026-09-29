#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Lesson 1 - test sounds: pure tones, harmonic series, sweep, stereo, missing fundamental.

    python3 make_sounds.py

Writes six WAV files to sounds/, 44.1 kHz, 16 bit, stereo, peak at -20 dBFS.
"""

import os
import wave

import numpy as np

SR = 44100
LEVEL = 10 ** (-20 / 20)        # -20 dBFS: a safe listening level
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")


def fade(x, ms=30):
    """Linear fade in and out, so that no click is heard at the edges."""
    n = int(SR * ms / 1000)
    env = np.ones(len(x))
    env[:n] = np.linspace(0, 1, n)
    env[-n:] = np.linspace(1, 0, n)
    return x * env


def save(name, left, right=None):
    right = left if right is None else right
    st = np.stack([left, right], axis=1)
    st = st / max(1e-9, np.abs(st).max()) * LEVEL
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def main():
    os.makedirs(OUT, exist_ok=True)
    t = np.arange(int(SR * 3)) / SR

    # pure tones: the open fifth string of the guitar and the tuning-fork A
    save("01_a_110hz.wav", fade(np.sin(2 * np.pi * 110 * t)))
    save("02_a_440hz.wav", fade(np.sin(2 * np.pi * 440 * t)))

    # 110 Hz with its first 12 harmonics, amplitude 1/k; the higher ones decay faster
    tone = sum((1 / k) * np.exp(-t * (1.2 + 0.6 * k)) * np.sin(2 * np.pi * 110 * k * t)
               for k in range(1, 13))
    save("03_a_harmonics.wav", fade(tone, 5))

    # logarithmic sweep 20 -> 16 000 Hz in 20 s, constant amplitude
    T, f0, f1 = 20, 20, 16000
    ts = np.arange(int(SR * T)) / SR
    k = np.log(f1 / f0)
    save("04_sweep.wav", fade(np.sin(2 * np.pi * f0 * T / k * (np.exp(ts * k / T) - 1)), 200))

    # the same A on the left, on the right, then on both channels (phantom image)
    tt = np.arange(int(SR * 1.5)) / SR
    b = fade(np.sin(2 * np.pi * 440 * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * tt)))
    z = np.zeros(int(SR * 0.4))
    save("05_left_right.wav",
         np.concatenate([b, z, 0 * b, z, b]),
         np.concatenate([0 * b, z, b, z, b]))

    # missing fundamental: the full A, the same without its fundamental, a pure 220 Hz
    t2 = np.arange(int(SR * 2.5)) / SR

    def partials(first):
        return sum((1 / k) * np.sin(2 * np.pi * 110 * k * t2) for k in range(first, 13))

    gap = np.zeros(int(SR * 0.6))
    blocks = [fade(partials(1) / np.abs(partials(1)).max(), 20),
              fade(partials(2) / np.abs(partials(2)).max(), 20),
              fade(np.sin(2 * np.pi * 220 * t2), 20)]
    save("06_missing_fundamental.wav",
         np.concatenate([blocks[0], gap, blocks[1], gap, blocks[2]]))


def sweep_frequency(seconds, T=20, f0=20, f1=16000):
    """Frequency of the sweep at a given second: turns a stopwatch reading into Hz."""
    return f0 * (f1 / f0) ** (seconds / T)


if __name__ == "__main__":
    main()
