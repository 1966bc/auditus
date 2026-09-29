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
        #: The status bar shows the file; the toolbar shows the time.
        self.file_text = tk.StringVar()
        self.time_text = tk.StringVar(value=self.get_time(0, 0))
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

        m_file.add_command(label=say("open_menu"), underline=0, accelerator="Ctrl+O",
                           command=self.on_open_file)
        m_file.add_command(label=say("log"), underline=0, command=self.on_log)
        m_file.add_separator()
        m_file.add_command(label=say("exit"), underline=0, command=self.parent.on_exit)

        for label, command in ((say("about"), self.on_about),
                               (say("licence"), self.on_licence),
                               (say("python"), self.on_python_version),
                               (say("tkinter"), self.on_tkinter_version)):
            m_about.add_command(label=label, underline=0, command=command)

        self.parent.config(menu=m_main)

    def init_toolbar(self):
        """Open and the transport, as image buttons; the oscilloscope span; the time.

        No control of the toolbar takes the keyboard focus. A focused button
        is pressed by the space bar, and the space bar is also the key that
        plays and pauses: the two together would play and stop at once.
        """
        say = self.engine.i18n.get
        background = self.engine.tools.get_rgb(*self.engine.tools.BACKGROUND)
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED, bg=background)

        # Kept on self: a PhotoImage that only a local variable points to is
        # collected, and the button goes blank.
        self.img_open = tk.PhotoImage(data=self.engine.get_icon("open"))
        self.img_rewind = tk.PhotoImage(data=self.engine.get_icon("rewind"))
        self.img_play = tk.PhotoImage(data=self.engine.get_icon("play"))
        self.img_pause = tk.PhotoImage(data=self.engine.get_icon("pause"))
        self.img_stop = tk.PhotoImage(data=self.engine.get_icon("stop"))

        buttons = []
        for image, command in ((self.img_open, self.on_open_file),
                               (self.img_rewind, self.on_rewind),
                               (self.img_play, self.on_play),
                               (self.img_stop, self.on_stop)):
            button = tk.Button(toolbar, image=image, relief=tk.FLAT, bg=background,
                               activebackground=background, takefocus=0, command=command)
            button.pack(side=tk.LEFT, padx=2, pady=2)
            buttons.append(button)
        #: The play button shows pause while the sound plays.
        self.btn_play = buttons[2]

        ttk.Label(toolbar, style="App.TLabel", text=say("oscilloscope")).pack(side=tk.LEFT,
                                                                          padx=(16, 2))
        self.cb_span = self.engine.tools.get_combo(toolbar)
        self.cb_span.configure(width=8, takefocus=0)
        self.cb_span["values"] = ["{0} ms".format(span) for span in SPANS]
        self.cb_span.current(SPANS.index(20))
        self.cb_span.bind("<<ComboboxSelected>>", self.on_span)
        self.cb_span.pack(side=tk.LEFT)

        self.chk_fit = ttk.Checkbutton(toolbar, style="App.TCheckbutton", text=say("fit"),
                                       variable=self.fit, takefocus=0, command=self.on_fit)
        self.chk_fit.pack(side=tk.LEFT, padx=(12, 0))

        ttk.Label(toolbar, style="Time.TLabel", textvariable=self.time_text).pack(side=tk.RIGHT,
                                                                                  padx=8)

        toolbar.pack(side=tk.TOP, fill=tk.X)

        # The keys every player uses, everywhere in the window.
        self.parent.bind_all("<space>", self.on_play)
        self.parent.bind_all("<Home>", self.on_rewind)
        self.parent.bind_all("<Escape>", self.on_stop)
        self.parent.bind_all("<Control-o>", self.on_open_file)

    def init_status_bar(self):
        """The file being looked at: its name, rate, channels, length and peak."""
        frm_status = ttk.Frame(self, style="StatusBar.TFrame", borderwidth=1, relief=tk.SUNKEN)
        ttk.Label(frm_status,
                  textvariable=self.file_text,
                  style="StatusBar.TLabel",
                  anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=1)
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

        self.file_text.set(self.engine.i18n.get("ready"))

    def on_open_file(self, evt=None):

        say = self.engine.i18n.get
        wildcard = [(say("wav_files"), "*.wav"), (say("all_files"), "*.*")]
        path = filedialog.askopenfilename(parent=self, title=say("open_title"),
                                          initialdir=os.getcwd(), filetypes=wildcard)
        if path:
            self.load_file(path)

    def load_file(self, path):
        """Read a file and show it from its first frame."""
        self.pause()
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
        self.time_text.set(self.get_time(frame / self.engine.wav.rate,
                                         self.engine.wav.get_duration()))

    def get_time(self, seconds, total):
        """'01:02.345 / 03:00.000': where the cursor is, and how long the file lasts."""
        texts = []
        for value in (seconds, total):
            minutes, rest = divmod(value, 60)
            texts.append("{0:02d}:{1:06.3f}".format(int(minutes), rest))
        return " / ".join(texts)

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
        """Play from the cursor, or pause: the same button and the same key do both."""
        if self.engine.wav.samples is not None:
            if self.playing:
                self.pause()
            else:
                self.start()

    def on_stop(self, evt=None):
        """Stop, and put the cursor back where playback started."""
        if self.engine.wav.samples is not None:
            self.pause()
            self.set_cursor(self.play_from)

    def on_rewind(self, evt=None):
        """Back to the first frame; while playing, the sound goes back with it."""
        if self.engine.wav.samples is not None:
            self.set_cursor(0)
            self.play_from = 0
            if self.playing:
                self.engine.player.play(self.engine.wav, 0)

    def start(self):

        if self.cursor >= self.engine.wav.get_frames() - 1:
            self.set_cursor(0)
        self.play_from = self.cursor
        self.engine.player.play(self.engine.wav, self.cursor)
        self.playing = True
        self.btn_play.configure(image=self.img_pause)
        self.after(TICK, self.follow)

    def pause(self):
        """Silence, with the cursor left where the sound was."""
        self.engine.player.stop()
        self.playing = False
        self.btn_play.configure(image=self.img_play)

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
                self.pause()
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
