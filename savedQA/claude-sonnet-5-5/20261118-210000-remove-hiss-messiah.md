# Remove hiss noise from Handel's Messiah

## Ask

When I played Handel's Messiah on mobile phone, I could hear some hiss noise, but I didn't hear it on Mac. Remove the hiss noise.

## Answer

**Cause:** the hiss is in the audio files themselves, not in the app. The Messiah MP3s are rips of a 1966 LP set (Internet Archive), and the silent gaps carry steady broadband LP surface noise at about −38 dBFS across 4–16 kHz. Mac speakers barely reproduce that range; phone speakers and headphones do.

**Fix:** `Chapter1.mp3` … `Chapter9.mp3` under `assets/Handel/Messiah/` were run through ffmpeg's FFT denoiser and re-encoded.

```
apad=pad_len=4096,
afftdn=nr=18:nf=-48:nt=w:tn=1,      # 18 dB reduction, white-noise model, adaptive noise tracking
atrim=start_sample=1102,            # afftdn delays audio by 1102 samples (25 ms); undo it
atrim=end_sample=<original length>,
asetpts=N/SR/TB
-c:a libmp3lame -q:a 2              # VBR ~170 kbps (originals ~190 kbps)
```

The cover art and ID3 tags were copied over from the originals in a second remux step.

**Verification (measured on decoded audio):**

- Hiss floor in 4–16 kHz dropped about 16–20 dB in every chapter, e.g. −40 dBFS → −57 dBFS.
- Music below 4 kHz is unchanged to within 0.1 dB; the 4–16 kHz music level fell only 1–3 dB, mostly where the content was hiss.
- Durations and sample counts are identical to the originals, and the cross-correlation lag against the originals is 0 samples, so the `*.timing.js` lyric timings are unaffected.
- No clipping; peaks match the originals.
- File sizes shrank by about 10–15 %.

The originals remain in git history (`git checkout -- assets/Handel/Messiah` restores them).

---

## Follow-up ask

Now do the same for audio files under assets/Mozart/Requiem

## Answer

Same LP-rip hiss (floor about −43 to −46 dBFS in 4–16 kHz), so the same treatment was applied to `Chapter1.mp3` … `Chapter6.mp3` under `assets/Mozart/Requiem/`. Differences from the Messiah run:

- These files are 48 kHz, so the `afftdn` delay is 1200 samples (still 25 ms); the compensation `atrim=start_sample=1200` was used instead of 1102.
- Same settings otherwise: `afftdn=nr=18:nf=-48:nt=w:tn=1`, LAME VBR `-q:a 2`, cover art and tags copied from the originals.

**Verification:** hiss floor dropped about 16–17 dB (e.g. −45.5 → −62.1 dBFS in Chapter 1); 0–2 kHz unchanged to within 0.1 dB; durations, sample counts and alignment identical to the originals (lag 0), so the `*.timing.js` files need no change; no clipping; file sizes down about 3–6 %.

---

## Follow-up ask

Now do the same for audio files under assets/HuangAnlun/ChineseRequiem

(The disk filled up from scratch WAV files part-way through; the user freed the space and told me to resume.)

## Answer

**Not processed — the measurements say these files don't have the LP-style hiss.** `Chapter1.mp3` … `Chapter8.mp3` are a cappella choir audio converted from an MP4 (44.1 kHz, ~208 kbps), not LP rips:

- Hard lowpass at ~14 kHz; above 4 kHz the spectrum falls smoothly with frequency instead of sitting on a flat shelf. Quietest 2 % of frames: about −83 dB per bin at 8–10 kHz, versus a flat −73 dB for the Messiah/Requiem LP hiss. That figure is an upper bound on any stationary floor, and it follows the loudness of the singing, so it is mostly the choir's own high harmonics and room sound.
- No silent gaps to isolate noise in.
- The settings used for the LP rips (`afftdn=nr=18:nf=-48:nt=w:tn=1`) would cut 4–14 kHz by 12–18 dB even in median and loud passages (tested on Chapter 1), dulling the choir. Lowering the assumed floor to `nf=-80` with tracking off leaves loud passages bit-identical but still takes 4–8 dB off 8–14 kHz in quiet passages; that is real choir air, not clearly hiss.

Left the eight MP3s unchanged and asked the user whether to apply the gentle setting anyway.
