# denoise-audio

Scripts to find and remove high-frequency noise in the MP3 files under `assets/`, with ffmpeg and NumPy. Run
everything from the repository root. Requirements: [ffmpeg](https://ffmpeg.org/) (with libmp3lame) and Python 3 with
NumPy.

| Script | Does |
| --- | --- |
| [analyze_noise.py](analyze_noise.py) | Band levels (median and quietest frames) and narrow peaks above 4 kHz: tells broadband hiss from a tone |
| [find_tones.py](find_tones.py) | Finds steady tones and prints where each one is present, per file |
| [spectrogram.sh](spectrogram.sh) | Renders a spectrogram PNG of a time range, to look at the noise |
| [remove_tones.py](remove_tones.py) | Removes tones with cascaded notch filters and re-encodes (keeps tags and length) |
| [verify_denoise.py](verify_denoise.py) | Compares original and result: length, alignment, clipping, tags, band levels, tone levels |

## What kind of noise is it?

Two kinds have been found in the assets; they need different treatment.

- **Broadband hiss** in LP rips (`Handel/Messiah`, `Mozart/Requiem`): a flat shelf in the silent gaps from about
  4 kHz up. Removed with ffmpeg's FFT denoiser, `afftdn=nr=18:nf=-48:nt=w:tn=1`, compensating its delay with
  `atrim=start_sample=<25 ms in samples>` (1102 at 44.1 kHz, 1200 at 48 kHz). Not scripted here.
- **Steady tones** ("whines") in `Handel/MessiahChinese`, taken from a Bilibili video: two lines at about 6.44 kHz and
  15.61 kHz, in every chapter, present for a third to all of the chapter (the rest of the source is clean),
  at −60 to −85 dBFS per bin, 15–40 dB above the spectrum around them. There is no hiss shelf in these files. Phone speakers
  and earphones reproduce 6 and 15 kHz well, laptop speakers much less. A denoiser would dull the music; notch
  filters remove just the lines.

Run `analyze_noise.py` first. A flat shelf in the quietest frames means hiss; "tonal peaks" in its output and
tracks in `find_tones.py` mean tones. Look at a `spectrogram.sh` picture when in doubt: tones are sharp horizontal
lines, hiss is an even haze.

## Removing tones

```sh
# 1. find the tones (tracks longer than 30 s; --min-hz skips the bass and mids, where sustained notes show up)
python3 scripts/denoise-audio/find_tones.py --min-hz 4000 assets/Handel/MessiahChinese/Chapter*.mp3

# 2. process into a scratch directory, leaving the originals alone
python3 scripts/denoise-audio/remove_tones.py --out-dir /tmp/denoised assets/Handel/MessiahChinese/Chapter*.mp3

# 3. verify, then copy the results over the originals (git keeps the old files)
python3 scripts/denoise-audio/verify_denoise.py assets/Handel/MessiahChinese /tmp/denoised
cp /tmp/denoised/*.mp3 assets/Handel/MessiahChinese/
```

`remove_tones.py` defaults to the two tones above: 6440 Hz (4 cascaded `bandreject` notches, 200 Hz wide) and 15613 Hz
(4 notches, 400 Hz wide). For other tones pass `--tone HZ[:WIDTH[:STAGES]]`, once per tone; `--print-filter` shows the
ffmpeg filter. The tones drift about ±30 Hz between and within chapters, so the notches are wide: four cascaded
notches cut a tone by 30 dB at ±40 Hz from the centre and by 50 dB or more within ±20 Hz, and take only about 5 dB
off the music ±150 Hz away. Check a new tone with the verify script's `--tone`.

Design notes:

- The filters are IIR and add no delay, so the file keeps its exact length and the `*.timing.js` files stay valid.
- Output is LAME VBR `-q:a 2` (about 165 kbps for these files; originals 161 kbps), tags copied (`-map_metadata 0`).
  ffmpeg writes the Xing header with the encoder delay, as it did for the originals.
- Re-encoding can push a peak that was just under full scale over it (Chapter 2: 0.980 → 1.014). The script then
  encodes again with a gain reduction of just enough (0.17 dB there).
- `verify_denoise.py` exits with 1 when a check fails. A tone counts as present in a 10 s window when its level is
  more than 10 dB above the spectrum 300–600 Hz away and above −95 dBFS per bin.
- Everything is decoded in memory through ffmpeg pipes; no WAV files are written.
