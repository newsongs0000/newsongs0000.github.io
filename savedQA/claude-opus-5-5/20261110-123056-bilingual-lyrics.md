# Bilingual lyrics: original | translation, side by side

## Ask

The lyrics are in Chinese, it will be translated into English, and I want to display both, when the song is playing,
the lyrics in both language will be selected at the same time; Divide the lyrics panel into two

## Answer

Each lyric line in a `.timing.js` file can now have an optional `"translation"`:

```javascript
    {"time":2.2,"text":"求主","translation":"O Lord,"},
```

If any line of a movement has a translation, the lyrics panel is split into two columns: Chinese on the left,
English on the right, with a thin divider down the middle. Each line and its translation are two cells of **one row**,
so they get the same highlight together (auto and manual mode, clicks, maximized view), and they stay level when the
English wraps. Movements without translations still show one full-width column.

Changes:

- `app.js`
  - `applyTimingDoc()` reads `translation` from each line into `movement.lyrics[i].translation`.
  - `renderLyrics()` adds class `bilingual` to `#lyrics-inner` and renders each row as
    `<span class="lyric-original">` + `<span class="lyric-translation">` when the movement has translations.
  - `timingDoc()` writes `translation` back, so **Save** / **Export** keep the translations (lines without one get no
    `translation` key).
  - Header comments updated.
- `common.css`: `#lyrics-inner.bilingual` gives each row a two-column grid, with a center divider (`::before`).
- `README.md`: layout diagram split into two columns, a "Translation" bullet under the song playing section, a
  translation example under "Flow: modifying lyrics", and the data-files table and precedence note updated.

No `.timing.js` file has translations yet, so the app looks the same until they are added.

### Verification

In headless Chrome over `npx http-server -c-1`:

- Chapter 2 (no translations): one column, no `bilingual` class, same as before.
- Chapter 1 with sample English injected for testing (not saved to any file): two columns. At 2:30, exactly one
  row was `current`, and its Chinese and English cells had the same top. The divider sat in the middle of the gap,
  and the layout also held in the maximized view.
- `timingFileText(timingDoc(...))` wrote the translations and `parseTimingFile()` read them back unchanged. Untranslated
  lines had no `translation` key.
