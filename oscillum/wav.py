# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""A WAV file in memory: its samples, its rate, its peak.

The standard library reads the file (wave), numpy turns the bytes into
numbers. Every sample becomes a float between -1 and 1, whatever its width
on disk, so the views never ask how the file was written.
"""

import os
import wave

import numpy as np


class Wav:
    """The samples of one file, shape (frames, channels), as float32."""

    #: The largest value of a sample, by width in bytes: what 1.0 stands for.
    FULL_SCALE = {1: 128.0, 2: 2.0 ** 15, 3: 2.0 ** 23, 4: 2.0 ** 31}

    def __init__(self):
        self.path = None
        self.samples = None
        self.rate = 0
        self.peak = 0.0

    def __str__(self):
        return "class: {0}\npath: {1}".format(self.__class__.__name__, self.path)

    def read(self, path):
        """Load a file: 8, 16, 24 or 32 bit integer PCM, any number of channels."""
        with wave.open(path) as f:
            channels = f.getnchannels()
            width = f.getsampwidth()
            rate = f.getframerate()
            raw = f.readframes(f.getnframes())

        if width not in self.FULL_SCALE:
            raise ValueError("{0}-bit samples are not supported".format(8 * width))

        self.samples = self.get_floats(raw, width).reshape(-1, channels)
        self.rate = rate
        self.path = path
        self.peak = float(np.abs(self.samples).max())

    def get_floats(self, raw, width):
        """The bytes of a file as floats between -1 and 1."""
        if width == 1:
            # 8 bit WAV is unsigned: silence is 128, not 0.
            values = np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128
        elif width == 2:
            values = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
        elif width == 3:
            # numpy has no 24 bit type: three bytes put together by hand,
            # then the sign taken from the highest bit.
            triple = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
            values = triple[:, 0] | (triple[:, 1] << 8) | (triple[:, 2] << 16)
            values = np.where(values & 0x800000, values - 0x1000000, values).astype(np.float32)
        else:
            values = np.frombuffer(raw, dtype=np.int32).astype(np.float32)

        return values / self.FULL_SCALE[width]

    def get_name(self):
        return os.path.basename(self.path)

    def get_frames(self):
        return self.samples.shape[0]

    def get_channels(self):
        return self.samples.shape[1]

    def get_duration(self):
        """Seconds of sound."""
        return self.get_frames() / self.rate

    def get_peak_db(self):
        """The highest sample in dBFS: 0 is full scale, silence is -inf."""
        level = float("-inf")
        if self.peak > 0:
            level = 20 * np.log10(self.peak)
        return level

    def get_block(self, start, size):
        """size frames from start, kept inside the file: where the views read."""
        begin = int(min(max(start, 0), max(self.get_frames() - size, 0)))
        return self.samples[begin:begin + size]
