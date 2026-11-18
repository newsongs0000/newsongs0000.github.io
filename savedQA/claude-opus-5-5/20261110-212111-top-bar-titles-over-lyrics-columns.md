# Top bar titles over the matching lyrics columns

## Question

Locate the original titles and translations on top panel approximitely matching the lyrics panels's width

## Answer

When the lyrics panel shows two columns, the top bar now splits the same way:

```
 ◀ Prev       安魂曲  I. 永远安息       │       (Requiem  I. Eternal Rest)          Next ▶
 ─────────────────────────────────────────────────────────────────────────────────
              I. 永远安息 [诗篇116:7,9]  │  I. Eternal Rest [Psalm 116:7,9]
              永远安息，                 │  rest in peace forever,
```

- **Same split.** The top bar uses the same `--lyrics-original-width` as the lyrics: 40% by default.
- **Divider and Maximize.** Dragging the divider moves the titles too. Maximized lyrics work the same way.
- **Accuracy.** In Chrome at 1400px, the split in the top bar is within about 10px of the lyrics divider at 40%, at 60% and when maximized.
- **Centered.** Each half is centered in its column. A title too long for its column is cut off with "…".
- **No split.** The top bar keeps its one centered line when the lyrics panel has one column. That happens when the movement's lyrics have no translations (e.g. II), or when one of the Show boxes is unchecked.
- **Parentheses.** The translations keep their parentheses.

Changes:

- `index.html`: the original titles (`#np-label`, `#np-title`) are wrapped in a new `#np-original`, so each half can be placed as one piece.
- `common.css`: while `#lyrics-inner.bilingual` exists, `#now-playing` becomes a 2-column grid, `var(--lyrics-original-width) 1fr`, using `#right-pane:has(...)`. No JavaScript change: the top bar follows the lyrics panel's own class.
- `README.md`: described the split under "Now playing".
