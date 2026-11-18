# Top bar titles follow the Show check boxes

## Question

When the show checkbox in Lyrics control panel is checked, display the corresponding titles at top; when unchecked, do not display them.

## Answer

The **Show: ☑ Original ☑ Translation** check boxes now control the titles in the top bar as well as the lyrics:

| Checked | Top bar |
|---|---|
| Both (default) | 安魂曲 I. 永远安息 (Requiem I. Eternal Rest) |
| Original only | 安魂曲 I. 永远安息 |
| Translation only | Requiem I. Eternal Rest |

- **Translation only** shows no parentheses. The translations take the original titles' place and styles: the work in small gold, the movement in white.
- **A title without a translation** shows its original when only Translation is checked, the same way the lyrics heading does.
- **When it updates.** The top bar changes as soon as you click a box. It stays in the chosen mode when you go to another movement.

Changes:

- `app.js`: the header code moved out of `loadMovement()` into a new `updateNowPlaying(work, movement)`. The function reads `state.lyricsShown`. The check box handler calls it after `renderLyrics()`. Added `currentWork()`, and `currentMovement()` now uses it. Updated the LYRICS SHOWN comment.
- `index.html`: the Show group's tooltip now says "Which lyrics and titles to show".
- `README.md`: documented the behavior under Show and Now playing.

I tested it in headless Chrome. I checked each combination, then Next, then both checked again.
