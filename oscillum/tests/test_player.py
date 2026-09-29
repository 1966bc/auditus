# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for player.py that make no sound: the clock and the states.

Playing itself needs aplay and a sound card, and is tried by hand.
"""

import time
import unittest

from log import Log
from player import Player


class TestPlayer(unittest.TestCase):
    """Where the sound is, reckoned from the clock."""

    def setUp(self):
        self.player = Player(Log("unused.log"))

    def test_nothing_plays_at_first(self):
        self.assertFalse(self.player.is_playing())

    def test_stop_without_playing_is_harmless(self):
        self.player.stop()
        self.assertFalse(self.player.is_playing())

    def test_the_frame_follows_the_clock(self):
        # Started one second ago from frame 1000, at 8000 frames a second.
        self.player.first = 1000
        self.player.started = time.monotonic() - 1.0
        frame = self.player.get_frame(8000)
        self.assertGreaterEqual(frame, 9000)
        self.assertLess(frame, 9000 + 800)


if __name__ == "__main__":
    unittest.main()
