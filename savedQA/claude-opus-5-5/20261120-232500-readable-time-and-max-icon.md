# Readable time display and an icon for Max

## Ask

on mobile, time-display is still hard to read, too faint? The label of btn-maximize is a special character, it is hard
to read, use icons

## Answer

### Time display (`common.css`)

- Color: `var(--text-muted)` (#484f58, very dim on the dark background) → `var(--text-primary)` (#e6edf3).
- Font: dropped `'Courier New', monospace` (thin strokes, especially on phones); it now uses the page's font with
  `font-variant-numeric: tabular-nums`, so the digits are all the same width and the text doesn't shift as the time
  changes.

This applies on all screen sizes, not only phones.

### Max button (`index.html`, `common.css`)

- The `⤢` character label is replaced by an inline SVG icon: two arrows pointing out to the top-right and bottom-left
  corners. It is the reverse of the Restore button's existing icon (two arrows pointing in to the middle), drawn in the
  same 12×12 box.
- Both icons share one CSS rule (`#btn-maximize svg, #btn-restore svg`): 0.9em square, drawn in the button's text
  color. The line width went from 1.4 to 1.6 so both icons are easier to see.

The result was not checked in a browser (the DevTools browser was in use by another session).
