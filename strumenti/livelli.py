#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Livelli di una registrazione: durata, picco, valore efficace (RMS), saturazione.

    python3 livelli.py registrazione.wav

Legge WAV a 16 o 32 bit, mono o stereo; un canale per riga.
Obiettivo in registrazione: picco intorno a -12 dBFS, nessun campione saturato.
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
        sys.exit(f"{path}: campioni da {8 * width} bit non gestiti")
    x = np.frombuffer(raw, dtype=dtype).reshape(-1, nch) / float(2 ** (8 * width - 1))
    return x, sr


def db(v):
    return 20 * np.log10(max(v, 1e-12))


def main(path):
    x, sr = read(path)
    print(f"{path}: {len(x) / sr:.1f} s, {sr} Hz, {x.shape[1]} canali")
    for ch in range(x.shape[1]):
        s = x[:, ch]
        peak = np.abs(s).max()
        rms = np.sqrt(np.mean(s ** 2))
        clipped = int((np.abs(s) > 0.999).sum())
        print(f"  canale {ch + 1}: picco {db(peak):6.1f} dBFS, RMS {db(rms):6.1f} dBFS, "
              f"saturati {clipped}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
