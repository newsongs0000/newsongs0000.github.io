# Smaller playback buttons, larger time and Max

## Ask

In the playback-controls panel, reduce the size of the first 6 buttons (btn-rewind-start, btn-rewind-15,
btn-play-pause, btn-ff-15, btn-ff-end) and progress-bar and the space between them, increase the font sizes of
time-display span and ctrl-btn button

(The selected `ctrl-btn` was line 104 of `index.html`: the Max button, `#btn-maximize`.)

## Answer

All changes are in `common.css`. The five buttons are selected with `#playback-controls > .ctrl-btn` (direct
children), so the Max button inside `#time-max` is no longer sized with them and gets its own rule.

### Wider window

| Item | Before | After |
|---|---|---|
| Gap between items | 6px | 4px |
| ◀◀, −15s, +15s, ▶▶ | padding 6px 10px, 0.8rem | padding 4px 8px, 0.72rem |
| Play/Pause | padding 7px 16px, min-width 44px, 1rem | padding 4px 12px, min-width 36px, 0.88rem |
| Progress bar | height 4px, min-width 60px | height 3px, min-width 40px |
| Time display | 0.75rem | 0.9rem |
| Max | padding 6px 10px, 0.8rem | padding 3px 9px, 1rem |

### Phone (portrait, and landscape on a touch screen)

| Item | Before | After |
|---|---|---|
| Gap between items | 4px | 3px |
| ◀◀, −15s, +15s, ▶▶ | padding 4px 7px, 0.72rem | padding 3px 6px, 0.66rem |
| Play/Pause | padding 4px 10px, min-width 34px, 0.85rem | padding 3px 8px, min-width 30px, 0.78rem |
| Time display | 0.75rem | 0.85rem |
| Max | padding 4px 7px, 0.72rem | padding 2px 7px, 0.9rem |

The progress bar still fills the space left in its row (`flex: 1`); on a wider window it has more room now that the
buttons are smaller. Max's vertical padding was reduced so its larger icon doesn't make the row much taller.

The result was not checked in a browser (the DevTools browser was in use by another session).
