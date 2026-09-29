# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Tests for i18n.py: every sentence in every language, the language chosen right."""

import string
import unittest
from unittest import mock

from i18n import I18n


class TestI18n(unittest.TestCase):
    """A translation is a promise: the same sentence, with the same blanks to fill."""

    def get_fields(self, text):
        """The placeholders of a text, as a sorted list: '{0} of {1}' -> ['0', '1']."""
        return sorted(field for _, field, _, _ in string.Formatter().parse(text)
                      if field is not None)

    def test_every_sentence_has_every_language(self):
        for key, row in I18n.WORDS.items():
            self.assertEqual(len(row), len(I18n.LANGUAGES), key)

    def test_no_sentence_is_left_empty(self):
        for key, row in I18n.WORDS.items():
            for text in row:
                self.assertTrue(text.strip(), key)

    def test_translations_keep_the_same_placeholders(self):
        # A translation that drops {1} would show the wrong number, or fail.
        for key, row in I18n.WORDS.items():
            english = self.get_fields(row[0])
            for text in row[1:]:
                self.assertEqual(self.get_fields(text), english, key)

    def test_the_language_asked_for_wins(self):
        with mock.patch.dict("os.environ", {"LANG": "en_US.UTF-8"}, clear=True):
            self.assertEqual(I18n("it").get("play"), "Suona")

    def test_the_system_language_is_used_by_default(self):
        with mock.patch.dict("os.environ", {"LANG": "it_IT.UTF-8"}, clear=True):
            self.assertEqual(I18n().language, "it")

    def test_lc_all_wins_over_lang(self):
        with mock.patch.dict("os.environ", {"LC_ALL": "it_IT.UTF-8", "LANG": "en_US.UTF-8"},
                             clear=True):
            self.assertEqual(I18n().language, "it")

    def test_an_unknown_language_falls_back_to_the_default(self):
        with mock.patch.dict("os.environ", {"LANG": "fi_FI.UTF-8"}, clear=True):
            self.assertEqual(I18n().language, I18n.DEFAULT)
        self.assertEqual(I18n("xx").language, I18n.DEFAULT)

    def test_no_system_language_means_the_default(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertEqual(I18n().language, I18n.DEFAULT)

    def test_an_unknown_key_fails_at_once(self):
        with self.assertRaises(KeyError):
            I18n("en").get("no_such_sentence")

    def test_accelerators_differ_in_each_language(self):
        # Open and Play are bound to Alt + their first letter: two equal
        # letters would make one of the two keys unreachable.
        for code in I18n.LANGUAGES:
            i18n = I18n(code)
            self.assertNotEqual(i18n.get("open")[0].lower(), i18n.get("play")[0].lower(), code)


if __name__ == "__main__":
    unittest.main()
