#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Lezione 1 - suoni di prova: onde pure, serie armonica, sweep, stereo.

    python3 genera_suoni.py

Scrive in suoni/ cinque file WAV, 44 100 Hz, 16 bit, stereo, a -20 dBFS.
"""

import os
import wave

import numpy as np

SR = 44100
LEVEL = 10 ** (-20 / 20)        # -20 dBFS: volume prudente
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "suoni")


def fade(x, ms=30):
    """Attacco e rilascio lineari, per non sentire un clic ai bordi."""
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

    # onde pure: il La della quinta corda e il La del diapason
    save("01_la_110.wav", fade(np.sin(2 * np.pi * 110 * t)))
    save("02_la_440.wav", fade(np.sin(2 * np.pi * 440 * t)))

    # 110 Hz con le prime 12 armoniche, ampiezza 1/k; le acute decadono prima
    tone = sum((1 / k) * np.exp(-t * (1.2 + 0.6 * k)) * np.sin(2 * np.pi * 110 * k * t)
               for k in range(1, 13))
    save("03_la_armoniche.wav", fade(tone, 5))

    # sweep logaritmico 20 -> 16 000 Hz in 20 s, ampiezza costante
    T, f0, f1 = 20, 20, 16000
    ts = np.arange(int(SR * T)) / SR
    k = np.log(f1 / f0)
    save("04_sweep.wav", fade(np.sin(2 * np.pi * f0 * T / k * (np.exp(ts * k / T) - 1)), 200))

    # lo stesso La a sinistra, a destra, poi su entrambi i canali (immagine fantasma)
    tt = np.arange(int(SR * 1.5)) / SR
    b = fade(np.sin(2 * np.pi * 440 * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * tt)))
    z = np.zeros(int(SR * 0.4))
    save("05_sinistra_destra.wav",
         np.concatenate([b, z, 0 * b, z, b]),
         np.concatenate([0 * b, z, b, z, b]))


def sweep_frequency(seconds, T=20, f0=20, f1=16000):
    """Frequenza dello sweep al secondo indicato: serve a leggere il limite d'udito."""
    return f0 * (f1 / f0) ** (seconds / T)


if __name__ == "__main__":
    main()
