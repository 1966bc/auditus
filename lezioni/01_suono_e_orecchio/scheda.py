#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""Scheda della lezione 1 - il suono e l'orecchio - in PDF da stampare."""

import os

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, Paragraph, Preformatted, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

D = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("R", f"{D}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("B", f"{D}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("I", f"{D}/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("M", f"{D}/DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("R", normal="R", bold="B", italic="I", boldItalic="B")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "scheda.pdf")
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
    """Due spettri affiancati: La 110 Hz completo e senza fondamentale, ampiezze 1/k."""
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
        d.add(String(x0 + pw / 2, 1, "frequenza (Hz)", fontName="I", fontSize=6.5,
                     textAnchor="middle", fillColor=GREY))

    panel(0, "La completo: fondamentale 110 Hz + armoniche", 1)
    panel(W - pw, "Senza fondamentale: si sente ancora un La", 2)
    return d


s = []
s.append(Paragraph("Lezione 1 — Il suono e l'orecchio", h1))
s.append(Paragraph("auditus · 29 settembre 2026 · suoni di prova in <font name='M'>suoni/</font>, "
                   "generati da <font name='M'>genera_suoni.py</font>", small))

s.append(Paragraph("Il suono", h2))
s.append(Paragraph("Un'onda di pressione <b>longitudinale</b>: compressioni e rarefazioni dell'aria "
                   "che si propagano a circa 343 m/s (20 °C). L'aria oscilla sul posto e trasmette "
                   "la perturbazione.", body))
s.append(table([
    ["Grandezza fisica", "Percezione", "Unità e note"],
    ["Frequenza", "Altezza", "Hz; l'ottava è un rapporto 2:1 (110 → 220 → 440 Hz)"],
    ["Ampiezza (pressione)", "Intensità (loudness)", "dB, scala logaritmica: +10 dB ≈ il doppio "
     "della sensazione di intensità"],
    ["Spettro (parziali e loro ampiezze)", "Timbro", "serie armonica: f, 2f, 3f…; l'inviluppo "
     "spettrale distingue gli strumenti"],
], [45, 35, 94]))

s.append(Paragraph("L'orecchio", h2))
s.append(table([
    ["Parte", "Funzione"],
    ["Esterno (padiglione, condotto, timpano)", "raccoglie l'onda e la converte in vibrazione del timpano"],
    ["Medio (martello, incudine, staffa)", "adattamento d'impedenza aria → liquido cocleare"],
    ["Interno (coclea)", "<b>tonotopia</b> della membrana basilare: acuti alla base, gravi "
     "all'apice; le cellule ciliate trasducono in segnale nervoso. Un analizzatore di spettro "
     "biologico"],
], [58, 116]))

s.append(Paragraph("Tre proprietà dell'udito", h2))
s.append(table([
    ["Fenomeno", "In breve"],
    ["Campo udibile e <b>presbiacusia</b>", "circa 20 Hz–20 kHz da giovani; il limite alto scende "
     "con l'età (norma ISO 7029), soprattutto sopra 8 kHz"],
    ["<b>Curve isofoniche</b> (Fletcher–Munson, ISO 226)", "massima sensibilità tra 2 e 5 kHz; "
     "a basso livello la soglia sotto i 200 Hz sale molto: i bassi \"spariscono\" prima"],
    ["Localizzazione binaurale", "<b>ITD</b> (differenza interaurale di tempo) sotto circa 1,5 kHz, "
     "<b>ILD</b> (di livello) sopra; due casse uguali danno un'<b>immagine fantasma</b> al centro"],
    ["<b>Altezza residua</b> (fondamentale mancante)", "il sistema uditivo ricava l'altezza dalla "
     "periodicità delle armoniche, anche se la fondamentale manca: stesso <b>croma</b>, registro "
     "(<i>pitch height</i>) meno certo"],
], [58, 116]))

s.append(KeepTogether([
    Paragraph("La fondamentale mancante, in figura", h2),
    spectra(),
    Paragraph("A destra manca la barra a 110 Hz, ma le armoniche restano distanziate di 110 Hz: "
              "l'altezza percepita resta un La. Per questo il Mi basso a 82 Hz si riconosce anche "
              "da casse che a 82 Hz rendono poco.", small),
]))

s.append(KeepTogether([
    Paragraph("I risultati del 29 settembre", h2),
    table([
        ["Prova (file)", "Risultato", "Lettura"],
        ["Sweep 20 Hz–16 kHz (04)", "udibile da 4,0 s a 19,26 s: circa <b>76 Hz – 12,5 kHz</b>",
         "limite basso = casse + livello; limite alto nella norma o sopra a 60 anni (±10% per il "
         "cronometro manuale)"],
        ["Onda pura / La con armoniche (01, 03)", "stessa nota, la pura sembra più acuta",
         "timbro che si confonde con l'altezza; le casse attenuano 110 Hz"],
        ["Sinistra, destra, centro (05)", "immagine fantasma al centro",
         "casse bilanciate, ascolto simmetrico"],
        ["Fondamentale mancante (06)", "stessa nota, timbro diverso, registro incerto",
         "altezza residua: stesso croma"],
        ["Livello d'ascolto", "serve OUTPUT a ore 12 invece di ore 9",
         "sinusoidi a −20 dBFS di picco (circa −23 dBFS RMS), 10 dB sotto la musica masterizzata"],
    ], [44, 58, 72]),
]))

s.append(Paragraph("Formula dello sweep", h2))
s.append(Paragraph("Sweep logaritmico da 20 a 16 000 Hz in 20 s: frequenza al secondo <i>t</i>", body))
s.append(Preformatted("f(t) = 20 · 800^(t/20) Hz        t = 4 s → 76 Hz    t = 19,26 s → 12,5 kHz",
                      code))

s.append(Paragraph("Per riascoltare", h2))
s.append(Preformatted("cd ~/Documents/projects/auditus/lezioni/01_suono_e_orecchio\n"
                      "for f in suoni/*.wav; do echo \"$f\"; aplay -q \"$f\"; done", code))
s.append(Paragraph("Prima di tornare alla musica riporta OUTPUT a ore 9.", small))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                        topMargin=14 * mm, bottomMargin=14 * mm,
                        title="auditus — Lezione 1: il suono e l'orecchio",
                        author="Giuseppe Costanzi")
doc.build(s)
print(OUT)
