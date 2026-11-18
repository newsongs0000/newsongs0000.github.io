# Session: relative paths in *.timing.js files

## Ask

Refactor file paths in *.timing.js file to be relative to their respective *.timing.js files

## Response

Each `.timing.js` file had one path, its `"audio"` entry, written relative to `index.html`
(e.g. `"assets/Mozart/Symphony40/Chapter1.mp3"`). A timing file always sits next to its MP3, so the
path relative to the timing file is just the MP3's name (`"Chapter1.mp3"`).

Changes:

- **All 25 `.timing.js` files** under `assets/` now have `"audio": "ChapterN.mp3"`.
- **`app.js`**: a new `timingFileAudio(movement)` returns the MP3's name, and `timingDoc` uses it, so
  Save, Export and browser recordings write the short form too. Without this, the next Save would have
  put the long path back. The LYRICS TIMING header comment explains the rule.
- **`README.md`**: the paths paragraph in "Flow: adding an artist, work or movement" now covers
  `.timing.js` files, and the step 5 example uses `"audio": "Chapter1.mp3"` with a note below it.

The app never reads `"audio"` from a timing file: it finds the timing file from the movement's `audio` in
`work.js`. So loading lyrics is unaffected.

Checked: `node --check app.js` passes; all 25 timing files parse the way the Load button reads them,
and each `"audio"` resolves to an existing MP3 beside its file. Not committed.
