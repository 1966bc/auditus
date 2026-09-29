#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Struttura di un file MIDI: tracce, strumenti General MIDI, tempo, metrica, durata.

    python3 midinfo.py brano.mid

Senza librerie esterne. Gli eventi di testo (titoli, testi karaoke) sono solo contati.
"""

import struct
import sys

GM = ["Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano",
      "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet", "Celesta", "Glockenspiel",
      "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer",
      "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion",
      "Harmonica", "Tango Accordion", "Nylon Guitar", "Steel Guitar", "Jazz Guitar",
      "Clean Electric Guitar", "Muted Guitar", "Overdriven Guitar", "Distortion Guitar",
      "Guitar Harmonics", "Acoustic Bass", "Finger Bass", "Pick Bass", "Fretless Bass",
      "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2", "Violin", "Viola", "Cello",
      "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani",
      "String Ensemble 1", "String Ensemble 2", "Synth Strings 1", "Synth Strings 2", "Choir Aahs",
      "Voice Oohs", "Synth Voice", "Orchestra Hit", "Trumpet", "Trombone", "Tuba", "Muted Trumpet",
      "French Horn", "Brass Section", "Synth Brass 1", "Synth Brass 2", "Soprano Sax", "Alto Sax",
      "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet", "Piccolo", "Flute",
      "Recorder", "Pan Flute"]


def main(path):
    d = open(path, "rb").read()
    fmt, ntrk, div = struct.unpack(">HHH", d[8:14])
    print(f"formato {fmt}, tracce {ntrk}, risoluzione {div} tick per quarto")

    def vlq(p):
        v = 0
        while True:
            b = d[p]
            p += 1
            v = (v << 7) | (b & 0x7F)
            if not b & 0x80:
                return v, p

    pos, maxtick, tempos, sigs, texts = 14, 0, [], [], 0
    for t in range(ntrk):
        ln = struct.unpack(">I", d[pos + 4:pos + 8])[0]
        p, end, pos = pos + 8, pos + 8 + ln, pos + 8 + ln
        tick, run, name, progs, notes = 0, 0, "", {}, {}
        while p < end:
            dt, p = vlq(p)
            tick += dt
            b = d[p]
            if b == 0xFF:
                typ = d[p + 1]
                ln2, p = vlq(p + 2)
                data = d[p:p + ln2]
                p += ln2
                if typ == 0x03:
                    name = data.decode("latin-1")
                elif typ == 0x51:
                    tempos.append((tick, round(60_000_000 / int.from_bytes(data, "big"))))
                elif typ == 0x58:
                    sigs.append((tick, f"{data[0]}/{2 ** data[1]}"))
                elif typ in (0x01, 0x05):
                    texts += 1
            elif b in (0xF0, 0xF7):
                ln2, p = vlq(p + 1)
                p += ln2
            else:
                if b & 0x80:
                    run = b
                    p += 1
                status, ch = run >> 4, run & 15
                if status in (0xC, 0xD):
                    if status == 0xC:
                        progs[ch] = d[p]
                    p += 1
                else:
                    if status == 0x9 and d[p + 1] > 0:
                        notes[ch] = notes.get(ch, 0) + 1
                    p += 2
        maxtick = max(maxtick, tick)
        for ch, n in sorted(notes.items()):
            inst = "batteria" if ch == 9 else (GM[progs[ch]] if progs.get(ch, 999) < len(GM)
                                               else f"programma {progs.get(ch)}")
            print(f"  traccia {t} {name!r}, canale {ch + 1}: {inst}, {n} note")

    print("tempo (tick, bpm):", tempos[:8], "| metrica (tick, misura):", sigs[:8])
    secs, last, bpm = 0.0, 0, 120
    for tk, b in tempos + [(maxtick, None)]:
        secs += (tk - last) / div * 60 / bpm
        last = tk
        if b:
            bpm = b
    print(f"durata circa {secs / 60:.1f} minuti; eventi di testo (non mostrati): {texts}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
