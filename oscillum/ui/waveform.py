# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""The whole file at a glance, one lane per channel, with the cursor on it."""

import tkinter as tk

import numpy as np


class WaveformCanvas(tk.Canvas):
    """Every pixel column shows the lowest and the highest sample it covers.

    A file of three seconds holds 132 300 frames per channel and the canvas
    a thousand pixels: drawing each sample would draw 132 lines on top of
    each other. The minimum and the maximum of the frames under a pixel are
    all the eye can see there, so that is all that is drawn.
    """

    #: Room on the left for the channel letters.
    LEFT_MARGIN = 22

    #: The lanes stop short of their edges, so the loudest sample is not cut.
    FILL = 0.95

    def __init__(self, parent, engine, **kwargs):
        kwargs.setdefault("bg", engine.tools.get_rgb(*engine.tools.WHITE))
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, **kwargs)

        self.engine = engine
        #: The frame under the cursor, and how much the lanes are enlarged.
        self.cursor = 0
        self.gain = 1.0
        self.bind("<Configure>", self.on_resize)

    def __str__(self):
        return "class: {0}".format(self.__class__.__name__)

    def set_gain(self, gain):

        self.gain = gain
        self.redraw()

    def set_cursor(self, frame):
        """Move the cursor only: the waveform itself does not change."""
        self.cursor = frame
        self.draw_cursor()

    def on_resize(self, evt=None):
        """Redrawn, not stretched: every pixel column is worked out again."""
        self.redraw()

    def redraw(self):

        self.delete("all")
        if self.engine.wav.samples is not None and self.winfo_width() > self.LEFT_MARGIN + 10:
            self.draw_all(self.winfo_width(), self.winfo_height())

    def draw_all(self, width, height):

        tools = self.engine.tools
        wav = self.engine.wav
        lanes = min(wav.get_channels(), 2)
        lane_height = height / lanes
        columns = width - self.LEFT_MARGIN
        edges = np.linspace(0, wav.get_frames(), columns + 1).astype(int)

        for lane in range(lanes):
            middle = lane_height * (lane + 0.5)
            half = lane_height / 2 * self.FILL * self.gain
            colour = tools.get_rgb(*tools.LEFT)
            letter = "L"
            if lane == 1:
                colour = tools.get_rgb(*tools.RIGHT)
                letter = "R"

            self.create_line(self.LEFT_MARGIN, middle, width, middle,
                             fill=tools.get_rgb(*tools.GRID))
            self.create_text(6, middle, text=letter, anchor=tk.W,
                             fill=tools.get_rgb(*tools.LABEL))

            samples = wav.samples[:, lane]
            for column in range(columns):
                block = samples[edges[column]:max(edges[column + 1], edges[column] + 1)]
                x = self.LEFT_MARGIN + column
                self.create_line(x, middle - block.max() * half,
                                 x, middle - block.min() * half + 1,
                                 fill=colour)

        if self.gain > 1.01:
            self.create_text(width - 4, 2, anchor=tk.NE, fill=tools.get_rgb(*tools.LABEL),
                             text="view x{0:.1f} ({1:+.0f} dB)".format(
                                 self.gain, 20 * np.log10(self.gain)))
        self.draw_cursor()

    def draw_cursor(self):

        self.delete("cursor")
        if self.engine.wav.samples is not None:
            x = self.get_x(self.cursor)
            self.create_line(x, 0, x, self.winfo_height(), tags="cursor", width=2,
                             fill=self.engine.tools.get_rgb(*self.engine.tools.EMPHASIS))

    def get_x(self, frame):
        """The pixel column of a frame."""
        columns = self.winfo_width() - self.LEFT_MARGIN
        return self.LEFT_MARGIN + frame / self.engine.wav.get_frames() * columns

    def get_frame(self, x):
        """The frame under a pixel column, kept inside the file."""
        columns = max(self.winfo_width() - self.LEFT_MARGIN, 1)
        share = min(max((x - self.LEFT_MARGIN) / columns, 0.0), 1.0)
        return int(share * (self.engine.wav.get_frames() - 1))
