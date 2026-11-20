#!/usr/bin/env python3
"""Print a *.timing.js file as a TSV: time, text, translation (see scripts/README.md).

The inverse of tsv_to_timing.py. A line without a time is written as "null".

Usage: python3 timing_to_tsv.py TIMING_JS > MOVEMENT.tsv
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for line in common.read_timing(sys.argv[1])["lines"]:
        time = "null" if line["time"] is None else line["time"]
        print(f"{time}\t{line['text']}\t{line.get('translation', '')}")


if __name__ == "__main__":
    main()
