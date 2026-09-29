#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Draw the Oscillum icon, once, and write it into the file 'app' as base64.

A build tool, not part of the program. It needs Pillow, Oscillum does not:
the PNGs are drawn when the picture changes and the result is committed.

The picture is the screen of an oscilloscope: a rounded square in the blue
of the keyboard focus, a faint grid, and on it two periods of an A with its
harmonics - the shape the oscilloscope view shows for the lesson 1 sound.
It is drawn at eight times each size and reduced, so the edges stay smooth.

    python3 make_icon.py

The file 'app' holds one PNG per line, 16, 32 and 48 pixels: the window
manager picks the size each place needs, so it is never scaled up and blurred.
"""

import base64
import io
import math
import os

from PIL import Image, ImageDraw

#: The sizes written to the file, smallest first.
SIZES = (16, 32, 48)

#: Each size is drawn this many times larger, then reduced.
SCALE = 8

SCREEN = (58, 110, 165, 255)            # Tools.FOCUS
GRID = (96, 142, 190, 255)
TRACE = (255, 255, 255, 255)
EDGE = (36, 72, 112, 255)

#: The harmonics of the trace: amplitude 1/k, like the lesson 1 sound.
HARMONICS = 6

#: How many periods the screen shows.
PERIODS = 2


def get_wave(phase):
    """The trace at a phase between 0 and 1 of the whole screen, between -1 and 1."""
    value = 0.0
    for k in range(1, HARMONICS + 1):
        value += math.sin(2 * math.pi * k * PERIODS * phase) / k
    return value / 1.6


def get_image(size):
    """One icon of size x size pixels."""
    big = size * SCALE
    image = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    margin = big * 0.04
    radius = big * 0.18
    draw.rounded_rectangle((margin, margin, big - margin, big - margin), radius=radius,
                           fill=SCREEN, outline=EDGE, width=max(int(big * 0.03), 1))

    # The grid only where it can be seen: at 16 pixels it would be noise.
    if size >= 32:
        line = max(int(big * 0.012), 1)
        for share in (0.25, 0.5, 0.75):
            position = big * share
            draw.line((margin * 3, position, big - margin * 3, position), fill=GRID, width=line)
            draw.line((position, margin * 3, position, big - margin * 3), fill=GRID, width=line)

    left = big * 0.14
    right = big * 0.86
    middle = big * 0.5
    height = big * 0.30
    points = []
    steps = 200
    for step in range(steps + 1):
        phase = step / steps
        points.append((left + phase * (right - left), middle - get_wave(phase) * height))
    # Thick where the icon is small, or the trace is lost; thinner where
    # there is room, so the wiggles of the harmonics read as a shape.
    thickness = 0.045
    if size <= 16:
        thickness = 0.09
    elif size <= 32:
        thickness = 0.06
    draw.line(points, fill=TRACE, width=max(int(big * thickness), 1), joint="curve")

    return image.resize((size, size), Image.LANCZOS)


def get_base64(image):
    """A PNG image as one line of base64 text."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def main():

    here = os.path.dirname(os.path.abspath(__file__))
    lines = [get_base64(get_image(size)) for size in SIZES]
    with open(os.path.join(here, "app"), "w") as f:
        f.write("\n".join(lines) + "\n")
    get_image(256).save(os.path.join(here, "icon.png"))
    print("app: {0} sizes, icon.png: 256 px".format(len(SIZES)))


if __name__ == "__main__":
    main()
