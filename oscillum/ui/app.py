# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""The application: the root window and the engine.

The facts about the program live here too, once: its version and date, who
wrote it, under which licence. The About window shows them.
"""

import tkinter as tk
from tkinter import messagebox

from engine import Engine
from ui.main import Main

__author__ = "Giuseppe Costanzi (1966bc)"
__copyright__ = "Copyright (c) 2026 1966bc"
__credits__ = ["hal9000", ]
__license__ = "MIT"
__version__ = "1"
__maintainer__ = "1966bc"
__email__ = "giuseppecostanzi@gmail.com"
__date__ = "autumnus MMXXVI"
__status__ = "production"


class App(tk.Tk):
    """The application: the root window and the engine."""

    #: 'clam' looks the same on Linux and Windows and its colours can be set.
    THEME = "clam"

    #: The size of the main window, in pixels: three charts need room.
    WIDTH = 1000
    HEIGHT = 780

    def __init__(self, title, log, i18n, files):
        super().__init__()

        self.engine = Engine(log, i18n)

        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.title(title)
        self.engine.tools.set_style(self.THEME)
        self.minsize(700, 560)
        self.set_icon()
        self.set_info()

        self.main = Main(self)
        self.main.pack(fill=tk.BOTH, expand=1)
        self.engine.tools.set_geometry(self, self.WIDTH, self.HEIGHT)
        self.main.on_open()
        # A file named on the command line is opened once the window has its
        # size: the charts draw themselves to the space they have.
        if files:
            self.after(200, lambda: self.main.load_file(files[0]))
        self.engine.log.trace("ready in {0}; the engine holds log, i18n, tools, wav, player".format(
            self.engine.i18n.language))

    def set_icon(self):
        # The icon in 16, 32 and 48 pixels: the window manager picks the
        # size each place needs, so it is never scaled up and blurred.
        # Kept on self: a PhotoImage only a local variable points to is collected.
        self.icons = [tk.PhotoImage(data=data) for data in self.engine.get_icons("app")]
        self.iconphoto(True, *self.icons)

    def set_info(self):
        """The facts the About window shows, from the metadata at the top of this module."""
        self.info = {"name": self.title(),
                     "version": __version__,
                     "date": __date__,
                     "author": __author__,
                     "licence": __license__}

    def report_callback_exception(self, exc, val, tb):
        """Tkinter calls this for an exception raised in a callback.

        A button, a menu, an after(): every error coming out of the interface
        ends up here, the one place where it is handled. It is written to the
        log with its traceback and shown, so the application goes on and
        nothing fails in silence.
        """
        self.engine.log.trace("{0}: {1}".format(exc.__name__, val))
        self.engine.log.exception("{0}: {1}".format(exc.__name__, val))
        messagebox.showerror(self.title(),
                             self.engine.i18n.get("details").format(val, self.engine.log.path),
                             parent=self)

    def on_exit(self, evt=None):
        if messagebox.askokcancel(self.title(), self.engine.i18n.get("quit"), parent=self):
            self.engine.player.stop()
            self.engine.log.trace("player stopped: goodbye")
            self.destroy()
