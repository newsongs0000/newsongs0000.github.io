# Session 2026-11-08 20:58 — Move each work's data into a JS file in its assets folder

## Ask

Move the data of a work of an artist into a Javascript file under the directory corresponding to the folder under
assets; for example, data of work id: "chinese-requiem" (lines 19 - 101) should be in a JS file under
assets/HuangAnlun/ChineseRequiem

## Answer

### New file: `assets/HuangAnlun/ChineseRequiem/work.js`

It holds the Chinese Requiem work object (id, title, year, description, the 8 movements …), moved as-is, wrapped in one
call:

```js
onePageMp3Work({
  id: "chinese-requiem",
  title: "安魂曲 (Requiem)",
  ...
  movements: [ ... ]
});
```

This is the same approach as the `ChapterN.timing.js` files. A `<script>` tag can load it when `index.html` is opened
as `file://`, where `fetch` of local files is blocked. The data matches the old app.js lines 19–101 exactly (checked
with `diff`).

### `app.js`

- The artist entry keeps `id`, `name`, `nameSort` and `bio`. Its `works: [ ... ]` is replaced by a list of work files:
  ```js
  workFiles: [
    "assets/HuangAnlun/ChineseRequiem/work.js"
  ]
  ```
- New **WORK FILES** section: `loadWorks()` loads every listed `work.js` (in parallel, each via a `<script>` tag),
  and the global `onePageMp3Work(work)` callback hands each work over. The result goes into `artist.works`, in
  `workFiles` order. All the rest of the code still reads `artist.works` unchanged.
- A missing or broken `work.js` logs a console warning and is skipped. It does not stop the page.
- INIT now waits for the work files before building the tree:
  `loadWorks().then(() => { buildFlatList(); buildTree(); updateNavButtons(); updateTimingPanel(); })`.
- The APP DATA header comment explains where work data now lives.

Movement `audio` / `thumbnail` paths are unchanged (still relative to `index.html`, e.g.
`assets/HuangAnlun/ChineseRequiem/Chapter1.mp3`), so `.timing.js` lookup, Save and Export behave as before.

### To add a work

Create `assets/<Artist>/<Work>/work.js` in the same format, and add its path to that artist's `workFiles` in `app.js`.

### Also updated

`workItems/draft/0003-20260222-add-mahler-mozart.md`: its steps now describe the work.js + `workFiles` layout instead
of putting works inline in `app.js`.

### Verified

Headless Chrome, both `file://` and `http://`: the tree shows 8 movements, Chapter 1 lyrics load (55 lines), Next goes
to "II. 深处祷告", the info pane shows the work, Maximize/Esc still work, and there are no errors. A missing work file
returns `null` with a warning.
