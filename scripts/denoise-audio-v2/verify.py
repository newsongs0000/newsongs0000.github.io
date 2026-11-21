#!/usr/bin/env python3
"""Compare original MP3 files with their cleaned versions and report whether the result is right.

Checks, per pair:
  * length: the decoded sample counts are identical (lyric timings stay valid);
  * alignment: the cross-correlation lag of 4 s excerpts at 25 %, 50 % and 75 % of the file is 0;
  * peak (decoded, float) and the number of samples at or above full scale;
  * tags: the same as the original (except `encoder`);
  * whine: where whine.py finds the whine in the original, the carrier and the mains sidebands (+-1 ... +-6 x
    49.9 Hz) of each family are measured in both files: demodulated with the phase tracked in the original (as
    whine.py tracks it), long-term spectrum, dB above the median of the surrounding +-25 Hz (+-4 Hz left out,
    and so are the narrow slices the subtraction took out of the result). The strongest in the result must be
    below MAX_WHINE_DB;
  * level change per band (dB) in the original's quietest 5 % of frames (pauses and soft passages: hiss), in
    frames between the 40th and 60th percentile, and in its loudest 10 %. Hiss reduction shows in the quiet
    column. In loud frames the bands lose the hiss under the music too, so the music itself is checked on its
    strong components: bins of the loudest frames at least 20 dB above the band's level in the quiet frames.
    These must change by at most MAX_MUSIC_CHANGE_DB in every band up to MUSIC_MAX_HZ except the two bands
    holding the whine families (*).

Usage: python3 scripts/denoise-audio-v2/verify.py ORIGINAL.mp3 CLEANED.mp3
       python3 scripts/denoise-audio-v2/verify.py ORIGINAL_DIR CLEANED_DIR       (every *.mp3 in both)
Exits with 1 when a check fails.
"""
import argparse
import glob
import os
import sys

import numpy as np

import whine as W
from common import Band, decode, tags

# The whine families get bands of their own (WHINE_BANDS), so that their removal is not mistaken for a change in
# the music next to them.
BANDS = [(0, 250), (250, 1000), (1000, 2000), (2000, 4000), (4000, 6050), (6050, 6850), (6850, 8000),
         (8000, 12000), (12000, 15200), (15200, 16000), (16000, 20000)]
WHINE_BANDS = {(6050, 6850), (15200, 16000)}     # the whine families with their sidebands (+-350 Hz)
MUSIC_MAX_HZ = 15200    # above, near the codec's cut-off, re-encoding alone moves levels by about 1 dB
N = 4096
MAX_WHINE_DB = 3.0
MAX_MUSIC_CHANGE_DB = 0.5
OFFSETS = [0, -1, 1, -2, 2, -3, 3, -4, 4, -5, 5, -6, 6]     # multiples of the mains sideband spacing
SPACING = 49.9


def spectra(x):
    """Per frame (N, hop N) power spectra of the mono mix, float32 (frames, bins)."""
    mono = x.mean(axis=1)
    n = len(mono) // N
    seg = mono[:n * N].reshape(n, N) * np.hanning(N).astype(np.float32)
    return (np.abs(np.fft.rfft(seg, axis=1)) ** 2).astype(np.float32)


def whine_levels(x, y, sr):
    """{(ch, f0): (original dB list, result dB list)} for OFFSETS where the whine is present in x; and seconds."""
    an = W.analyse(x, sr)
    if not an['runs']:
        return {}, 0.0
    n, m, t = an['n'], an['m'], an['t']
    res = {}
    for ch in range(2):
        yc = np.zeros(m)
        yc[:n] = y[:, ch]
        Y = np.fft.rfft(yc)
        del yc
        for f0 in W.DEFAULT_WHINES:
            b = an['bands'][ch, f0]
            by = Band(Y, m, sr, f0, W.HALF, W.DEC)
            acc = {'orig': [], 'new': []}
            for run, f, _, _ in an['tracks'][ch, f0]:
                phi = W.refine_phase(b.z, b.rate, t, f)
                gate = (np.interp(np.arange(len(b.z)) / b.rate, t, run.astype(float)) > 0.99).astype(float)
                for label, z in (('orig', b.z), ('new', by.z)):
                    fr, db, _ = W.demod_spectrum(z * np.exp(-1j * phi), b.rate, gate)
                    if fr is not None:
                        acc[label].append((fr, db, gate.sum()))
            if not acc['orig']:
                continue
            spec = {}
            for label in ('orig', 'new'):
                wsum = sum(wt for _, _, wt in acc[label])
                spec[label] = 10 * np.log10(sum(10 ** (d / 10) * wt for _, d, wt in acc[label]) / wsum)
            fr = acc['orig'][0][0]
            # the slices the subtraction took out (10 dB or more below the original) are not "surroundings"
            hole = spec['new'] < spec['orig'] - 10
            out = {}
            for label in ('orig', 'new'):
                db = spec[label]
                levels = []
                for k in OFFSETS:
                    d = np.abs(fr - k * SPACING)
                    ring = (d >= 4) & (d <= 25) & ~hole
                    if ring.sum() < 20:
                        ring = (d >= 4) & (d <= 25)
                    levels.append(float(db[d <= 1.5].max() - np.median(db[ring])))
                out[label] = levels
            res[ch, f0] = (out['orig'], out['new'])
    return res, float(sum(r['stop'] - r['start'] for r in an['runs']))


def compare(orig, new):
    ok = True
    x, sr = decode(orig)
    y, sr2 = decode(new)
    print(f'== {os.path.basename(orig)}  ({len(x) / sr:.0f} s)')

    def check(cond, msg):
        nonlocal ok
        ok &= bool(cond)
        print(f'   {"ok  " if cond else "FAIL"} {msg}')

    check(len(x) == len(y) and sr == sr2, f'length {len(x)} -> {len(y)} samples, {sr} -> {sr2} Hz')
    n = min(len(x), len(y))
    lags = []
    for frac in (0.25, 0.5, 0.75):
        i = int(n * frac)
        a = x[i:i + 4 * sr].mean(axis=1)
        b = y[i - 200:i + 4 * sr + 200].mean(axis=1)
        c = np.correlate(b, a, mode='valid')
        lags.append(int(np.argmax(c)) - 200)
    check(all(lag == 0 for lag in lags), f'alignment lags {lags} samples')
    clip = int((np.abs(y) >= 1.0).sum())
    check(clip == 0, f'peak {np.abs(x).max():.3f} -> {np.abs(y).max():.3f}, samples at full scale: {clip}')
    ta, tb = tags(orig), tags(new)
    ta.pop('encoder', None)
    tb.pop('encoder', None)
    check(ta == tb, 'tags unchanged' if ta == tb else f'tags differ: {set(ta.items()) ^ set(tb.items())}')

    res, present = whine_levels(x[:n], y[:n], sr)
    if not res:
        print('   --   no whine found in the original')
    else:
        worst = max(max(v[1]) for v in res.values())
        print(f'   whine present {present:.0f} s; carrier and sidebands, dB above their surroundings, at offsets ' +
              ' '.join(f'{k:+d}' for k in OFFSETS) + f' x {SPACING:g} Hz (original > result):')
        for (ch, f0), (a, b) in sorted(res.items()):
            print(f'     ch{ch} {f0:5.0f} Hz  ' + ' '.join(f'{u:3.0f}>{v:3.0f}' for u, v in zip(a, b)))
        check(worst < MAX_WHINE_DB, f'strongest whine line in the result: {worst:.1f} dB above the floor '
                                    f'(limit {MAX_WHINE_DB:g})')

    Px, Py = spectra(x[:n]), spectra(y[:n])
    f = np.fft.rfftfreq(N, 1 / sr)
    tx = 10 * np.log10(Px.sum(axis=1) + 1e-20)
    groups = {'quiet 5%': tx <= np.percentile(tx, 5),
              'p40-60': (tx >= np.percentile(tx, 40)) & (tx <= np.percentile(tx, 60)),
              'loud 10%': tx >= np.percentile(tx, 90)}
    loud = groups['loud 10%']
    print('   level change, dB; "strong": the loudest frames\' bins at least 20 dB above the quiet-frame level '
          '(music);')
    print('   in brackets the original\'s level in the quiet frames, dBFS per bin:')
    print('     ' + 'band'.ljust(15) + ''.join(g.rjust(10) for g in list(groups) + ['strong']))
    worst_strong = 0.0
    to_dbfs = 20 * np.log10(2 / np.hanning(N).sum())
    for lo, hi in BANDS:
        if lo >= sr / 2:
            continue
        k = (f >= lo) & (f < min(hi, sr / 2))
        cells = []
        for sel in groups.values():
            d = 10 * np.log10(Py[sel][:, k].sum() / Px[sel][:, k].sum())
            cells.append(f'{d:+10.1f}')
        floor = Px[groups['quiet 5%']][:, k].mean(axis=0)              # per bin
        strong = Px[loud][:, k] > 100 * floor
        if strong.sum() > 100:
            d = 10 * np.log10(Py[loud][:, k][strong].sum() / Px[loud][:, k][strong].sum())
            cells.append(f'{d:+10.2f}')
            if hi <= MUSIC_MAX_HZ and (lo, hi) not in WHINE_BANDS:
                worst_strong = max(worst_strong, abs(d))
        else:
            cells.append('-'.rjust(10))
        quiet_lvl = 10 * np.log10(floor.mean()) + to_dbfs
        name = f'{lo / 1000:4.1f}-{hi / 1000:4.1f} kHz' + ('*' if (lo, hi) in WHINE_BANDS else ' ')
        print(f'     {name}' + ''.join(cells) + f'   [{quiet_lvl:5.0f}]')
    check(worst_strong <= MAX_MUSIC_CHANGE_DB,
          f'strong music components change by at most {worst_strong:.2f} dB per band up to '
          f'{MUSIC_MAX_HZ / 1000:g} kHz, whine bands (*) excepted (limit {MAX_MUSIC_CHANGE_DB:g})')
    return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('original')
    ap.add_argument('cleaned')
    a = ap.parse_args()
    if os.path.isdir(a.original):
        pairs = [(p, os.path.join(a.cleaned, os.path.basename(p)))
                 for p in sorted(glob.glob(os.path.join(a.original, '*.mp3')))
                 if os.path.exists(os.path.join(a.cleaned, os.path.basename(p)))]
    else:
        pairs = [(a.original, a.cleaned)]
    all_ok = True
    for p, q in pairs:
        all_ok &= compare(p, q)
        sys.stdout.flush()
    print('ALL OK' if all_ok else 'SOME CHECKS FAILED')
    sys.exit(0 if all_ok else 1)
