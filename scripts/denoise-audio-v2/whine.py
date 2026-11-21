#!/usr/bin/env python3
"""Remove frequency-modulated whines (and their sidebands) by tracking and subtraction.

The whines in assets/Handel/MessiahChinese are not steady tones. Each one wobbles about +-22 Hz around its centre
twice per second (a smooth, nearly sinusoidal FM with a period of about 0.5 s), and carries sidebands from mains
hum modulating it, 49.9 Hz apart: centre +-50, +-100, +-150, +-200 Hz ... Two families are present, at about
6420-6460 Hz and 15590-15630 Hz (the second one's FM mirrored), mostly in the left channel (about 15 dB weaker in
the right), at about -48 dBFS, in long stretches of every chapter. Fixed notch filters cannot follow the wobble,
so they must be wide, and they leave the sidebands beyond +-50 Hz in place.

Method, per channel and per family:

  1. Take the band centre +-400 Hz to complex baseband (exact, in the frequency domain) and decimate it.
  2. Track the strongest line within +-SEARCH Hz of the centre frame by frame (93 ms windows, 5.8 ms hop).
  3. Presence: the whine's FM repeats every 0.5 s, music never does. Where the tracked frequency correlates with
     itself one period earlier (2 s windows) in any channel/family, the whine is present; runs of at least 1.5 s
     seed it, gaps shorter than GAP_S between runs are bridged (loud passages hide the FM from the tracker), and
     the result is widened by PAD_S. All channels and families share this mask. A second pass tracks again
     within only the range the carrier covered in the first (+-NARROW_MARGIN): in some numbers the whine is
     20-30 dB weaker, and music partials elsewhere in the wide window outshine it. Such stretches are found by
     the same score over 8 s windows (WEAK_SCORE), which also bridges longer gaps (WEAK_GAP_S) when it stays
     moderately high across them.
  4. Per present run, the band with the clearest FM is the guide. Its track is cleaned: frames off the median
     of the track 1-3 FM periods before and after are replaced by it, and stretches where the tracker lost the
     whine are filled by repeating the FM pattern from both sides. All whines share this FM (the 15.6 kHz
     family runs mirrored), so every other band's track is the guide's FM, mirrored or not, around the band's
     own centre: weak bands (the right channel, 15.6 kHz under loud music) would otherwise follow music.
  5. Refine the carrier phase twice (demodulate, low-pass, correct the remaining drift). After demodulating
     with it, every member of the family becomes a fixed line: the carrier at 0 Hz, the sidebands at multiples of
     +-50 Hz, and a few small lines from FM detail the tracker smoothed over.
  6. Find these lines in the long-term spectrum of the demodulated signal where the whine is present, add the
     mains comb (49.9 Hz apart) up to +-300 Hz, and extract each line with a narrow low-pass (+-LINE_BW Hz).
     The sum, faded in and out with the mask, re-modulated and brought back to full rate, is the whine; it is
     subtracted.

What is removed is the whine plus whatever lies within +-LINE_BW Hz of each line's moving trajectory: a few Hz
of bandwidth per line, inaudible. No notch hole is left, no delay is added, and the length is unchanged.

Diagnostics:  python3 scripts/denoise-audio-v2/whine.py FILE.mp3 [...] [--whine HZ ...]
prints where the whine is present, the FM period, and per channel and family the centre, swing, level and lines.
"""
import argparse
import math
import sys

import numpy as np

from common import Band, decode, fast_len, gauss_lowpass, medfilt, runs, to_real

DEFAULT_WHINES = (6440.0, 15600.0)
HALF = 400            # analysed band: centre +- HALF Hz (holds sidebands up to +-350 Hz)
DEC = 32              # decimation: 44.1 kHz -> 1378 Hz baseband
SEARCH = 90           # the carrier is searched within centre +- SEARCH Hz
WIN_S = 0.093         # tracking window
HOP_S = 0.0058        # tracking hop
PERIOD_S = (0.48, 0.53)   # the FM period (about 0.5 s) is searched in this range
SCORE_WIN_S = 2.0     # presence score: correlation of the tracked frequency with itself one FM period earlier
ON_SCORE = 0.75       # over SCORE_WIN_S; present where the score exceeds this ...
SEED_S = 1.5          # ... for at least this long,
WEAK_WIN_S = 8.0      # or where the second pass's score over WEAK_WIN_S (steadier, for a weak whine) exceeds
WEAK_SCORE = 0.55     # WEAK_SCORE for at least WEAK_SEED_S. A singer's vibrato on a harmonic near the whine
WEAK_SEED_S = 3.0     # can reach 0.5 over 8 s; a whine 25 dB weaker than usual scores 0.5-0.9 there
WEAK_GAP_S = 120      # longer gaps (up to this) are bridged too when the 8 s score's median over the gap exceeds
WEAK_GAP_MEDIAN = 0.4  # this (music without the whine: 0.05-0.15; a weak whine under music: 0.5-0.6)
GAP_S = 30            # gaps shorter than this between present runs are bridged
PAD_S = 1.5           # present runs are widened by this much on both sides
RELIABLE_SCORE = 0.6  # inside the mask, a band's own track is trusted where its own score exceeds this
LINE_DB = 4           # lines this far above their surroundings in the demodulated spectrum are removed
COMB_HZ = 49.9        # mains sidebands (measured: 49.9 Hz apart) are always removed up to +-COMB_MAX Hz,
COMB_MAX = 300        # each at the strongest point within +-1.5 Hz of its expected place
LINE_BW = 3.0         # each line is extracted with a Gaussian low-pass, -6 dB at +-LINE_BW Hz
MAX_LINES = 48        # at most this many detected lines per band and run (the comb comes on top)
NARROW_MARGIN = 12    # second pass: the carrier is searched only where it was seen in the first, +- this (Hz)


def track(z, rate, centre=0.0, search=SEARCH):
    """Frame-wise strongest line within centre +- search Hz (offsets from the band centre): times (s), offsets (Hz)."""
    N = int(round(WIN_S * rate)) // 2 * 2
    hop = max(1, int(round(HOP_S * rate)))
    nfft = 1024
    w = np.hanning(N)
    zp = np.concatenate([np.zeros(N // 2, complex), z, np.zeros(N, complex)])
    nfr = len(z) // hop + 1
    fr = np.fft.fftshift(np.fft.fftfreq(nfft, 1 / rate))
    sel = np.where(np.abs(fr - centre) <= search)[0]
    df = fr[1] - fr[0]
    f = np.empty(nfr)
    for s in range(0, nfr, 8192):
        e = min(nfr, s + 8192)
        idx = np.arange(s, e)[:, None] * hop + np.arange(N)[None, :]
        Ps = np.abs(np.fft.fftshift(np.fft.fft(zp[idx] * w, nfft, axis=1), axes=1)[:, sel]) ** 2
        k = np.clip(np.argmax(Ps, axis=1), 1, len(sel) - 2)
        rows = np.arange(len(k))
        a, b, c = (np.log(Ps[rows, k + d] + 1e-30) for d in (-1, 0, 1))
        den = a - 2 * b + c
        delta = np.where(den < 0, 0.5 * (a - c) / np.where(den < 0, den, -1), 0.0)
        f[s:e] = fr[sel][k] + np.clip(delta, -0.5, 0.5) * df
    t = np.arange(nfr) * hop / rate
    return t, f


def _sliding_corr(f, lag, win):
    """Correlation of f[i + lag : i + lag + win] with f[i : i + win], for every i."""
    a, b = f[lag:], f[:-lag]

    def wsum(v):
        c = np.concatenate([[0.0], np.cumsum(v)])
        return c[win:] - c[:-win]
    sa, sb = wsum(a), wsum(b)
    cov = wsum(a * b) - sa * sb / win
    va = wsum(a * a) - sa * sa / win
    vb = wsum(b * b) - sb * sb / win
    return cov / np.sqrt(np.maximum(va * vb, 1e-9))


def periodicity(t, f, end_s, win_s=SCORE_WIN_S):
    """Per frame: best correlation of the tracked frequency with itself one FM period earlier, over a centred
    window of win_s seconds.

    Frames whose window reaches past end_s (the end of the audio; the signal is zero-padded beyond it) get -1:
    there the track jumps to a constant, and a step correlates with itself one period later."""
    fps = 1 / (t[1] - t[0])
    win = int(win_s * fps)
    lags = range(int(PERIOD_S[0] * fps), int(PERIOD_S[1] * fps) + 1)
    n = len(f) - lags[-1] - win
    score = np.full(len(f), -1.0)
    if n <= 0:
        return score
    best = np.max([_sliding_corr(f, lag, win)[:n] for lag in lags], axis=0)
    off = (win + lags[-1]) // 2
    score[off:off + n] = best
    score[t > end_s - (win + lags[-1] - off) / fps] = -1.0
    return score


def seeds(t, score, threshold, min_s):
    """Frames where score exceeds threshold for at least min_s seconds."""
    fps = 1 / (t[1] - t[0])
    mask = score > threshold
    for a, b in runs(mask):
        if (b - a) / fps < min_s:
            mask[a:b] = False
    return mask


def presence(t, seed, weak=None):
    """Boolean mask (per frame) of where the whine is present, from the seed frames (and the 8 s score)."""
    fps = 1 / (t[1] - t[0])
    mask = seed.copy()
    for a, b in runs(~mask):           # bridge gaps between seeds
        if 0 < a and b < len(mask):
            gap = (b - a) / fps
            if gap < GAP_S or (weak is not None and gap < WEAK_GAP_S and np.median(weak[a:b]) > WEAK_GAP_MEDIAN):
                mask[a:b] = True
    pad = int(PAD_S * fps)
    for a, b in runs(mask):
        mask[max(0, a - pad):b + pad] = True
    return mask


def fm_period(f, sel):
    """FM period in frames (fractional) from the autocorrelation of the track over the frames `sel`.

    Measured at about 8 periods for precision (the FM is phase-stable over many seconds)."""
    v = np.where(sel, f - np.median(f[sel]), 0.0)
    fps = 1 / HOP_S

    def peak(lo, hi):
        lags = np.arange(max(1, lo), hi + 1)
        c = np.array([np.dot(v[lag:], v[:-lag]) for lag in lags])
        k = int(np.argmax(c))
        if 0 < k < len(c) - 1:
            den = c[k - 1] - 2 * c[k] + c[k + 1]
            if den < 0:
                return lags[k] + 0.5 * (c[k - 1] - c[k + 1]) / den
        return float(lags[k])
    p1 = peak(int(PERIOD_S[0] * fps), int(PERIOD_S[1] * fps) + 1)
    p8 = peak(int(8 * p1) - 4, int(8 * p1) + 4)
    return p8 / 8 if abs(p8 / 8 - p1) < 0.5 else p1


def clean_track(f, mask, reliable, period):
    """Repair the tracked frequency where music pulled the tracker away from the whine.

    The FM repeats every `period` frames. Frames more than 4 Hz off the median of the track 1, 2 and 3 periods
    before and after are replaced by that median. Unreliable stretches inside the mask longer than 0.5 s are
    rebuilt by repeating the pattern forwards from before and backwards from after, cross-faded."""
    n = len(f)
    i = np.arange(n, dtype=float)
    model = np.median(np.vstack([np.interp(i + k * period, i, f) for k in (-3, -2, -1, 1, 2, 3)]), axis=0)
    out = f.copy()
    bad = mask & (np.abs(f - model) > 4)
    out[bad] = model[bad]
    min_len = int(0.5 / HOP_S)
    for a, b in runs(mask & ~reliable):
        if b - a < min_len:
            continue
        fwd = out.copy()
        for j in range(a, b):                          # repeat from before
            p = j - period
            if p >= 0:
                lo = int(p)
                fwd[j] = fwd[lo] + (p - lo) * (fwd[lo + 1] - fwd[lo])
        bwd = out.copy()
        for j in range(b - 1, a - 1, -1):              # repeat from after
            p = j + period
            if p < n - 1:
                lo = int(p)
                bwd[j] = bwd[lo] + (p - lo) * (bwd[lo + 1] - bwd[lo])
        has_past = a - 2 * period >= 0 and reliable[max(0, a - int(2 * period)):a].mean() > 0.5
        has_future = b + 2 * period < n and reliable[b:b + int(2 * period)].mean() > 0.5
        wgt = np.linspace(1, 0, b - a) if (has_past and has_future) else np.full(b - a, 1.0 if has_past else 0.0)
        if has_past or has_future:
            out[a:b] = wgt * fwd[a:b] + (1 - wgt) * bwd[a:b]
    return medfilt(out, 5)


def refine_phase(z, rate, t, f):
    """Phase of the carrier: integrate the tracked frequency, then correct the remaining drift twice."""
    ts = np.arange(len(z)) / rate
    fz = np.interp(ts, t, f)
    for L in (8.0, 20.0):
        phi = 2 * np.pi * np.cumsum(fz) / rate
        y = gauss_lowpass(z * np.exp(-1j * phi), rate, L)
        d = np.angle(y[1:] * np.conj(y[:-1])) * rate / (2 * np.pi)      # remaining frequency error
        d = np.concatenate([[0.0], d])
        fz = fz + gauss_lowpass(d, rate, L)
    return 2 * np.pi * np.cumsum(fz) / rate


def demod_spectrum(yd, rate, gate, nper=8192):
    """Long-term power spectrum (Hz, dB) of the demodulated signal over the windows lying entirely where gate == 1,
    and the number of windows averaged."""
    hop = nper // 2
    w = np.hanning(nper)
    starts = [s for s in range(0, len(yd) - nper, hop) if gate[s:s + nper].min() > 0.99]
    if len(starts) < 4:
        return None, None, 0
    acc = np.zeros(nper)
    for s in starts:
        acc += np.abs(np.fft.fft(yd[s:s + nper] * w)) ** 2
    fr = np.fft.fftshift(np.fft.fftfreq(nper, 1 / rate))
    return fr, 10 * np.log10(np.fft.fftshift(acc / len(starts)) + 1e-30), len(starts)


def local_excess(fr, db, width=12, guard=1.0):
    """dB above the median of the surrounding +-width Hz (the centre +-guard Hz excluded)."""
    df = fr[1] - fr[0]
    pad, g = int(width / df), int(guard / df)
    view = np.lib.stride_tricks.sliding_window_view(np.pad(db, pad, mode='edge'), 2 * pad + 1)
    keep = np.ones(2 * pad + 1, bool)
    keep[pad - g:pad + g + 1] = False
    return db - np.median(view[:, keep], axis=1)


def demod_lines(yd, rate, gate, half=HALF):
    """Lines [(offset Hz, dB above surroundings)], strongest first, of the demodulated signal where present."""
    fr, db, count = demod_spectrum(yd, rate, gate)
    if fr is None:                                       # too short to measure: the carrier and the mains comb
        return [(0.0, 0.0)] + [(sg * k * COMB_HZ, 0.0) for k in range(1, int(COMB_MAX / COMB_HZ) + 1)
                               for sg in (-1, 1)]
    ex = local_excess(fr, db)
    lim = half - 30
    # an average of `count` power spectra scatters by about 4.34 / sqrt(count) dB; over the ~4000 bins searched,
    # 4 times that is where chance peaks end (short runs average few windows)
    thr = max(LINE_DB, 4 * 4.34 / math.sqrt(count))
    cand = [i for i in range(1, len(db) - 1)
            if db[i] >= db[i - 1] and db[i] >= db[i + 1] and ex[i] > thr and abs(fr[i]) < lim]
    cand.sort(key=lambda i: -ex[i])
    lines = []
    for i in cand:                                       # one line per +-1.5 Hz
        if all(abs(fr[i] - o) > 1.5 for o, _ in lines):
            lines.append((float(fr[i]), float(ex[i])))
        if len(lines) >= MAX_LINES:
            break
    if not any(abs(o) < 1.5 for o, _ in lines):
        lines.insert(0, (0.0, 0.0))
    # mains sidebands: the spacing from the +-1st pair when it stands out, then every multiple up to COMB_MAX
    pair = [abs(o) for o, e in lines if abs(abs(o) - COMB_HZ) < 1.0 and e > 6]
    spacing = float(np.mean(pair)) if pair else COMB_HZ
    for k in range(1, int(COMB_MAX / spacing) + 1):
        for target in (-k * spacing, k * spacing):
            near = np.where(np.abs(fr - target) <= 1.5)[0]
            o = float(fr[near[np.argmax(db[near])]]) if len(near) else target
            if all(abs(o - p) > 1.5 for p, _ in lines):
                lines.append((o, float(ex[near].max()) if len(near) else 0.0))
    return lines


def remove_family(band, t, run_list, info):
    """Baseband estimate of one band's whine family (same shape as band.z), over all present runs.

    run_list: [(run mask, track)], the track (Hz offsets from band.fc, per frame) valid inside the run."""
    z, rate = band.z, band.rate
    ts = np.arange(len(z)) / rate
    whine = np.zeros_like(z)
    for run_mask, fr in run_list:
        phi = refine_phase(z, rate, t, fr)
        gate = np.interp(ts, t, run_mask.astype(float))
        gate = np.clip(gauss_lowpass(gate, rate, 3.0), 0, 1)
        gate[gate < 1e-3] = 0
        yd = z * np.exp(-1j * phi)
        lines = demod_lines(yd, rate, gate)
        resid = yd
        est = np.zeros_like(yd)
        for o, _ in lines:
            rot = np.exp(-2j * np.pi * o * ts)
            c = gauss_lowpass(resid * rot, rate, LINE_BW) / rot
            est += c
            resid = resid - c
        part = est * gate * np.exp(1j * phi)
        whine += part
        info.setdefault('runs', []).append({
            'centre': band.fc + float(np.median(fr[run_mask])),
            'swing': float(np.percentile(fr[run_mask], 95) - np.percentile(fr[run_mask], 5)) / 2,
            'lines': lines,
            # power of the real whine = half the mean |analytic|^2, averaged over the whole file
            'level_db': 10 * math.log10(float(np.mean(np.abs(part) ** 2)) / 2 + 1e-30)})
    return whine


def guided_track(f, guide, run_mask):
    """A band's track rebuilt from the guide's FM: centre + sign * guide, sign and centre from the band itself.

    All the whines share one FM (the 15.6 kHz family mirrored), but a weak band's own tracker often follows a
    music partial instead. The sign is the one under which the band's own track agrees with it more often;
    the centre is the most common difference between the two."""
    best = None
    for sign in (1.0, -1.0):
        d = f[run_mask] - sign * guide[run_mask]
        hist, edges = np.histogram(d, bins=np.arange(-SEARCH, SEARCH + 0.5, 0.5))
        hist = np.convolve(hist, np.ones(5), mode='same')
        centre = float(edges[np.argmax(hist)] + 0.25)
        pred = centre + sign * guide
        agree = float(np.mean(np.abs(f[run_mask] - pred[run_mask]) < 3))
        if best is None or agree > best[0]:
            best = (agree, pred, sign)
    return best[1], best[2], best[0]


def analyse(x, sr, whines=DEFAULT_WHINES):
    """Find the whines in stereo samples (n, 2): where they are present, and each band's track per present run.

    Two passes. The first tracks the carrier within +-SEARCH Hz and finds the stretches where the FM shows
    clearly. Where the whine is weaker (some numbers have it 20-25 dB lower), music partials inside that window
    often outshine it and the tracker follows them. So the second pass tracks each band again, but only within the
    range the carrier covered in the first pass (+- NARROW_MARGIN), and the presence is taken from both passes.
    Presence is shared: the whines start and stop together in both channels."""
    n, nch = x.shape
    m = fast_len(n, DEC)                           # zero-padded to a fast FFT length
    end = n / sr
    bands, wide, wide_scores = {}, {}, {}
    for ch in range(nch):
        xc = np.zeros(m)
        xc[:n] = x[:, ch]
        X = np.fft.rfft(xc)
        del xc
        for f0 in whines:
            b = Band(X, m, sr, f0, HALF, DEC)
            t, f = track(b.z, b.rate)
            bands[ch, f0], wide[ch, f0], wide_scores[ch, f0] = b, f, periodicity(t, f, end)
        del X
    fps = 1 / (t[1] - t[0])
    top = np.max(list(wide_scores.values()), axis=0)
    seed = seeds(t, top, ON_SCORE, SEED_S)
    tracks, scores, weak_top = wide, wide_scores, None
    if seed.any():
        tracks, scores, weak = {}, {}, []
        for k, b in bands.items():
            sel = wide_scores[k] > ON_SCORE
            if sel.sum() < 5 * fps:
                sel = top > ON_SCORE
            lo, hi = np.percentile(wide[k][sel], [1, 99])
            _, f = track(b.z, b.rate, centre=(lo + hi) / 2, search=min(SEARCH, (hi - lo) / 2 + NARROW_MARGIN))
            tracks[k], scores[k] = f, np.maximum(wide_scores[k], periodicity(t, f, end))
            weak.append(periodicity(t, f, end, WEAK_WIN_S))
        seed |= seeds(t, np.max(list(scores.values()), axis=0), ON_SCORE, SEED_S)
        weak_top = np.max(weak, axis=0)
        seed |= seeds(t, weak_top, WEAK_SCORE, WEAK_SEED_S)
    mask = presence(t, seed, weak_top)
    result = {'n': n, 'm': m, 't': t, 'bands': bands, 'mask': mask, 'runs': [],
              'tracks': {k: [] for k in bands}}
    for a, b in runs(mask):
        run_mask = np.zeros_like(mask)
        run_mask[a:b] = True
        best = max(tracks, key=lambda k: np.mean(scores[k][run_mask]))      # the guide: clearest band
        sel = run_mask & (scores[best] > ON_SCORE)
        period = fm_period(tracks[best], sel if sel.sum() > 5 * fps else run_mask)
        own = clean_track(tracks[best], run_mask, run_mask & (scores[best] > RELIABLE_SCORE), period)
        guide = own - np.median(own[run_mask])
        result['runs'].append({'start': a / fps, 'stop': b / fps, 'period_s': period / fps, 'guide': best})
        for k in bands:
            if k == best:
                fr, sign, agree = own, 1.0, 1.0
            else:
                fr, sign, agree = guided_track(tracks[k], guide, run_mask)
            result['tracks'][k].append((run_mask, fr, sign, agree))
    return result


def remove_whines(x, sr, whines=DEFAULT_WHINES, log=None):
    """Remove the whine families from stereo float samples (n, 2). Returns (float32 samples (n, 2), report)."""
    an = analyse(x, sr, whines)
    n, m, t = an['n'], an['m'], an['t']
    report = {'runs': an['runs'], 'families': []}
    out = np.array(x, dtype=np.float32)
    if an['runs']:
        for ch in range(x.shape[1]):
            parts = []
            for f0 in whines:
                k = (ch, f0)
                info = {'ch': ch, 'f0': f0, 'fit': [(sg, ag) for _, _, sg, ag in an['tracks'][k]]}
                run_list = [(rm, fr) for rm, fr, _, _ in an['tracks'][k]]
                parts.append((an['bands'][k], remove_family(an['bands'][k], t, run_list, info)))
                report['families'].append(info)
            out[:, ch] -= to_real(parts, m)[:n].astype(np.float32)
            for f0 in whines:
                an['bands'][ch, f0] = None
    if log:
        log(describe(report))
    return out, report


def describe(report):
    if not report['runs']:
        return '  whine: not present'
    dur = sum(r['stop'] - r['start'] for r in report['runs'])
    lines = [f'  whine present {dur:.0f} s:']
    for k, r in enumerate(report['runs']):
        lines.append(f'    run {k + 1}: {r["start"]:.0f}-{r["stop"]:.0f} s, FM period {r["period_s"]:.4f} s, '
                     f'guide ch{r["guide"][0]} {r["guide"][1]:.0f} Hz')
    for info in report['families']:
        for k, sub in enumerate(info['runs']):
            sign, agree = info['fit'][k]
            lines.append(f'  ch{info["ch"]} {info["f0"]:.0f} Hz run {k + 1}: centre {sub["centre"]:.1f} Hz, '
                         f'swing +-{sub["swing"]:.0f} Hz, FM {"+" if sign > 0 else "-"}guide '
                         f'(own track agrees {100 * agree:.0f} %), removed {sub["level_db"]:.1f} dBFS rms, '
                         f'{len(sub["lines"])} lines: ' +
                         ' '.join(f'{o:+.1f}:{e:.0f}' for o, e in sorted(sub['lines'])))
    return '\n'.join(lines)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--whine', type=float, action='append', help='family centre in Hz (default 6440 and 15600)')
    a = ap.parse_args()
    for path in a.files:
        x, sr = decode(path)
        print(f'== {path}  ({len(x) / sr:.0f} s)')
        remove_whines(x, sr, a.whine or DEFAULT_WHINES, log=print)
        sys.stdout.flush()
