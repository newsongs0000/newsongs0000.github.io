# Remove the remaining high-pitched noise from Messiah (Chinese) — second attempt

## Ask

> I used other scripts to remove noise from the MP3 files under assets/Handel/MessiahChinese but there are still
> some high pitch noises, try agian and do your best to remove all noises and save your scripts in a separate
> directory

## Answer

New scripts are in `scripts/denoise-audio-v2/` (see its README). All nine `assets/Handel/MessiahChinese/Chapter*.mp3`
were re-made from the **original** files (git commit `4a0bb5e`), not from the notch-filtered ones, and replaced.

### What was still there

1. **The whines wobble, and they have sidebands.** Both tones (about 6.42–6.46 kHz and 15.59–15.63 kHz; the
   exact centre differs per chapter) swing ±22 Hz twice a second (FM, period 0.500 s). The 15.6 kHz one mirrors
   the 6.4 kHz one. Each carries sidebands from mains hum every 49.9 Hz (±50 … ±300 Hz). The previous fixed
   notches (6440 / 15613 Hz) were sometimes 20 Hz off-centre (Chapter 9: 6424 Hz) and only reached the ±50 Hz
   sidebands. The ±100–250 Hz sidebands were still 8–15 dB above their surroundings: the remaining high-pitched
   noise.
2. **Quieter whine stretches.** In some numbers the whine is 20–30 dB weaker and partly hidden under the music
   (Chapter 3, 300–405 s; Chapter 9, 330–470 s).
3. **Hiss.** A white noise floor from 1.5 kHz up to 17 kHz, about −67 dBFS rms in the pauses (−95 dBFS per bin of
   a 4096-point FFT). The earlier README said there was no hiss in these files.

### What the new scripts do

- `whine.py`:
  - tracks the wobbling carrier frame by frame;
  - finds where the whine is present: the FM repeats every 0.5 s and music doesn't (a second, narrower pass,
    scored over 8 s windows, finds the quiet stretches);
  - drives all four bands (two families × two channels) from the clearest one's FM;
  - demodulates, so that the carrier and every sideband become fixed lines;
  - subtracts each line with a ±3 Hz extraction.
  
  No notch hole is left.
- `dehiss.py`: an STFT noise suppressor that tracks the noise floor, capped so dense music isn't taken for noise.
  It uses decision-directed Wiener gains and one gain for both channels. It cuts at most 18 dB above 2 kHz,
  easing to 4 dB below 250 Hz.
- `clean.py`: decode → whine → hiss → encode once. The length is the same to the sample, so the timing files
  stay valid, and the tags are kept.
- `verify.py`: checks length, alignment, peaks, tags, the remaining whine lines (limit 3 dB above their
  surroundings) and the change in strong music components (limit 0.5 dB).
- `spectrogram.py`: zoomed spectrogram pictures.

### Results (verify.py: all checks pass)

| Chapter | Whine present | Strongest whine line, original → result | Music change |
| --- | --- | --- | --- |
| 1 | 222 s | +38 → −2.3 dB | ≤ 0.38 dB |
| 2 | 393 s | +43 → −2.3 dB | ≤ 0.30 dB |
| 3 | 694 s | +41 → −2.2 dB | ≤ 0.32 dB |
| 4 | 682 s | +38 → −0.3 dB | ≤ 0.08 dB |
| 5 | 275 s | +44 → −0.8 dB | ≤ 0.33 dB |
| 6 | 412 s | +40 → −3.2 dB | ≤ 0.23 dB |
| 7 | 515 s | +40 → −2.5 dB | ≤ 0.27 dB |
| 8 | 357 s | +40 → −2.7 dB | ≤ 0.38 dB |
| 9 | 510 s | +39 → −2.7 dB | ≤ 0.29 dB |

Hiss in the pauses drops by 16–18 dB from 2 to 12 kHz (10–13 dB above that).

### Left alone

Faint wobbling lines at 16.05–16.15 kHz (about −100 dBFS, sharing neither whine's FM: probably codec artifacts),
and the room tone and hum below 300 Hz.

### Not done

Nothing was committed. The results were checked by measurement and spectrograms only, not by listening.
