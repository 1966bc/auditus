#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Compose the GitHub social preview, docs/social-preview.png.

A build tool, like oscillum/make_icon.py, and like it it needs Pillow. The
image is 1280 by 640, the size GitHub asks for, with everything that matters
kept away from the edges, which some sites crop. The layout is the one of
calendarium's preview, so the author's projects look like one family.

On the left the Oscillum icon, the name and what it is; on the right
Oscillum itself, from oscillum/screenshot.png, showing the A at 110 Hz of
lesson 1 with its harmonics.

GitHub has no API for the social preview: upload the result by hand, in
Settings > General > Social preview.

    python3 docs/make_social_preview.py
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "oscillum"))

from make_icon import get_image as draw_icon  # noqa: E402

WIDTH, HEIGHT = 1280, 640
MARGIN = 70

#: How wide the Oscillum window is drawn on the right, in pixels.
CARD_WIDTH = 590

BACKGROUND = (246, 245, 240)
INK = (33, 37, 41)
MUTED = (110, 115, 120)
ACCENT = (58, 110, 165)         # the blue of the icon, Tools.FOCUS
CARD_EDGE = (150, 150, 150)
SHADOW = (0, 0, 0, 60)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")

TITLE = "auditus"
TAGLINE = "Hear it, then see it"
POINTS = (
    "A course in sound for musicians",
    "Lessons with test sounds to listen to",
    "Oscillum: waveform, scope, spectrum",
    "Python, Tkinter and numpy, on Linux",
)
FOOTER = "github.com/1966bc/auditus"


def paste_card(canvas, card, x, y):
    """The window as a card: a soft shadow under it and a thin edge round it."""
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle(
        (x + 8, y + 10, x + card.width + 8, y + card.height + 10), fill=SHADOW)
    canvas.alpha_composite(shadow)
    canvas.paste(card, (x, y))
    ImageDraw.Draw(canvas).rectangle(
        (x - 1, y - 1, x + card.width, y + card.height), outline=CARD_EDGE, width=2)


def main():

    canvas = Image.new("RGBA", (WIDTH, HEIGHT), BACKGROUND + (255,))
    pen = ImageDraw.Draw(canvas)

    card = Image.open(os.path.join(ROOT, "oscillum", "screenshot.png")).convert("RGBA")
    height = round(card.height * CARD_WIDTH / card.width)
    card = card.resize((CARD_WIDTH, height), Image.LANCZOS)
    card_x = WIDTH - MARGIN - card.width
    card_y = (HEIGHT - card.height) // 2
    paste_card(canvas, card, card_x, card_y)

    x = MARGIN
    canvas.alpha_composite(draw_icon(128), (x - 6, 78))

    title = ImageFont.truetype(BOLD, 64)
    tagline = ImageFont.truetype(REGULAR, 30)
    point = ImageFont.truetype(REGULAR, 25)
    footer = ImageFont.truetype(REGULAR, 22)

    pen.text((x, 222), TITLE, font=title, fill=INK)
    pen.text((x, 304), TAGLINE, font=tagline, fill=ACCENT)

    y = 370
    for text in POINTS:
        pen.ellipse((x + 2, y + 10, x + 12, y + 20), fill=ACCENT)
        pen.text((x + 26, y), text, font=point, fill=INK)
        y += 40

    pen.text((x, HEIGHT - MARGIN - 22), FOOTER, font=footer, fill=MUTED)

    # The text is measured where it was drawn: the points start 26 further in.
    right = max([pen.textbbox((x, 0), TITLE, font=title)[2],
                 pen.textbbox((x, 0), TAGLINE, font=tagline)[2]]
                + [pen.textbbox((x + 26, 0), text, font=point)[2] for text in POINTS])
    if right + 26 > card_x:
        raise SystemExit("text runs into the window: {0} > {1}".format(right + 26, card_x))

    path = os.path.join(ROOT, "docs", "social-preview.png")
    canvas.convert("RGB").save(path, optimize=True)
    print("{0}: {1}x{2}, {3} bytes".format(path, WIDTH, HEIGHT, os.path.getsize(path)))


if __name__ == "__main__":
    main()
