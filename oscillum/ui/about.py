# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""About Oscillum: what it is, who wrote it, what it runs on."""

import sys
import tkinter as tk
import webbrowser
from tkinter import ttk


class UI(tk.Toplevel):
    """A small window with the name and a few facts."""

    #: Where the source lives. Opened with webbrowser, from the standard library.
    SOURCE = "https://github.com/1966bc/auditus"

    def __init__(self, parent, info):
        super().__init__(name="about")

        self.parent = parent
        self.engine = parent.engine
        #: The facts, from the metadata in ui/app.py: version, date, author...
        self.info = info
        self.engine.tools.hide_me(self)
        self.transient(parent)
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.title(self.engine.i18n.get("about_title").format(self.info["name"]))
        self.init_ui()
        self.engine.tools.center_me(self)

    def init_ui(self):

        say = self.engine.i18n.get
        frm_main = ttk.Frame(self, style="App.TFrame", padding=16)

        # The largest of the icon's sizes. Kept on self: a PhotoImage that only
        # a local variable points to is collected, and the label goes blank.
        self.icon = tk.PhotoImage(data=self.engine.get_icons("app")[-1])
        ttk.Label(frm_main, image=self.icon).grid(row=0, column=0, rowspan=2,
                                                  sticky=tk.N, padx=(0, 12))
        ttk.Label(frm_main, style="Title.TLabel",
                  text=self.info["name"]).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(frm_main, style="App.TLabel",
                  text=say("tagline")).grid(
                      row=1, column=1, sticky=tk.W)

        ttk.Separator(frm_main).grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=12)

        facts = ((say("version"), "{0}, {1}".format(self.info["version"], self.info["date"])),
                 (say("author"), self.info["author"]),
                 (say("licence_fact"), self.info["licence"]),
                 (say("python_fact"), ".".join(map(str, sys.version_info[:3]))),
                 (say("tk_fact"), self.tk.call("info", "patchlevel")))

        frm_facts = ttk.Frame(frm_main, style="App.TFrame")
        for row, (label, value) in enumerate(facts):
            ttk.Label(frm_facts, style="App.TLabel", text=label).grid(row=row, column=0,
                                                                     sticky=tk.W)
            ttk.Label(frm_facts, style="App.TLabel", text=value).grid(row=row, column=1,
                                                                     sticky=tk.W, padx=(8, 0))

        ttk.Label(frm_facts, style="App.TLabel", text=say("source")).grid(row=len(facts), column=0,
                                                                      sticky=tk.W)
        link = ttk.Label(frm_facts, style="Link.TLabel", text=self.SOURCE, cursor="hand2")
        link.grid(row=len(facts), column=1, sticky=tk.W, padx=(8, 0))
        link.bind("<Button-1>", self.on_source)
        frm_facts.grid(row=3, column=0, columnspan=2, sticky=tk.W)

        buttons = self.engine.tools.get_button_column(frm_main,
                                                      ((say("close"), self.on_cancel),),
                                                      window=self)
        buttons.grid(row=4, column=0, columnspan=2, sticky=tk.E, pady=(12, 0))

        frm_main.pack(fill=tk.BOTH, expand=1)

    def on_source(self, evt=None):
        webbrowser.open(self.SOURCE)

    def on_cancel(self, evt=None):
        self.destroy()
