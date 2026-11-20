# Recreate Messiah timing files, work.txt and work.pdf

## Ask

Recreate the *.timing.js files, work.txt and work.pdf under assets/Handel/Messiah

## Answer

Rebuilt `Chapter2.timing.js` … `Chapter9.timing.js` from the recording itself, then regenerated `work.txt` and
`work.pdf` with `scripts/make-work-txt.js` and `scripts/make-work-pdf.js`. `Chapter1.timing.js` (the Overture: two
already-timed tempo lines, no words) was left unchanged.

### Result

| File | Lines before (untimed) | Lines after (untimed) |
| --- | --- | --- |
| Chapter2 | 52 (0) | 93 (0) |
| Chapter3 | 57 (46) | 110 (0) |
| Chapter4 | 27 (22) | 51 (0) |
| Chapter5 | 11 (7) | 40 (0) |
| Chapter6 | 57 (44) | 110 (0) |
| Chapter7 | 33 (25) | 75 (0) |
| Chapter8 | 12 (7) | 26 (0) |
| Chapter9 | 44 (34) | 87 (0) |

- Every line now has a time. The lyrics follow what is actually sung, so a line appears again each time the singers
  return to it (da capo sections, chorus entries), in the style of `MessiahChinese`.
- All number headings, the English text and the 和合本 translations were kept. New lines exist only for text Handel
  sets that was missing ("I'll shake the heav'ns, the earth, the sea and the dry land, / all nations I'll shake;" in
  No. 4) or for splits/joins of existing lines (e.g. "they shoot out their lips," / "and shake their heads, saying:").
- Corrected heading/line times that were wrong in the old files, e.g. No. 44: "by man came also the resurrection"
  starts at 412.9 s, not 394.3 s (each Grave is sung twice); No. 28's heading moved to 810 s.

### Method

1. Transcribed every number (heading to heading) with OpenAI Whisper `medium` (local, Apple GPU), with word
   timestamps and the number's libretto as the prompt.
2. Aligned the transcribed words to libretto lines (repeats allowed) to draft each line's start.
3. Re-transcribed short clips wherever the draft was doubtful (`large-v3` for No. 25), and used loudness for No. 44,
   then reviewed every number by hand against the structure of Handel's score.

### Chapter 2 hand timing

Chapter 2 had been timed by hand, but checks against the recording showed several times were well off, e.g.
"comfort ye my people" (2nd) 24.7 s → 29.2 s; "Yet once, a little while" 570.5 s → 567.6 s; "and the desire of all
nations" 596.6 s → 605.8 s; "For He is like a refiner's fire" 687.2 s → 753.2 s (the Larghetto runs until ~750 s).
So Chapter 2 was rebuilt the same way as the others. The old version is in git history.

### Accuracy

Times are generally within about ±1 s for solo numbers; in polyphonic choruses a line marks where that text starts
in the leading voice and is less precise. Fine-tune any line with the app's **● Rec** flow (README:
"Flow: timing the lyrics").

Also updated the Messiah line in README.md's project structure. Nothing was committed.

---

## Ask

Save the scripts that you used to rebuild the timing files for Chapters 2–9 from the recording itself

## Answer

Saved them, cleaned up and tested, in `scripts/timing-from-audio/`, and documented the workflow in
`scripts/README.md` (section "timing-from-audio"):

| Script | Does |
| --- | --- |
| `transcribe.py` | Transcribes each number of a movement with Whisper, with word timestamps |
| `show_words.py` | Prints the transcripts word by word, with times and confidence |
| `propose.py` | Drafts the movement's timed lines from the transcripts, as a TSV to review |
| `probe.py` | Transcribes short clips, to check doubtful times |
| `loudness.py` | Prints the loudness second by second, for passages Whisper cannot hear |
| `timing_to_tsv.py` / `tsv_to_timing.py` | Convert between `*.timing.js` and the TSV |
| `common.py`, `whisper_model.py` | Shared code (incl. the workarounds that make Whisper run on the Apple GPU) |

Tests:
- All 9 Messiah timing files round-trip `timing_to_tsv.py` → `tsv_to_timing.py` unchanged apart from `saved`,
  also a file with untimed (`null`) lines; a TSV with a time going backwards is rejected.
- `transcribe.py` on Chapter 8 reproduces the earlier transcripts word for word (504 s of audio in 25 s);
  `show_words.py`, `propose.py`, `probe.py` and `loudness.py` reproduce the earlier outputs.

The scripts need Python 3 with openai-whisper (on this Mac: `/opt/homebrew/opt/python@3.13/bin/python3.13`; the
`python3` on PATH lacks it) and ffmpeg. Also added `__pycache__/` to `.gitignore`. Nothing was committed.

---

## Ask

commit

## Answer

Committed on a new branch `messiah-timing-from-audio` (not on `main`), in two commits:

1. The recreated Messiah timing files, `work.txt`, `work.pdf` and the README.md line.
2. The `scripts/timing-from-audio/` scripts, their section in `scripts/README.md`, `.gitignore`, and these notes.

Not pushed. To put them on `main`: `git checkout main && git merge --ff-only messiah-timing-from-audio`.
