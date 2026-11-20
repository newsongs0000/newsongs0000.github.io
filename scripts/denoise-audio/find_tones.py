#!/usr/bin/env python3
"""Find steady narrow-band tones ("whines") in MP3 files and report where each one is present.

A steady tone is a line on a spectrogram: the same frequency in nearly every frame. Music rarely holds one
frequency that long at a level above its surroundings, so the test is: in every WINDOW seconds, a bin counts as a
tone if its 25th-percentile level over the window's frames stands at least MIN_DB above the median level of its
neighbouring bins. Tones found in consecutive windows at nearly the same frequency are merged into one track.

Usage: python3 scripts/denoise-audio/find_tones.py [--min-hz 1000] [--min-db 12] [--min-level -95] [--min-track 30] [--window 10] FILE.mp3 [...]

Prints one line per track: start-end (s), median frequency, frequency spread, and level (dBFS) above neighbours.
"""
import argparse

import numpy as np

from analyze_noise import decode

N = 32768          # FFT size (1.35 Hz resolution at 44.1 kHz)
HOP = 16384
PAD = 100          # neighbourhood: +-PAD bins (+-135 Hz), with the centre +-GUARD bins excluded
GUARD = 12


def window_floor_excess(frames_db):
    """Per-bin excess (dB) of the 25th-percentile spectrum over the median of its neighbours."""
    p25 = np.percentile(frames_db, 25, axis=0)
    padded = np.pad(p25, PAD, mode='edge')
    view = np.lib.stride_tricks.sliding_window_view(padded, 2 * PAD + 1)       # (bins, 2*PAD+1)
    mask = np.ones(2 * PAD + 1, dtype=bool)
    mask[PAD - GUARD:PAD + GUARD + 1] = False
    local = np.median(view[:, mask], axis=1)
    return p25, p25 - local


def find(path, min_hz, min_db, min_level, window_s, min_track):
    x, sr = decode(path)
    win = np.hanning(N).astype(np.float32)
    scale = 2.0 / win.sum()
    freqs = np.arange(N // 2 + 1) * sr / N
    per_window = int(window_s * sr / HOP)
    nframes = 1 + (len(x) - N) // HOP
    hits = []                                                                  # (window start s, freq, level, excess)
    for w0 in range(0, nframes - per_window + 1, per_window):
        db = np.empty((per_window, N // 2 + 1), dtype=np.float32)
        for k in range(per_window):
            i = w0 + k
            db[k] = 20 * np.log10(np.abs(np.fft.rfft(x[i * HOP:i * HOP + N] * win)) * scale + 1e-10)
        p25, excess = window_floor_excess(db)
        idx = np.where((freqs > min_hz) & (excess > min_db) & (p25 > min_level))[0]
        groups = []
        for i in idx:
            if groups and i - groups[-1][-1] <= 4:
                groups[-1].append(i)
            else:
                groups.append([i])
        for g in groups:
            j = g[int(np.argmax(excess[g]))]
            hits.append((w0 * HOP / sr, freqs[j], p25[j], excess[j]))
    # merge windows into tracks
    tracks = []
    for t, f, lvl, ex in hits:
        for tr in tracks:
            if abs(tr['f'][-1] - f) < 40 and t - tr['t'][-1] <= 2 * window_s:
                tr['t'].append(t); tr['f'].append(f); tr['lvl'].append(lvl); tr['ex'].append(ex)
                break
        else:
            tracks.append({'t': [t], 'f': [f], 'lvl': [lvl], 'ex': [ex]})
    print(f'== {path}  ({len(x) / sr:.0f} s)')
    if not tracks:
        print('   no steady tones')
    for tr in tracks:
        if tr['t'][-1] + window_s - tr['t'][0] < min_track:
            continue
        print(f'   {tr["t"][0]:7.0f}-{tr["t"][-1] + window_s:7.0f} s  {np.median(tr["f"]):8.1f} Hz '
              f'(±{np.ptp(tr["f"]) / 2:4.1f})  level {np.median(tr["lvl"]):6.1f} dBFS  +{np.median(tr["ex"]):4.1f} dB over neighbours')
    print()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--min-hz', type=float, default=1000)
    ap.add_argument('--min-db', type=float, default=12, help='dB above neighbouring bins')
    ap.add_argument('--min-level', type=float, default=-95, help='ignore tones quieter than this (dBFS per bin)')
    ap.add_argument('--min-track', type=float, default=30, help='ignore tones present for less than this many seconds')
    ap.add_argument('--window', type=float, default=10, help='window length in seconds')
    a = ap.parse_args()
    for p in a.files:
        find(p, a.min_hz, a.min_db, a.min_level, a.window, a.min_track)
