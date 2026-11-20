#!/usr/bin/env python3
"""Measure high-frequency noise in MP3 files, to decide whether (and how) to denoise them.

Decodes each file with ffmpeg through a pipe (no scratch files), takes a short-time spectrum and prints:

  * band levels (dBFS per FFT bin) over the whole file: median frame and quietest 2 % of frames. The quietest
    frames approximate the stationary noise floor. LP-rip hiss shows as a flat shelf from ~4 kHz up; a clean
    digital recording falls smoothly with frequency instead.
  * narrow tonal peaks above 4 kHz in the median spectrum (whines, pilot tones, carrier leakage), which are a
    different kind of "high frequency noise" that broadband denoising does not fix.

Usage: python3 scripts/denoise-audio/analyze_noise.py FILE.mp3 [FILE.mp3 ...]
"""
import subprocess
import sys

import numpy as np

N = 4096          # FFT size
HOP = 2048
BANDS = [(0, 2000), (2000, 4000), (4000, 8000), (8000, 12000), (12000, 16000), (16000, 20000), (20000, 22050)]


def decode(path, channels=1):
    """Return (float32 samples, sample rate): shape (n,) for mono, (n, channels) otherwise."""
    probe = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=sample_rate',
         '-of', 'csv=p=0', path], capture_output=True, text=True, check=True)
    sr = int(probe.stdout.strip())
    raw = subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', str(channels), '-f', 'f32le', '-'],
        capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    return (x if channels == 1 else x.reshape(-1, channels)), sr


def spectra(x):
    """Per-frame power spectra in dBFS per bin (a full-scale sine reads about 0 dB)."""
    win = np.hanning(N).astype(np.float32)
    nframes = 1 + (len(x) - N) // HOP
    out = np.empty((nframes, N // 2 + 1), dtype=np.float32)
    scale = 2.0 / win.sum()
    for i in range(nframes):
        seg = x[i * HOP:i * HOP + N] * win
        out[i] = np.abs(np.fft.rfft(seg)) * scale
    return 20 * np.log10(out + 1e-10)


def band_mean_db(spec, lo, hi, sr):
    """Mean power of each frame inside the band, in dB (per bin)."""
    k0, k1 = int(lo * N / sr), int(hi * N / sr) + 1
    k1 = min(k1, spec.shape[1])
    if k1 <= k0:
        return None
    p = (10 ** (spec[:, k0:k1] / 10)).mean(axis=1)
    return 10 * np.log10(p + 1e-20)


def tonal_peaks(spec, sr):
    med = np.median(spec, axis=0)
    # compare each bin with the median of its neighbourhood (+-12 bins), above 4 kHz only
    pad = 12
    padded = np.pad(med, pad, mode='edge')
    local = np.array([np.median(padded[i:i + 2 * pad + 1]) for i in range(len(med))])
    freqs = np.arange(len(med)) * sr / N
    hits = [(f, m, m - l) for f, m, l in zip(freqs, med, local) if f > 4000 and m - l > 8]
    return hits


def report(path):
    x, sr = decode(path)
    spec = spectra(x)
    print(f'== {path}  ({len(x) / sr:.1f} s, {sr} Hz, {spec.shape[0]} frames)')
    print(f'   {"band":>14} {"median":>8} {"quiet2%":>8}   (dBFS per bin)')
    for lo, hi in BANDS:
        if lo >= sr / 2:
            continue
        b = band_mean_db(spec, lo, min(hi, sr / 2), sr)
        if b is None:
            continue
        print(f'   {lo / 1000:5.1f}-{min(hi, sr / 2) / 1000:4.1f} kHz {np.median(b):8.1f} {np.percentile(b, 2):8.1f}')
    peaks = tonal_peaks(spec, sr)
    if peaks:
        print('   tonal peaks above 4 kHz (median spectrum, dB above neighbourhood):')
        for f, m, d in peaks[:12]:
            print(f'     {f:8.0f} Hz  {m:6.1f} dB  +{d:4.1f}')
    else:
        print('   no narrow tonal peaks above 4 kHz')
    print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        report(p)
