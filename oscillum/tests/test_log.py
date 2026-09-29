# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for log.py, on a file in a temporary directory."""

import contextlib
import io
import os
import tempfile
import unittest

from log import Log


class TestLog(unittest.TestCase):
    """Each entry says when, how serious, where and what."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.log = Log(os.path.join(self.folder.name, "oscillum.log"))

    def tearDown(self):
        self.folder.cleanup()

    def get_text(self):
        with open(self.log.path, "r", encoding="utf-8") as f:
            text = f.read()
        return text

    def test_error_says_level_where_and_what(self):
        self.log.error("something went wrong")
        text = self.get_text()
        self.assertIn("ERROR", text)
        self.assertIn("test_error_says_level_where_and_what", text)
        self.assertIn("something went wrong", text)

    def test_exception_adds_the_traceback(self):
        try:
            int("abc")
        except ValueError:
            self.log.exception("not a number")
        text = self.get_text()
        self.assertIn("Traceback (most recent call last)", text)
        self.assertIn("ValueError", text)

    def test_empty_until_the_first_entry(self):
        self.assertTrue(self.log.is_empty())
        self.log.error("first")
        self.assertFalse(self.log.is_empty())

    def test_a_full_file_is_rotated(self):
        self.log.MAX_SIZE = 50
        self.log.error("x" * 60)
        self.log.error("after the rotation")
        self.assertTrue(os.path.exists("{0}.1".format(self.log.path)))
        self.assertIn("after the rotation", self.get_text())

    def test_trace_prints_only_when_tracing(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.log.trace("silent")
            self.log.tracing = True
            self.log.trace("loud")
        self.assertNotIn("silent", out.getvalue())
        self.assertIn("loud", out.getvalue())


if __name__ == "__main__":
    unittest.main()
