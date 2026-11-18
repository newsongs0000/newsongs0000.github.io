# Session 2026-11-08 — Timing file not picked up when opened as file://

## Ask

> I deleted local storage for file:///Users/weiping/sharing/one-page-mp3/index.html,
> /Users/weiping/sharing/one-page-mp3/assets/AnlunHuang/ChineseRequiem/Chapter1.timing.json should be select to time
> the selection of Chapter1 lyrics, but looks like it was not

## Answer

**Cause:** the page was opened as `file://`. The app loaded the timing file next to the MP3 with `fetch()`, and
browsers block `fetch()` of local files from `file://` pages. The error was caught and silently ignored, so Chapter 1
fell back to "0 / 55 lines timed". The JSON itself was fine: 55 lines, matching the 55 lyric lines exactly.
(Reproduced in headless Chrome: empty localStorage, `file://` → no timing.)

**Fix:** the timing file is now `<audio>.timing.js` instead of `<audio>.timing.json`. It holds the same JSON, wrapped
in a single `onePageMp3Timing( ... );` call, so the app can load it with a `<script>` tag, which browsers allow from
`file://` pages.

- Auto-load: `<script src="…/Chapter1.timing.js">` replaces `fetch()`. A missing file is skipped quietly. A recording
  in this browser (localStorage) still takes priority over the file.
- Save / Export now write `.timing.js` (same layout: one lyric line per row, easy to hand-edit).
- Load accepts `.timing.js` and older `.timing.json` files.
- `assets/AnlunHuang/ChineseRequiem/Chapter1.timing.js` was generated from the existing `Chapter1.timing.json`
  (verified identical content). The `.json` file is no longer read automatically and can be deleted.

**Verified** in headless Chrome, both `file://` and `http://`: with empty localStorage, selecting Chapter 1 shows
"55 / 55 lines timed · Chapter1.timing.js". Chapter 2 (no file) stays untimed with no errors.

**Note:** timing only drives the highlight in **Auto** mode. The page starts in Manual mode unless opened with
`?highlight-mode=auto`, so switch to Auto to see it.

---

## Ask

> The lyrics is not in two places: for example Chapter1.timing.js and index.html lines 635 - 916, can you use
> timing.js files only?

## Answer

Done: the lyrics are now only in the `.timing.js` files. `index.html` has none.

- **`index.html`:** removed the `lyrics: [...]` arrays from all 8 movements in `APP_DATA` (−288 lines). When a
  movement is first opened, the app loads `<audio>.timing.js` and takes **both the text and the times** from it.
- **New files** `Chapter2.timing.js` … `Chapter8.timing.js`: generated from the lyrics that were in `index.html`,
  with `"time":null` on every line (not timed yet). `Chapter1.timing.js` was kept as you left it. Its text wins
  over the old `index.html` copy, which only differed by a trailing space on line 1.
- **Recording in the browser:** a recording in localStorage now overrides only the file's *times*, never its text.
  So hand-editing the text in a `.timing.js` file always shows up. Clear goes back to the file's times.
- **Save / Export** write the file's text with the current times.
- **Load** of a timing file also keeps the text from the movement's own `.timing.js`.
- A movement with no `.timing.js` shows "No lyrics available".
- `README.md` "Flow of modifying lyrics" now says to edit the text in the `.timing.js` file.

Verified in headless Chrome over `file://` and http:
- Chapters 1, 2, 5 and 8 load their lyrics from their files.
- Chapter 1 auto-mode highlighting follows the recorded times.
- A Chapter 2 recording survives a reload, and Clear removes it.
- Recording on Chapter 1 then Clear returns to the file's times.
- Load for an unopened chapter keeps the file's text.
- A missing file shows "No lyrics available".
- Save round-trips all 55 Chapter 1 lines.

Note: the blank lines that grouped Chapter 1's stanzas in `index.html` were never displayed, so the `.timing.js`
files don't have them.
