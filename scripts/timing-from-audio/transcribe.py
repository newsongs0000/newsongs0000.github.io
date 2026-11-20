#!/usr/bin/env python3
"""Transcribe each number of a movement with Whisper, with word timestamps (see scripts/README.md).

A movement is split into numbers at its heading lines ("No. …"), using the heading times already in its
*.timing.js file. Each number is transcribed with its own lyrics as the prompt, and saved as
<asr dir>/<movement>_<index>.json with times relative to the start of the MP3. Numbers that already have
a transcript are skipped, so an interrupted run can be restarted.

Usage: python3 transcribe.py WORK_DIR [MOVEMENT ...] [--asr DIR] [--model medium] [--device mps] [--beam N]
  MOVEMENT is the audio's stem, e.g. Chapter3. Default: every *.timing.js in WORK_DIR.
"""
import argparse
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import whisper_model  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("work_dir")
    ap.add_argument("movements", nargs="*")
    ap.add_argument("--asr", help="output directory (default: a folder per work in the system temp directory)")
    ap.add_argument("--model", default="medium", help="Whisper model (default: medium)")
    ap.add_argument("--device", help="mps, cuda or cpu (default: mps or cuda if available)")
    ap.add_argument("--beam", type=int, help="beam size (default: greedy decoding)")
    args = ap.parse_args()

    movements = args.movements or sorted(
        os.path.basename(p)[: -len(".timing.js")] for p in glob.glob(os.path.join(args.work_dir, "*.timing.js")))
    asr_dir = args.asr or common.default_asr_dir(args.work_dir)
    os.makedirs(asr_dir, exist_ok=True)
    print(f"transcripts: {asr_dir}", flush=True)

    model = whisper_model.load(args.model, args.device)
    for movement in movements:
        mp3 = common.audio_path(args.work_dir, movement)
        numbers = common.split_numbers(common.read_timing(common.timing_path(args.work_dir, movement)))
        total = common.duration(mp3)
        for k, number in enumerate(numbers):
            out = os.path.join(asr_dir, f"{movement}_{k}.json")
            if os.path.exists(out):
                continue
            # half a second of overlap with the neighbours, in case a heading time is a little late
            t0 = max(0.0, number["time"] - 0.5)
            t1 = numbers[k + 1]["time"] + 0.5 if k + 1 < len(numbers) else total
            started = time.time()
            result = whisper_model.transcribe(
                model, common.decode(mp3, t0, t1), common.prompt_text(number["lines"]), args.beam)
            for seg in result["segments"]:
                seg["start"] += t0
                seg["end"] += t0
                for w in seg.get("words", []):
                    w["start"] += t0
                    w["end"] += t0
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"movement": movement, "index": k, "head": number["head"], "time": number["time"],
                           "t0": t0, "t1": t1,
                           "lines": number["lines"], "segments": result["segments"]}, f, ensure_ascii=False)
            print(f"{movement}_{k} {number['head'][:50]}: {t1 - t0:.0f} s of audio in "
                  f"{time.time() - started:.0f} s", flush=True)


if __name__ == "__main__":
    main()
