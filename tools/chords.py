#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Chords per half bar of a recording, chosen among the given candidates.

    python3 chords.py song.wav --chords A,D7,E7,F#m,F,D,C#m,Bm,Cm

Restricting the candidates to the chords of the song cuts errors a lot.
Close chords (F#m/F, D/D7) are easily confused: an aid, not a transcription.
"""

import argparse

import numpy as np

from analysis import Analysis, chord_template, parse_chord, read_channel


def main():
    ap = argparse.ArgumentParser(description="Chords per half bar.")
    ap.add_argument("wav")
    ap.add_argument("--chords", required=True, help="comma-separated candidates, e.g. A,D7,F#m")
    ap.add_argument("--channel", type=int, help="1 = left, 2 = right (default: the loudest)")
    args = ap.parse_args()

    names = [c.strip() for c in args.chords.split(",") if c.strip()]
    templates = {n: chord_template(*parse_chord(n)) for n in names}

    x, sr = read_channel(args.wav, None if args.channel is None else args.channel - 1)
    an = Analysis(x, sr)
    t, s = an.onsets()
    beats = an.beat_grid(t[0], an.global_beat(), t, s)
    phase = an.downbeat_phase(beats)
    print(f"tempo: {60 / np.median(np.diff(beats)):.0f} bpm")

    def best(a, b):
        v = an.segment(a, b)
        return max(templates, key=lambda n: v @ templates[n])

    bars = []
    for i in range(phase, len(beats) - 4, 4):
        first, second = best(beats[i], beats[i + 2]), best(beats[i + 2], beats[i + 4])
        bars.append(first if first == second else f"{first} {second}")
    for i in range(0, len(bars), 4):
        print(f"{i + 1:3d}  | " + " | ".join(f"{c:9s}" for c in bars[i:i + 4]) + " |")


if __name__ == "__main__":
    main()
