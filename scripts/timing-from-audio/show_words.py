#!/usr/bin/env python3
"""Print a movement's transcripts word by word, with the time of each word (see scripts/README.md).

  SEG 840.0-849.1 cr=1.0                       one Whisper segment; cr is its compression ratio
      Who@838.9? shall@840.3 lay@841.0 …       word@start; "?" = Whisper's confidence is below 0.3
  SEG 753.2-758.1 cr=3.8 LOOP                  cr > 2.4: Whisper repeated itself (often in melismas);
                                               only the first words are shown, and only they are usable

Usage: python3 show_words.py WORK_DIR MOVEMENT [INDEX ...] [--asr DIR]
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

LOOP_RATIO = 2.4  # Whisper's own threshold for a repetitive (compressible) segment
LOW_PROBABILITY = 0.3


def transcripts(asr_dir, movement, indexes=None):
    files = glob.glob(os.path.join(asr_dir, f"{movement}_*.json"))
    files.sort(key=lambda p: int(re.search(r"_(\d+)\.json$", p).group(1)))
    docs = [json.load(open(p, encoding="utf-8")) for p in files]
    return [d for d in docs if not indexes or d["index"] in indexes]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("work_dir")
    ap.add_argument("movement")
    ap.add_argument("indexes", nargs="*", type=int, help="numbers to show (0 = first; default: all)")
    ap.add_argument("--asr", help="transcript directory (default: as in transcribe.py)")
    args = ap.parse_args()
    docs = transcripts(args.asr or common.default_asr_dir(args.work_dir), args.movement, args.indexes)
    if not docs:
        sys.exit(f"no transcripts for {args.movement}; run transcribe.py first")
    for d in docs:
        print(f"## [{d['index']}] {d['head']}  ({d['t0']:.1f}-{d['t1']:.1f} s)")
        for seg in d["segments"]:
            loop = seg["compression_ratio"] > LOOP_RATIO
            print(f"SEG {seg['start']:.1f}-{seg['end']:.1f} cr={seg['compression_ratio']:.1f}{' LOOP' if loop else ''}")
            shown = seg["words"][:12] if loop else seg["words"]
            print("    " + " ".join(f"{w['word'].strip()}@{w['start']:.1f}" + ("?" if w["probability"] < LOW_PROBABILITY else "")
                                    for w in shown))


if __name__ == "__main__":
    main()
