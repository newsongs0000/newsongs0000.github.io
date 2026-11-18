# No parentheses on any title translation

## Ask

There is still parentheses around the song title and movement title translations to the top panel except the first
movement of the first song

## Answer

**Cause.** The parentheses were removed only while the lyrics panel shows two columns
(`#right-pane:has(#lyrics-inner.bilingual)`). Only Chapter 1 has lyric translations so far, so every other movement
shows one column of lyrics, and its title translations still got the `(` `)` from `#np-translation::before/::after`.

**Fix.** Removed the parentheses in all cases:

- `common.css` — deleted the `#np-translation::before { content: '('; }` / `::after { content: ')'; }` rules and the
  two-column override that turned them off. The translations still follow the original titles with a 2em gap, in the
  secondary text color.
- `app.js` — `updateNowPlaying()` comment no longer mentions parentheses.
- `README.md` — "Now playing" and the `work.js` example comments now show
  "安魂曲 I. 永远安息  Requiem I. Eternal Rest".

**Checked** in headless Chrome:

- Chapter 2 (one column): "安魂曲 II. 深处祷告    Requiem II. Prayer from the Depths", no parentheses.
- Chapter 1 (two columns): still split over the two lyrics columns, no parentheses.
