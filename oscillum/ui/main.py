# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""The main window: the three views, the toolbar and the menus.

The module keeps the name main, a homage to C's main(); the program itself
starts from main() in oscillum.py.
"""

import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import ui.about
import ui.licence
from ui.scope import ScopeCanvas
from ui.spectrum import SpectrumCanvas
from ui.waveform import WaveformCanvas

#: The spans the oscilloscope offers, in milliseconds.
SPANS = (5, 10, 20, 50, 100)

#: How often the cursor follows playback, in milliseconds: 20 times a
#: second is smooth to the eye and costs little.
TICK = 50


class Main(ttk.Frame):
    """Open a file, play it, and watch it: waveform, oscilloscope, spectrum."""

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.engine = parent.engine
        #: The frame under the cursor, and where playback started from.
        self.cursor = 0
        self.play_from = 0
        #: True from Play to the end of the sound: the window remembers it,
        #: so it knows when playback has ended on its own.
        self.playing = False
        #: 1 enlarges waveform and oscilloscope to fill the lanes.
        self.fit = tk.IntVar(value=1)
        #: The status bar: the file on the left, the cursor on the right.
        self.file_text = tk.StringVar()
        self.cursor_text = tk.StringVar()
        self.init_menu()
        self.init_toolbar()
        self.init_status_bar()
        self.init_ui()

    def init_menu(self):

        m_main = tk.Menu(self, bd=1)
        m_file = tk.Menu(m_main, tearoff=0, bd=1)
        m_about = tk.Menu(m_main, tearoff=0, bd=1)

        say = self.engine.i18n.get

        for label, menu in ((say("file"), m_file), ("?", m_about)):
            m_main.add_cascade(label=label, underline=0, menu=menu)

        for label, command in ((say("open_menu"), self.on_open_file), (say("log"), self.on_log)):
            m_file.add_command(label=label, underline=0, command=command)
        m_file.add_separator()
        m_file.add_command(label=say("exit"), underline=0, command=self.parent.on_exit)

        for label, command in ((say("about"), self.on_about),
                               (say("licence"), self.on_licence),
                               (say("python"), self.on_python_version),
                               (say("tkinter"), self.on_tkinter_version)):
            m_about.add_command(label=label, underline=0, command=command)

        self.parent.config(menu=m_main)

    def init_toolbar(self):

        say = self.engine.i18n.get
        toolbar = ttk.Frame(self, style="App.TFrame", padding=4)

        ttk.Button(toolbar, style="App.TButton", text=say("open"), underline=0,
                   command=self.on_open_file).pack(side=tk.LEFT, padx=2)
        self.btn_play = ttk.Button(toolbar, style="App.TButton", text=say("play"), underline=0,
                                   width=6, command=self.on_play)
        self.btn_play.pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, style="App.TLabel", text=say("oscilloscope")).pack(side=tk.LEFT,
                                                                          padx=(12, 2))
        self.cb_span = self.engine.tools.get_combo(toolbar)
        self.cb_span.configure(width=8)
        self.cb_span["values"] = ["{0} ms".format(span) for span in SPANS]
        self.cb_span.current(SPANS.index(20))
        self.cb_span.bind("<<ComboboxSelected>>", self.on_span)
        self.cb_span.pack(side=tk.LEFT)

        self.chk_fit = ttk.Checkbutton(toolbar, style="App.TCheckbutton", text=say("fit"),
                                       variable=self.fit, command=self.on_fit)
        self.chk_fit.pack(side=tk.LEFT, padx=(12, 0))

        toolbar.pack(side=tk.TOP, fill=tk.X)

        # The same keys everywhere in the window, whatever has the focus. The
        # Alt letters are the first of each word in the language shown, the
        # one underlined on the button: Open is Alt+O, Apri is Alt+A.
        self.parent.bind_all("<space>", self.on_play)
        self.parent.bind_all("<Alt-{0}>".format(say("open")[0].lower()), self.on_open_file)
        self.parent.bind_all("<Alt-{0}>".format(say("play")[0].lower()), self.on_play)

    def init_status_bar(self):
        """The file on the left, the cursor on the right."""
        frm_status = ttk.Frame(self, style="StatusBar.TFrame", borderwidth=1, relief=tk.SUNKEN)
        ttk.Label(frm_status,
                  textvariable=self.file_text,
                  style="StatusBar.TLabel",
                  anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=1)
        ttk.Label(frm_status,
                  textvariable=self.cursor_text,
                  style="StatusBar.TLabel",
                  anchor=tk.E).pack(side=tk.RIGHT)
        frm_status.pack(side=tk.BOTTOM, fill=tk.X)

    def init_ui(self):

        say = self.engine.i18n.get
        frm_main = ttk.Frame(self, style="App.TFrame", padding=8)

        lbl_waveform = ttk.LabelFrame(frm_main, style="App.TLabelframe", text=say("waveform"))
        self.cnv_waveform = WaveformCanvas(lbl_waveform, self.engine, height=150)
        self.cnv_waveform.pack(fill=tk.BOTH, expand=1)
        self.cnv_waveform.bind("<Button-1>", self.on_seek)
        self.cnv_waveform.bind("<B1-Motion>", self.on_seek)
        lbl_waveform.pack(fill=tk.BOTH, expand=1, pady=(0, 6))

        lbl_scope = ttk.LabelFrame(frm_main, style="App.TLabelframe", text=say("oscilloscope"))
        self.cnv_scope = ScopeCanvas(lbl_scope, self.engine, height=190)
        self.cnv_scope.pack(fill=tk.BOTH, expand=1)
        lbl_scope.pack(fill=tk.BOTH, expand=1, pady=(0, 6))

        lbl_spectrum = ttk.LabelFrame(frm_main, style="App.TLabelframe", text=say("spectrum"))
        self.cnv_spectrum = SpectrumCanvas(lbl_spectrum, self.engine, height=230)
        self.cnv_spectrum.pack(fill=tk.BOTH, expand=1)
        lbl_spectrum.pack(fill=tk.BOTH, expand=1)

        frm_main.pack(fill=tk.BOTH, expand=1)

    def on_open(self, evt=None):

        say = self.engine.i18n.get
        self.file_text.set(say("ready").format(say("open")[0].upper()))
        self.cursor_text.set("")

    def on_open_file(self, evt=None):

        say = self.engine.i18n.get
        wildcard = [(say("wav_files"), "*.wav"), (say("all_files"), "*.*")]
        path = filedialog.askopenfilename(parent=self, title=say("open_title"),
                                          initialdir=os.getcwd(), filetypes=wildcard)
        if path:
            self.load_file(path)

    def load_file(self, path):
        """Read a file and show it from its first frame."""
        self.stop()
        self.engine.tools.busy(self)
        try:
            self.engine.wav.read(path)
        finally:
            self.engine.tools.not_busy(self)

        say = self.engine.i18n.get
        wav = self.engine.wav
        self.parent.title("{0} - {1}".format(self.parent.info["name"], wav.get_name()))
        channels = say("channels").format(wav.get_channels())
        if wav.get_channels() == 1:
            channels = say("mono")
        elif wav.get_channels() == 2:
            channels = say("stereo")
        self.file_text.set(say("file_info").format(
            wav.get_name(), wav.rate, channels, wav.get_duration(), wav.get_peak_db()))
        self.engine.log.trace("{0}: {1} frames".format(path, wav.get_frames()))

        self.set_gain()
        self.set_cursor(0)

    def set_gain(self):
        """Enlarge waveform and oscilloscope so that the peak of the file fills them."""
        gain = 1.0
        if self.fit.get() and self.engine.wav.peak > 0:
            gain = 1 / self.engine.wav.peak
        self.cnv_waveform.set_gain(gain)
        self.cnv_scope.set_gain(gain)

    def set_cursor(self, frame):
        """Put every view on this frame."""
        self.cursor = frame
        self.cnv_waveform.set_cursor(frame)
        self.cnv_scope.set_cursor(frame)
        self.cnv_spectrum.set_cursor(frame)
        self.cursor_text.set(self.engine.i18n.get("cursor").format(frame / self.engine.wav.rate))

    def on_fit(self, evt=None):

        if self.engine.wav.samples is not None:
            self.set_gain()

    def on_span(self, evt=None):

        self.cnv_scope.set_span(SPANS[self.cb_span.current()])

    def on_seek(self, evt=None):
        """A click on the waveform moves the cursor; while playing, the sound follows."""
        if self.engine.wav.samples is not None:
            self.set_cursor(self.cnv_waveform.get_frame(evt.x))
            if self.playing:
                self.play_from = self.cursor
                self.engine.player.play(self.engine.wav, self.cursor)

    def on_play(self, evt=None):
        """Play from the cursor, or stop: the same key does both."""
        if self.engine.wav.samples is not None:
            if self.playing:
                self.stop()
            else:
                self.start()

    def start(self):

        if self.cursor >= self.engine.wav.get_frames() - 1:
            self.set_cursor(0)
        self.play_from = self.cursor
        self.engine.player.play(self.engine.wav, self.cursor)
        self.playing = True
        self.btn_play.configure(text=self.engine.i18n.get("stop"))
        self.after(TICK, self.follow)

    def stop(self):

        self.engine.player.stop()
        self.playing = False
        self.btn_play.configure(text=self.engine.i18n.get("play"))

    def follow(self):
        """Move the cursor with the sound, TICK by TICK, on the main loop.

        When the sound has ended on its own, the cursor goes back to where it
        started, like a tape recorder: the end of a file is usually silence,
        and the views would have nothing to show there.
        """
        if self.playing:
            if self.engine.player.is_playing():
                frame = self.engine.player.get_frame(self.engine.wav.rate)
                self.set_cursor(min(frame, self.engine.wav.get_frames() - 1))
                self.after(TICK, self.follow)
            else:
                self.stop()
                self.set_cursor(self.play_from)

    def show_window(self, name, build):
        """One window per name: brought forward if open, built if not."""
        window = self.parent.children.get(name)
        if window is not None and window.winfo_exists():
            window.lift()
        else:
            build()

    def on_about(self):
        self.show_window("about", lambda: ui.about.UI(self, self.parent.info))

    def on_licence(self):
        self.show_window("licence", lambda: ui.licence.UI(self))

    def on_python_version(self):
        messagebox.showinfo(self.parent.title(), self.engine.get_python_version(), parent=self)

    def on_tkinter_version(self):
        text = self.engine.i18n.get("tkinter_version").format(self.tk.call("info", "patchlevel"))
        messagebox.showinfo(self.parent.title(), text, parent=self)

    def on_log(self):
        # The log is born with the first error: until then there is nothing to open.
        if self.engine.log.is_empty():
            messagebox.showinfo(self.parent.title(), self.engine.i18n.get("log_empty"),
                                parent=self)
        else:
            self.engine.open_log()
