# Is the timing-line field information in README.md?

## Question

Is this information in the README.md file?

(Refers to the previous answer: line 10 of `Chapter1.timing.js` is a JavaScript object with `time`, `text` and `translation`, and the names are quoted because the file is JSON.)

## Answer

Mostly. The README covers the fields but not why they are quoted.

**Already covered:**

- **Flow: modifying lyrics.** Each lyric line is one row `{"time":…,"text":…}`. `"time"` is the start in seconds, or `null` if not timed yet. A time belongs to its row. `"translation"` is optional and shows the line in the right column. Save and Export keep translations.
- **Add the lyrics — `<mp3 name>.timing.js`.** A complete example file, wrapped in `onePageMp3Timing({...})`.
- **Data files reference.** The `.timing.js` file holds one `{time, text, translation}` per line (`translation` optional). Each data file is one call to a function `app.js` defines, so it loads with a `<script>` tag.

**Not covered:**

- That each row is a JavaScript object, and why its property names are in double quotes: the contents are JSON. Save writes them with `JSON.stringify`, and the Load button reads them with `JSON.parse`.
- The README's rule, "Keep the file valid JavaScript: rows are separated by commas, with no comma after the last row", is slightly off. Valid JavaScript allows unquoted names, single quotes, trailing commas and comments. All of these play fine, but the Load button rejects them. The real rule is valid JSON inside the `onePageMp3Timing(...)` call.

Offered to replace that bullet in "Flow: modifying lyrics" with a "valid JSON" rule: double-quoted names and strings, commas between rows, none after the last, no comments. No change made yet.
