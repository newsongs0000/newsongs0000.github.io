# README: timing file rows must be valid JSON

## Question

yws

(i.e. "yes": a reply to the offer to replace the "Keep the file valid JavaScript" bullet in README "Flow: modifying lyrics" with a "valid JSON" rule.)

## Answer

In `README.md` › Flow: modifying lyrics › step 1, this bullet:

> Keep the file valid JavaScript: rows are separated by commas, with no comma after the last row.

is now:

> Each row is a JavaScript object, and everything inside `onePageMp3Timing(...)` must be valid **JSON**: Save writes it with `JSON.stringify`, and **Load** reads it with `JSON.parse`. So put names and strings in double quotes (`"time"`, not `time` or `'time'`), separate rows with commas but put none after the last row, and do not add comments. A file that breaks these rules may still play, but **Load** rejects it.

No other changes.
