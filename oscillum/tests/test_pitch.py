# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for pitch.py: the open strings of the guitar, and a tuner's cents."""

import unittest

from i18n import I18n
from pitch import Pitch


class TestPitch(unittest.TestCase):
    """A frequency is named as a musician would name it, in either convention."""

    def setUp(self):
        self.english = self.get_pitch("en")
        self.italian = self.get_pitch("it")

    def get_pitch(self, language):
        i18n = I18n(language)
        return Pitch(i18n.get("note_names").split(), int(i18n.get("octave_shift")))

    def test_the_tuning_fork_a(self):
        self.assertEqual(self.english.get_note(440.0), ("A4", 0))
        self.assertEqual(self.italian.get_note(440.0), ("La3", 0))

    def test_the_open_strings_of_the_guitar(self):
        strings = ((82.41, "E2", "Mi1"), (110.00, "A2", "La1"), (146.83, "D3", "Re2"),
                   (196.00, "G3", "Sol2"), (246.94, "B3", "Si2"), (329.63, "E4", "Mi3"))
        for frequency, english, italian in strings:
            self.assertEqual(self.english.get_note(frequency)[0], english)
            self.assertEqual(self.italian.get_note(frequency)[0], italian)

    def test_middle_c(self):
        self.assertEqual(self.english.get_note(261.63)[0], "C4")
        self.assertEqual(self.italian.get_note(261.63)[0], "Do3")

    def test_cents_sharp_and_flat(self):
        # A quarter of a semitone above and below A 440.
        self.assertEqual(self.english.get_note(440.0 * 2 ** (25 / 1200)), ("A4", 25))
        self.assertEqual(self.english.get_note(440.0 * 2 ** (-25 / 1200)), ("A4", -25))

    def test_more_than_half_a_semitone_is_the_next_note(self):
        name, cents = self.english.get_note(440.0 * 2 ** (60 / 1200))
        self.assertEqual(name, "A#4")
        self.assertEqual(cents, -40)


if __name__ == "__main__":
    unittest.main()
