#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Tempo, swing and accents of a recorded rhythm guitar part.

    python3 accents.py verse.wav [--channel 2]

The downbeat is found where the harmony changes: this works when chords change
on the beat. With vocals or clipping the accents are less reliable.
"""

import argparse

import numpy as np

from analysis import Analysis, read_channel


def main():
    ap = argparse.ArgumentParser(description="Tempo, swing and accents of a recording.")
    ap.add_argument("wav")
    ap.add_argument("--channel", type=int, help="1 = left, 2 = right (default: the loudest)")
    args = ap.parse_args()

    x, sr = read_channel(args.wav, None if args.channel is None else args.channel - 1)
    an = Analysis(x, sr)
    t, s = an.onsets()
    if len(t) < 8:
        raise SystemExit("too few onsets to analyse")
    beats = an.beat_grid(t[0], an.global_beat(), t, s)
    phase = an.downbeat_phase(beats)
    step = np.median(np.diff(beats))
    print(f"tempo: {60 / step:.0f} bpm, beats: {len(beats)}")

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
    print("accent per beat (100 = the strongest):")
    for p in range(4):
        print(f"  {p + 1}: {acc[p]:4.0f}  {'#' * int(acc[p] / 5)}")
    if swing:
        print(f"offbeat at {np.median(swing):.2f} of the beat "
              "(0.50 straight eighths, 0.67 triplet)")


if __name__ == "__main__":
    main()
