#!/usr/bin/env python3
"""Clean MP3 files: remove the FM whines (whine.py), reduce the hiss (dehiss.py), and encode once.

Start from the ORIGINAL files, not from files that were already filtered and re-encoded (see README.md for how to
get them out of git): every MP3 generation loses a little, and earlier notch filters would leave holes.

Usage:
  python3 scripts/denoise-audio-v2/clean.py --out-dir DIR ORIGINAL.mp3 [...]
  python3 scripts/denoise-audio-v2/clean.py --out-dir DIR --reduction 12 --no-whine ORIGINAL.mp3

The output has the same number of samples as the input (lyric timings stay valid), the input's tags (and cover
art, if any), LAME VBR quality --quality (default 2). A peak that the encoder pushes over full scale is
corrected with a small gain reduction (see common.encode_mp3).
"""
import argparse
import os
import sys
import time

import numpy as np

from common import decode, encode_mp3
from dehiss import REDUCTION_DB, dehiss
from whine import DEFAULT_WHINES, remove_whines


def clean(src, dst, whines, reduction_db, quality, log=print):
    t0 = time.time()
    x, sr = decode(src)
    log(f'== {src}  ({len(x) / sr:.0f} s, {sr} Hz)')
    y = x
    if whines:
        y, _ = remove_whines(y, sr, whines, log=log)
    if reduction_db > 0:
        y, _ = dehiss(y, sr, reduction_db, log=log)
    y = np.asarray(y, dtype=np.float32)
    assert y.shape == x.shape
    gain = encode_mp3(y, sr, src, dst, quality)
    if gain:
        log(f'  peak over full scale after encoding: applied {gain:.2f} dB')
    log(f'  -> {dst}  ({os.path.getsize(src) / 1e6:.1f} MB -> {os.path.getsize(dst) / 1e6:.1f} MB, '
        f'{time.time() - t0:.0f} s)')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--out-dir', required=True, help='write the results here, under the same file names')
    ap.add_argument('--whine', type=float, action='append',
                    help='whine family centre in Hz, may be repeated (default: 6440 and 15600)')
    ap.add_argument('--no-whine', action='store_true', help='skip whine removal')
    ap.add_argument('--reduction', type=float, default=REDUCTION_DB,
                    help=f'maximum hiss reduction above 2 kHz in dB (default {REDUCTION_DB:g}; 0 skips it)')
    ap.add_argument('--quality', type=int, default=2, help='LAME VBR quality, 0 (best) - 9 (default 2)')
    a = ap.parse_args()
    whines = [] if a.no_whine else (a.whine or list(DEFAULT_WHINES))
    for src in a.files:
        dst = os.path.join(a.out_dir, os.path.basename(src))
        if os.path.abspath(dst) == os.path.abspath(src):
            sys.exit(f'{dst}: the output would overwrite the input; choose another --out-dir')
        clean(src, dst, whines, a.reduction, a.quality, log=lambda s: print(s, flush=True))
