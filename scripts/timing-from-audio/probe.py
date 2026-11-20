#!/usr/bin/env python3
"""Transcribe short clips of an MP3 to check doubtful times (see scripts/README.md).

A clip of 10-40 s gives tighter word times than a whole number, and an optional prompt (the words you
expect) helps Whisper hear them. Words are printed with times from the start of the MP3; "?" marks low
confidence. A prompt can also make Whisper "hear" words that are not there, so try with and without.

Usage: python3 probe.py MP3 START-END[:PROMPT] ... [--model medium] [--device mps]
  e.g. python3 probe.py assets/Handel/Messiah/Chapter2.mp3 "20-36:Comfort ye my people" "565-575"
  --model large-v3 hears more, but is much slower.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import whisper_model  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mp3")
    ap.add_argument("clips", nargs="+", metavar="START-END[:PROMPT]")
    ap.add_argument("--model", default="medium")
    ap.add_argument("--device")
    args = ap.parse_args()

    model = whisper_model.load(args.model, args.device)
    for clip in args.clips:
        span, _, prompt = clip.partition(":")
        t0, t1 = (float(x) for x in span.split("-"))
        result = whisper_model.transcribe(model, common.decode(args.mp3, t0, t1), prompt)
        ws = [w for seg in result["segments"] for w in seg["words"]]
        print(f"[{t0:g}-{t1:g}] " + " ".join(
            f"{w['word'].strip()}@{w['start'] + t0:.1f}" + ("?" if w["probability"] < 0.3 else "") for w in ws))


if __name__ == "__main__":
    main()
