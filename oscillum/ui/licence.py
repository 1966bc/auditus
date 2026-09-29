# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""The licence, as it is written in the LICENSE file of the repository."""

import tkinter as tk
from tkinter import ttk


class UI(tk.Toplevel):
    """The text of the licence, read-only, and a button to close it."""

    def __init__(self, parent):
        super().__init__(name="licence")

        self.parent = parent
        self.engine = parent.engine
        self.engine.tools.hide_me(self)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.title(self.engine.i18n.get("licence"))
        self.init_ui()
        self.engine.tools.center_me(self)

    def init_ui(self):

        frm_main = ttk.Frame(self, style="App.TFrame", padding=8)

        frm_text = ttk.Frame(frm_main, style="App.TFrame")
        self.txt_licence = self.engine.tools.get_text(frm_text)
        self.txt_licence.configure(width=72, height=24)
        self.engine.tools.set_text(self.txt_licence, self.engine.get_license())
        frm_text.pack(fill=tk.BOTH, expand=1)

        close = self.engine.i18n.get("close")
        buttons = self.engine.tools.get_button_column(frm_main,
                                                      ((close, self.on_cancel),),
                                                      window=self)
        buttons.pack(anchor=tk.E, pady=(8, 0))

        frm_main.pack(fill=tk.BOTH, expand=1)

    def on_cancel(self, evt=None):
        self.destroy()
