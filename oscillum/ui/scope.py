# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""An oscilloscope: a few milliseconds around the cursor, the wave itself."""

import tkinter as tk

import numpy as np


class ScopeCanvas(tk.Canvas):
    """The samples of a short span, joined by a line, both channels on one screen.

    At 20 ms a 110 Hz tone shows two periods and a bit: long enough to see
    its shape, short enough to see every wiggle the harmonics add to it.
    """

    #: The trace stops short of the edges, so the loudest sample is not cut.
    FILL = 0.95

    def __init__(self, parent, engine, **kwargs):
        kwargs.setdefault("bg", engine.tools.get_rgb(*engine.tools.WHITE))
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, **kwargs)

        self.engine = engine
        self.cursor = 0
        self.gain = 1.0
        #: How many milliseconds the screen holds.
        self.span = 20
        self.bind("<Configure>", self.on_resize)

    def __str__(self):
        return "class: {0}".format(self.__class__.__name__)

    def set_gain(self, gain):

        self.gain = gain
        self.redraw()

    def set_span(self, milliseconds):

        self.span = milliseconds
        self.redraw()

    def set_cursor(self, frame):

        self.cursor = frame
        self.redraw()

    def on_resize(self, evt=None):
        self.redraw()

    def redraw(self):

        self.delete("all")
        if self.winfo_width() > 10:
            self.draw_grid(self.winfo_width(), self.winfo_height())
            if self.engine.wav.samples is not None:
                self.draw_trace(self.winfo_width(), self.winfo_height())

    def draw_grid(self, width, height):

        tools = self.engine.tools
        grid = tools.get_rgb(*tools.GRID)
        label = tools.get_rgb(*tools.LABEL)

        for share in (0.25, 0.5, 0.75):
            self.create_line(0, height * share, width, height * share, fill=grid)
        for tenth in range(1, 10):
            self.create_line(width * tenth / 10, 0, width * tenth / 10, height, fill=grid)

        # What the top of the screen stands for: full scale, or less when the
        # view is enlarged to fit a quiet file.
        top = 1 / self.gain
        self.create_text(4, 2, anchor=tk.NW, fill=label, text="+{0:.2f}".format(top))
        self.create_text(4, height - 2, anchor=tk.SW, fill=label, text="-{0:.2f}".format(top))
        self.create_text(width - 4, height - 2, anchor=tk.SE, fill=label,
                         text=self.engine.i18n.get("division").format(self.span, self.span / 10))

    def draw_trace(self, width, height):

        tools = self.engine.tools
        wav = self.engine.wav
        size = max(int(self.span / 1000 * wav.rate), 2)
        block = wav.get_block(self.cursor - size // 2, size)
        xs = np.linspace(0, width, len(block))
        half = height / 2 * self.FILL * self.gain

        # The right channel first, so the left one is drawn on top of it.
        for channel in range(min(block.shape[1], 2) - 1, -1, -1):
            colour = tools.get_rgb(*tools.LEFT)
            if channel == 1:
                colour = tools.get_rgb(*tools.RIGHT)
            ys = height / 2 - block[:, channel] * half
            points = np.column_stack([xs, ys]).ravel().tolist()
            if len(points) >= 4:
                self.create_line(*points, fill=colour)
