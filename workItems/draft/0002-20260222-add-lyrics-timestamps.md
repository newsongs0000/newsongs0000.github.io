# Add Per-Line Timestamps to Chinese Requiem Lyrics

**Created:** 2026-02-22

## Description

Add `time` fields (seconds from movement start) to each lyric entry in `APP_DATA` inside `index.html` for all 7 movements of *Chinese Requiem (Op.63)*. This enables accurate line-by-line highlighting instead of the current linear interpolation fallback.

## Pre-requisites

- All 7 chapter MP3 files must exist and be playable (blocked by: **20260222-000001-convert-split-audio**)

## Background

The app data structure already supports timed lyrics:
```js
{ text: "歌词内容", time: 42 }  // time in seconds from movement start
```
Without `time`, the app evenly distributes lines across the duration (linear interpolation). With `time`, each line highlights precisely when it is sung.

## Steps

1. Listen to each chapter MP3
2. Note the elapsed time (in seconds) when each lyric line begins
3. Update `APP_DATA` in `index.html` for each of the 7 movements, adding `time` to every lyric entry
4. Reload the app and verify highlighting tracks the audio correctly

## Acceptance Criteria

- Every lyric entry in all 7 movements has a `time` field
- The highlighted line visibly matches the audio during playback
- No regression in behavior when a movement has no audio file loaded
