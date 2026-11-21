# Same playback-control sizes in landscape as in portrait

## Ask

On mobile devices and lyrics mode is normal (not maximized), when the orientation changes from portrait to landscape,
the buttons in playback-controls panel become larger and the spaces between them, leading to the btn-maximize not
visible in some cases; make the sizes of these buttons and spaces in landscape as same as in portrait.

## Answer

Cause: the compact paddings and gaps were only in the `@media (max-width: 700px)` (portrait) block of
[common.css](../../common.css). A phone in landscape is wider than 700px, so it got the desktop values (button padding
`6px 10px`, Play `7px 16px` / min-width 44px, gap 6px, panel padding `10px 18px`, time–Max gap 12px). The controls
stay on one row there, so on a narrow landscape screen the row overflowed and Max was pushed off the right edge.

Change in [common.css](../../common.css): the size and spacing rules moved from the portrait-only block into the
shared smartphone block (`(max-width: 700px), (orientation: landscape) and (max-height: 500px) and (pointer: coarse)`),
next to the font sizes that were already shared:

- `#playback-controls` padding `6px 4px 6px 8px`, gap 4px
- `.ctrl-btn` padding `4px 7px`; Play padding `4px 10px`, min-width 34px
- `#time-max` gap 8px; `#time-display` min-width 0

The portrait block keeps only its layout rules (wrapping, the progress bar on its own row, the time and Max at the
right end).

Verified with headless Chrome emulating a touch phone, old CSS vs new:

| Viewport | Before | After |
| --- | --- | --- |
| 390×844 portrait | buttons 39×27, gap 4px | same (unchanged) |
| 844×390 landscape | buttons 45×31, gap 6px | 39×27, gap 4px |
| 932×430 landscape | buttons 45×31, gap 6px | 39×27, gap 4px |
| 740×360 landscape | row 810px wide on a 740px screen: **Max cut off** | row fits, Max visible |

Not committed.
