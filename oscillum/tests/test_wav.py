# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for wav.py, on files written in a temporary directory.

Each file holds a sine of known amplitude, so what is read back can be
checked against what was written, for every sample width WAV allows.
"""

import math
import os
import tempfile
import unittest
import wave

import numpy as np

from wav import Wav

RATE = 8000


class TestWav(unittest.TestCase):
    """A file is read as floats between -1 and 1, whatever its width on disk."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.wav = Wav()

    def tearDown(self):
        self.folder.cleanup()

    def write(self, width, channels=1, amplitude=0.5, frames=RATE):
        """A 440 Hz sine of this amplitude, as integers of this width, in a new file."""
        t = np.arange(frames) / RATE
        sine = amplitude * np.sin(2 * math.pi * 440 * t)
        full = self.wav.FULL_SCALE[width]
        values = np.round(sine * (full - 1)).astype(np.int64)
        if width == 1:
            data = (values + 128).astype(np.uint8).tobytes()
        elif width == 3:
            little = values.astype("<i4").view(np.uint8).reshape(-1, 4)[:, :3]
            data = little.tobytes()
        else:
            data = values.astype("<i{0}".format(width)).tobytes()
        if channels == 2:
            data = self.interleave(data, width)
        path = os.path.join(self.folder.name, "sine_{0}.wav".format(width))
        with wave.open(path, "wb") as f:
            f.setnchannels(channels)
            f.setsampwidth(width)
            f.setframerate(RATE)
            f.writeframes(data)
        return path

    def interleave(self, data, width):
        """The same samples on two channels: L R L R..."""
        frames = np.frombuffer(data, dtype=np.uint8).reshape(-1, width)
        return np.hstack([frames, frames]).tobytes()

    def test_every_width_reads_back_the_same_sine(self):
        for width in (1, 2, 3, 4):
            self.wav.read(self.write(width))
            self.assertEqual(self.wav.rate, RATE, width)
            self.assertEqual(self.wav.get_channels(), 1, width)
            # 8 bit has 256 levels: the peak is right to one level in 128.
            self.assertAlmostEqual(self.wav.peak, 0.5, delta=1 / 128, msg=width)

    def test_samples_are_between_minus_one_and_one(self):
        self.wav.read(self.write(2, amplitude=1.0))
        self.assertLessEqual(np.abs(self.wav.samples).max(), 1.0)

    def test_stereo_has_two_channels(self):
        self.wav.read(self.write(2, channels=2))
        self.assertEqual(self.wav.get_channels(), 2)
        self.assertTrue(np.array_equal(self.wav.samples[:, 0], self.wav.samples[:, 1]))

    def test_duration_and_frames(self):
        self.wav.read(self.write(2, frames=RATE * 2))
        self.assertEqual(self.wav.get_frames(), RATE * 2)
        self.assertAlmostEqual(self.wav.get_duration(), 2.0)

    def test_peak_in_dbfs(self):
        self.wav.read(self.write(2, amplitude=0.1))
        self.assertAlmostEqual(self.wav.get_peak_db(), -20.0, places=1)

    def test_silence_is_minus_infinity(self):
        self.wav.read(self.write(2, amplitude=0.0))
        self.assertEqual(self.wav.get_peak_db(), float("-inf"))

    def test_a_block_stays_inside_the_file(self):
        self.wav.read(self.write(2, frames=1000))
        self.assertEqual(len(self.wav.get_block(-500, 100)), 100)
        self.assertEqual(len(self.wav.get_block(990, 100)), 100)
        self.assertTrue(np.array_equal(self.wav.get_block(990, 100), self.wav.samples[900:1000]))

    def test_the_name_is_the_file_name(self):
        self.wav.read(self.write(2))
        self.assertEqual(self.wav.get_name(), "sine_2.wav")


if __name__ == "__main__":
    unittest.main()
