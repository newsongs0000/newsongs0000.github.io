#!/usr/bin/env python3
"""Replace the lines of a *.timing.js file with the rows of a TSV (see scripts/README.md).

TSV rows: time<TAB>text<TAB>translation, as printed by propose.py or timing_to_tsv.py.
- time is in seconds, or "null" for an untimed line; the translation may be empty;
- anything after the third column (propose.py's #evidence) is ignored, and so are empty lines and
  lines starting with "#";
- the times must not go backwards.
The file's format, version, composer, work, movement and audio are kept; "saved" is set to now.

Usage: python3 tsv_to_timing.py TIMING_JS MOVEMENT.tsv
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def read_rows(path):
    rows = []
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        raw = raw.rstrip("\n")
        if not raw.strip() or raw.startswith("#"):
            continue
        cols = raw.split("\t")
        if len(cols) < 2 or not cols[1]:
            sys.exit(f"{path}:{n}: expected time<TAB>text[<TAB>translation]")
        if cols[0] == "null":
            time = None
        else:
            t = float(cols[0])
            time = int(t) if t == int(t) else t
        row = {"time": time, "text": cols[1]}
        if len(cols) > 2 and cols[2] and not cols[2].startswith("#"):
            row["translation"] = cols[2]
        rows.append((n, row))
    return rows


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    timing_js, tsv = sys.argv[1:]
    rows = read_rows(tsv)
    last = None
    for n, row in rows:
        if row["time"] is not None:
            if last is not None and row["time"] < last:
                sys.exit(f"{tsv}:{n}: time {row['time']} is before the previous time {last}")
            last = row["time"]
    common.write_timing(timing_js, common.read_timing(timing_js), [row for _, row in rows])
    print(f"wrote {timing_js}: {len(rows)} lines")


if __name__ == "__main__":
    main()
