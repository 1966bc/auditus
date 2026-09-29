# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""The words of the interface, in more than one language, written by hand.

The standard library has `gettext`, which does this for large programs:
translations kept in .po files, compiled to .mo, looked up by the English
text itself. This class does only what Oscillum needs, so that a reader can
see what translating an interface comes down to: every sentence has a key,
and each key has one text per language.

The texts are kept side by side, one row per sentence and one column per
language, so a missing translation shows as a gap in the row. Adding a
language means adding a column to every row, and its code to LANGUAGES.

Placeholders follow str.format: the caller fills them, the translation may
move them, because another language may want the words in another order.
"""

import os


class I18n:
    """Every sentence of the interface, by key, in the chosen language."""

    #: The languages known, in the order of the columns of WORDS.
    LANGUAGES = ("en", "it")

    #: Used when the system asks for a language not known here.
    DEFAULT = "en"

    WORDS = {
        # the menus
        "file": ("File", "File"),
        "open_menu": ("Open...", "Apri..."),
        "log": ("Log", "Log"),
        "exit": ("Exit", "Esci"),
        "about": ("About", "Informazioni"),
        "licence": ("Licence", "Licenza"),
        "python": ("Python", "Python"),
        "tkinter": ("Tkinter", "Tkinter"),

        # the toolbar: the transport buttons are icons, they need no words
        "oscilloscope": ("Oscilloscope", "Oscilloscopio"),
        "fit": ("Fit", "Adatta"),

        # the charts
        "waveform": ("Waveform", "Forma d'onda"),
        "spectrum": ("Spectrum", "Spettro"),
        "left": ("L", "S"),
        "right": ("R", "D"),
        "view": ("view x{0:.1f} ({1:+.0f} dB)", "vista x{0:.1f} ({1:+.0f} dB)"),
        "division": ("{0} ms, {1:g} ms per division", "{0} ms, {1:g} ms per divisione"),
        "peak_at": ("peak {0:.1f} Hz, {1:.1f} dBFS", "picco {0:.1f} Hz, {1:.1f} dBFS"),
        "note_at": ("{0} {1:+d} cents", "{0} {1:+d} cent"),

        # the notes: the twelve names from C, and how octaves are numbered
        # (the A at 440 Hz is A4 in English, La3 in Italian: pitch.py)
        "note_names": ("C C# D D# E F F# G G# A A# B",
                       "Do Do# Re Re# Mi Fa Fa# Sol Sol# La La# Si"),
        "octave_shift": ("0", "-1"),

        # the status bar and the file
        "ready": ("Open a WAV file: File, Open... or Ctrl+O. Space plays and pauses, "
                  "Home goes to the start, Esc stops.",
                  "Apri un file WAV: File, Apri... oppure Ctrl+O. Spazio suona e mette in "
                  "pausa, Home torna all'inizio, Esc ferma."),
        "file_info": ("{0}   {1} Hz, {2}, {3:.1f} s, peak {4:.1f} dBFS",
                      "{0}   {1} Hz, {2}, {3:.1f} s, picco {4:.1f} dBFS"),
        "mono": ("mono", "mono"),
        "stereo": ("stereo", "stereo"),
        "channels": ("{0} channels", "{0} canali"),
        "open_title": ("Open a WAV file...", "Apri un file WAV..."),
        "wav_files": ("WAV files", "File WAV"),
        "all_files": ("All files", "Tutti i file"),

        # messages
        "quit": ("Do you want to quit?", "Vuoi uscire?"),
        "details": ("{0}\n\nDetails in {1}", "{0}\n\nDettagli in {1}"),
        "log_empty": ("The log is empty: nothing has gone wrong so far.",
                      "Il log è vuoto: finora non è andato storto niente."),
        "python_version": ("Python version:\n{0}", "Versione di Python:\n{0}"),
        "tkinter_version": ("Tkinter patchlevel\n{0}", "Versione di Tkinter\n{0}"),

        # the About and Licence windows
        "about_title": ("About {0}", "Informazioni su {0}"),
        "tagline": ("Listen to a sound and see it: waveform, oscilloscope, spectrum.",
                    "Ascolta un suono e guardalo: forma d'onda, oscilloscopio, spettro."),
        "version": ("Version:", "Versione:"),
        "author": ("Author:", "Autore:"),
        "licence_fact": ("Licence:", "Licenza:"),
        "python_fact": ("Python:", "Python:"),
        "tk_fact": ("Tk:", "Tk:"),
        "source": ("Source:", "Sorgente:"),
        "close": ("Close", "Chiudi"),
    }

    def __init__(self, language=None):
        self.language = self.get_language(language)
        self.column = self.LANGUAGES.index(self.language)

    def __str__(self):
        return "class: {0}\nlanguage: {1}".format(self.__class__.__name__, self.language)

    def get_language(self, asked):
        """The language to speak: the one asked for, else the system's, else DEFAULT.

        The system's is read as a Unix program reads it: LC_ALL wins over
        LC_MESSAGES, which wins over LANG. 'it_IT.UTF-8' is Italian.
        """
        found = asked
        if found is None:
            for name in ("LC_ALL", "LC_MESSAGES", "LANG"):
                value = os.environ.get(name, "")
                if found is None and value:
                    found = value[:2].lower()
        if found not in self.LANGUAGES:
            found = self.DEFAULT
        return found

    def get(self, key):
        """The text of a key in the current language.

        A key that is not in WORDS raises KeyError at once: a window with a
        hole in it is worse than an error that says which word is missing.
        """
        return self.WORDS[key][self.column]
