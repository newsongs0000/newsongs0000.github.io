# Are "time", "text", "translation" JavaScript object field names?

## Question

In line 10, are "time", "text", "translation" field names of a JavaScript object?

(Line 10 of `assets/HuangAnlun/ChineseRequiem/Chapter1.timing.js`:
`{"time":0.1,"text":" ( 以祷告的心 )", "translation": " ( Prayerfully )"},`)

## Answer

Yes. Line 10 is a JavaScript object literal with three properties:

| Property | Value | Meaning |
|---|---|---|
| `time` | `0.1` | when the line starts, in seconds into the MP3 (`null` if not timed yet) |
| `text` | `" ( 以祷告的心 )"` | the original lyric line |
| `translation` | `" ( Prayerfully )"` | its translation (optional) |

It is one element of the `lines` array, which is a property of the object passed to `onePageMp3Timing({...})`. When the page loads the file with a `<script>` tag, that call stores the object, and the lines become `movement.lyrics`.

**Why the names are in quotes.** In JavaScript, quotes around property names are optional: `{time: 0.1, text: "..."}` is the same object. The file uses them because its contents are also JSON, and JSON requires quoted names:

- **Save** writes the file with `JSON.stringify` (`timingFileText()` in `app.js`).
- **Load** (LYRICS TIMING panel) reads a file back with `JSON.parse` (`parseTimingFile()`), after removing the `onePageMp3Timing(` … `);` wrapper.

So when you edit these files by hand, keep the double quotes, as well as the other JSON rules: double-quoted strings, no trailing commas, no comments. Without the quotes, the file still plays in the app, which runs it as a script. But loading it through the Load button would fail with a JSON error.
