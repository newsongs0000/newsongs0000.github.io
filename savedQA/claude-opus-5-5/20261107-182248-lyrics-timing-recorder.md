# Session 2026-11-07 18:22 — Lyrics timing recorder

## Ask

> Add code to create controls at the bottom of left pane to record the timing of manual selection of lyrics lines,
> save in a file; then in auto lyrics mode, use those timing data;

## Response

Added a **LYRICS TIMING** panel at the bottom of the left pane (`index.html`), with a status area and four buttons:

| Button | What it does |
|---|---|
| **● Rec / ■ Stop** | Arms recording and switches to Manual mode. While the audio **plays**, each line you advance to (↓ / → key, or clicking a later line) gets the current audio time as its start time. Moving back (↑ / ←, or clicking an earlier line) is a correction and records nothing; advancing again overwrites the time. Switching to Auto stops recording. A red "● REC" marker also shows in the lyrics area, so it stays visible when the panel is maximized. |
| **Save** | Writes the current movement's timing to `<audio name>.timing.json`, e.g. `Chapter1.timing.json`. In Chrome/Edge a save dialog opens so you can save it straight into `assets/AnlunHuang/ChineseRequiem/`. Other browsers download it. |
| **Load** | Reads one or more `.timing.json` files. Each file names its own movement. |
| **Clear** | Discards the timing recorded in this browser for the current movement (asks for confirmation). |

The status area shows the movement, how many lines are timed (e.g. `4 / 54 lines timed`), where the timing came from
(`this browser`, `Chapter1.timing.json` or `built-in`), and a recording hint.

### Where timing comes from (highest priority first)

1. A recording or loaded file kept in this browser's localStorage. It is saved automatically after every recorded line, so it survives a reload.
2. `<audio name>.timing.json` next to the MP3, fetched automatically when the movement is selected. This only works when
   the page is served over http(s) (e.g. GitHub Pages or a local server). Browsers block it for a page opened as `file://`.
   In that case use **Load**.
3. `time` fields in `APP_DATA` lyrics (existing format).
4. Otherwise: the existing linear interpolation.

### Auto mode with timing

- The highlighted line is the one that started most recently. Nothing is highlighted before the first timed line
  (intro music). Untimed lines are skipped.
- Clicking a line in Auto mode seeks the audio to its recorded start time.

### File format (one lyric line per row, easy to hand-edit)

```json
{
  "format": "onepagemp3-lyrics-timing",
  "version": 1,
  "composer": "anlun-huang",
  "work": "chinese-requiem",
  "movement": "ch1",
  "audio": "assets/AnlunHuang/ChineseRequiem/Chapter1.mp3",
  "saved": "2026-11-08T00:22:22.629Z",
  "lines": [
    {"time":0.398,"text":"求主"},
    {"time":1.108,"text":"赐他们永远"},
    {"time":null,"text":"安息在您怀里。"}
  ]
}
```

### Suggested workflow

1. Select a movement → **Rec** → play (Space) → press ↓ at the start of each line.
2. If you press too early, press ↑, then ↓ again when the line really starts.
3. To redo a section, use −15s, go back with ↑ (or click an earlier line while paused), then press ↓ at each line as before.
4. **Stop** → **Save** → put `ChapterN.timing.json` next to `ChapterN.mp3` and commit it.

### Verification

Tested in headless Chrome over CDP: recording (paused presses not recorded, corrections, backward clicks), localStorage
restore after reload, Auto-mode lookup and click-to-seek, Save (download), auto-load of a `.timing.json` next to the
MP3, Load, Clear, rejecting an invalid file, and a `file://` page (fetch blocked, nothing breaks).

Note: Python's `http.server` doesn't support HTTP Range requests, so the audio can't seek when the app is served that way.
The Auto-mode checks were run on a range-capable server.

---

## Ask

> export the lyrics timing data from localStorage to the same directory as the mp3 file

## Response

The recordings are in the browser's localStorage, which only the page can read, and a web page can write files only
into a folder the user picks. So I added a full-width **Export N to MP3 folders** button under Rec / Save / Load / Clear
(N = how many movements have timing kept in this browser; the button is disabled when N is 0).

Clicking it:

1. Opens a folder picker (Chrome / Edge). Pick the **app folder** (the one containing `index.html`). Picking the MP3
   folder itself (e.g. `assets/AnlunHuang/ChineseRequiem`) also works. The folder is remembered for the rest of the session.
2. For every movement with timing in localStorage, writes `ChapterN.timing.json` into the folder of `ChapterN.mp3`.
   As a check, it writes only where it actually finds that MP3.
3. Shows a summary of the files written and any it couldn't write. If nothing was written (wrong folder), the folder is
   forgotten so the next click asks again.

In Firefox / Safari (no folder access) the files are downloaded instead, to be moved next to the MP3s by hand.

Once exported, the files are picked up automatically when the app is served over http. localStorage still takes
precedence in this browser (use **Clear** to fall back to the file).

### Verification

Headless Chrome, with the folder picker standing in for Chrome's private test file system laid out like `assets/…`:
- 3 stored timings, Chapter2.mp3 missing → 2 files written next to their MP3s, 1 reported.
- The second export reuses the folder.
- Picking the MP3 folder itself works.
- Picking the wrong folder → nothing written, and the folder is forgotten.
- Cancelling the picker → no message.
- No-folder-access fallback → 3 downloads.
