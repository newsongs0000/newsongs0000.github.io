# Drop the parentheses in the split top bar

## Question

yes

(Reply to "Are the parentheses still needed…?" It approves dropping the parentheses in the split top bar and keeping them on the one-line top bar.)

## Answer

Done:

| Top bar | Shows |
|---|---|
| Split (lyrics in two columns, e.g. I) | 安魂曲 I. 永远安息 │ Requiem I. Eternal Rest |
| One line (lyrics without translations, e.g. II) | 安魂曲 II. 深处祷告 (Requiem II. Prayer from the Depths) |

Changes:

- `index.html`: removed the literal `(` and `)` from `#np-translation`.
- `common.css`: the parentheses now come from `#np-translation::before` / `::after`. The split-layout rule (`#right-pane:has(#lyrics-inner.bilingual)`) sets their `content: none`.
- `README.md`: "Now playing" says the split top bar has no parentheses.

Checked in headless Chrome. In the split top bar, the computed `::before` / `::after` content is `none`. On the one-line top bar it is `"("` / `")"`. Screenshots of both looked right.
