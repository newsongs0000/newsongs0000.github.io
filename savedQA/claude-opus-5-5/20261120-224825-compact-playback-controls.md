# Compact playback controls (time display, icon-only Max / Norm)

## Ask

Further reduce the space in the playback-controls panel so it won't become two lines, below are what I could think of:

- remove the space before and after the / sign in time-display field;
- Remove the label of Max / Norm button

## Answer

Changes:

- **Time display** — `0:00 / 0:00` → `0:00/0:00`, both the initial markup ([index.html](../../index.html),
  [index1.html](../../index1.html)) and `setTimeDisplay()` in [app.js](../../app.js).
- **`#time-display` min-width** in [common.css](../../common.css) — `90px` → `9ch` (exactly `0:00/0:00` in the
  monospace font). Otherwise the old 90px reservation would have kept the width the same on desktop, so removing the
  spaces would save nothing there. On phones it was already `min-width: 0`.
- **Max button** — label removed, only the ⤢ icon remains. Added `aria-label="Maximize lyrics panel"`; the tooltip is
  unchanged.
- **Norm button** (top right while maximized) — label removed, only the arrows-pointing-in icon remains, matching Max.
  Added `aria-label="Back to the normal layout"`.
- [README.md](../../README.md) — layout diagram and the text about Max / Norm updated to the icon-only buttons; the
  CSS comment about the restore icon updated too.

Verified with headless Chrome at 320px width: before, the time and Max wrapped to a second row; after, the buttons,
time and ⤢ fit on one row (with the progress bar on its own row below, as designed). Desktop width looks fine.

Not committed.
