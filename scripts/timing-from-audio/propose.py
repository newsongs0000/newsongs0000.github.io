#!/usr/bin/env python3
"""Draft a movement's timed lyrics from its transcripts, as a TSV for review (see scripts/README.md).

For each number, every transcribed word is assigned to one of the number's lyric lines by a Viterbi
search: a word scores for a line that contains it (rarer words score more), staying on a line is free,
moving to the next line is cheap, and going back to an earlier line (a repeat) or skipping ahead costs
more. Each run of words on one line becomes a row, timed at the run's first reliable word.

Output (stdout), one row per line, tab-separated:  time  text  translation  #evidence
  - heading rows keep their time from the *.timing.js file;
  - the evidence is the run's words ("?" = unreliable time); "~N" means the first N words were unreliable
    and the time was estimated back from a later word; "?" alone means no word in the run was reliable.
Review and edit it (show_words.py, probe.py, loudness.py help), then write it with tsv_to_timing.py.

Usage: python3 propose.py WORK_DIR MOVEMENT [--asr DIR] > MOVEMENT.tsv
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from show_words import LOOP_RATIO, LOW_PROBABILITY, transcripts  # noqa: E402

STAY, NEXT, BACK, SKIP, SKIP_EACH, MISS = 0, -2.5, -5, -6, -1.5, -1.0
SECONDS_PER_WORD = 0.45  # to estimate a run's start from a later word


def usable_words(doc):
    """The transcript's words, each flagged reliable or not; a loop is cut where its times collapse."""
    out, prev_end = [], None
    for seg in doc["segments"]:
        ws, loop = seg["words"], seg["compression_ratio"] > LOOP_RATIO
        for i, w in enumerate(ws):
            n = common.norm(w["word"])
            if not n:
                continue
            if loop and i > 0 and abs(w["start"] - ws[i - 1]["start"]) < 0.05:
                break
            reliable = w["probability"] >= LOW_PROBABILITY
            # the first word of a segment that starts where the previous one ended is pinned to the boundary
            if i == 0 and prev_end is not None and abs(w["start"] - prev_end) < 0.05:
                reliable = False
            # several words at the same instant: the alignment collapsed
            if i + 1 < len(ws) and abs(ws[i + 1]["start"] - w["start"]) < 0.05:
                reliable = False
            out.append({"stem": common.stem(n), "t": w["start"], "p": w["probability"],
                        "reliable": reliable, "raw": w["word"].strip()})
        prev_end = seg["end"]
    return out


def align(lines, ws):
    """Viterbi: the most likely line index for every word."""
    sets = [set(common.stem(w) for w in common.words(t)) for t in lines]
    n = len(sets)
    df = {}
    for s in sets:
        for w in s:
            df[w] = df.get(w, 0) + 1

    def emit(w, j):
        if w["stem"] not in sets[j]:
            return MISS
        weight = 0.4 + 0.6 * min(1, w["p"] / 0.5)
        return weight * math.log(1 + 3 * (n + 1) / (df[w["stem"]] + 0.5))

    def move(k, j):
        if k == j:
            return STAY
        if j == k + 1:
            return NEXT
        return BACK if j < k else SKIP + SKIP_EACH * (j - k - 1)

    score = [emit(ws[0], j) - (0 if j == 0 else 2) for j in range(n)]
    back = []
    for w in ws[1:]:
        prev, score, ptr = score, [], []
        for j in range(n):
            k = max(range(n), key=lambda k: prev[k] + move(k, j))
            score.append(prev[k] + move(k, j) + emit(w, j))
            ptr.append(k)
        back.append(ptr)
    j = max(range(n), key=lambda k: score[k])
    path = [j]
    for ptr in reversed(back):
        j = ptr[j]
        path.append(j)
    return path[::-1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("work_dir")
    ap.add_argument("movement")
    ap.add_argument("--asr", help="transcript directory (default: as in transcribe.py)")
    args = ap.parse_args()

    data = common.read_timing(common.timing_path(args.work_dir, args.movement))
    translation = {}
    for line in data["lines"]:
        translation.setdefault(line["text"], line.get("translation", ""))
    docs = transcripts(args.asr or common.default_asr_dir(args.work_dir), args.movement)
    if not docs:
        sys.exit(f"no transcripts for {args.movement}; run transcribe.py first")

    for doc in docs:
        if doc["head"]:
            print(f"{doc['time']}\t{doc['head']}\t{translation.get(doc['head'], '')}\t#heading")
        lines = list(dict.fromkeys(doc["lines"]))  # each distinct line once; repeats come from the alignment
        ws = usable_words(doc)
        if not lines or not ws:
            continue
        runs = []
        for w, j in zip(ws, align(lines, ws)):
            if runs and runs[-1][0] == j:
                runs[-1][1].append(w)
            else:
                runs.append((j, [w]))
        for j, run in runs:
            k = next((i for i, w in enumerate(run) if w["reliable"]), None)
            if k is None:
                t, flag = run[0]["t"], "?"
            else:
                t, flag = run[k]["t"] - SECONDS_PER_WORD * k, (f"~{k}" if k else "")
            evidence = " ".join(w["raw"] + ("" if w["reliable"] else "?") for w in run)
            print(f"{t:.1f}\t{lines[j]}\t{translation.get(lines[j], '')}\t#{flag} {evidence[:120]}")


if __name__ == "__main__":
    main()
