#!/usr/bin/env python3
"""Reduce broadband hiss with a short-time spectral (STFT) noise suppressor.

The MP3 files under assets/Handel/MessiahChinese carry a white hiss: in the gaps between numbers the spectrum is
flat at about -95 dBFS per bin (2048-point FFT) from 1.5 kHz up to the codec's cut-off near 17 kHz, about
-67 dBFS rms, with uncorrelated left and right channels. Under the music it is masked; in soft passages and
pauses it is heard as a steady "shhh".

Method:

  * STFT, 2048-point Hann window, 512 hop (75 % overlap), weighted overlap-add; with unit gains the output equals
    the input to rounding error. Frames are centred on their hop, so nothing is delayed.
  * Noise level per channel, per 1/6-octave band, per frame, by minimum statistics: band power smoothed over
    ~60 ms, its minimum over a sliding MINWIN_S window, smoothed, bias-corrected (the bias is measured once on
    white noise run through the same estimator). In dense music the minimum can sit above the hiss, so the
    estimate is capped twice: by a white-noise model, the level of the 6-14 kHz bands (music is thin there) times
    the file's own noise shape (taken from its quietest frames) +3 dB; and, because the hiss is steady through a
    file while long dense passages (a chorus with no rest for minutes) lift the minimum, by the band's own 10th
    percentile over the file +6 dB.
  * Gain per bin: Wiener rule with a "decision-directed" a-priori SNR (alpha 0.98), which keeps "musical noise"
    (twinkling residue) away. Left and right share one gain, computed from their summed powers, so the stereo
    image does not wander. The gain is floored: at most REDUCTION_DB (default 18) above 2 kHz, easing to 4 dB
    below 250 Hz, where the "noise" is mostly room tone and hum, not hiss. Gains are smoothed over 3 bins.

Usage (diagnostics: prints the estimated hiss level per minute):
  python3 scripts/denoise-audio-v2/dehiss.py FILE.mp3 [...]
"""
import argparse
import math
import sys

import numpy as np

from common import decode

N = 2048
HOP = 512
SMOOTH_FRAMES = 5       # band power smoothing (moving average, ~ 60 ms)
SILENCE = 1e-7          # frames 70 dB below the median frame power count as digital silence
MINWIN_S = 6.0          # minimum-statistics window
CAP_DB = 3.0            # the per-band estimate may exceed the white-noise model by this much at most,
GLOBAL_PCT = 10         # and the file's GLOBAL_PCT percentile of the estimate (per band)
GLOBAL_DB = 6.0         # by this much at most
DD_ALPHA = 0.98         # decision-directed a-priori SNR smoothing
REDUCTION_DB = 18.0     # maximum reduction above 2 kHz
LOW_REDUCTION_DB = 4.0  # maximum reduction below 250 Hz
HF_REF = (6000, 14000)  # bands used for the white-noise level


def window():
    return np.hanning(N + 1)[:N].astype(np.float32)          # periodic Hann: exact overlap-add at 75 %


def bands(sr):
    """Bin edges of ~1/6-octave bands from 60 Hz to Nyquist, at least 3 bins wide."""
    edges = [0]
    f = 60.0
    while f < sr / 2:
        k = int(round(f * N / sr))
        if k - edges[-1] >= 3:
            edges.append(k)
        f *= 2 ** (1 / 6)
    edges.append(N // 2 + 1)
    return np.array(edges)


def padded(x):
    """The signal with N zeros before and 2N after, so that every sample is covered by four full frames."""
    return np.concatenate([np.zeros(N, np.float32), np.asarray(x, np.float32), np.zeros(2 * N, np.float32)])


def nframes(n):
    return (n + N - 1) // HOP + 1


def stft_frames(xp, start, stop):
    """Complex spectra of frames start..stop-1 of a padded signal (frame j starts at xp[j * HOP])."""
    idx = np.arange(start, stop)[:, None] * HOP + np.arange(N)[None, :]
    return np.fft.rfft(xp[idx] * window(), axis=1).astype(np.complex64)


def band_powers(x, edges, chunk=4096):
    """Mean power per band and frame: (frames, bands), float64."""
    xp = padded(x)
    nf = nframes(len(x))
    out = np.empty((nf, len(edges) - 1))
    for s in range(0, nf, chunk):
        e = min(nf, s + chunk)
        P = np.abs(stft_frames(xp, s, e)) ** 2
        c = np.concatenate([np.zeros((e - s, 1)), np.cumsum(P, axis=1, dtype=np.float64)], axis=1)
        out[s:e] = (c[:, edges[1:]] - c[:, edges[:-1]]) / np.diff(edges)
    return out


def _sliding_min(v, win):
    """Minimum over a centred window of `win` frames along axis 0."""
    n = v.shape[0]
    half = win // 2
    padded = np.concatenate([np.repeat(v[:1], half, 0), v, np.repeat(v[-1:], half, 0)])
    blk = max(1, win // 16)                                   # block minima, then minimum of blocks
    nb = int(math.ceil(len(padded) / blk))
    pb = np.concatenate([padded, np.repeat(padded[-1:], nb * blk - len(padded), 0)])
    bmin = pb.reshape(nb, blk, -1).min(axis=1)
    k = int(math.ceil(win / blk))
    out = np.empty_like(v)
    for i in range(n):
        b0 = i // blk
        out[i] = bmin[b0:b0 + k].min(axis=0)
    return out


def _smooth_time(v, frames):
    """Moving average along axis 0 (centred)."""
    c = np.cumsum(np.concatenate([np.zeros((1, v.shape[1])), v]), axis=0)
    half = frames // 2
    i = np.arange(v.shape[0])
    lo = np.clip(i - half, 0, v.shape[0])
    hi = np.clip(i + half + 1, 0, v.shape[0])
    return (c[hi] - c[lo]) / (hi - lo)[:, None]


def min_stats(bp, sr):
    """Raw minimum-statistics track of band powers (frames, bands).

    Digital silence (and the padding at both ends) would pull the minimum to zero for MINWIN_S around it, so
    frames whose smoothing window touches a silent frame are left out, and the track is carried over them."""
    k = SMOOTH_FRAMES
    s = _smooth_time(bp, k)
    total = bp.sum(axis=1)
    ref = np.median(total[total > 0]) if (total > 0).any() else 0.0
    silent = total <= ref * SILENCE
    near = np.convolve(silent.astype(float), np.ones(k), mode='same') > 0
    s[near] = np.inf
    fps = sr / HOP
    m = _sliding_min(s, int(MINWIN_S * fps))
    ok = np.isfinite(m[:, 0])
    if not ok.any():
        return np.zeros_like(bp)
    idx = np.where(ok, np.arange(len(m)), 0)
    np.maximum.accumulate(idx, out=idx)                   # carry the last finite value forwards ...
    m = m[idx]
    first = np.argmax(ok)
    m[:first] = m[first]                                  # ... and the first one backwards
    return _smooth_time(m, int(1.0 * fps))


_BIAS = {}


def bias(sr, edges):
    """Mean power / minimum-statistics estimate, per band, for white noise (measured once)."""
    key = (sr, len(edges))
    if key not in _BIAS:
        rng = np.random.default_rng(1)
        noise = rng.standard_normal(int(40 * sr)).astype(np.float32)
        bp = band_powers(noise, edges)
        est = min_stats(bp, sr)
        _BIAS[key] = bp.mean(axis=0) / np.median(est[len(est) // 4:-len(est) // 4], axis=0)
    return _BIAS[key]


def noise_estimate(x, sr, edges):
    """Noise power per band and frame (frames, bands) for one channel, and the report numbers."""
    bp = band_powers(x, edges)
    est = min_stats(bp, sr) * bias(sr, edges)
    centres = np.sqrt(np.maximum(edges[:-1], 1) * edges[1:]) * sr / N
    hf = (centres >= HF_REF[0]) & (centres <= HF_REF[1])
    # the file's noise shape: band powers relative to the 6-14 kHz level, in its quietest 3 % of frames
    level = bp[:, hf].mean(axis=1)
    valid = level > level.max() * 1e-12                        # not digital silence (or the padding)
    if valid.sum() < 100:
        return est, est[:, hf].mean(axis=1)
    quiet = valid & (level <= np.percentile(level[valid], 3))
    shape = np.median(bp[quiet] / level[quiet, None], axis=0)
    white = est[:, hf].mean(axis=1)                            # white-noise level over time
    cap = white[:, None] * shape[None, :] * 10 ** (CAP_DB / 10)
    # the hiss is steady through a file, the estimate is not: in long dense passages the minimum over MINWIN_S
    # is music. So no band may exceed the file's own low (GLOBAL_PCT) level by more than GLOBAL_DB.
    good = valid & np.isfinite(est).all(axis=1)
    glob = np.percentile(est[good], GLOBAL_PCT, axis=0) * 10 ** (GLOBAL_DB / 10)
    est = np.minimum(np.minimum(est, cap), glob[None, :])
    return est, est[:, hf].mean(axis=1)


def gain_floor(sr, reduction_db):
    f = np.arange(N // 2 + 1) * sr / N
    lo, hi = math.log(250), math.log(2000)
    r = np.clip((np.log(np.maximum(f, 1)) - lo) / (hi - lo), 0, 1)
    red = LOW_REDUCTION_DB + r * (reduction_db - LOW_REDUCTION_DB)
    return (10 ** (-red / 20)).astype(np.float32)


def dehiss(x, sr, reduction_db=REDUCTION_DB, log=None, chunk=2048):
    """Hiss-reduced copy of stereo float samples (n, 2), same length. Returns (y, report)."""
    n, nch = x.shape
    edges = bands(sr)
    nf = nframes(n)
    noise = []
    whites = []
    for ch in range(nch):
        nb, white = noise_estimate(np.ascontiguousarray(x[:, ch], dtype=np.float32), sr, edges)
        noise.append(nb)
        whites.append(white)
    # band -> bin interpolation matrix (linear in band index across centres)
    centres_bin = (edges[:-1] + edges[1:] - 1) / 2
    bins = np.arange(N // 2 + 1)
    gmin = gain_floor(sr, reduction_db)
    w = window()
    norm = (w ** 2).sum() / HOP                                # 1.5 for Hann at 75 % overlap
    y = np.zeros((n + 3 * N, nch), np.float32)
    prev_g2gamma = None
    xs = [padded(x[:, ch]) for ch in range(nch)]
    for s in range(0, nf, chunk):
        e = min(nf, s + chunk)
        Y = [stft_frames(xs[ch], s, e) for ch in range(nch)]
        lam = sum(np.array([np.interp(bins, centres_bin, row) for row in noise[ch][s:e]], np.float32)
                  for ch in range(nch))
        P = sum(np.abs(Yc) ** 2 for Yc in Y)
        gamma = P / np.maximum(lam, 1e-20)
        G = np.empty_like(gamma)
        for i in range(e - s):
            ml = np.maximum(gamma[i] - 1, 0)
            xi = ml if prev_g2gamma is None else DD_ALPHA * prev_g2gamma + (1 - DD_ALPHA) * ml
            g = xi / (1 + xi)
            g = np.maximum(g, gmin)
            G[i] = g
            prev_g2gamma = g * g * gamma[i]
        G[:, 1:-1] = 0.25 * G[:, :-2] + 0.5 * G[:, 1:-1] + 0.25 * G[:, 2:]      # smooth over 3 bins
        for ch in range(nch):
            frames = np.fft.irfft(Y[ch] * G, N, axis=1) * w / norm
            for i in range(e - s):
                p = (s + i) * HOP
                y[p:p + N, ch] += frames[i]
    out = y[N:N + n]
    report = {'hiss_dbfs': [to_dbfs(float(np.median(wv))) for wv in whites]}
    if log:
        for ch in range(nch):
            log(f'  ch{ch} hiss per minute (dBFS per bin): ' + per_minute(whites[ch], sr))
    return out, report


def to_dbfs(power):
    """Raw STFT bin power -> dBFS per bin (a full-scale sine reads 0 dB)."""
    return 10 * math.log10(power * (2 / window().sum()) ** 2 + 1e-30)


def per_minute(white, sr):
    per = int(60 * sr / HOP)
    return ' '.join(f'{to_dbfs(float(np.median(white[i:i + per]))):.0f}' for i in range(0, len(white), per))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    a = ap.parse_args()
    for path in a.files:
        x, sr = decode(path)
        print(f'== {path}  ({len(x) / sr:.0f} s)')
        edges = bands(sr)
        for ch in range(x.shape[1]):
            _, white = noise_estimate(np.ascontiguousarray(x[:, ch]), sr, edges)
            print(f'  ch{ch} hiss per minute (dBFS per bin): ' + per_minute(white, sr))
        sys.stdout.flush()
