# Clicking a lyric line seeks in Manual mode too

## Ask

do the same for manual lyrics mode

(Follow-up to [20261111-093947-click-lyric-line-seeks.md](20261111-093947-click-lyric-line-seeks.md): in Auto mode,
clicking a lyric line now seeks the audio to where that line starts.)

## Answer

**Change (app.js).** In Manual mode, clicking a line still moves the highlight to it, and now also seeks the audio to
that line's start: the same `lyricLineStartTime` as Auto mode. That is the line's recorded time, or an even-spaced
estimate if it has none.

**Exception: while recording (● Rec), a click does not seek.** A click during recording records the line's time from
where the audio *is*. Seeking would also make the audio jump whenever you click back to fix a line you advanced
past by mistake. A click while recording works exactly as before: it moves the highlight and records the time when
moving forward.

**README.md.** Updated the Auto/Manual table, added a paragraph on where a click seeks to (including untimed lines),
and added a recording rule for clicks. I also removed the "only timed lines" wording left over from the Auto-mode fix.

**Verified** in headless Chrome with real mouse clicks:

| Case | Clicked line | Audio | Highlight |
|---|---|---|---|
| Manual, Chapter 2 (untimed) | 0 / 40 / 95 / 5 | 0.01 / 239.1 / 567.9 / 29.9 s | the clicked line |
| Manual, Chapter 3 | 21 (timed) / 30 / 36 (untimed) | 56.04 / 252.1 / 382.8 s | the clicked line |
| Recording, click forward 24 → 25 | 25 | kept playing (no jump) | 25; time 101.548 s recorded |
| Recording, click back 36 → 25 | 25 | kept playing (no jump) | 25; nothing recorded |

In Manual mode the highlight follows the click, so untimed lines (Chapter 3, lines 23–37) are highlighted too. In
Auto mode the highlight on those lines still stays on the last timed line.
