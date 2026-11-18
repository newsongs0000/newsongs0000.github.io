# Separate original titles from their translations in the top bar

## Question

Currently origianl Work title, movement title and translations are mixed together as:
Work title (Work titleTranslation).  movement number. movement title(movement titleTranslation); Seperate original Work title, movement title from the translation. For example, currently 安魂曲 (Requiem) I. 永远安息 (Eternal Rest), should be changed to 安魂曲 I. 永远安息  (Requiem  I. Eternal Rest)

## Answer

The top bar now shows the original titles first, then both translations together in one pair of parentheses:

```
before:  安魂曲 (Requiem)   I. 永远安息 (Eternal Rest)
after:   安魂曲  I. 永远安息    (Requiem  I. Eternal Rest)
```

- **Same styles in both halves.** In the translation, "Requiem" uses the small gold style of the work title, and "I. Eternal Rest" uses the movement title style. The parentheses are grey.
- **Spacing.** There is a 1em gap between the work and the movement in each half, and a 2em gap before the "(". Before this change the gap between the work and the movement was 2.5em. With the translation added, the line got wide, so I made that gap smaller.
- **Missing translations.** If only one title has a translation, the parentheses show only that one, e.g. "(I. Eternal Rest)". If neither title has a translation, the parentheses are hidden.

Changes:

- `index.html`: added `#np-translation` (holds `#np-label-translation` and `#np-title-translation`) after `#np-title`.
- `common.css`: the translation spans use the same styles as `#np-label` and `#np-title`. Added the gap and the grey colour for `#np-translation`.
- `app.js`: `loadMovement()` fills the original and translated spans separately. Removed `translatedTitle()`, which nothing else used.
- `README.md`: updated the `titleTranslation` comments in the `work.js` example.

I checked it in headless Chrome. The header reads "安魂曲 I. 永远安息 (Requiem I. Eternal Rest)".
