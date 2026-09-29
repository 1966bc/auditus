#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Shared functions to analyse a guitar recording: onsets, tempo, beat grid,
chromagram. Used by accents.py and chords.py.
"""

import wave

import numpy as np

NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def read_channel(path, channel=None):
    """One channel as float in [-1, 1]; by default the one with the highest peak."""
    with wave.open(path) as w:
        width, nch, sr = w.getsampwidth(), w.getnchannels(), w.getframerate()
        raw = w.readframes(w.getnframes())
    dtype = {2: np.int16, 4: np.int32}[width]
    x = np.frombuffer(raw, dtype=dtype).reshape(-1, nch) / float(2 ** (8 * width - 1))
    if channel is None:
        channel = int(np.argmax(np.abs(x).max(axis=0)))
    return x[:, channel], sr


class Analysis:
    """Short-time spectrum and everything derived from it."""

    def __init__(self, x, sr, n=4096, hop=512):
        self.sr, self.n, self.hop = sr, n, hop
        frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
        self.spec = np.abs(np.fft.rfft(frames, axis=1))
        self.fps = sr / hop
        # onset strength: positive spectral flux minus its moving average
        mag = np.log1p(100 * self.spec)
        flux = np.concatenate([[0], np.maximum(np.diff(mag, axis=0), 0).sum(axis=1)])
        k = int(self.fps * 0.3)
        self.flux = np.maximum(flux - np.convolve(flux, np.ones(k) / k, mode="same"), 0)
        self._chroma = None

    def onsets(self, rel=0.2, min_gap=0.09):
        """Onsets: times in seconds and their strength."""
        f = self.flux
        thr, gap = rel * np.percentile(f, 99), int(min_gap * self.fps)
        idx = [i for i in range(1, len(f) - 1)
               if f[i] > thr and f[i] == f[max(0, i - gap):i + gap].max()]
        return np.array(idx) / self.fps, f[idx]

    def global_beat(self, bpm_min=55, bpm_max=100):
        """Beat duration from the autocorrelation of the spectral flux."""
        f = self.flux
        ac = np.correlate(f, f, mode="full")[len(f) - 1:]
        lo, hi = int(self.fps * 60 / bpm_max), int(self.fps * 60 / bpm_min)
        return (lo + np.argmax(ac[lo:hi])) / self.fps

    def beat_grid(self, start, beat, t, s, follow=0.1):
        """Adaptive grid: each beat locks onto the strongest nearby onset."""
        bt, beats = start, []
        while bt < t[-1] + 0.5 * beat:
            near = np.abs(t - bt) < 0.2 * beat
            if near.any():
                nb = t[np.argmax(np.where(near, s, -1))]
                if beats:
                    beat = (1 - follow) * beat + follow * (nb - beats[-1])
                bt = nb
            beats.append(bt)
            bt += beat
        return np.array(beats)

    @property
    def chroma(self):
        """Energy per pitch class, 0 = C; band 70-1200 Hz."""
        if self._chroma is None:
            freqs = np.fft.rfftfreq(self.n, 1 / self.sr)
            band = (freqs > 70) & (freqs < 1200)
            pc = ((np.round(12 * np.log2(freqs[band] / 440)) + 9) % 12).astype(int)
            lin = self.spec[:, band]
            self._chroma = np.stack([lin[:, pc == c].sum(axis=1) for c in range(12)], axis=1)
        return self._chroma

    def segment(self, a, b):
        """Mean, normalised chroma between times a and b."""
        i, j = int(a * self.fps), max(int(b * self.fps), int(a * self.fps) + 1)
        v = self.chroma[i:j].mean(axis=0)
        return v / (np.linalg.norm(v) + 1e-12)

    def downbeat_phase(self, beats, per_bar=4):
        """The beat where harmony changes most: that is where the bar starts."""
        change = np.zeros(per_bar)
        for i in range(1, len(beats) - 1):
            change[i % per_bar] += 1 - self.segment(beats[i - 1], beats[i]) @ \
                                       self.segment(beats[i], beats[i + 1])
        return int(np.argmax(change))


def chord_template(root, intervals):
    v = np.zeros(12)
    v[[(root + i) % 12 for i in intervals]] = 1
    return v / np.linalg.norm(v)


QUALITIES = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10)}


def parse_chord(name):
    """'F#m' -> (6, (0, 3, 7))."""
    root = name[:2] if len(name) > 1 and name[1] in "#b" else name[:1]
    quality = name[len(root):]
    pc = NAMES.index(root) if "#" in root or len(root) == 1 else (NAMES.index(root[0]) - 1) % 12
    return pc, QUALITIES[quality]
