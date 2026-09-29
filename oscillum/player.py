# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Playback through aplay, the ALSA player every Linux desktop has.

aplay runs as a separate process and reads raw 16 bit samples from its
standard input, so playback can start from any point of the file: what is
written to the pipe is what is heard. A thread writes, because a write to a
pipe blocks until aplay has taken the data, and the window must not wait.

Where the sound is now is not asked of aplay, which cannot tell: it is
reckoned from the clock, started when the first sample was sent.
"""

import subprocess
import threading
import time

import numpy as np


class Player:
    """One aplay at a time, fed from a given frame."""

    def __init__(self, log):
        self.log = log
        self.process = None
        #: When playback started, from time.monotonic(), and from which frame.
        self.started = 0.0
        self.first = 0

    def __str__(self):
        return "class: {0}".format(self.__class__.__name__)

    def play(self, wav, first):
        """Play wav from frame first, stopping whatever was playing."""
        self.stop()
        samples = np.clip(wav.samples[first:], -1, 1)
        data = (samples * 32767).astype(np.int16).tobytes()
        command = ["aplay", "-q", "-t", "raw", "-f", "S16_LE",
                   "-r", str(wav.rate), "-c", str(wav.get_channels())]
        self.log.trace("{0} from frame {1}".format(" ".join(command), first))

        self.process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL)
        self.first = first
        self.started = time.monotonic()
        feeder = threading.Thread(target=self.feed, args=(self.process, data), daemon=True)
        feeder.start()

    def feed(self, process, data):
        """Write the samples to aplay; runs in its own thread.

        A pipe closed by stop() while writing is not an error: the listener
        asked for silence.
        """
        try:
            process.stdin.write(data)
            process.stdin.close()
        except (BrokenPipeError, ValueError):
            pass

    def is_playing(self):
        return self.process is not None and self.process.poll() is None

    def get_frame(self, rate):
        """The frame being heard now, reckoned from the clock."""
        return self.first + int((time.monotonic() - self.started) * rate)

    def stop(self):

        if self.is_playing():
            self.process.terminate()
        self.process = None
