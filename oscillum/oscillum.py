#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Start Oscillum, the sound viewer of the auditus course.

    python3 oscillum.py                   start it
    python3 oscillum.py file.wav          start it with a file open
    python3 oscillum.py --trace file.wav  and print on the terminal what it does

A WAV file is played through aplay while three views follow it: the whole
waveform, an oscilloscope of a few milliseconds and the spectrum.
"""

import os
import sys
from tkinter import messagebox

from log import Log
from ui.app import App

#: The folder of this file: the log lives here, beside the program.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

#: The options the program knows. Anything else starting with -- is refused.
OPTIONS = ("--trace",)


def main():

    # The options, read by hand: sys.argv[0] is the program, the rest is ours.
    arguments = sys.argv[1:]
    options = [argument for argument in arguments if argument.startswith("--")]
    files = [argument for argument in arguments if not argument.startswith("--")]
    unknown = [option for option in options if option not in OPTIONS]
    if unknown:
        raise SystemExit("unknown option: {0}\n"
                         "usage: python3 oscillum.py [--trace] [file.wav]".format(" ".join(unknown)))

    # The log comes first, so that even a failure to start is written down.
    log = Log(os.path.join(PROJECT_DIR, "oscillum.log"), "--trace" in options)
    log.trace("options = {0}, files = {1}".format(options, files))

    # Before the main loop there is no report_callback_exception yet:
    # a failure here is written to the log, shown, and raised again.
    try:
        app = App("Oscillum", log, files)
    except Exception as exc:
        log.exception("start failed: {0}".format(exc))
        messagebox.showerror("Oscillum", "{0}\n\nDetails in {1}".format(exc, log.path))
        raise

    app.mainloop()


if __name__ == "__main__":
    main()
