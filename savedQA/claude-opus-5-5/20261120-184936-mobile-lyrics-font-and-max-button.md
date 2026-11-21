# Mobile lyrics font size; Max button in the playback controls

## Ask

Set the font size of lyrics panels to 50% of its current value on mobile devices; Change the label of the
Maximize button to Max and move it to the playback-controls, next to btn-ff-end button but put some
space between them

## Answer

- **Lyrics font on a phone** (the existing smartphone layout, window 700 px wide or narrower): in the `max-width: 700px`
  media query of `common.css`, lyric lines are now `0.975rem` (was `1.95rem`) and, maximized, `1.35rem` (was
  `2.7rem`), still multiplied by the A− / A+ scale. Checked in Chrome at 390 px: 31.2px → 15.6px, maximized 43.2px →
  21.6px. The movement heading lines (`.lyric-meta`, already 0.78rem) are unchanged.
- **Max button**: `#btn-maximize` moved out of the View Options panel into `#playback-controls`, right after
  `#btn-ff-end`, labelled "⤢ Max" (icon kept, matching "✕ Exit"), with `margin-left: 14px` to set it apart. Done in
  both `index.html` and `index1.html`, which share `app.js` and `common.css`. It is hidden while maximized, together
  with the rest of the playback controls.
- Updated comments in `app.js` / `common.css` and the README (layout diagram, left pane, smartphone layout, playback
  control section, lyric lines, Maximized lyrics).

## Ask

Move the Max button to the beginning of playback-controls panel (in front of the btn-rewind-start)

## Answer

- `#btn-maximize` is now the first button in `#playback-controls`, before `#btn-rewind-start`, in both `index.html`
  and `index1.html`. The 14px gap moved to its right side (`margin-right`), so it is set apart from ◀◀.
- On a phone the progress bar stays on its own first row; the button row starts with Max.
- Updated the comments in `app.js` / `common.css` and the README (layout diagram, playback control section).

## Ask

Remove the space before the Max button

## Answer

- On a computer Max already sits at the bar's normal 18px padding, lined up with Prev below it; unchanged.
- In the smartphone layout the button row was centered, so Max started at 26px while the progress bar and Prev
  start at 8px. The row is now left-aligned (`justify-content: flex-start` in the `max-width: 700px` query), so Max
  starts at 8px. The time display grows to fill the rest of its row (`flex: 1 0 auto`) and stays centered there.

## Ask

Ok, I guess I want the Max button at the right most, next to time-display, but separated by a little space, less
padding at right side on mobile devices

## Answer

- `#time-display` and `#btn-maximize` are now wrapped in `#time-max` (a flex group with a 12px gap) at the end of
  `#playback-controls`, in both `index.html` and `index1.html`. On a computer: buttons, progress bar, time, then Max at
  the right end, lined up with Next below.
- Smartphone layout: the right padding of the bar is 4px (left stays 8px). The button row is centered again (the left
  alignment was only for Max at the start). The time + Max group grows to fill and is right-aligned, so it sits at the
  right end of the button row when it fits, otherwise on its own row (as at 390px wide); it never splits, so Max never
  ends up alone on a row.
- Updated the comments in `app.js` / `common.css` and the README (layout diagram, playback control section).

## Ask

In max lyrics mode, the label of Exit button and its icon is misleading, change it to Norm (meaning mormalize) and a
matching icon

## Answer

- `#btn-restore` (shown only while maximized, at the top right) now reads "Norm" instead of "✕ Exit", in both
  `index.html` and `index1.html`. Its tooltip is "Back to the normal layout (Esc)".
- The icon is an inline SVG: two arrows on the same diagonal as Max's ⤢, pointing in to the middle (the usual
  "exit full screen" sign), so the pair reads expand / shrink. Unicode has no single inward-arrows glyph. Styled in
  `common.css` (`#btn-restore svg`: 0.9em, `currentColor` stroke, so it follows the button's hover color).
- README "Maximized lyrics" now mentions the Norm button next to Esc.
