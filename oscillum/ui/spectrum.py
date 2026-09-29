# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""The spectrum at the cursor: which frequencies the sound is made of."""

import tkinter as tk

import numpy as np


class SpectrumCanvas(tk.Canvas):
    """A Fourier transform of the frames around the cursor, in dBFS.

    8192 frames at 44.1 kHz are 186 ms: bins 5.4 Hz apart, fine enough to
    tell 110 Hz from its neighbours. The frames are multiplied by a Hann
    window first, so the edges of the block do not smear energy over the
    whole spectrum. The frequency axis is logarithmic, like the ear and
    like a keyboard: every octave takes the same room.
    """

    SIZE = 8192

    #: The bottom of the scale: below this nothing is drawn.
    FLOOR = -100.0

    LOW = 20.0
    HIGH = 20000.0

    #: The gridlines: the octaves of A, which a musician reads at once.
    OCTAVES = (27.5, 55, 110, 220, 440, 880, 1760, 3520, 7040, 14080)

    LEFT_MARGIN = 38
    TOP_MARGIN = 8
    BOTTOM_MARGIN = 20
    RIGHT_MARGIN = 8

    def __init__(self, parent, engine, **kwargs):
        kwargs.setdefault("bg", engine.tools.get_rgb(*engine.tools.WHITE))
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, **kwargs)

        self.engine = engine
        self.cursor = 0
        self.bind("<Configure>", self.on_resize)

    def __str__(self):
        return "class: {0}".format(self.__class__.__name__)

    def set_cursor(self, frame):

        self.cursor = frame
        self.redraw()

    def on_resize(self, evt=None):
        self.redraw()

    def redraw(self):

        self.delete("all")
        if self.winfo_width() > self.LEFT_MARGIN + 20:
            self.draw_grid()
            if self.engine.wav.samples is not None:
                self.draw_spectrum()

    def get_high(self):
        """The highest frequency drawn: 20 kHz, or less for a low sample rate."""
        high = self.HIGH
        if self.engine.wav.samples is not None:
            high = min(self.HIGH, self.engine.wav.rate / 2)
        return high

    def get_x(self, frequency):
        """The pixel column of a frequency, on a logarithmic axis."""
        right = self.winfo_width() - self.RIGHT_MARGIN
        share = ((np.log10(frequency) - np.log10(self.LOW))
                 / (np.log10(self.get_high()) - np.log10(self.LOW)))
        return self.LEFT_MARGIN + share * (right - self.LEFT_MARGIN)

    def get_y(self, level):
        """The pixel row of a level in dBFS: 0 at the top, FLOOR at the bottom."""
        bottom = self.winfo_height() - self.BOTTOM_MARGIN
        return self.TOP_MARGIN + level / self.FLOOR * (bottom - self.TOP_MARGIN)

    def draw_grid(self):

        tools = self.engine.tools
        grid = tools.get_rgb(*tools.GRID)
        label = tools.get_rgb(*tools.LABEL)
        right = self.winfo_width() - self.RIGHT_MARGIN
        bottom = self.winfo_height() - self.BOTTOM_MARGIN

        for frequency in self.OCTAVES:
            if self.LOW <= frequency <= self.get_high():
                x = self.get_x(frequency)
                self.create_line(x, self.TOP_MARGIN, x, bottom, fill=grid)
                self.create_text(x, bottom + 3, anchor=tk.N, fill=label,
                                 text="{0:g}".format(frequency))

        for level in range(0, int(self.FLOOR) - 1, -20):
            y = self.get_y(level)
            self.create_line(self.LEFT_MARGIN, y, right, y, fill=grid)
            self.create_text(self.LEFT_MARGIN - 4, y, anchor=tk.E, fill=label,
                             text=str(level))

    def get_spectrum(self, block):
        """Frequencies and levels in dBFS of a block of frames.

        The channels are averaged first: one spectrum per file. The level is
        scaled so that a full-scale sine reads 0 dBFS.
        """
        mono = block.mean(axis=1)
        if len(mono) < self.SIZE:
            mono = np.pad(mono, (0, self.SIZE - len(mono)))
        window = np.hanning(self.SIZE)
        magnitude = np.abs(np.fft.rfft(mono * window)) / (window.sum() / 2)
        levels = np.maximum(20 * np.log10(np.maximum(magnitude, 1e-12)), self.FLOOR)
        frequencies = np.fft.rfftfreq(self.SIZE, 1 / self.engine.wav.rate)
        return frequencies, levels

    def get_peak(self, frequencies, levels):
        """The strongest bin, refined between its neighbours by a parabola.

        The bins are 5.4 Hz apart: the parabola through the peak and the two
        beside it finds the top between them, so 110 Hz reads 110.0 and not
        the nearest bin.
        """
        inside = (frequencies >= self.LOW) & (frequencies <= self.get_high())
        index = int(np.argmax(np.where(inside, levels, self.FLOOR - 1)))
        shift = 0.0
        if 0 < index < len(levels) - 1:
            before, top, after = levels[index - 1], levels[index], levels[index + 1]
            curve = before - 2 * top + after
            if curve != 0:
                shift = 0.5 * (before - after) / curve
        step = frequencies[1] - frequencies[0]
        return (index + shift) * step, levels[index]

    def draw_spectrum(self):

        tools = self.engine.tools
        wav = self.engine.wav
        block = wav.get_block(self.cursor - self.SIZE // 2, self.SIZE)
        frequencies, levels = self.get_spectrum(block)

        # One point per pixel column: the highest of the bins that fall in it.
        inside = (frequencies >= self.LOW) & (frequencies <= self.get_high())
        columns = self.get_x(frequencies[inside]).astype(int)
        highest = {}
        for column, level in zip(columns, levels[inside]):
            if level > highest.get(column, self.FLOOR - 1):
                highest[column] = level
        points = []
        for column in sorted(highest):
            points.extend((column, self.get_y(highest[column])))
        if len(points) >= 4:
            self.create_line(*points, fill=tools.get_rgb(*tools.LEFT))

        frequency, level = self.get_peak(frequencies, levels)
        if level > self.FLOOR + 10:
            self.create_text(self.winfo_width() - self.RIGHT_MARGIN, self.TOP_MARGIN,
                             anchor=tk.NE, fill=tools.get_rgb(*tools.FOREGROUND),
                             text="peak {0:.1f} Hz, {1:.1f} dBFS".format(frequency, level))
