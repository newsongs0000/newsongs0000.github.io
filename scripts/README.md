# Scripts

Helper scripts for maintaining the assets. Run everything from the repository root.

- `make-work-txt.js` and `make-work-pdf.js` need [Node.js](https://nodejs.org/) only (no `npm install`);
  `make-work-pdf.js` also needs Google Chrome or Microsoft Edge.
- The [timing-from-audio](#timing-from-audio) scripts, which time lyrics from a recording, need Python 3 with
  OpenAI Whisper, and ffmpeg.
- The [denoise-audio](denoise-audio/README.md) scripts, which find and remove high-frequency noise from MP3 files,
  need Python 3 with NumPy, and ffmpeg.
- The [denoise-audio-v2](denoise-audio-v2/README.md) scripts, which remove the wobbling whines and the hiss from
  `assets/Handel/MessiahChinese` (replacing the notch filters of denoise-audio for those files), need Python 3 with
  NumPy, and ffmpeg.

| Script | Output (next to each `work.js`) |
| --- | --- |
| [make-work-txt.js](make-work-txt.js) | `work.txt`: plain text, each lyric line followed by its translation |
| [make-work-pdf.js](make-work-pdf.js) | `work.pdf`: original language on the left, translation on the right |

Both read the same input (a work's `work.js` and the `*.timing.js` of its movements, loaded by
[lib/load-work.js](lib/load-work.js)), and both overwrite an existing output file. Rerun them after editing
`work.js` or any `*.timing.js`. The times in the timing files are ignored.

Without arguments a script processes every directory under `assets/` that contains a `work.js`; or pass one or
more work directories:

```sh
node scripts/make-work-txt.js
node scripts/make-work-txt.js assets/Handel/Messiah
node scripts/make-work-pdf.js assets/Handel/Messiah
node scripts/make-work-pdf.js assets/Mozart/Requiem assets/HuangAnlun/ChineseRequiem
```

## make-work-txt.js

Generates a plain-text version of a work. It combines the titles and movement headers from `work.js` with the
lyrics (and translations) from every movement's `*.timing.js` (named after the movement's `audio`:
`Chapter1.mp3` → `Chapter1.timing.js`). Only `lines[].text` and the optional `lines[].translation` are used.

### Output layout

Blocks are separated by a blank line:

```text
Messiah                                  <- title
弥赛亚                                    <- translated title

I Overture                               <- movement header: number + title,
Orchestra                                   voicing, then the same two lines
I 序曲                                      in the translation language
管弦乐

Sinfony (Overture) · Grave               <- one block per lyric line:
序曲 · 庄板                                 text, then its translation

Allegro moderato
中庸的快板
```

- The main language comes first, as in `work.js` (`language` / `translationLanguage`): English for Messiah and
  Mozart's Requiem, Chinese for the Chinese Requiem.
- Lines without a translation (Chinese Requiem chapters 2–8) appear as a block of their own.
- Line breaks inside a lyric are kept; leading and trailing spaces are trimmed.
- A movement's `subtitle` and `description` are not included.

### Notes

The output is called `work.txt`, not `lyrics.txt`, because `assets/HuangAnlun/ChineseRequiem/Lyrics.txt` is the source
lyrics and the two names collide on case-insensitive file systems (macOS, Windows).

## make-work-pdf.js

Generates `work.pdf`, an A4 PDF with two columns: the original language on the left (`language` in `work.js`) and
the translation on the right (`translationLanguage`, in blue). Each lyric line is one row, so a line and its
translation sit side by side; rows are never split across pages. The work title and every movement header
(number, title, voicing) are laid out the same way, and pages are numbered.

The PDF is rendered by headless Chrome from a temporary HTML page, so the CJK text uses the fonts of the machine
running the script. The browser is found automatically on macOS, Linux and Windows (Chrome, Edge or Chromium);
otherwise point to it:

```sh
CHROME="/path/to/chrome" node scripts/make-work-pdf.js
```

- Lines without a translation (Chinese Requiem chapters 2–8) leave the right column empty.
- A movement's `subtitle` and `description` are not included.
- A PDF is about 1 MB because the CJK font is embedded.

## timing-from-audio

Scripts in [timing-from-audio/](timing-from-audio/) that draft the times of a movement's lyric lines from its
recording, so that you review a draft instead of recording every line with **● Rec**. They were used to rebuild
`assets/Handel/Messiah/Chapter2…9.timing.js`. Whisper hears sung English well enough in recitatives and airs
(times within about ±1 s); in polyphonic choruses the draft needs more checking.

| Script | Does |
| --- | --- |
| [transcribe.py](timing-from-audio/transcribe.py) | Transcribes each number of a movement with Whisper, with word timestamps |
| [show_words.py](timing-from-audio/show_words.py) | Prints the transcripts word by word, with times and confidence |
| [propose.py](timing-from-audio/propose.py) | Drafts the movement's timed lines from the transcripts, as a TSV to review |
| [probe.py](timing-from-audio/probe.py) | Transcribes short clips, to check doubtful times |
| [loudness.py](timing-from-audio/loudness.py) | Prints the loudness second by second, for passages Whisper cannot hear |
| [timing_to_tsv.py](timing-from-audio/timing_to_tsv.py) | Prints a `*.timing.js` as a TSV |
| [tsv_to_timing.py](timing-from-audio/tsv_to_timing.py) | Writes a reviewed TSV into a `*.timing.js` |

[common.py](timing-from-audio/common.py) and [whisper_model.py](timing-from-audio/whisper_model.py) are shared
code. Each script prints its usage with `-h` (or with no arguments, for the TSV converters).

### Requirements

- [ffmpeg](https://ffmpeg.org/) (`brew install ffmpeg`).
- Python 3 with [OpenAI Whisper](https://github.com/openai/whisper): `brew install openai-whisper` or
  `pip install openai-whisper`. Run the scripts with the Python that has it; with Homebrew's formula that is
  `$(brew --prefix)/opt/python@3.13/bin/python3.13`, which may not be the `python3` on your `PATH`. The examples
  below write `python3`.
- A model is downloaded on first use to `~/.cache/whisper`: `medium` (default, 1.5 GB) or `large-v3` (3 GB).
- On an Apple Silicon Mac the GPU (MPS) is used, with workarounds described in `whisper_model.py`. On an M4 Pro,
  `medium` transcribes about 12× faster than real time, so Messiah Chapters 2–9 (2.3 hours) take about 12 minutes.
  `large-v3` is much slower and is best kept for short clips.

### TSV format

`propose.py`, `timing_to_tsv.py` and `tsv_to_timing.py` share one format, one lyric line per row:

```text
time<TAB>text<TAB>translation<TAB>#evidence
```

- `time` is in seconds, or `null` for an untimed line. The translation may be empty.
- `tsv_to_timing.py` ignores everything after the translation, empty lines and lines starting with `#`, and stops
  if a time is earlier than the one before it.

### Workflow

The example is one movement, `assets/Handel/Messiah/Chapter5`.

1. **Number boundaries.** The `*.timing.js` file must already have the movement's lyric lines, and a timed heading
   line (starting with `No.` or `Nos.`) at the start of each number. Each number is transcribed separately, with
   its own lines as the prompt. A movement without headings is transcribed as one piece, which works less well. To
   find the boundaries, look for silences:

   ```sh
   ffmpeg -i assets/Handel/Messiah/Chapter5.mp3 -af silencedetect=noise=-38dB:d=0.8 -f null - 2>&1 | grep silence_end
   ```

2. **Transcribe.** Transcripts are saved as JSON, by default in `onepagemp3-asr/<Artist>-<Work>/` under the
   system temp directory (`--asr DIR` to change). Numbers already transcribed are skipped. Leave out the movement
   names to transcribe every movement of the work.

   ```sh
   python3 scripts/timing-from-audio/transcribe.py assets/Handel/Messiah Chapter5
   ```

3. **Draft.** For each number, every transcribed word is assigned to a lyric line, allowing the text to go back
   to earlier lines (repeats, da capo). Each run of words on one line becomes a row.

   ```sh
   python3 scripts/timing-from-audio/propose.py assets/Handel/Messiah Chapter5 > Chapter5.tsv
   ```

4. **Review the TSV.** Go through it number by number with the transcript beside it:

   ```sh
   python3 scripts/timing-from-audio/show_words.py assets/Handel/Messiah Chapter5      # all numbers
   python3 scripts/timing-from-audio/show_words.py assets/Handel/Messiah Chapter5 1    # the second number only
   ```

   - **Split repeats.** A line sung several times in a row is drafted as one row. Add a row for each repeat you
     want shown, at the time of its first word.
   - **Distrust these times:** words marked `?` (low confidence); words in `LOOP` segments, where Whisper repeats
     itself (common in melismas); and the first word of a segment that starts exactly where the previous one ended.
   - **Watch for invented words.** Because the lyrics are the prompt, Whisper sometimes "hears" them in
     instrumental passages. Check against the form of the music, e.g. that a ritornello or a da capo falls where
     it should.
   - **Check doubtful spots with short clips,** with and without a prompt. A clip gives tighter times than a whole
     number. Use `--model large-v3` for a passage `medium` cannot hear (Messiah No. 25):

     ```sh
     python3 scripts/timing-from-audio/probe.py assets/Handel/Messiah/Chapter5.mp3 "440-480:He gave His back to the smiters" "520-560"
     ```

   - **Use loudness where Whisper hears nothing,** e.g. soft a cappella passages between loud orchestral ones
     (Messiah No. 44). A drop to about -55 dB or lower marks a rest:

     ```sh
     python3 scripts/timing-from-audio/loudness.py assets/Handel/Messiah/Chapter8.mp3 376 503
     ```

   - **Add missing text.** For words that are sung but missing from the lyric lines, add rows with a translation.
     The draft takes translations from the existing lines.

5. **Write and check.** Write the TSV into the timing file, check it in the app (Auto mode; clicking a line jumps
   to its time), fine-tune single lines with **● Rec**, then regenerate `work.txt` and `work.pdf`:

   ```sh
   python3 scripts/timing-from-audio/tsv_to_timing.py assets/Handel/Messiah/Chapter5.timing.js Chapter5.tsv
   node scripts/make-work-txt.js assets/Handel/Messiah
   node scripts/make-work-pdf.js assets/Handel/Messiah
   ```

To edit an existing timing file the same way, start from `timing_to_tsv.py` instead of `propose.py`:

```sh
python3 scripts/timing-from-audio/timing_to_tsv.py assets/Handel/Messiah/Chapter5.timing.js > Chapter5.tsv
```
