#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""Lesson 1 handout - sound and hearing - as a printable PDF."""

import os

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, Paragraph, Preformatted, SimpleDocTemplate,
                                Table, TableStyle)

D = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("R", f"{D}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("B", f"{D}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("I", f"{D}/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("M", f"{D}/DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("R", normal="R", bold="B", italic="I", boldItalic="B")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "handout.pdf")
ACCENT = colors.HexColor("#2f6fd0")
GREY = colors.HexColor("#8a8a8a")

h1 = ParagraphStyle("h1", fontName="B", fontSize=17, leading=21, spaceAfter=2)
h2 = ParagraphStyle("h2", fontName="B", fontSize=12, leading=15, spaceBefore=9, spaceAfter=3)
body = ParagraphStyle("body", fontName="R", fontSize=9.3, leading=12.3, spaceAfter=3)
small = ParagraphStyle("small", parent=body, fontSize=8.3, leading=10.8, textColor=GREY)
cell = ParagraphStyle("cell", fontName="R", fontSize=8.4, leading=10.4)
cellb = ParagraphStyle("cellb", parent=cell, fontName="B")
code = ParagraphStyle("code", fontName="M", fontSize=8.5, leading=10.5,
                      backColor=colors.HexColor("#f2f2f2"), borderPadding=4, spaceBefore=2,
                      spaceAfter=6)


def table(rows, widths):
    data = [[Paragraph(c, cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.black),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return t


def spectra():
    """Two spectra side by side: A 110 Hz complete and without fundamental, amplitudes 1/k."""
    W, H = 178 * mm, 50 * mm
    d = Drawing(W, H)
    pw, ph, base = 80 * mm, 30 * mm, 11 * mm

    def panel(x0, title, first):
        d.add(String(x0, H - 6, title, fontName="B", fontSize=8.5))
        d.add(Line(x0, base, x0 + pw, base, strokeColor=colors.black, strokeWidth=0.6))
        step = pw / 13
        for k in range(1, 13):
            x = x0 + k * step
            if k >= first:
                h = ph / k
                d.add(Rect(x - 2.2, base, 4.4, h, fillColor=ACCENT if k == 1 else GREY,
                           strokeColor=None))
            else:
                d.add(Rect(x - 2.2, base, 4.4, ph, fillColor=None, strokeColor=ACCENT,
                           strokeWidth=0.6, strokeDashArray=[2, 2]))
            if k in (1, 2, 3, 4, 6, 8, 12):
                d.add(String(x, base - 9, str(110 * k), fontName="R", fontSize=6,
                             textAnchor="middle"))
        d.add(String(x0 + pw / 2, 1, "frequency (Hz)", fontName="I", fontSize=6.5,
                     textAnchor="middle", fillColor=GREY))

    panel(0, "Complete A: fundamental 110 Hz + harmonics", 1)
    panel(W - pw, "Without fundamental: still heard as an A", 2)
    return d


s = []
s.append(Paragraph("Lesson 1 — Sound and hearing", h1))
s.append(Paragraph("auditus · 29 September 2026 · test sounds in <font name='M'>sounds/</font>, "
                   "made by <font name='M'>make_sounds.py</font>", small))

s.append(Paragraph("Sound", h2))
s.append(Paragraph("A <b>longitudinal</b> pressure wave: compressions and rarefactions of the air "
                   "travelling at about 343 m/s (20 °C). The air oscillates in place and passes "
                   "the disturbance on.", body))
s.append(table([
    ["Physical quantity", "Perception", "Units and notes"],
    ["Frequency", "Pitch", "Hz; the octave is a 2:1 ratio (110 → 220 → 440 Hz)"],
    ["Amplitude (pressure)", "Loudness", "dB, a logarithmic scale: +10 dB ≈ twice as loud"],
    ["Spectrum (partials and their amplitudes)", "Timbre", "harmonic series: f, 2f, 3f…; the "
     "spectral envelope tells instruments apart"],
], [45, 35, 94]))

s.append(Paragraph("The ear", h2))
s.append(table([
    ["Part", "Function"],
    ["Outer (pinna, ear canal, eardrum)", "collects the wave and turns it into vibration of the eardrum"],
    ["Middle (malleus, incus, stapes)", "impedance matching from air to cochlear fluid"],
    ["Inner (cochlea)", "<b>tonotopy</b> of the basilar membrane: high frequencies at the base, "
     "low at the apex; hair cells transduce into nerve signals. A biological spectrum analyser"],
], [58, 116]))

s.append(Paragraph("Four properties of hearing", h2))
s.append(table([
    ["Phenomenon", "In short"],
    ["Hearing range and <b>presbycusis</b>", "about 20 Hz–20 kHz when young; the upper limit drops "
     "with age (ISO 7029), mostly above 8 kHz"],
    ["<b>Equal-loudness contours</b> (Fletcher–Munson, ISO 226)", "highest sensitivity between 2 "
     "and 5 kHz; at low levels the threshold below 200 Hz rises steeply: bass \"disappears\" first"],
    ["Binaural localisation", "<b>ITD</b> (interaural time difference) below about 1.5 kHz, "
     "<b>ILD</b> (level difference) above; two equal speakers give a central <b>phantom image</b>"],
    ["<b>Residue pitch</b> (missing fundamental)", "the auditory system derives pitch from the "
     "periodicity of the harmonics, even without the fundamental: same <b>chroma</b>, less certain "
     "<i>pitch height</i>"],
], [58, 116]))

s.append(KeepTogether([
    Paragraph("The missing fundamental, in a picture", h2),
    spectra(),
    Paragraph("On the right the 110 Hz bar is missing, yet the harmonics are still 110 Hz apart: "
              "the perceived pitch is still an A. This is why the low E at 82 Hz is recognisable "
              "even on speakers that reproduce little at 82 Hz.", small),
]))

s.append(KeepTogether([
    Paragraph("Results of 29 September", h2),
    table([
        ["Test (file)", "Result", "Reading"],
        ["Sweep 20 Hz–16 kHz (04)", "heard from 4.0 s to 19.26 s: about <b>76 Hz – 12.5 kHz</b>",
         "low limit = speakers + level; high limit at or above average at 60 (±10% for the "
         "hand-held stopwatch)"],
        ["Pure tone / A with harmonics (01, 03)", "same note, the pure tone sounds higher",
         "timbre mistaken for pitch; the speakers attenuate 110 Hz"],
        ["Left, right, centre (05)", "phantom image in the centre",
         "balanced speakers, symmetrical listening position"],
        ["Missing fundamental (06)", "same note, different timbre, uncertain register",
         "residue pitch: same chroma"],
        ["Listening level", "OUTPUT at 12 o'clock instead of 9",
         "sines peaking at −20 dBFS (about −23 dBFS RMS), 10 dB below mastered music"],
    ], [44, 58, 72]),
]))

s.append(Paragraph("Sweep formula", h2))
s.append(Paragraph("Logarithmic sweep from 20 to 16 000 Hz in 20 s: frequency at second <i>t</i>", body))
s.append(Preformatted("f(t) = 20 · 800^(t/20) Hz        t = 4 s → 76 Hz    t = 19.26 s → 12.5 kHz",
                      code))

s.append(Paragraph("To listen again", h2))
s.append(Preformatted("cd ~/Documents/projects/auditus/lessons/01_sound_and_hearing\n"
                      "for f in sounds/*.wav; do echo \"$f\"; aplay -q \"$f\"; done", code))
s.append(Paragraph("Before going back to music, turn OUTPUT back to 9 o'clock.", small))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                        topMargin=14 * mm, bottomMargin=14 * mm,
                        title="auditus — Lesson 1: sound and hearing",
                        author="Giuseppe Costanzi")
doc.build(s)
print(OUT)
