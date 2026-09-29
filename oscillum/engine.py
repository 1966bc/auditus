# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
import os
import subprocess
import sys

from player import Player
from tools import Tools
from wav import Wav


class Engine:
    """The one object every window reaches: it owns the parts, it is none of them.

    Composition, not inheritance: Engine is not a player, it has one. Each
    part is an attribute, so a call says who does the work -
    engine.wav.read(...), engine.player.play(...) - and each part can be
    built and tested on its own.
    """

    def __init__(self, log):
        self.log = log
        # Styles and widget helpers.
        self.tools = Tools()
        # The file being looked at.
        self.wav = Wav()
        # The sound, through aplay.
        self.player = Player(log)

    def __str__(self):
        return "class: {0}\nparts: log, tools, wav, player".format(self.__class__.__name__)

    def get_python_version(self):
        return "Python version:\n{0}".format(".".join(map(str, sys.version_info[:3])))

    def get_file(self, file):
        """A file beside the program, wherever it is started from."""
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), file)

    def get_license(self):
        """The licence, which lives at the top of the auditus repository."""
        with open(self.get_file(os.path.join("..", "LICENSE")), "r") as f:
            text = f.read()
        return text

    def get_icons(self, which):
        """Every size of an icon: its file holds one base64 PNG per line (make_icon.py)."""
        with open(self.get_file(which), "r") as f:
            icons = f.read().split()
        return icons

    def open_file(self, path):
        """Open a file with the program the system uses for it."""
        if not os.path.exists(path):
            raise FileNotFoundError("no such file: {0}".format(path))

        if os.name == "posix":
            subprocess.Popen(["xdg-open", path])
        else:
            os.startfile(path)

    def open_log(self):
        """Open the log file with the program the system uses for text."""
        self.open_file(self.log.path)
