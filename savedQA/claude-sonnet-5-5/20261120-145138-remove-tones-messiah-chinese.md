# Remove high-frequency noise from Handel's Messiah (Chinese version)

## Ask

When I played assets/Handel/MessiahChinese on mobile devices, I could hear some high frequency noises, but didn't
hear on desktop; I asked you to remove these kind of noise before (refer
savedQA/claude-sonnet-5-5/20261118-210000-remove-hiss-messiah.md), do it again, but save the scripts you use.

## Answer

**Not the same noise as before, so not the same filter.** Measured first: these nine MP3s (taken from a Bilibili
video, 44.1 kHz, ~161 kbps) have no LP-style hiss shelf. The high band is clean, −85 to −95 dBFS per bin in the
quietest frames. What they have are two **steady tones** that show as sharp horizontal lines on a spectrogram:

- about **6.44 kHz** and **15.61 kHz**, in every chapter (about a third to all of each chapter, e.g. from 2 min 54 s
  to the end of Chapter 5), at −60 to −85 dBFS per bin, 15–40 dB above the spectrum around them;
- the pitch drifts ±30 Hz between and within chapters (6.40–6.47 kHz and 15.58–15.64 kHz).

Phone speakers and earphones reproduce 6 and 15 kHz well; laptop speakers much less, which matches "heard on mobile,
not on desktop". The FFT denoiser used for the LP rips would have dulled the music without removing a pure tone
cleanly, so notch filters were used instead.

**Fix:** `Chapter1.mp3` … `Chapter9.mp3` under `assets/Handel/MessiahChinese/` were filtered with 4 cascaded
ffmpeg `bandreject` notches at 6440 Hz (200 Hz wide) and 4 at 15613 Hz (400 Hz wide), and re-encoded with LAME VBR
`-q:a 2`; ID3 tags kept. Chapter 2's decoded peak overshot full scale after re-encoding (1.014), so it was encoded
again 0.17 dB lower.

**Verification (decoded audio, original vs result):**

- Both tones drop by 26–40 dB in the median (e.g. Chapter 5: 6.44 kHz −64 → −104 dBFS, 15.61 kHz −72 → −106 dBFS);
  after processing they are below −95 dBFS per bin (inaudible) in every 10 s window except one in Chapter 8, where
  the tone had drifted down to about 6.40 kHz and is cut by 21 dB, to −95 dBFS.
- Music is untouched: 0–6 kHz and 7–15 kHz change by 0.0–0.2 dB; the strips right beside the notches (6.00–6.25,
  6.63–7.00, 15.00–15.40 kHz) by 0.5–1.5 dB.
- Sample counts identical to the originals and cross-correlation lag 0, so the `*.timing.js` files are unaffected;
  durations identical; no clipped samples; tags unchanged.
- File sizes grew about 2 % (165 MB in total), bit rate 161 → 165 kbps.

The originals remain in git history (`git checkout -- assets/Handel/MessiahChinese` restores them).

**Scripts saved** in `scripts/denoise-audio/` (documented in its README.md and linked from scripts/README.md):

- `analyze_noise.py`: band levels and narrow peaks, tells hiss from tones;
- `find_tones.py`: finds steady tones and where they are present;
- `spectrogram.sh`: spectrogram PNG of a time range;
- `remove_tones.py`: notch filtering, re-encode, tag copy, automatic headroom;
- `verify_denoise.py`: the checks above, exit status 1 on failure.

The hiss recipe from the LP-rip runs is described in the README (not scripted).

Reproduce:

```sh
python3 scripts/denoise-audio/remove_tones.py --out-dir /tmp/denoised assets/Handel/MessiahChinese/Chapter*.mp3
python3 scripts/denoise-audio/verify_denoise.py assets/Handel/MessiahChinese /tmp/denoised
```

(Verification of the originals vs results is meaningful against the git version of the files, i.e. before copying
`/tmp/denoised` over them.)
