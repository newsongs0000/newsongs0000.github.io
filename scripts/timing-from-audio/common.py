"""Shared helpers for the timing-from-audio scripts (see scripts/README.md).

Reading and writing *.timing.js files, splitting a movement into numbers at its heading lines,
decoding audio with ffmpeg, and normalising lyric text for matching.
"""
import datetime
import json
import os
import re
import subprocess
import tempfile

import numpy as np

# A heading line starts a new number, e.g. "No. 5 · Air (contralto) [Malachi 3:2]" or "Nos. 8–9 · …".
HEADING_RE = re.compile(r"^Nos?\. ")
# A leading voice label such as "(Chorus) " or "(Soprano) " is not sung.
VOICE_LABEL_RE = re.compile(r"^\((\w+)\)\s*")
SAMPLE_RATE = 16000  # what Whisper expects


def timing_path(work_dir, movement):
    """movement is the audio's stem, e.g. "Chapter3"."""
    return os.path.join(work_dir, f"{movement}.timing.js")


def audio_path(work_dir, movement):
    return os.path.join(work_dir, f"{movement}.mp3")


def default_asr_dir(work_dir):
    """Where transcripts go unless --asr is given: outside the repository, one folder per work."""
    work = os.path.abspath(work_dir).rstrip(os.sep)
    name = f"{os.path.basename(os.path.dirname(work))}-{os.path.basename(work)}"
    return os.path.join(tempfile.gettempdir(), "onepagemp3-asr", name)


def read_timing(path):
    """Return the object passed to onePageMp3Timing(...) in a *.timing.js file."""
    src = open(path, encoding="utf-8").read()
    return json.loads(src[src.index("(") + 1: src.rindex(")")])


def write_timing(path, header, rows):
    """Write a *.timing.js file in the format the app saves.

    header: the old file's object (its format/version/composer/work/movement/audio are kept).
    rows:   [{"time": float|None, "text": str, "translation": str (optional)}, ...]
    """
    saved = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    out = "onePageMp3Timing({\n"
    for key in ("format", "version", "composer", "work", "movement", "audio"):
        out += f"  {json.dumps(key)}: {json.dumps(header[key], ensure_ascii=False)},\n"
    out += f'  "saved": "{saved}",\n  "lines": [\n'
    out += ",\n".join("    " + json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows)
    out += "\n  ]\n});\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)


def split_numbers(data):
    """Split a timing file's lines into numbers at heading lines.

    Returns [{"time": heading time, "head": heading text, "lines": [lyric texts]}]. Lines before the
    first heading (or all lines, when there is no heading) form a number with an empty heading at 0 s.
    """
    numbers = []
    for line in data["lines"]:
        if HEADING_RE.match(line["text"]):
            if line["time"] is None:
                raise ValueError(f"heading has no time: {line['text']}")
            numbers.append({"time": line["time"], "head": line["text"], "lines": []})
        else:
            if not numbers:
                numbers.append({"time": 0, "head": "", "lines": []})
            numbers[-1]["lines"].append(line["text"])
    return numbers


def duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out)


def decode(path, start=None, end=None, rate=SAMPLE_RATE):
    """Decode [start, end] seconds of an audio file to mono float32 samples."""
    cmd = ["ffmpeg", "-loglevel", "error"]
    if start is not None:
        cmd += ["-ss", str(start)]
    if end is not None:
        cmd += ["-to", str(end)]
    cmd += ["-i", path, "-ac", "1", "-ar", str(rate), "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def norm(word):
    """Lower-case a word and drop punctuation; expand the libretto's elisions (ev'ry, heav'ns, pardon'd)."""
    w = word.lower().replace("’", "'")
    w = w.replace("ev'ry", "every").replace("heav'ns", "heavens").replace("ev'n", "even")
    w = re.sub(r"'d\b", "ed", w)
    return re.sub(r"[^a-z]", "", w)


def stem(word):
    for suffix in ("eth", "ed", "es", "s", "ing"):
        if len(word) > 4 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def words(text):
    """The normalised words of a lyric line, without its voice label."""
    return [w for w in (norm(x) for x in VOICE_LABEL_RE.sub("", text).split()) if w]


def prompt_text(lines):
    """A number's lyrics as one Whisper prompt, each distinct line once."""
    return " ".join(VOICE_LABEL_RE.sub("", line) for line in dict.fromkeys(lines))
