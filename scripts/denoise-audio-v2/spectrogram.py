#!/usr/bin/env python3
"""Render a zoomed spectrogram (time range x frequency range) of one or more audio files into a PNG, stacked.

Unlike ffmpeg's showspectrumpic, the FFT size is free, so narrow features show: the 0.5 s wobble of the whines
needs about 4096 points (93 ms, 10.8 Hz bins); a steady line is sharper with 16384.

Usage:
  python3 scripts/denoise-audio-v2/spectrogram.py OUT.png START END FMIN FMAX FILE [FILE ...] [--n 4096] [--range -130 -50]

Example (the 6.4 kHz whine in the original and in the cleaned file):
  python3 scripts/denoise-audio-v2/spectrogram.py /tmp/w.png 100 110 6100 6800 orig/Chapter2.mp3 assets/Handel/MessiahChinese/Chapter2.mp3

Requires matplotlib.
"""
import argparse
import os

import numpy as np

from common import decode


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out')
    ap.add_argument('start', type=float)
    ap.add_argument('end', type=float)
    ap.add_argument('fmin', type=float)
    ap.add_argument('fmax', type=float)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--n', type=int, default=4096, help='FFT size (default 4096); the hop is a quarter of it')
    ap.add_argument('--range', type=float, nargs=2, default=(-130, -50), metavar=('LOW', 'HIGH'),
                    help='colour range in dBFS per bin (default -130 -50)')
    a = ap.parse_args()

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(a.files), 1, figsize=(16, 4.5 * len(a.files)), squeeze=False)
    for ax, path in zip(axes[:, 0], a.files):
        x, sr = decode(path, start=a.start, duration=a.end - a.start)
        mono = x.mean(axis=1)
        n, hop = a.n, a.n // 4
        w = np.hanning(n).astype(np.float32)
        nfr = 1 + (len(mono) - n) // hop
        idx = np.arange(nfr)[:, None] * hop + np.arange(n)[None, :]
        S = 20 * np.log10(np.abs(np.fft.rfft(mono[idx] * w, axis=1)) * 2 / w.sum() + 1e-12)
        f = np.fft.rfftfreq(n, 1 / sr)
        k0, k1 = np.searchsorted(f, [a.fmin, a.fmax])
        im = ax.imshow(S[:, k0:k1].T, origin='lower', aspect='auto', cmap='magma', vmin=a.range[0], vmax=a.range[1],
                       extent=[a.start, a.start + nfr * hop / sr, f[k0], f[k1 - 1]])
        ax.set_title(os.path.join(os.path.basename(os.path.dirname(path)), os.path.basename(path)))
        ax.set_xlabel('s')
        ax.set_ylabel('Hz')
        fig.colorbar(im, ax=ax, label='dBFS per bin')
    plt.tight_layout()
    plt.savefig(a.out, dpi=70)
    print(a.out)


if __name__ == '__main__':
    main()
