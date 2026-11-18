# Session: Lyrics Transcription Attempt
**Date:** 2026-02-24
**Model:** claude-sonnet-4-6

---

## User Request

The MP3 files for the 8 chapters of the Chinese Requiem (黄安伦《安魂曲》Op. 63) have been created. The existing `Lyrics.txt` does not match what's actually sung. Can you generate accurate lyrics, saved separately for each chapter?

---

## Investigation

### Current State of Files

- 8 MP3 files: `Chapter1.mp3` through `Chapter8.mp3` (7–16 MB each, ~90 MB total)
- 8 JPG thumbnails: `Chapter1.jpg` through `Chapter8.jpg`
- Existing `Lyrics.txt`: Published libretto (词：唐佑之，根据圣经), covering 7 movements (I–VII)
- Original score described as "A Cappella for Mix Voices in 7 movements" — but split into **8** chapters here

### Lyrics.txt Contents (7 movements)
| Movement | Title | Voice |
|----------|-------|-------|
| I | 永远安息 (诗篇116) | 合唱 |
| II | 深处祷告 (诗篇130, 启示录21) | 女中音独唱与合唱 |
| III | 称颂耶稣 (腓立比书4, 哥林多前书15, 希伯来书) | 合唱 |
| IV | 圣洁颂歌 (以赛亚书6, 希伯来书12, 启示录4) | 合唱 |
| V | 羔羊赞颂 (启示录1, 5, 14, 15) | 男高音、女中音领唱，合唱 |
| VI | 永享自由 (启示录 + 葛里高利圣咏639) | 男高音独唱，合唱 |
| VII | 永远照耀 (以赛亚书60, 帖撒罗尼迦前书4, 诗篇23) | 男高音、女中音领唱，合唱 |

The 8th chapter is likely the **Psalm 23 section** that ends movement VII, split into its own chapter — but this was not confirmed.

---

## Approach Attempted: OpenAI Whisper

### Installation
```
pip3 install openai-whisper --break-system-packages
```
Successfully installed `openai-whisper-20250625` with torch, ffmpeg (already present).

### Medium Model Test (Chapter 1)
```
python3 -m whisper Chapter1.mp3 --language Chinese --model medium --output_format txt
```
**Result:** Completely failed — output was "祝福 祝福 祝福 祝福..." repeated throughout. Classic Whisper hallucination pattern on choral music.

### Large Model Test (Chapter 1, with initial_prompt)
```
python3 -m whisper Chapter1.mp3 --language Chinese --model large \
  --initial_prompt "求主赐他们永远安息，安息在您怀里..." --output_format txt
```
**Result:** Still failed — mixed partial hits ("安息在您怀里", "唯有耶和华所亲爱的") with hallucinations ("祈祷神父", "中文字幕——YK" repeated).

### Why Whisper Fails on A Cappella Choral Music
1. **Multiple simultaneous voices** harmonizing blend phonemes into ambiguous signals
2. **Held notes** stretch vowels far beyond speech recognition norms
3. **Reverberation** blurs consonants
4. Whisper was designed for speech, not polyphonic choral music

---

## Conclusion / Next Steps

Whisper is not a viable tool for transcribing this a cappella choral requiem.

### Options for getting accurate lyrics:
1. **Manual transcription** — listen and type what's sung (most reliable)
2. **Score/liner notes** — if the original score PDF or CD booklet is available, that would be authoritative
3. **Use existing libretto as base** — split `Lyrics.txt` into 8 chapter files; annotate repetitions manually
4. **Confirm chapter split** — clarify how the 7 movements map to 8 chapters (is Chapter 8 the Psalm 23 section from movement VII?)

### Unresolved Question
How do the 7 movements in `Lyrics.txt` map to the 8 MP3 chapters? Specifically: does movement VII get split into two chapters (永远照耀 + 诗篇23)?

---

## Tools/Models Installed This Session
- `openai-whisper-20250625` (via pip3, system-wide)
- Whisper `medium` model (~1.5 GB, cached in `~/.cache/whisper/`)
- Whisper `large` model (~2.9 GB, cached in `~/.cache/whisper/`)
