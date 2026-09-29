#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Accordi per mezza battuta di una registrazione, scelti tra quelli indicati.

    python3 accordi.py brano.wav --accordi A,D7,E7,F#m,F,D,C#m,Bm,Cm

Limitare i candidati agli accordi del brano riduce molto gli errori.
Confonde facilmente accordi vicini (F#m/F, D/D7): è un aiuto, non una trascrizione.
"""

import argparse

import numpy as np

from analisi import Analysis, chord_template, parse_chord, read_channel


def main():
    ap = argparse.ArgumentParser(description="Accordi per mezza battuta.")
    ap.add_argument("wav")
    ap.add_argument("--accordi", required=True, help="candidati separati da virgole, es. A,D7,F#m")
    ap.add_argument("--canale", type=int, help="1 = sinistro, 2 = destro (default: il più forte)")
    args = ap.parse_args()

    names = [c.strip() for c in args.accordi.split(",") if c.strip()]
    templates = {n: chord_template(*parse_chord(n)) for n in names}

    x, sr = read_channel(args.wav, None if args.canale is None else args.canale - 1)
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
