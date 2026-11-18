# Clicking a lyric line does not seek the audio

## Ask

Clicking on a lyric line does not seek to the audio to the corresponding location

## Answer

**Cause.** In Auto mode the click handler only seeked when the clicked line had a time in its
`.timing.js`. Chapters 2, 4, 5, 6 and 7 have no timed lines yet (every `"time"` is `null`), and
lines 23–37 of Chapter 3 are untimed, so clicking those lines did nothing — even though Auto
mode still highlights them by linear interpolation.

**Fix (app.js).** New `lyricLineStartTime(movement, idx)`; the click handler seeks to it:

- A timed line: its own time (as before).
- An untimed line: placed evenly between the nearest timed lines around it; the start and end of
  the audio stand in where there is none. With no timing at all this is the inverse of the
  linear interpolation the highlight uses, so the clicked line becomes the highlighted one.
- The interpolated time is nudged 0.01 s later: without it, rounding put the highlight on the
  line before for about 7.5% of lines.

Manual mode is unchanged: clicking moves the highlight and does not seek.

**Verified** in headless Chrome with real mouse clicks (served by `npx http-server -c-1`):

| Chapter | Clicked line | Seeks to | Highlighted |
|---|---|---|---|
| 2 (untimed) | 0 / 5 / 40 / 95 | 0.01 / 29.9 / 239.1 / 567.9 s | the clicked line |
| 3 (timed lines) | 3 / 21 | 8.79 / 56.04 s (file times) | the clicked line |
| 3 (untimed tail) | 22 / 30 / 36 | 77.8 / 252.1 / 382.8 s | line 21 (see note) |
| 1 (fully timed) | 0 / 10 / 55 | file times | the clicked line |

**Note.** In a partly timed movement (Chapter 3), Auto mode never highlights an untimed line: the
highlight stays on the last timed line before it. So clicking an untimed tail line seeks to an
estimated position, but the highlight stays on line 22 (index 21) until those lines are recorded.

Seeking also needs a server that supports HTTP Range requests (`npx http-server -c-1`, see the
README). `python3 -m http.server` doesn't support them, so the audio jumps back to 0.
