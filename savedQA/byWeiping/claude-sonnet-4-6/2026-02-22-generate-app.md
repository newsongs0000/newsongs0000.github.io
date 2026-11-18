# Session: Generate OnePageMP3 Application
**Date:** 2026-02-22
**Model:** claude-sonnet-4-6

---

## Question

> Generate code for the application OnePageMP3

---

## Answer

Generated `/Users/weiping/sharing/one-page-mp3/index.html` — a complete single-page offline web application.

### What was created

**File:** `index.html`

A self-contained HTML5/CSS3/JavaScript application with no external dependencies.

### Architecture

- **Technology:** Vanilla JS (ES6+), CSS Grid, HTML5 `<audio>` — no frameworks, no external CDN
- **Offline-capable:** All code and data embedded in the single HTML file; only references local asset files (MP3s)

### Layout

```
+------------------+---------------------------+
| Left Nav (280px) | Top Controls (Prev/Next)  |
|  Composer Tree   +---------------------------+
|  • Huang         | Lyrics Display            |
|    ▶ Requiem     |   (scrollable, centered)  |
|      I. 永远安息  +---------------------------+
|      II. 深处祷告 | Bottom Controls           |
|      ...         |   ⏮ -15s ▶ +15s ⏭ —— 0:00|
|                  +---------------------------+
|                  | Info Pane                 |
|                  |   Composer / Work / Desc  |
+------------------+---------------------------+
```

### Features

1. **Left navigation tree** — composers and works sorted alphabetically; collapsible tree nodes
2. **Lyrics display** — all lines shown in scrollable view; current line highlighted in gold, context lines dimmed, distant lines very faint; auto-scrolls to keep current line centered
3. **Lyrics sync** — supports explicit timestamps (`{ text: "...", time: 42 }`) or linear interpolation fallback when no timestamps provided
4. **Audio controls** — Rewind-to-start, −15s, Play/Pause, +15s, Fast-forward-to-end, seek bar, time display
5. **Navigation** — Prev/Next movement buttons; auto-advances to next movement on song end
6. **Keyboard shortcuts** — Space (play/pause), ←/→ (±5s), Shift+←/→ (±15s)
7. **Configuration via URL parameters:**
   - `above-color` — text color for lyrics above current line
   - `above-bg` — background for lyrics above current line
   - `below-color` — text color for lyrics below current line
   - `below-bg` — background for lyrics below current line
   - Example: `index.html?above-color=%23aaaaaa&below-color=%23aaaaaa`
8. **Graceful degradation** — if an MP3 file is missing, lyrics still display; app does not crash
9. **Auto-advance** — plays next movement automatically when current ends

### Data

- All 7 movements of *Chinese Requiem (Op.63)* by 黄安伦 (An-Lun Huang) included
- Movement VII (`永远照耀`) references the existing MP3 at `assets/AnlunHuang/ChineseRequiem/manualWorkInProgress/Chapter7.mp3`
- Movements I–VI reference `assets/AnlunHuang/ChineseRequiem/Chapter1.mp3` etc. (to be generated from AllChapters.mp4)

### Next Steps

1. **Convert and split audio:** Convert `/Users/weiping/Downloads/AllChapters.mp4` to 7 MP3 chapters using ffmpeg:
   ```bash
   ffmpeg -i AllChapters.mp4 -q:a 0 -map a AllChapters.mp3
   # Then split by chapter timestamps
   ```
2. **Add lyrics timestamps** (optional): For precise line-by-line sync, add `time` fields to each lyric entry in the `APP_DATA` JavaScript object
3. **Add Mahler and Mozart works** when assets are ready: extend the `APP_DATA.composers` array
