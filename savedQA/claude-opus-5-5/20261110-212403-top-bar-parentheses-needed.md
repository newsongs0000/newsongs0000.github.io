# Are the parentheses around the top bar translations still needed?

## Question

Are the parentheses still needed for work title and movement title translations on the top panel?

## Answer

Only when the titles and translations share one line. When the top bar is split into columns, the parentheses aren't needed.

- **Split top bar** (the lyrics panel has two columns): the column position already marks the translation, so the parentheses add nothing. The translation column's heading in the lyrics panel ("I. Eternal Rest [Psalm 116:7,9]") has no parentheses, and the top bar would match it without them.
- **One line** (the lyrics have no translations yet, currently II–VIII, with both Show boxes checked): "安魂曲 II. 深处祷告 (Requiem II. Prayer from the Depths)". Here the parentheses are what separate the translation from the original, so they are still useful.
- **Translation only:** there are already no parentheses.

Recommendation: drop them in the split top bar and keep them on the one-line top bar. This is a CSS-only change. `(` and `)` move from literal text in `index.html` to `#np-translation::before` / `::after`, and the split rule turns them off.

No change made yet; waiting for the user's decision.
