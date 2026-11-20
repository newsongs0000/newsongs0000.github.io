#!/usr/bin/env python3
"""Print the loudness of an MP3, step by step, to find sections Whisper cannot hear (see scripts/README.md).

Useful where a number alternates soft and loud passages, e.g. the a cappella Graves and the orchestral
Allegros of Messiah No. 44: a drop to near silence marks a rest between sections.

Usage: python3 loudness.py MP3 START END [--step SECONDS]
  Prints "time:dB" pairs (RMS level, dBFS; about -60 is silence).
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

RATE = 8000


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mp3")
    ap.add_argument("start", type=float)
    ap.add_argument("end", type=float)
    ap.add_argument("--step", type=float, default=1.0)
    args = ap.parse_args()

    audio = common.decode(args.mp3, args.start, args.end, RATE)
    size = int(RATE * args.step)
    cells = []
    for i in range(len(audio) // size):
        rms = np.sqrt(np.mean(audio[i * size:(i + 1) * size] ** 2))
        cells.append(f"{args.start + i * args.step:g}:{20 * np.log10(rms + 1e-9):.0f}")
    print(" ".join(cells))


if __name__ == "__main__":
    main()
