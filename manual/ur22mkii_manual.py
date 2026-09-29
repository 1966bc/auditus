#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""A short manual for the Steinberg UR22mkII on Linux, as a printable PDF."""

import os

from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
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

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UR22mkII_manual.pdf")
ACCENT = colors.HexColor("#2f6fd0")
GREY = colors.HexColor("#8a8a8a")

h1 = ParagraphStyle("h1", fontName="B", fontSize=17, leading=21, spaceAfter=2)
h2 = ParagraphStyle("h2", fontName="B", fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=4)
body = ParagraphStyle("body", fontName="R", fontSize=9.5, leading=12.5, spaceAfter=4)
small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=11, textColor=GREY)
cell = ParagraphStyle("cell", fontName="R", fontSize=8.5, leading=10.5)
cellb = ParagraphStyle("cellb", parent=cell, fontName="B")
code = ParagraphStyle("code", fontName="M", fontSize=8, leading=10,
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


def panel():
    """Front panel, drawn: the controls to check are in colour."""
    W, H = 180 * mm, 62 * mm
    d = Drawing(W, H)
    sx = W / 712                       # drawing units: 712 wide
    X = lambda x: (x - 24) * sx
    cy = H - 34 * mm
    d.add(Rect(0, cy - 60 * sx, W, 120 * sx, rx=6, ry=6, fillColor=None, strokeColor=GREY,
               strokeWidth=1))
    tint = colors.Color(0.18, 0.44, 0.82, 0.12)

    def knob(x, on):
        c = ACCENT if on else GREY
        d.add(Circle(X(x), cy, 18 * sx, fillColor=tint if on else None,
                     strokeColor=c, strokeWidth=1.8 if on else 1))
        d.add(Line(X(x), cy, X(x), cy + 14 * sx, strokeColor=c, strokeWidth=1.6))

    def jack(x, on):
        c = ACCENT if on else GREY
        d.add(Circle(X(x), cy, 22 * sx, fillColor=tint if on else None,
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

    knob(64, False); label(64, "GAIN 1", "low", False)
    jack(126, False); label(126, "Input 1", "free", False)
    led(184, False); label(184, "PEAK", "", False)
    led(228, True); label(228, "+48V", "on", True)
    led(272, False); label(272, "PEAK", "", False)
    led(316, False); label(316, "USB", "", False)
    jack(376, True); label(376, "Input 2", "microphone", True)
    knob(444, True); label(444, "GAIN 2", "12-2 o'clock", True)
    d.add(Rect(X(488), cy - 14 * sx, 28 * sx, 28 * sx, rx=3, ry=3,
               fillColor=tint, strokeColor=ACCENT, strokeWidth=1.8))
    label(502, "HI-Z", "out", True)
    knob(560, True); label(560, "MIX", "DAW", True)
    knob(614, False); label(614, "PHONES", "medium", False)
    jack(662, False); label(662, "phones", "", False)
    knob(708, False); label(708, "OUTPUT", "half", False)
    d.add(String(0, 2, "Rear panel: +48V switch, POWER SOURCE selector (on USB), outputs to the "
                       "speakers.", fontName="I", fontSize=7.5, fillColor=GREY))
    return d


s = []
s.append(Paragraph("Steinberg UR22mkII on Linux — a short manual", h1))
s.append(Paragraph("29 September 2026 · Steinberg ST-M01 microphone · Debian 12, PulseAudio", small))

s.append(Paragraph("The panel", h2))
s.append(Paragraph("The five controls to check before every recording are in colour; the others "
                   "stay as they are.", body))
s.append(panel())
s.append(Spacer(1, 4))
s.append(table([
    ["Control", "What it does", "Usually"],
    ["INPUT 1 GAIN", "How much input 1 is amplified", "Low: nothing is connected"],
    ["Input 1 (combo)", "XLR socket for a microphone or jack for an instrument/line", "Free"],
    ["PEAK", "Lights up when the signal of that input is close to clipping",
     "Off, or only on the strongest hits"],
    ["+48V (LED)", "On = phantom power active on <b>both</b> inputs", "On, for the ST-M01"],
    ["USB (LED)", "On = interface connected and powered", "On"],
    ["Input 2 (combo)", "Same as input 1", "ST-M01 microphone"],
    ["INPUT 2 GAIN", "How much input 2 is amplified", "2 o'clock guitar, 12 o'clock with voice"],
    ["INPUT 2 HI-Z", "Pressed = input 2 set for an electric guitar on a jack",
     "<b>Out</b> (released) with the microphone"],
    ["MIX", "What you hear: INPUT (left) = inputs only, DAW (right) = computer only, "
            "centre = both", "DAW to record and play back"],
    ["PHONES", "Volume of the interface headphone socket", "To taste"],
    ["OUTPUT", "Volume of the outputs to the speakers", "About half"],
    ["+48V (rear)", "Phantom power switch, top right: OFF left, ON right", "On with the microphone"],
    ["POWER SOURCE (rear)", "Where the interface takes power from: 5V DC socket or USB",
     "<b>USB</b>: on 5V DC, with no power supply, the interface stays off"],
], [34, 88, 52]))
s.append(Paragraph("The ST-M01 has a blue light: on when it receives phantom power, off when "
                   "+48V is off.", small))

s.append(Paragraph("Connections", h2))
s.append(table([
    ["What", "Where", "Settings"],
    ["ST-M01 microphone (condenser)", "Input 2, XLR cable", "+48V on, HI-Z out"],
    ["Acoustic guitar", "In front of the microphone, 20–30 cm away",
     "Microphone aimed where the neck meets the body, not at the sound hole; it picks up from "
     "the side with the <i>steinberg</i> logo"],
    ["Electric guitar", "Input 2, jack cable", "HI-Z pressed, no +48V needed"],
    ["Speakers", "LINE OUTPUT L / R on the rear", "Volume with OUTPUT"],
    ["Headphones", "In the speakers' socket", "With headphones plugged in, the speakers are mute"],
    ["PC", "USB on the rear", "Also powers the interface"],
], [44, 50, 80]))

s.append(KeepTogether([
    Paragraph("Setting the gain", h2),
    Paragraph("Target: peak around −12 dBFS. The PEAK LED lights only when you are already close "
              "to clipping: if it stays off while you play, that is normal.", body),
    table([
        ["Measured peak", "What it means", "What to do"],
        ["below −30 dBFS", "Too low, hiss becomes audible", "Turn GAIN up"],
        ["−18 to −6 dBFS", "Right", "Nothing"],
        ["0 dBFS, clipped samples", "The sound is cut off and cannot be recovered",
         "Turn GAIN down and try again"],
    ], [44, 70, 60]),
    Paragraph("Singing close to the microphone raises the signal a lot: on 29 September, with GAIN "
              "at 2 o'clock, the recording reached 0 dBFS. Tapping the grille lights PEAK even with "
              "little gain.", small),
]))

s.append(KeepTogether([
    Paragraph("Monitoring and feedback", h2),
    table([
        ["MIX", "You hear", "When"],
        ["Fully left (INPUT)", "The microphone only", "To test it, with the speakers muted"],
        ["Centre", "Microphone and computer", "To play along with a track, on headphones"],
        ["Fully right (DAW)", "The computer only", "To record and to play back"],
    ], [44, 50, 80]),
    Paragraph("<b>Feedback</b> is the howl of a microphone picking up the speakers. Avoid it with "
              "MIX on DAW, or OUTPUT at minimum, or with headphones plugged into the speakers.", body),
]))

s.append(KeepTogether([
    Paragraph("Everyday use (music, video)", h2),
    Paragraph("Spotify, YouTube and the browser play through PulseAudio, which uses the UR22mkII "
              "as default output and input. Volume is set with OUTPUT.", body),
    table([
        ["Control", "Position", "Why"],
        ["MIX", "Fully on DAW", "You hear the computer only"],
        ["GAIN 1 and 2", "Minimum", "No noise from the inputs"],
        ["+48V", "OFF", "Only for recording or video calls"],
        ["Desktop volume", "100%, never above", "Above 100% PulseAudio distorts"],
        ["OUTPUT", "The actual volume control", "9–12 o'clock to listen; clean up to three quarters"],
        ["Speaker knob", "Fixed, set once", "Too high and the speakers clip"],
    ], [40, 50, 84]),
    Paragraph("<b>Setting the speakers, once:</b> desktop volume 100%, OUTPUT at minimum, speakers "
              "at half; with a loud track raise OUTPUT to the highest volume you will ever use. If "
              "you get there with OUTPUT almost at minimum, or hear clipping, lower the speaker knob "
              "and repeat, until the maximum comes with OUTPUT at 12–2 o'clock. Then leave the "
              "speaker knob alone.", body),
    Paragraph("<b>Reference position</b> (29 September 2026, tested with Hans Zimmer's "
              "<i>Cornfield Chase</i> and <i>Time</i>): desktop volume 100%, <b>speaker knob at "
              "half</b>. With OUTPUT at <b>three quarters</b> the speakers are still clean, with "
              "headroom above: already very loud, and for normal listening OUTPUT between 9 and 12 "
              "o'clock is enough.", body),
    Paragraph("The UR22mkII outputs are at a higher level than many desktop speakers expect: it is "
              "the speakers' input that clips, not the interface. If the desk vibrates on bass notes, "
              "put some foam under the speakers.", small),
]))

s.append(Paragraph("On Linux", h2))
s.append(table([
    ["Item", "Value"],
    ["Device", "hw:1,0 (card 1, Steinberg UR22mkII); check with <font name='M'>arecord -l</font>"],
    ["Format", "S32_LE only (32 bit): <font name='M'>-f cd</font> fails"],
    ["Channels", "2: left = input 1, right = input 2"],
    ["Sample rates", "44 100 to 192 000 Hz; 44 100 is enough"],
    ["Software controls", "None (<font name='M'>amixer -c 1</font> is empty): everything is on "
                          "the knobs"],
    ["Playback", "<font name='M'>aplay file.wav</font> goes through PulseAudio (default output: the "
                 "UR22). <font name='M'>-D plughw:1,0</font> bypasses PulseAudio: only when nothing "
                 "else is playing"],
    ["Recording", "<font name='M'>arecord -D hw:1,0</font> works while PulseAudio plays: the input "
                  "is free as long as no program uses the microphone"],
], [34, 140]))

s.append(KeepTogether([
    Paragraph("Ready-made commands", h2),
    Paragraph("Record 30 seconds (MIX on DAW):", body),
    Preformatted("arecord -D hw:1,0 -f S32_LE -c 2 -r 44100 -d 30 take.wav", code),
    Paragraph("Record with no time limit, stop with Ctrl+C (with voice: GAIN 2 at 12 o'clock):", body),
    Preformatted("arecord -D hw:1,0 -f S32_LE -c 2 -r 44100 song.wav", code),
    Paragraph("Play back (through PulseAudio, even while the browser is playing):", body),
    Preformatted("aplay song.wav", code),
    Paragraph("About 21 MB per minute. Count \"one, two, three, four\" out loud before playing. "
              "The file name is relative to the folder you are in.", small),
]))

s.append(Paragraph("When something goes wrong", h2))
s.append(table([
    ["Symptom", "Likely cause", "Remedy"],
    ["Silent recording", "HI-Z pressed, +48V off, GAIN low, cable",
     "HI-Z out, +48V on, GAIN at 2 o'clock; then try another cable"],
    ["Microphone not heard on headphones", "MIX on DAW", "MIX on INPUT, speakers muted"],
    ["Computer not heard", "MIX on INPUT, volumes at zero", "MIX on DAW or centre, raise the volume"],
    ["Loud howl", "Feedback", "MIX on DAW or OUTPUT at minimum"],
    ["Bang when pressing HI-Z or +48V", "Normal with high volumes", "Lower GAIN, PHONES, OUTPUT first"],
    ["Hiss with GAIN at maximum", "Preamp noise", "GAIN at 12–2 o'clock"],
    ["Peak at 0 dBFS", "Clipping, often when singing", "GAIN 2 towards 12 o'clock"],
    ["Sample format non available", "-f S32_LE missing", "Use the ready-made commands"],
    ["No such file or directory", "Wrong path for the current folder",
     "Just the file name, or the full path"],
    ["Device or resource busy", "PulseAudio is already using the interface (browser, Spotify)",
     "Drop <font name='M'>-D plughw:1,0</font>: <font name='M'>aplay file.wav</font>"],
], [46, 56, 72]))

s.append(KeepTogether([
    Paragraph("Safe order: how to switch the microphone off", h2),
    Paragraph("The ST-M01 has no switch: it is turned off by switching +48V off. The cable comes "
              "off only afterwards.", body),
    table([
        ["To start", "To finish"],
        ["1. OUTPUT, PHONES and GAIN 2 at minimum", "1. OUTPUT, PHONES and GAIN 2 at minimum"],
        ["2. Connect the microphone to input 2 (HI-Z out)",
         "2. Switch +48V off: the red LED and the blue light on the microphone go out"],
        ["3. Switch +48V on, on the rear", "3. Only now, if you like, unplug the XLR; it may also "
                                           "stay connected"],
        ["4. Raise GAIN 2, then OUTPUT and PHONES", ""],
    ], [87, 87]),
    Paragraph("Unplugging the XLR with +48V on makes a loud bang in headphones and speakers and, "
              "in the long run, stresses microphone and speakers.", small),
]))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                        topMargin=14 * mm, bottomMargin=14 * mm,
                        title="Steinberg UR22mkII on Linux — a short manual",
                        author="Giuseppe Costanzi")
doc.build(s)
print(OUT)
