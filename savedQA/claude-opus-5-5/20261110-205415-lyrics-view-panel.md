# Move Lyrics mode and Maximize to a left-pane panel

## Question

group the Lyrics mode controls(lable and the Auto, Manual buttons), Maximize button on the top panel to new panel, put it under the "Lyrics Timing" panel at left

## Answer

Moved **Lyrics: Auto | Manual** and **⤢ Maximize** out of the top bar into a new panel, `#view-panel`, at the bottom of the left pane, directly under the LYRICS TIMING panel. It is always visible (it does not collapse), with the mode toggle on the left and Maximize on the right. The top bar now holds only ◀ Prev, the now-playing title and Next ▶.

- `index.html`: moved the `#mode-toggle` group and `#btn-maximize` into `<div id="view-panel">` after `#timing-panel`. The ids are unchanged, so `app.js` needed no logic changes.
- `common.css`: added `#view-panel` styles (top border, flex row) and smaller buttons sized for the 280px pane.
- `app.js`: updated the comment above the maximize code. Maximize still works because maximizing hides the whole left pane, panel included, and Esc restores it.
- `README.md`: updated the screen-layout diagram and the text that described these controls as being in the top bar.

I checked it with a headless Chrome screenshot at 1280×800. All three controls fit on one row.
