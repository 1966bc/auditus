#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""Manualetto della Steinberg UR22mkII su hal9000, in PDF da stampare."""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, String
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Preformatted, KeepTogether)

D = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("R", f"{D}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("B", f"{D}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("I", f"{D}/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("M", f"{D}/DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("R", normal="R", bold="B", italic="I", boldItalic="B")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UR22mkII_manualetto.pdf")
ACCENT = colors.HexColor("#2f6fd0")
GREY = colors.HexColor("#8a8a8a")

h1 = ParagraphStyle("h1", fontName="B", fontSize=17, leading=21, spaceAfter=2)
h2 = ParagraphStyle("h2", fontName="B", fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=4)
body = ParagraphStyle("body", fontName="R", fontSize=9.5, leading=12.5, spaceAfter=4)
small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=11, textColor=GREY)
cell = ParagraphStyle("cell", fontName="R", fontSize=8.5, leading=10.5)
cellb = ParagraphStyle("cellb", parent=cell, fontName="B")
code = ParagraphStyle("code", fontName="M", fontSize=8, leading=10, backColor=colors.HexColor("#f2f2f2"),
                      borderPadding=4, spaceBefore=2, spaceAfter=6)


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


def panel():
    """Front panel, drawn: the controls to check in colour."""
    W, H = 180 * mm, 62 * mm
    d = Drawing(W, H)
    sx = W / 712                       # units of the drawing: 712 wide, as the online version
    X = lambda x: (x - 24) * sx
    cy = H - 34 * mm
    d.add(Rect(0, cy - 60 * sx, W, 120 * sx, rx=6, ry=6, fillColor=None, strokeColor=GREY, strokeWidth=1))

    def knob(x, on):
        c = ACCENT if on else GREY
        d.add(Circle(X(x), cy, 18 * sx, fillColor=colors.Color(0.18, 0.44, 0.82, 0.12) if on else None,
                     strokeColor=c, strokeWidth=1.8 if on else 1))
        d.add(Line(X(x), cy, X(x), cy + 14 * sx, strokeColor=c, strokeWidth=1.6))

    def jack(x, on):
        c = ACCENT if on else GREY
        d.add(Circle(X(x), cy, 22 * sx, fillColor=colors.Color(0.18, 0.44, 0.82, 0.12) if on else None,
                     strokeColor=c, strokeWidth=1.8 if on else 1))
        d.add(Circle(X(x), cy, 8 * sx, fillColor=None, strokeColor=c, strokeWidth=1))

    def led(x, on):
        d.add(Circle(X(x), cy + 40 * sx, 6 * sx, fillColor=ACCENT if on else None,
                     strokeColor=ACCENT if on else GREY, strokeWidth=1))

    def label(x, name, setting, on):
        d.add(String(X(x), cy - 60 * sx - 14, name, fontName="B" if on else "R", fontSize=8,
                     textAnchor="middle"))
        if setting:
            d.add(String(X(x), cy - 60 * sx - 25, setting, fontName="R", fontSize=7.5,
                         textAnchor="middle", fillColor=GREY))

    knob(64, False); label(64, "GAIN 1", "basso", False)
    jack(126, False); label(126, "Ingr. 1", "libero", False)
    led(184, False); label(184, "PEAK", "", False)
    led(228, True); label(228, "+48V", "acceso", True)
    led(272, False); label(272, "PEAK", "", False)
    led(316, False); label(316, "USB", "", False)
    jack(376, True); label(376, "Ingr. 2", "microfono", True)
    knob(444, True); label(444, "GAIN 2", "ore 12-14", True)
    d.add(Rect(X(488), cy - 14 * sx, 28 * sx, 28 * sx, rx=3, ry=3,
               fillColor=colors.Color(0.18, 0.44, 0.82, 0.12), strokeColor=ACCENT, strokeWidth=1.8))
    label(502, "HI-Z", "fuori", True)
    knob(560, True); label(560, "MIX", "DAW", True)
    knob(614, False); label(614, "PHONES", "medio", False)
    jack(662, False); label(662, "cuffie", "", False)
    knob(708, False); label(708, "OUTPUT", "metà", False)
    d.add(String(0, 2, "Sul retro: interruttore +48V, selettore POWER SOURCE (su USB), uscite verso le casse.",
                 fontName="I",
                 fontSize=7.5, fillColor=GREY))
    return d


s = []
s.append(Paragraph("Steinberg UR22mkII su hal9000 — manualetto", h1))
s.append(Paragraph("29 settembre 2026 · microfono Steinberg ST-M01 · Debian 12", small))

s.append(Paragraph("Il pannello", h2))
s.append(Paragraph("In colore i cinque comandi da controllare prima di ogni registrazione; "
                   "gli altri restano come sono.", body))
s.append(panel())
s.append(Spacer(1, 4))
s.append(table([
    ["Comando", "A cosa serve", "Di solito"],
    ["INPUT 1 GAIN", "Quanto amplificare l'ingresso 1", "Basso: non c'è collegato niente"],
    ["Ingresso 1 (combo)", "Presa XLR per microfono o jack per strumento/linea", "Libero"],
    ["PEAK", "Si accende quando il segnale di quell'ingresso è vicino alla saturazione",
     "Spenta, o solo sui colpi più forti"],
    ["+48V (spia)", "Accesa = alimentazione phantom attiva su <b>entrambi</b> gli ingressi",
     "Accesa, per lo ST-M01"],
    ["USB (spia)", "Accesa = scheda collegata e alimentata", "Accesa"],
    ["Ingresso 2 (combo)", "Come l'ingresso 1", "Microfono ST-M01"],
    ["INPUT 2 GAIN", "Quanto amplificare l'ingresso 2", "Ore 14 chitarra, ore 12 se canti"],
    ["INPUT 2 HI-Z", "Premuto = ingresso 2 per chitarra elettrica col jack",
     "<b>Fuori</b> (sporgente) col microfono"],
    ["MIX", "Cosa senti: INPUT (sinistra) = solo gli ingressi, DAW (destra) = solo il computer, "
            "a metà = tutti e due", "DAW per registrare e riascoltare"],
    ["PHONES", "Volume della presa cuffie della scheda", "A piacere"],
    ["OUTPUT", "Volume delle uscite verso le casse", "Circa metà"],
    ["+48V (retro)", "Interruttore della phantom, in alto a destra: OFF a sinistra, ON a destra",
     "Acceso col microfono"],
    ["POWER SOURCE (retro)", "Da dove la scheda prende corrente: presa 5V DC o USB",
     "<b>USB</b>: su 5V DC, senza alimentatore, la scheda resta spenta"],
], [34, 88, 52]))
s.append(Paragraph("Lo ST-M01 ha una lucetta blu: accesa quando riceve la phantom, spenta con il +48V spento.",
                   small))

s.append(Paragraph("Collegamenti", h2))
s.append(table([
    ["Cosa", "Dove", "Impostazioni"],
    ["Microfono ST-M01 (condensatore)", "Ingresso 2, cavo XLR", "+48V acceso, HI-Z fuori"],
    ["Chitarra acustica", "Davanti al microfono, a 20–30 cm",
     "Microfono puntato dove il manico incontra il corpo, non sulla buca; "
     "capta dal lato della scritta <i>steinberg</i>"],
    ["Chitarra elettrica", "Ingresso 2, cavo jack", "HI-Z premuto, +48V non serve"],
    ["Casse", "LINE OUTPUT L / R sul retro", "Volume con OUTPUT"],
    ["Cuffie", "Nella presa delle casse", "Con le cuffie infilate le casse tacciono"],
    ["PC", "USB sul retro", "Si alimenta da lì"],
], [44, 50, 80]))

s.append(KeepTogether([
    Paragraph("Regolare il guadagno", h2),
    Paragraph("Obiettivo: picco intorno a −12 dBFS. La spia PEAK si accende solo quando si è già "
              "vicini alla saturazione: se resta spenta mentre suoni è normale.", body),
    table([
        ["Picco misurato", "Cosa vuol dire", "Cosa fare"],
        ["sotto −30 dBFS", "Troppo basso, si sente il fruscio", "Alza il GAIN"],
        ["da −18 a −6 dBFS", "Giusto", "Niente"],
        ["0 dBFS, campioni saturati", "Suono tagliato, non si recupera", "Abbassa il GAIN e ripeti"],
    ], [44, 70, 60]),
    Paragraph("Cantando vicino al microfono il segnale sale molto: il 29 settembre, col GAIN a ore 14, "
              "si è arrivati a 0 dBFS. Toccare la griglia accende la PEAK anche con poco guadagno.", small),
]))

s.append(KeepTogether([
    Paragraph("Ascoltarsi e il larsen", h2),
    table([
        ["MIX", "Senti", "Quando"],
        ["Tutta a sinistra (INPUT)", "Solo il microfono", "Per provarlo, con le casse mute"],
        ["A metà", "Microfono e computer", "Per suonare sopra una base, in cuffia"],
        ["Tutta a destra (DAW)", "Solo il computer", "Per registrare e per riascoltare"],
    ], [44, 50, 80]),
    Paragraph("Il <b>larsen</b> è il fischio del microfono che riprende le casse. Si evita con MIX su DAW, "
              "oppure OUTPUT al minimo, oppure con le cuffie infilate nelle casse.", body),
]))

s.append(KeepTogether([
    Paragraph("Uso di tutti i giorni (musica, video)", h2),
    Paragraph("Spotify, YouTube e il browser suonano attraverso PulseAudio, che usa la UR22mkII come uscita "
              "e ingresso predefiniti. Il volume si regola con OUTPUT.", body),
    table([
        ["Comando", "Posizione", "Perché"],
        ["MIX", "Tutta su DAW", "Senti solo il computer"],
        ["GAIN 1 e 2", "Al minimo", "Nessun rumore dagli ingressi"],
        ["+48V", "OFF", "Solo per registrare o videochiamate"],
        ["Volume di XFCE", "100%, mai oltre", "Oltre il 100% PulseAudio distorce"],
        ["OUTPUT", "Il volume vero e proprio", "Ore 9–12 per ascoltare; pulito fino a tre quarti"],
        ["Manopola delle casse", "Fissa, regolata una volta", "Se è troppo alta le casse saturano"],
    ], [40, 50, 84]),
    Paragraph("<b>Regolare le casse, una volta sola:</b> XFCE al 100%, OUTPUT al minimo, casse a metà; con un "
              "brano forte alza OUTPUT fino al volume più alto che userai. Se ci arrivi con OUTPUT quasi al "
              "minimo, o senti saturazione, abbassa la manopola delle casse e ripeti, finché il massimo arriva "
              "con OUTPUT a ore 12–14. Poi la manopola delle casse non si tocca più.", body),
    Paragraph("<b>Posizione di riferimento</b> (29 settembre 2026, provata con <i>Cornfield Chase</i> e "
              "<i>Time</i> di Hans Zimmer): XFCE al 100%, <b>manopola delle casse a metà</b>. Con OUTPUT a "
              "<b>tre quarti</b> le casse suonano ancora pulite, con margine sopra: è già un volume molto alto, "
              "e per l'ascolto normale basta OUTPUT tra ore 9 e ore 12. "
              "Se qualcuno sposta la manopola delle casse, rimettila a metà.", body),
    Paragraph("Le uscite della UR22mkII hanno un livello più alto di quello che molte casse da scrivania si "
              "aspettano: satura l'ingresso delle casse, non la scheda. Se il tavolo vibra sui bassi, "
              "metti sotto le casse della gommapiuma.", small),
]))

s.append(Paragraph("Su Linux (hal9000)", h2))
s.append(table([
    ["Voce", "Valore"],
    ["Dispositivo", "hw:1,0 (card 1, Steinberg UR22mkII); verifica con <font name='M'>arecord -l</font>"],
    ["Formato", "Solo S32_LE (32 bit): <font name='M'>-f cd</font> dà errore"],
    ["Canali", "2: sinistro = ingresso 1, destro = ingresso 2"],
    ["Frequenze", "Da 44 100 a 192 000 Hz; 44 100 basta"],
    ["Controlli software", "Nessuno (<font name='M'>amixer -c 1</font> è vuoto): si regola dalle manopole"],
    ["Riproduzione", "<font name='M'>aplay file.wav</font> passa da PulseAudio (uscita predefinita: "
                     "la UR22). Con <font name='M'>-D plughw:1,0</font> si scavalca PulseAudio: "
                     "solo se nient'altro suona"],
    ["Registrazione", "<font name='M'>arecord -D hw:1,0</font> funziona anche mentre PulseAudio suona: "
                      "l'ingresso resta libero finché nessun programma usa il microfono"],
], [34, 140]))

s.append(KeepTogether([
    Paragraph("Ricette pronte", h2),
    Paragraph("Registrare 30 secondi (MIX su DAW):", body),
    Preformatted("arecord -D hw:1,0 -f S32_LE -c 2 -r 44100 -d 30 prova.wav", code),
    Paragraph("Registrare senza limite, fermando con Ctrl+C (con la voce: GAIN 2 a ore 12):", body),
    Preformatted("arecord -D hw:1,0 -f S32_LE -c 2 -r 44100 brano.wav", code),
    Paragraph("Riascoltare (passa da PulseAudio, anche se il browser sta suonando):", body),
    Preformatted("aplay brano.wav", code),
    Paragraph("Circa 21 MB al minuto. Prima di suonare conta ad alta voce «uno, due, tre, quattro». "
              "Il nome del file è relativo alla cartella in cui ti trovi.", small),
]))

s.append(Paragraph("Quando qualcosa non va", h2))
s.append(table([
    ["Sintomo", "Causa probabile", "Rimedio"],
    ["Registrazione muta", "HI-Z premuto, +48V spento, GAIN basso, cavo",
     "HI-Z fuori, +48V acceso, GAIN a ore 14; poi un altro cavo"],
    ["Non senti il microfono in cuffia", "MIX su DAW", "MIX su INPUT, casse mute"],
    ["Non senti il computer", "MIX su INPUT, volumi a zero", "MIX su DAW o a metà, alza il volume"],
    ["Fischio forte", "Larsen", "MIX su DAW oppure OUTPUT al minimo"],
    ["Botto premendo HI-Z o +48V", "Normale con volumi alti", "Prima abbassa GAIN, PHONES, OUTPUT"],
    ["Fruscio col GAIN al massimo", "Rumore del preamplificatore", "GAIN a ore 12–14"],
    ["Picco a 0 dBFS", "Saturazione, spesso cantando", "GAIN 2 verso ore 12"],
    ["Sample format non available", "Manca -f S32_LE", "Usa i comandi delle ricette"],
    ["No such file or directory", "Percorso sbagliato rispetto alla cartella", "Solo il nome del file, o il percorso completo"],
    ["Device or resource busy", "PulseAudio sta già usando la scheda (browser, Spotify)",
     "Togli <font name='M'>-D plughw:1,0</font>: <font name='M'>aplay file.wav</font>"],
], [46, 56, 72]))

s.append(KeepTogether([
    Paragraph("Ordine sicuro: come si spegne il microfono", h2),
    Paragraph("Lo ST-M01 non ha un interruttore: si spegne spegnendo il +48V. "
              "Il cavo si stacca solo dopo.", body),
    table([
        ["Per cominciare", "Per finire"],
        ["1. OUTPUT, PHONES e GAIN 2 al minimo", "1. OUTPUT, PHONES e GAIN 2 al minimo"],
        ["2. Collega il microfono all'ingresso 2 (HI-Z fuori)", "2. Spegni il +48V: si spengono la spia rossa e la lucetta blu del microfono"],
        ["3. Accendi il +48V dal retro", "3. Solo ora, se vuoi, stacca l'XLR; può anche restare attaccato"],
        ["4. Alza GAIN 2, poi OUTPUT e PHONES", ""],
    ], [87, 87]),
    Paragraph("Staccare l'XLR con il +48V acceso fa un botto forte in cuffia e nelle casse e, alla lunga, "
              "stressa microfono e casse.", small),
]))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                        topMargin=14 * mm, bottomMargin=14 * mm,
                        title="Steinberg UR22mkII — manualetto", author="Giuseppe Costanzi")
doc.build(s)
print(OUT)
