# Convert and Split AllChapters.mp4 into 8 Chapter MP3s + Thumbnails

**Created:** 2026-02-22
**Updated:** 2026-02-23

## Description

Convert `/Users/weiping/Downloads/AllChapters.mp4` into:
- 8 individual MP3 audio files, one per chapter
- 8 thumbnail images (one per chapter, captured at the midpoint of each chapter) for display before playback

The `manualWorkInProgress/` directory is ignored; all 8 chapters will be created fresh from `AllChapters.mp4`.

## Pre-requisites

- `ffmpeg` installed and available on PATH ✓ (installed 2026-02-23)
- Source file `/Users/weiping/Downloads/AllChapters.mp4` is present ✓
- Chapter boundary timestamps determined via silence detection ✓ (see below)

## Chapter Boundaries

Determined by `ffmpeg silencedetect` (noise=-40dB, min duration=1.5s).
Total duration: 3773.9s (1:02:53).

| Chapter | Start (s) | End (s) | Midpoint (s) | Duration |
|---------|-----------|---------|--------------|----------|
| Ch1 | 0.000 | 431.055 | 215.5 | 7:11 |
| Ch2 | 435.736 | 1009.611 | 722.7 | 9:33 |
| Ch3 | 1013.084 | 1417.695 | 1215.4 | 6:44 |
| Ch4 | 1421.119 | 1864.454 | 1642.8 | 7:23 |
| Ch5 | 1868.479 | 2385.958 | 2127.2 | 8:37 |
| Ch6 | 2390.043 | 3045.109 | 2717.6 | 10:55 |
| Ch7 | 3049.386 | 3335.248 | 3192.3 | 4:45 |
| Ch8 | 3338.681 | 3762.565 | 3550.6 | 7:03 |

> Note: Ch8 end is set to 3762.565s (start of the final 11s silence) to trim trailing silence.

## Output Files

All files under `assets/AnlunHuang/ChineseRequiem/`:
- `Chapter1.mp3` … `Chapter8.mp3` — audio
- `Chapter1.jpg` … `Chapter8.jpg` — thumbnail screenshots at chapter midpoints

## Steps

1. Run ffmpeg commands to extract MP3 + thumbnail for each chapter (see commands below)
2. Verify each MP3 plays correctly and covers the right musical content
3. Update `index.html` APP_DATA to reference 8 movements with correct `src` and `thumbnail` paths

## ffmpeg Commands

```bash
OUT="assets/AnlunHuang/ChineseRequiem"

# Chapter 1
ffmpeg -i AllChapters.mp4 -ss 0       -to 431.055  -q:a 0 -map a "$OUT/Chapter1.mp3"
ffmpeg -i AllChapters.mp4 -ss 215.5   -vframes 1   "$OUT/Chapter1.jpg"

# Chapter 2
ffmpeg -i AllChapters.mp4 -ss 435.736 -to 1009.611 -q:a 0 -map a "$OUT/Chapter2.mp3"
ffmpeg -i AllChapters.mp4 -ss 722.7   -vframes 1   "$OUT/Chapter2.jpg"

# Chapter 3
ffmpeg -i AllChapters.mp4 -ss 1013.084 -to 1417.695 -q:a 0 -map a "$OUT/Chapter3.mp3"
ffmpeg -i AllChapters.mp4 -ss 1215.4   -vframes 1   "$OUT/Chapter3.jpg"

# Chapter 4
ffmpeg -i AllChapters.mp4 -ss 1421.119 -to 1864.454 -q:a 0 -map a "$OUT/Chapter4.mp3"
ffmpeg -i AllChapters.mp4 -ss 1642.8   -vframes 1   "$OUT/Chapter4.jpg"

# Chapter 5
ffmpeg -i AllChapters.mp4 -ss 1868.479 -to 2385.958 -q:a 0 -map a "$OUT/Chapter5.mp3"
ffmpeg -i AllChapters.mp4 -ss 2127.2   -vframes 1   "$OUT/Chapter5.jpg"

# Chapter 6
ffmpeg -i AllChapters.mp4 -ss 2390.043 -to 3045.109 -q:a 0 -map a "$OUT/Chapter6.mp3"
ffmpeg -i AllChapters.mp4 -ss 2717.6   -vframes 1   "$OUT/Chapter6.jpg"

# Chapter 7
ffmpeg -i AllChapters.mp4 -ss 3049.386 -to 3335.248 -q:a 0 -map a "$OUT/Chapter7.mp3"
ffmpeg -i AllChapters.mp4 -ss 3192.3   -vframes 1   "$OUT/Chapter7.jpg"

# Chapter 8
ffmpeg -i AllChapters.mp4 -ss 3338.681 -to 3762.565 -q:a 0 -map a "$OUT/Chapter8.mp3"
ffmpeg -i AllChapters.mp4 -ss 3550.6   -vframes 1   "$OUT/Chapter8.jpg"
```

## Acceptance Criteria

- 8 MP3 files at `assets/AnlunHuang/ChineseRequiem/Chapter1.mp3` through `Chapter8.mp3`
- 8 JPEG thumbnails at `assets/AnlunHuang/ChineseRequiem/Chapter1.jpg` through `Chapter8.jpg`
- Each chapter plays the correct portion of the recording with no missing audio and no overlap
- `index.html` updated to reference all 8 chapters and their thumbnails
