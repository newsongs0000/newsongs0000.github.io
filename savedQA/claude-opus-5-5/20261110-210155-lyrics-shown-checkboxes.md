# Original / Translation check boxes in the lyrics control panel

## Question

Add a check box group in the new lyrics control panel with two check boxes: one for original lyrics, if checked, display original lyrics; another one for lyrics translation; at least one must be checked;

## Answer

Added a **Show: ☑ Original ☑ Translation** row to the lyrics control panel at the bottom of the left pane, under Lyrics Auto/Manual and Maximize.

| Checked | Lyrics panel |
|---|---|
| Both (default) | Same as before: two columns when the movement has translations, else the original in one column |
| Original only | Original lyrics and heading, one full-width column, no divider |
| Translation only | Translations and translated heading, one full-width column. A line with no translation shows its original. A movement with no translations shows its original lyrics |

- **At least one checked.** When only one box is checked, it is disabled, so it can't be unchecked. The group's tooltip explains why.
- **The highlighted line stays put** when you change the boxes, in both Auto and Manual modes (`renderLyrics(movement, true)`).
- **Keyboard.** After a click the box loses focus, so Space and the arrow keys keep controlling playback and the lyrics.
- **Not saved.** The choice applies to every movement and resets to both checked when the page reloads, the same as the divider width.

Files changed:
- `index.html`: the `#lyrics-shown` group.
- `common.css`: styles for the row and the check boxes, using the accent color.
- `app.js`: `state.lyricsShown`, the new LYRICS SHOWN section, and `renderLyrics` choosing the columns and text.
- `README.md`: the layout diagram and a description of the boxes.

I tested it in headless Chrome with Chapter 1 in Manual mode on line 3, covering every combination of the boxes, the disabled last box, and Chapter 2, which has no translations.
