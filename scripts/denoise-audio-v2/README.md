# denoise-audio-v2

Scripts that remove the whines and reduce the hiss in `assets/Handel/MessiahChinese/*.mp3`. They replace the
notch filters of [../denoise-audio](../denoise-audio/README.md) for these files. Run everything from the repository
root.

Requirements: [ffmpeg](https://ffmpeg.org/) with libmp3lame, and Python 3 with NumPy (`spectrogram.py` also needs
matplotlib).

| Script | Does |
| --- | --- |
| [clean.py](clean.py) | The whole job: decode, remove the whines, reduce the hiss, encode once (same length, same tags) |
| [whine.py](whine.py) | Whine removal by tracking and subtraction; run alone it prints what it finds in a file |
| [dehiss.py](dehiss.py) | Hiss reduction (STFT noise suppressor); run alone it prints the estimated hiss level per minute |
| [verify.py](verify.py) | Compares originals with results: length, alignment, peaks, tags, remaining whine, hiss and music levels |
| [spectrogram.py](spectrogram.py) | Zoomed spectrogram PNG of a time and frequency range, with a free FFT size |
| [common.py](common.py) | Shared code: ffmpeg decode/encode, exact complex baseband of a band, filters |

## What the noise is

Measured on the original files (the Bilibili download, commit `4a0bb5e`):

- **Two whines that wobble.** One sits at about 6420–6460 Hz, the other at 15590–15630 Hz; the exact centre
  differs per chapter. Their frequency swings about ±22 Hz twice a second: a smooth FM with a period of 0.500 s.
  Both whines follow the same FM, the 15.6 kHz one mirrored. Each also carries sidebands from mains hum,
  49.9 Hz apart (±50, ±100 … ±300 Hz). They are about −48 dBFS, 30–45 dB above the music around them, and
  mostly in the left channel (about 15 dB weaker in the right). They appear in long stretches of every chapter
  (for example Chapter 2, 0–392 s), and stop and start with a number. In some numbers they are 20–30 dB weaker
  and hidden under the music most of the time.
- **Hiss.** A flat (white) floor from about 1.5 kHz up to the codec's cut-off near 17 kHz. In the pauses between
  numbers it is about −95 dBFS per bin of a 4096-point FFT, or about −67 dBFS rms. The left and right channels
  are uncorrelated. It is masked under music and heard in soft passages and pauses as a steady "shhh".

Why the first attempt left noise behind: notch filters at fixed frequencies must be wide to cover the wobble, and
the centre they assume can be 20 Hz off (Chapter 9's whine is at 6424 Hz, not 6440). They also cut only the
±50 Hz sidebands. `verify.py` on those files shows sidebands still 8–15 dB above their surroundings: the remaining
"high-pitched noise". The notches also cut a hole in the music under them (about 120 Hz wide at 6.4 kHz and
more at 15.6 kHz, in every chapter, whether the whine is there or not), and they leave the hiss untouched.

Two things in the originals are deliberately left alone. Faint wobbling lines at 16.05–16.15 kHz sit at about
−100 dBFS; they do not share either whine's FM, so they are probably codec artifacts. The rise below 300 Hz in the
pauses is room tone and hum, not hiss.

## How it is removed

**Whines** ([whine.py](whine.py), details in its docstring). Each family's band (centre ±400 Hz) is taken to
complex baseband, and its carrier is tracked frame by frame.

- **Presence:** the track repeats every 0.5 s where the whine is present, and music never does that.
- **Quiet whine:** in some numbers the whine is 20–30 dB weaker (for example Chapter 3, 300–405 s, and
  Chapter 9, 330–470 s), and music outshines it inside the tracker's search range. A second pass searches only
  the range the carrier covered in the first pass, and scores over 8 s instead of 2 s. A singer's vibrato on a
  harmonic near the whine scores up to 0.5 there, so the threshold is 0.55.
- **Guide:** in each present stretch, the clearest band (usually the left channel at 6.4 kHz) supplies the FM
  for all four bands.
- **Demodulation:** after demodulating with the refined carrier phase, the carrier and all its sidebands become
  fixed spectral lines.
- **Subtraction:** each line is extracted with a ±3 Hz low-pass, put back on its moving trajectory, and
  subtracted.

Only a few Hz around each line's path is touched. No notch hole is left, and no delay is added.

**Hiss** ([dehiss.py](dehiss.py)):

- **Analysis:** STFT with 2048-point Hann windows and 75 % overlap; the output equals the input exactly at unity
  gain.
- **Noise estimate:** per 1/6-octave band, by minimum statistics over 6 s, ignoring digital silence. It is capped
  by a white-noise model and by the file's own low (10th percentile) level +6 dB. Without these caps, long dense
  choruses would be taken for noise.
- **Gain:** Wiener gain with a decision-directed SNR estimate, which avoids twinkling "musical noise". Left and
  right share one gain, so the stereo image does not wander.
- **Limit:** at most 18 dB of reduction above 2 kHz, easing to 4 dB below 250 Hz.

## Workflow

Start from the **original** files, not from the notch-filtered ones: those already lost the music beside the
notches, and every MP3 generation loses a little more.

```sh
# 1. the originals, from git, into a scratch directory
mkdir -p /tmp/messiah-orig
for i in 1 2 3 4 5 6 7 8 9; do
  git show 4a0bb5e:assets/Handel/MessiahChinese/Chapter$i.mp3 > /tmp/messiah-orig/Chapter$i.mp3
done

# 2. clean (about 1-1.5 min per 20-minute chapter on an M4 Pro, up to 4.5 GB of memory for the longest chapter;
#    run at most two in parallel on a 24 GB machine)
python3 scripts/denoise-audio-v2/clean.py --out-dir /tmp/messiah-clean /tmp/messiah-orig/Chapter*.mp3

# 3. verify (exits with 1 if a check fails), then copy over the assets (git keeps the old files)
python3 scripts/denoise-audio-v2/verify.py /tmp/messiah-orig /tmp/messiah-clean
cp /tmp/messiah-clean/*.mp3 assets/Handel/MessiahChinese/
```

Options of `clean.py`: `--reduction DB` (hiss, default 18; 0 skips it), `--no-whine`, `--whine HZ` (repeatable;
default 6440 and 15600, each searched ±90 Hz), `--quality` (LAME VBR, default 2).

To look at a result, for example the 6.4 kHz whine before and after:

```sh
python3 scripts/denoise-audio-v2/spectrogram.py /tmp/w.png 100 110 6100 6800 \
  /tmp/messiah-orig/Chapter2.mp3 assets/Handel/MessiahChinese/Chapter2.mp3
```

## What verify.py checks

- The decoded length is identical to the sample, so the `*.timing.js` files stay valid, and the alignment lag is 0.
- No samples reach full scale, and the tags are unchanged.
- The whine's carrier and sidebands (offsets 0, ±1 … ±6 × 49.9 Hz) in the result are at most 3 dB above their
  surroundings ±25 Hz, measured in the long-term spectrum after demodulating with the phase tracked in the
  original.
- Levels per band in the quietest 5 % of frames (where the hiss reduction shows), in the middle frames and in
  the loudest 10 %. On the loudest frames' strong components (bins at least 20 dB above the quiet level, i.e.
  music), every band up to 15.2 kHz except the two whine bands changes by at most 0.5 dB.

Results for the files now in `assets/Handel/MessiahChinese` (all checks pass):

| Chapter | Whine present | Strongest whine line, original → result | Hiss 8–12 kHz, quiet frames | Music change |
| --- | --- | --- | --- | --- |
| 1 | 222 s | +38 → −2.3 dB | −10.0 dB | ≤ 0.38 dB |
| 2 | 393 s | +43 → −2.3 dB | −2.5 dB | ≤ 0.30 dB |
| 3 | 694 s | +41 → −2.2 dB | −4.7 dB | ≤ 0.32 dB |
| 4 | 682 s | +38 → −0.3 dB | −1.1 dB | ≤ 0.08 dB |
| 5 | 275 s | +44 → −0.8 dB | −12.5 dB | ≤ 0.33 dB |
| 6 | 412 s | +40 → −3.2 dB | −0.8 dB | ≤ 0.23 dB |
| 7 | 515 s | +40 → −2.5 dB | −1.7 dB | ≤ 0.27 dB |
| 8 | 357 s | +40 → −2.7 dB | −3.8 dB | ≤ 0.38 dB |
| 9 | 510 s | +39 → −2.7 dB | −1.1 dB | ≤ 0.29 dB |

The quiet-frame column is the quietest 5 % of frames, which are mostly soft music, so it understates the
effect. In the pauses themselves the hiss drops by 16–18 dB from 2 to 12 kHz, and by 10–13 dB above that
(measured in Chapter 2). For comparison, `verify.py` on the notch-filtered files these replace still finds
the ±100 to ±250 Hz sidebands 8–15 dB above their surroundings.

## Design notes

- Whole-file FFTs are zero-padded to a length with no prime factor above 7. For other lengths NumPy falls back to
  a Bluestein FFT, which needs several GB of memory and is much slower.
- The output has exactly the input's sample count. It is encoded once with LAME VBR `-q:a 2`, with the input's
  tags and cover art. If encoding pushes a peak over full scale, the file is encoded again with just enough gain
  reduction (0.1–0.2 dB).
- Everything is decoded in memory through ffmpeg pipes; no WAV files are written.
- Hiss reduction can be gentler: `--reduction 12` keeps more air in soft high strings, at the price of more hiss
  in the pauses.
