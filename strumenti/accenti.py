#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Tempo, shuffle e accenti di una ritmica di chitarra registrata.

    python3 accenti.py strofa.wav [--canale 2]

L'uno della battuta si trova dove cambia l'armonia: funziona se gli accordi
cambiano in battere. Con la voce o con saturazione gli accenti sono meno affidabili.
"""

import argparse

import numpy as np

from analisi import Analysis, read_channel


def main():
    ap = argparse.ArgumentParser(description="Tempo, shuffle e accenti di una registrazione.")
    ap.add_argument("wav")
    ap.add_argument("--canale", type=int, help="1 = sinistro, 2 = destro (default: il più forte)")
    args = ap.parse_args()

    x, sr = read_channel(args.wav, None if args.canale is None else args.canale - 1)
    an = Analysis(x, sr)
    t, s = an.onsets()
    if len(t) < 8:
        raise SystemExit("troppo pochi attacchi per un'analisi")
    beats = an.beat_grid(t[0], an.global_beat(), t, s)
    phase = an.downbeat_phase(beats)
    step = np.median(np.diff(beats))
    print(f"tempo: {60 / step:.0f} bpm, movimenti: {len(beats)}")

    acc, cnt, swing = np.zeros(4), np.zeros(4), []
    for i, b in enumerate(beats):
        near = np.abs(t - b) < 0.15 * step
        if near.any():
            acc[(i - phase) % 4] += s[near].max()
            cnt[(i - phase) % 4] += 1
        mid = (t > b + 0.3 * step) & (t < b + 0.85 * step)
        if mid.any():
            swing.append((t[mid][np.argmax(s[mid])] - b) / step)
    acc = acc / np.maximum(cnt, 1)
    acc = acc / acc.max() * 100
    print("accenti per movimento (100 = il più forte):")
    for p in range(4):
        print(f"  {p + 1}: {acc[p]:4.0f}  {'#' * int(acc[p] / 5)}")
    if swing:
        print(f"colpo corto a {np.median(swing):.2f} del movimento "
              "(0.50 crome dritte, 0.67 terzina)")


if __name__ == "__main__":
    main()
