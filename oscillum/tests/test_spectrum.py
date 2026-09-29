# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for the arithmetic of ui/spectrum.py: the level and the peak it reads.

SpectrumCanvas is a widget, so these tests need a display; without one they
are skipped rather than failed.
"""

import math
import tkinter as tk
import unittest

import numpy as np

from engine import Engine
from i18n import I18n
from log import Log
from ui.spectrum import SpectrumCanvas

RATE = 44100


class TestSpectrum(unittest.TestCase):
    """A sine of known frequency and amplitude is read back as itself."""

    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
        except tk.TclError as exc:
            raise unittest.SkipTest("no display: {0}".format(exc))
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.engine = Engine(Log("unused.log"), I18n("en"))
        self.engine.wav.rate = RATE
        self.canvas = SpectrumCanvas(self.root, self.engine)

    def tearDown(self):
        self.canvas.destroy()

    def get_block(self, frequency, amplitude):
        """A stereo block of SpectrumCanvas.SIZE frames of a sine."""
        t = np.arange(SpectrumCanvas.SIZE) / RATE
        sine = amplitude * np.sin(2 * math.pi * frequency * t)
        return np.column_stack([sine, sine])

    def test_the_peak_is_found_between_the_bins(self):
        # 110 Hz falls between two bins 5.4 Hz apart: the parabola finds it.
        frequencies, levels = self.canvas.get_spectrum(self.get_block(110.0, 0.1))
        peak, level = self.canvas.get_peak(frequencies, levels)
        self.assertAlmostEqual(peak, 110.0, delta=0.3)

    def test_a_full_scale_sine_reads_zero_dbfs(self):
        frequencies, levels = self.canvas.get_spectrum(self.get_block(1000.0, 1.0))
        peak, level = self.canvas.get_peak(frequencies, levels)
        # The Hann window loses up to 1.4 dB between bins; on a bin nothing.
        self.assertAlmostEqual(level, 0.0, delta=1.5)

    def test_the_level_follows_the_amplitude(self):
        loud = self.canvas.get_peak(*self.canvas.get_spectrum(self.get_block(1000.0, 1.0)))[1]
        quiet = self.canvas.get_peak(*self.canvas.get_spectrum(self.get_block(1000.0, 0.1)))[1]
        self.assertAlmostEqual(loud - quiet, 20.0, delta=0.1)

    def test_silence_stays_on_the_floor(self):
        frequencies, levels = self.canvas.get_spectrum(self.get_block(1000.0, 0.0))
        self.assertTrue(np.all(levels == SpectrumCanvas.FLOOR))


if __name__ == "__main__":
    unittest.main()
