#!/usr/bin/python3
# -----------------------------------------------------------------------------
# project:  auditus
# authors:  1966bc aka Giuseppe Costanzi
# licence:  MIT
# -----------------------------------------------------------------------------
"""
Oscillum - un analizzatore di suoni: ascolti un file WAV e intanto lo vedi.

    python3 oscillum.py [file.wav]

Tre viste sincronizzate con l'ascolto:

    forma d'onda   tutto il file, canale sinistro e destro, con il cursore
    oscilloscopio  pochi millisecondi intorno al cursore: l'onda vera e propria
    spettro        la trasformata di Fourier al cursore: fondamentale e armoniche

Clic sulla forma d'onda per spostare il cursore; barra spaziatrice per suonare
e fermare. L'audio passa da aplay (PulseAudio), il disegno da un Canvas Tkinter.
"""

import os
import subprocess
import sys
import threading
import time
import tkinter as tk
import wave
from tkinter import filedialog, messagebox, ttk

import numpy as np

__version__ = "0.1"

BG = "#1e1e1e"
GRID = "#3a3a3a"
TEXT = "#b0b0b0"
LEFT = "#4fa3ff"
RIGHT = "#ff9f43"
CURSOR = "#ffffff"

SCOPE_SPANS = ("5 ms", "10 ms", "20 ms", "50 ms", "100 ms")
FFT_SIZE = 8192
DB_FLOOR = -100.0


def read_wav(path):
    """Campioni come float32 in [-1, 1], forma (n, canali), e la frequenza."""
    with wave.open(path) as w:
        nch, width, sr = w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(w.getnframes())
    if width == 1:
        x = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128) / 128
    elif width == 2:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 2 ** 15
    elif width == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        v = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        v = np.where(v & 0x800000, v - 0x1000000, v)
        x = v.astype(np.float32) / 2 ** 23
    elif width == 4:
        x = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2 ** 31
    else:
        raise ValueError(f"campioni da {8 * width} bit non gestiti")
    return x.reshape(-1, nch), sr


class Player:
    """aplay in un sottoprocesso; i campioni gli arrivano dallo stdin a partire da un punto."""

    def __init__(self):
        self.proc = None
        self.started = 0.0
        self.offset = 0

    def play(self, samples, sr, start):
        self.stop()
        pcm = (np.clip(samples[start:], -1, 1) * 32767).astype(np.int16)
        self.proc = subprocess.Popen(
            ["aplay", "-q", "-t", "raw", "-f", "S16_LE", "-r", str(sr), "-c", str(samples.shape[1])],
            stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.offset, self.started = start, time.monotonic()
        threading.Thread(target=self._feed, args=(self.proc, pcm.tobytes()), daemon=True).start()

    @staticmethod
    def _feed(proc, data):
        try:
            proc.stdin.write(data)
            proc.stdin.close()
        except (BrokenPipeError, ValueError):
            pass

    def position(self, sr):
        """Campione che sta suonando ora, stimato dall'orologio."""
        return self.offset + int((time.monotonic() - self.started) * sr)

    @property
    def playing(self):
        return self.proc is not None and self.proc.poll() is None

    def stop(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
        self.proc = None


class Main(tk.Tk):

    def __init__(self, path=None):
        super().__init__()
        self.title("Oscillum")
        self.geometry("1000x720")
        self.minsize(700, 520)
        self.configure(bg=BG)

        self.samples = None
        self.sr = 44100
        self.peak = 1.0
        self.cursor = 0
        self.play_from = 0
        self.player = Player()
        self.overview = None          # immagine della forma d'onda, ricalcolata al resize

        self.init_ui()
        self.bind("<space>", lambda e: self.on_play_stop())
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        if path:
            self.after(100, lambda: self.load(path))

    # ui -------------------------------------------------------------------

    def init_ui(self):
        bar = ttk.Frame(self, padding=4)
        bar.pack(fill=tk.X)
        ttk.Button(bar, text="Apri…", command=self.on_open).pack(side=tk.LEFT)
        self.btn_play = ttk.Button(bar, text="▶ Suona", command=self.on_play_stop)
        self.btn_play.pack(side=tk.LEFT, padx=4)
        ttk.Label(bar, text="Oscilloscopio:").pack(side=tk.LEFT, padx=(12, 2))
        self.span = tk.StringVar(value="20 ms")
        cb = ttk.Combobox(bar, textvariable=self.span, values=SCOPE_SPANS, width=7, state="readonly")
        cb.pack(side=tk.LEFT)
        cb.bind("<<ComboboxSelected>>", lambda e: self.draw_views())
        self.fit = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar, text="Adatta", variable=self.fit,
                        command=self.redraw_all).pack(side=tk.LEFT, padx=(12, 0))
        self.info = tk.StringVar(value="Apri un file WAV")
        ttk.Label(bar, textvariable=self.info).pack(side=tk.RIGHT)

        self.cv_wave = self.canvas(160, "Forma d'onda")
        self.cv_scope = self.canvas(200, "Oscilloscopio")
        self.cv_spec = self.canvas(240, "Spettro")
        self.cv_wave.bind("<Button-1>", self.on_seek)
        self.cv_wave.bind("<B1-Motion>", self.on_seek)
        self.bind("<Configure>", lambda e: self.after_idle(self.redraw_all))

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status, padding=4).pack(fill=tk.X)

    def canvas(self, height, title):
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=3)
        tk.Label(frame, text=title, bg=BG, fg=TEXT, anchor="w").pack(fill=tk.X)
        cv = tk.Canvas(frame, height=height, bg=BG, highlightthickness=0)
        cv.pack(fill=tk.BOTH, expand=True)
        return cv

    # file -----------------------------------------------------------------

    def on_open(self):
        path = filedialog.askopenfilename(filetypes=[("WAV", "*.wav"), ("Tutti", "*")])
        if path:
            self.load(path)

    def load(self, path):
        try:
            self.samples, self.sr = read_wav(path)
        except Exception as e:
            messagebox.showerror("Oscillum", f"Non riesco a leggere il file:\n{e}")
            return
        self.player.stop()
        self.cursor = 0
        n, nch = self.samples.shape
        peak = np.abs(self.samples).max()
        self.peak = peak if peak > 0 else 1.0
        peak_db = 20 * np.log10(peak) if peak > 0 else DB_FLOOR
        self.title(f"Oscillum · {os.path.basename(path)}")
        self.info.set(f"{self.sr} Hz · {'stereo' if nch == 2 else f'{nch} canali'} · "
                      f"{n / self.sr:.1f} s · picco {peak_db:.1f} dBFS")
        self.redraw_all()

    # disegno --------------------------------------------------------------

    def redraw_all(self):
        if self.samples is None:
            return
        self.draw_overview()
        self.draw_views()

    @property
    def gain(self):
        """Ingrandimento verticale di forma d'onda e oscilloscopio: 1 = fondo scala."""
        return 1 / self.peak if self.fit.get() else 1.0

    def gain_label(self):
        g = self.gain
        return "" if g <= 1.01 else f"vista ×{g:.1f} ({20 * np.log10(g):+.0f} dB)"

    def draw_overview(self):
        cv = self.cv_wave
        cv.delete("all")
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 10:
            return
        n, nch = self.samples.shape
        lanes = min(nch, 2)
        lane_h = h / lanes
        g = self.gain * 0.95
        edges = np.linspace(0, n, w + 1).astype(int)
        for c in range(lanes):
            x = self.samples[:, c]
            mid = lane_h * (c + 0.5)
            cv.create_line(0, mid, w, mid, fill=GRID)
            cv.create_text(4, lane_h * c + 2, text="S" if c == 0 else "D", anchor="nw", fill=TEXT)
            colour = LEFT if c == 0 else RIGHT
            for px in range(w):
                a, b = edges[px], max(edges[px + 1], edges[px] + 1)
                seg = x[a:b]
                lo, hi = seg.min() * g, seg.max() * g
                cv.create_line(px, mid - hi * lane_h / 2, px, mid - lo * lane_h / 2 + 1, fill=colour)
        if self.gain_label():
            cv.create_text(w - 4, 2, text=self.gain_label(), anchor="ne", fill=TEXT)
        self.draw_cursor()

    def window_start(self, size):
        """Inizio di una finestra di 'size' campioni intorno al cursore, dentro il file."""
        return int(min(max(self.cursor - size // 2, 0), max(len(self.samples) - size, 0)))

    def draw_cursor(self):
        cv = self.cv_wave
        cv.delete("cursor")
        w, h = cv.winfo_width(), cv.winfo_height()
        x = self.cursor / len(self.samples) * w
        cv.create_line(x, 0, x, h, fill=CURSOR, tags="cursor")

    def draw_views(self):
        if self.samples is None:
            return
        self.draw_scope()
        self.draw_spectrum()
        t = self.cursor / self.sr
        self.status.set(f"cursore {t:6.2f} s")

    def draw_scope(self):
        cv = self.cv_scope
        cv.delete("all")
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 10:
            return
        span = int(float(self.span.get().split()[0]) / 1000 * self.sr)
        a = self.window_start(span)
        seg = self.samples[a:a + span]
        g = self.gain * 0.95
        for frac in (0.25, 0.5, 0.75):
            cv.create_line(0, h * frac, w, h * frac, fill=GRID)
        full = f"{1 / g:.2f}" if g > 1.01 else "1"
        cv.create_text(4, 2, text=f"+{full}", anchor="nw", fill=TEXT)
        cv.create_text(4, h - 2, text=f"−{full}", anchor="sw", fill=TEXT)
        cv.create_text(w - 4, h - 2, text=self.span.get(), anchor="se", fill=TEXT)
        if len(seg) < 2:
            return
        xs = np.linspace(0, w, len(seg))
        for c in range(min(seg.shape[1], 2) - 1, -1, -1):   # destro sotto, sinistro sopra
            ys = h / 2 - seg[:, c] * g * (h / 2 - 4)
            pts = np.column_stack([xs, ys]).ravel().tolist()
            cv.create_line(*pts, fill=LEFT if c == 0 else RIGHT)

    def draw_spectrum(self):
        cv = self.cv_spec
        cv.delete("all")
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 10:
            return
        top, bottom, left = 8, h - 18, 34
        fmin, fmax = 20.0, min(20000.0, self.sr / 2)
        fx = lambda f: left + (np.log10(f) - np.log10(fmin)) / (np.log10(fmax) - np.log10(fmin)) * (w - left - 6)
        dy = lambda db: top + (0 - db) / (0 - DB_FLOOR) * (bottom - top)

        # griglia: ottave dei La e decadi in dB
        for f in (27.5, 55, 110, 220, 440, 880, 1760, 3520, 7040, 14080):
            if fmin <= f <= fmax:
                x = fx(f)
                cv.create_line(x, top, x, bottom, fill=GRID)
                cv.create_text(x, bottom + 2, text=f"{f:g}", anchor="n", fill=TEXT)
        for db in range(0, int(DB_FLOOR) - 1, -20):
            cv.create_line(left, dy(db), w - 6, dy(db), fill=GRID)
            cv.create_text(left - 4, dy(db), text=str(db), anchor="e", fill=TEXT)

        a = self.window_start(FFT_SIZE)
        seg = self.samples[a:a + FFT_SIZE].mean(axis=1)
        if len(seg) < FFT_SIZE:
            seg = np.pad(seg, (0, FFT_SIZE - len(seg)))
        win = np.hanning(FFT_SIZE)
        mag = np.abs(np.fft.rfft(seg * win)) / (win.sum() / 2)      # 0 dBFS = sinusoide a fondo scala
        db = np.maximum(20 * np.log10(np.maximum(mag, 1e-12)), DB_FLOOR)
        freqs = np.fft.rfftfreq(FFT_SIZE, 1 / self.sr)

        # un punto per pixel: il massimo dei bin che vi cadono
        keep = (freqs >= fmin) & (freqs <= fmax)
        px = fx(freqs[keep]).astype(int)
        vals = db[keep]
        best = {}
        for p, v in zip(px, vals):
            if v > best.get(p, DB_FLOOR - 1):
                best[p] = v
        pts = []
        for p in sorted(best):
            pts += [p, dy(best[p])]
        if len(pts) >= 4:
            cv.create_line(*pts, fill=LEFT)

        # il picco più alto, con la sua frequenza
        k = int(np.argmax(np.where(keep, db, DB_FLOOR - 1)))
        if db[k] > DB_FLOOR + 10:
            # interpolazione parabolica sul bin del massimo
            if 0 < k < len(db) - 1:
                y0, y1, y2 = db[k - 1], db[k], db[k + 1]
                d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2) if (y0 - 2 * y1 + y2) != 0 else 0
            else:
                d = 0
            f_peak = (k + d) * self.sr / FFT_SIZE
            cv.create_text(w - 8, top + 2, anchor="ne", fill=CURSOR,
                           text=f"picco {f_peak:.1f} Hz · {db[k]:.1f} dBFS")

    # ascolto --------------------------------------------------------------

    def on_play_stop(self):
        if self.samples is None:
            return
        if self.player.playing:
            self.player.stop()
            self.btn_play.configure(text="▶ Suona")
            return
        if self.cursor >= len(self.samples) - 1:
            self.cursor = 0
        self.play_from = self.cursor
        self.player.play(self.samples, self.sr, self.cursor)
        self.btn_play.configure(text="■ Stop")
        self.tick()

    def tick(self):
        if not self.player.playing:
            # finito da solo: il cursore torna dove era partito, come un registratore
            if self.player.proc is not None:
                self.player.proc = None
                self.cursor = self.play_from
                self.draw_cursor()
                self.draw_views()
            self.btn_play.configure(text="▶ Suona")
            return
        self.cursor = min(self.player.position(self.sr), len(self.samples) - 1)
        self.draw_cursor()
        self.draw_views()
        self.after(50, self.tick)

    def on_seek(self, event):
        if self.samples is None:
            return
        w = self.cv_wave.winfo_width()
        self.cursor = int(min(max(event.x / w, 0), 1) * (len(self.samples) - 1))
        was_playing = self.player.playing
        self.draw_cursor()
        self.draw_views()
        if was_playing:
            self.player.play(self.samples, self.sr, self.cursor)

    def on_close(self):
        self.player.stop()
        self.destroy()


def main():
    app = Main(sys.argv[1] if len(sys.argv) > 1 else None)
    app.mainloop()


if __name__ == "__main__":
    main()
