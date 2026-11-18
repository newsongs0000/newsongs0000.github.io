# Session 2026-11-06 — Lyrics highlight mode (auto / manual)

## Ask

> Add a control to select the mode of how the next lyrics are highlighted: automatic(current) and manual(operator type any of these keys: space, arrow)

## Response

Added a **Lyrics: [Auto] [Manual]** toggle at the right end of the bottom control bar in `index.html`.

### Auto (default, unchanged behavior)
- Highlight follows audio time (timestamps, or linear interpolation).
- Keys: Space = play/pause, ←/→ = ±5s, Shift+←/→ = ±15s.

### Manual
- Audio time no longer moves the highlight.
- **Space / ↓ / →** highlight the next line; **↑ / ←** step back one line (to fix a mis-press).
- Clicking a lyric line jumps the highlight to that line (instead of seeking audio).
- Loading a movement starts with no line highlighted; the first key press highlights line 1.
- "Rewind to beginning" also resets the highlight to the start.
- Holding a key advances only one line (key auto-repeat ignored); Cmd/Ctrl/Alt combos are left to the browser.
- Advancing hides the thumbnail overlay, so lyrics can be driven with no audio playing (e.g. live singing).
- A small hint pill in the bottom-right of the lyrics area shows the keys while in Manual mode.
- Use the on-screen buttons for play/pause and seeking while in Manual mode.

### Switching modes
- Manual → Auto: highlight immediately resyncs to the audio position.
- Auto → Manual: continues from the currently highlighted line.

### Configuration
- URL param `?highlight-mode=manual` starts the app in Manual mode.
  (Superseded below: Manual is now the default.)

### Other fix
- The progress bar no longer swallows Space/arrow keys after it has been dragged
  (keyboard handler now only skips text inputs, not range inputs).

### Verified (Chrome via DevTools)
- Space/↓/→ advance, ← steps back, audio not toggled in Manual mode.
- Space with the Next button focused does not change the movement.
- Arrow with the progress bar focused advances lyrics, slider unchanged.
- Rewind resets to no highlight; clicking a line jumps; new movement starts unhighlighted;
  switching to Auto resyncs. No console errors.

---

## Ask

> set the manaul mode as default

## Response

Manual is now the default highlight mode on page load.

- `index.html` state init: `highlight-mode` URL param now defaults to `manual`; only `?highlight-mode=auto` starts in Auto.
- Config comment updated to `index.html?highlight-mode=auto  (default: manual)`.
- Verified in Chrome: no param → Manual selected, key hint shown; `?highlight-mode=auto` → Auto selected, hint hidden.
- The Auto/Manual toggle still switches modes at any time.

---

## Ask

> Space was used to pause/play, change it back that way

## Response

Space is play/pause again in both modes; Manual mode lyric control is arrow keys only.

- Manual mode: **↓ / →** next line, **↑ / ←** previous line; **Space** play/pause.
- Auto mode unchanged: Space play/pause, ←/→ ±5s, Shift+←/→ ±15s.
- `MANUAL_KEYS` no longer includes Space; the manual-mode branch only intercepts arrow keys, so Space falls through to the shared play/pause handler.
- Updated the Manual button tooltip, the on-screen hint (`Manual · ↓ / → next · ↑ / ← back`), and the KEYBOARD SHORTCUTS comment.
- Verified in Chrome (Manual mode, Chapter 1): Space started playback with highlight unchanged; ↓ → ↑ moved highlight to line 2 then back to line 1; Space paused.

---

## Ask

> Enable maximizing (not full screen) of lyrics panel (the one that displays the lyrics):
> 1. Move the Lyrics control to the top panel, next to the Prev button;
> 2. Add a toggle at top panel before the Next button, to switch maximizing the lyrics panel by hiding the left nav panel, the bottom panel where song description is displayed;
> 3. When lyrics panel is maximized, increase the font size of lyrics.

## Response

Top bar is now: `◀ Prev | Lyrics: [Auto] [Manual] | <now playing> | ⤢ Maximize | Next ▶`.

1. **Lyrics control moved** from the bottom control bar to the top bar, right after Prev.
2. **Maximize / Restore toggle** before Next. When on (`#app.lyrics-maximized`):
   - left nav pane and the info pane (composer / work / description) are hidden;
   - the playback control bar (rewind, play/pause, progress) stays visible;
   - the button shows as pressed and reads `⤡ Restore`.
   This is an in-page layout change, not browser full screen.
3. **Larger lyrics when maximized**: lines 1.05rem → 1.6rem, current line 1.2rem → 1.9rem, movement heading 0.78rem → 1rem.

Implementation notes:
- Pure CSS for the layout switch (grid columns → `1fr`, right-pane rows drop the info row).
- Extracted `centerCurrentLine()` from `highlightLyricLine()`; the toggle calls it after the 0.3s font-size transition so the current line stays centered.
- `.ctrl-btn.active` pressed style is now shared by the mode toggle and the maximize button.

Verified in Chrome: maximize hides nav + info panes, right pane spans full width, fonts 30.4px / 25.6px, current line centered (0px offset); Restore brings back 280px nav and 100px info pane, fonts 19.2px, still centered. No console errors.

---

## Ask

> Reduce the height of the space between the lyrics lines, keep the same lines being displayed, increase the font size to use the space

## Response

Cut the vertical whitespace per lyric line and grew the font so each line's box keeps its old height (same number of lines on screen).

| `.lyric-line`         | Before        | After         |
|-----------------------|---------------|---------------|
| padding (vertical)    | 10px          | 4px           |
| line-height           | 1.9           | 1.4           |
| font (normal)         | 1.05rem       | 1.95rem       |
| font (normal, current)| 1.2rem        | 2.15rem       |
| font (maximized)      | 1.6rem        | 2.7rem        |
| font (max, current)   | 1.9rem        | 3.1rem        |

Font sizes solved from: box height = font-size × 1.4 + 8px = old box height.

Verified in Chrome (Chapter 1, same viewport):
- Normal: 23 lines visible before and after; line box 52px / current 56px both before and after.
- Maximized: 19 lines visible before and after; line box 69→68px / current 78→77px.

Caveat: long single-line lyrics (Chapters 2–8) wrap sooner at the larger font, so those chapters show fewer lyric entries per screen; short-line lyrics (like the reworked Chapter 1) are unaffected.

---

## Ask

> Slightly increase the brightness of the lyrics lines before and after the highlighted line

## Response

Raised the opacity of `.lyric-line.before` and `.lyric-line.after` (the 4 lines above / below the current line) from **0.75 → 0.9**, about 17% brighter on the dark background. Colors are unchanged and still configurable via `above-color` / `below-color` URL params. Lines farther away (`.distant`, opacity 0.28) are unchanged, so the fade-out beyond ±4 lines remains.

Verified in Chrome: computed opacity before/after = 0.9, distant = 0.28, current = 1.

---

## Ask

> Opacity is good, now slightly increase the brightness of the color of the lines before and after highlighted one

## Response

Brightened the default `--lyrics-above-color` and `--lyrics-below-color` from **#6e8199** (110,129,153) to **#7f94b0** (127,148,176), about 15% brighter with the same blue-gray hue. Opacity stays at 0.9. URL params `above-color` / `below-color` still override these defaults.

Verified in Chrome: before/after lines computed `rgb(127, 148, 176)` at opacity 0.9.

---

## Ask

> reduce the prominence of the currently selected control buttons of lyrics and maximizing (do not use yellowish color)

## Response

Changed the shared pressed style `.ctrl-btn.active` (used by Lyrics Auto/Manual and Maximize/Restore) from gold accent to neutral gray:

| Property     | Before                  | After                               |
|--------------|-------------------------|-------------------------------------|
| text         | `--accent` #c9a227 gold | `--text-primary` #e6edf3 light gray |
| border       | `--accent` #c9a227 gold | `--text-muted` #484f58 mid gray     |
| background   | `--nav-active` #1f2937  | unchanged                           |

Selected button now reads as a slightly lighter, filled slate button next to the unselected ones (gray text #8b949e, dark border #21262d). Hovering a selected button keeps the gray border.

Verified in Chrome: Manual and Restore computed `rgb(230,237,243)` text, `rgb(72,79,88)` border, `rgb(31,41,55)` background; Auto unchanged.
