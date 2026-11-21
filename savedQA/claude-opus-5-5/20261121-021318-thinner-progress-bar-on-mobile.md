# Thinner progress bar on mobile

## Q1

On mobile devices, what's the meagurement of progress-bar? I want to make it thinner (smaller line, smaller slider)

## A1

**Before:** `#progress-bar` had only `height: 3px` and `accent-color` set. On a phone it got its own row (`flex: 1 1 100%`),
so in a 390px-wide viewport its box measured **378 × 3px**. The browser drew the slider itself (`appearance: auto`), so it
ignored that height: Chrome drew a **~16px thumb** and a track about 2–3px thick, with the thumb sticking out of the 3px
box. iOS Safari draws its own native slider, which may be a different size.

**Change:** On mobile (`(max-width: 700px), (pointer: coarse) and (hover: none)`, the same query as the other mobile
rules) the bar is now drawn by CSS instead of the browser:

- `common.css`
  - `appearance: none`; **2px track**, **10px thumb** (accent color); the box is **12px** tall so it's still easy to touch.
  - Unplayed track: `var(--text-muted)`. Played part: a `linear-gradient` that stops at the thumb's center,
    `calc(5px + (100% - 10px) * var(--progress))`. Firefox uses `::-moz-range-track` / `::-moz-range-progress` /
    `::-moz-range-thumb`.
  - In the phone layout the bar has `margin: -3px 0 -6px`, so the 12px box overlaps the 3px gap above it and the 6px
    padding below it. Its row still takes only 3px and the playback controls stay **42px** tall.
- `app.js`: new `setProgress(ratio)` sets the bar's value and `--progress`. It is called from `timeupdate`, the
  bar's `input` handler (while dragging) and `resetProgress()`.

Desktop is unchanged (native slider). Checked in headless Chrome (390 × 844, touch, coarse pointer): before, the
thumb was 16px with a 3px box; after, the line is 2px, the thumb 10px, the fill ends at the thumb, and the controls are
still 42px tall.
