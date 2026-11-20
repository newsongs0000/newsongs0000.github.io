#!/usr/bin/env python3
"""Compare an original MP3 with its denoised version and report whether the change is safe.

Checks, per pair:
  * length: decoded sample counts must be identical (lyric timings stay valid);
  * alignment: lag from the cross-correlation of an 8 s excerpt from the middle must be 0 samples;
  * peaks and clipped samples;
  * level change per frequency band (median frame and quietest 2 % of frames): bands without a tone should
    change by about 0 dB, bands holding a tone drop only slightly;
  * each tone: in a 10 s window it is "present" when its level (strongest bin within +-70 Hz of the centre, 25th
    percentile over the window) is more than 10 dB above the untouched spectrum 300-600 Hz away, and above
    -95 dBFS per bin (a sine that quiet is inaudible; near 15 kHz the reference itself lies at -110 dBFS, so the
    relative test alone would call the residual floor a tone). Every window where it was present before must
    have it absent after; the drop in level is reported;
  * ID3 tags (except `encoder`) are unchanged.

Usage: python3 scripts/denoise-audio/verify_denoise.py [--tone HZ ...] ORIGINAL.mp3 NEW.mp3
       python3 scripts/denoise-audio/verify_denoise.py [--tone HZ ...] ORIGINAL_DIR NEW_DIR      (all *.mp3 in both)
Default tones: 6440 and 15613 Hz.
"""
import argparse
import glob
import json
import os
import subprocess
import sys

import numpy as np

from analyze_noise import decode
from find_tones import HOP, N

# The bands next to the default tones are narrow, so that the change in the tone band can be told from the change
# in the music next to it.
BANDS = [(0, 2000), (2000, 4000), (4000, 6000), (6000, 6250), (6250, 6630), (6630, 7000), (7000, 12000),
         (12000, 15000), (15000, 15400), (15400, 15830), (15830, 16500), (16500, 22050)]
WINDOW_S = 10
HALF = 70           # a tone is measured as the strongest bin within +-HALF Hz of its centre
AUDIBLE = -95       # dBFS per bin; a tone quieter than this does not count as present
REF = (300, 600)    # its reference level: median of the bins REF Hz away on both sides (only the lower side for
                    # tones above 14 kHz, because the upper side runs into the codec's lowpass at about 16 kHz)


def measure(path, tones):
    x, sr = decode(path, channels=2)
    m = {'samples': x.shape[0], 'sr': sr, 'peak': float(np.abs(x).max()), 'clipped': int((np.abs(x) >= 0.9999).sum())}
    mono = x.mean(axis=1)
    mid = len(mono) // 2
    m['excerpt'] = mono[mid:mid + 8 * sr].copy()
    del x
    win = np.hanning(N).astype(np.float32)
    scale = 2.0 / win.sum()
    freqs = np.arange(N // 2 + 1) * sr / N
    nframes = 1 + (len(mono) - N) // HOP
    per_window = int(WINDOW_S * sr / HOP)
    band_idx = [(np.searchsorted(freqs, lo), np.searchsorted(freqs, min(hi, sr / 2))) for lo, hi in BANDS]
    band_db = np.full((nframes, len(BANDS)), np.nan)
    excess = {t: [] for t in tones}
    block = []
    for i in range(nframes):
        spec = np.abs(np.fft.rfft(mono[i * HOP:i * HOP + N] * win)) * scale
        for b, (k0, k1) in enumerate(band_idx):
            if k1 > k0:
                band_db[i, b] = 10 * np.log10((spec[k0:k1] ** 2).mean() + 1e-20)
        block.append(20 * np.log10(spec + 1e-10))
        if len(block) == per_window:
            p25 = np.percentile(np.array(block, dtype=np.float32), 25, axis=0)
            for t in tones:
                k0, k1 = np.searchsorted(freqs, [t - HALF, t + HALF])
                r0, r1 = np.searchsorted(freqs, [t - REF[1], t - REF[0]])
                r2, r3 = np.searchsorted(freqs, [t + REF[0], t + REF[1]])
                ref = np.median(p25[r0:r1] if t > 14000 else np.concatenate([p25[r0:r1], p25[r2:r3]]))
                excess[t].append((float(p25[k0:k1].max()), float(p25[k0:k1].max() - ref)))
            block = []
    m['band_median'] = np.nanmedian(band_db, axis=0)
    m['band_quiet'] = np.nanpercentile(band_db, 2, axis=0)
    m['excess'] = {t: np.array(v) for t, v in excess.items()}
    return m


def tags(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format_tags', '-of', 'json', path],
                         capture_output=True, text=True, check=True).stdout
    t = json.loads(out).get('format', {}).get('tags', {})
    return {k.lower(): v for k, v in t.items() if k.lower() != 'encoder'}


def lag_samples(a, b):
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    size = 1 << (2 * n - 1).bit_length()
    c = np.fft.irfft(np.fft.rfft(a, size) * np.conj(np.fft.rfft(b, size)), size)
    k = int(np.argmax(c))
    return k if k < size // 2 else k - size


def compare(orig, new, tones):
    print(f'== {os.path.basename(orig)}')
    o, n = measure(orig, tones), measure(new, tones)
    ok = True

    same_len = o['samples'] == n['samples']
    lag = lag_samples(o['excerpt'], n['excerpt'])
    print(f'   samples: {o["samples"]} -> {n["samples"]}  {"OK" if same_len else "DIFFERENT"};  '
          f'lag {lag} samples  {"OK" if lag == 0 else "MISALIGNED"}')
    ok &= same_len and lag == 0
    print(f'   peak {o["peak"]:.3f} -> {n["peak"]:.3f}; clipped samples {o["clipped"]} -> {n["clipped"]}')
    ok &= n['clipped'] <= o['clipped']
    t_o, t_n = tags(orig), tags(new)
    print(f'   tags: {"unchanged" if t_o == t_n else "CHANGED " + str(sorted(set(t_o.items()) ^ set(t_n.items())))}')
    ok &= t_o == t_n

    print('   band level change, dB (median frame / quietest 2 %):')
    for b, (lo, hi) in enumerate(BANDS):
        if np.isnan(o['band_median'][b]):
            continue
        has_tone = any(lo <= t <= hi for t in tones)
        print(f'     {lo / 1000:5.1f}-{min(hi, o["sr"] / 2) / 1000:5.2f} kHz  '
              f'{n["band_median"][b] - o["band_median"][b]:+6.2f} / {n["band_quiet"][b] - o["band_quiet"][b]:+6.2f}'
              f'{"   (holds a tone)" if has_tone else ""}')
    for t in tones:
        lo_, eo = np.array(o['excess'][t]).T          # level, excess over reference
        ln_, en = np.array(n['excess'][t]).T
        present = (eo > 10) & (lo_ > AUDIBLE)
        if present.sum() == 0:
            print(f'   tone {t:g} Hz: not present in this file (no window more than 10 dB above the reference)')
            continue
        drop = lo_[present] - ln_[present]
        still = int(((en[present] > 10) & (ln_[present] > AUDIBLE)).sum())
        print(f'   tone {t:g} Hz: present in {present.sum()}/{len(eo)} windows; level {np.median(lo_[present]):.0f} -> '
              f'{np.median(ln_[present]):.0f} dBFS per bin, drop median {np.median(drop):.0f} dB, '
              f'smallest {drop.min():.0f} dB; still present after in {still} windows')
        ok &= still == 0
    print(f'   => {"PASS" if ok else "CHECK"}\n')
    return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('original')
    ap.add_argument('new')
    ap.add_argument('--tone', type=float, action='append', help='tone centre in Hz, may be repeated')
    a = ap.parse_args()
    tones = a.tone or [6440, 15613]
    if os.path.isdir(a.original):
        pairs = [(f, os.path.join(a.new, os.path.basename(f))) for f in sorted(glob.glob(os.path.join(a.original, '*.mp3')))]
    else:
        pairs = [(a.original, a.new)]
    results = [compare(o, n, tones) for o, n in pairs]
    sys.exit(0 if all(results) else 1)
