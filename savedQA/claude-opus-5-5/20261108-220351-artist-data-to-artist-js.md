# Session 2026-11-08 22:03 — Move each artist's data into a JS file in its assets folder

## Ask

Move data of an artist into a Javascript file under the directory corresponding to the folder under assets; for
example, data of artist id: "anlun-huang" (lines 16 - 23) should be in a JS file under assets/AnlunHuang

## Answer

### New file: `assets/AnlunHuang/artist.js`

```js
onePageMp3Artist({
  id: "anlun-huang",
  name: "黄安伦",
  nameSort: "Huang, An-Lun",
  bio: "黄安伦（1949–），加拿大华人作曲家。",
  workFiles: [
    "assets/HuangAnlun/ChineseRequiem/work.js"
  ]
});
```

The artist object is moved as-is. It follows the same approach as `work.js` and `.timing.js`: one callback call, so a
`<script>` can load it from `file://`.

### `app.js`

- `APP_DATA` now only lists the artist files:
  ```js
  const APP_DATA = {
    version: "1.0",
    artistFiles: [
      "assets/AnlunHuang/artist.js"
    ],
    artists: []  // filled from artistFiles
  };
  ```
- The WORK FILES section is now **ARTIST AND WORK FILES**. One loader, `loadDataFile(url, callback)`, handles both
  kinds of file. Each file must call the callback for its kind (`onePageMp3Artist` or `onePageMp3Work`). A file that
  is missing, broken, or calls the wrong one is skipped with a console warning.
- `loadArtists()` (was `loadWorks()`) fills `APP_DATA.artists` from `artistFiles`, then each artist's `works` from its
  `workFiles`, keeping the listed order. INIT now calls it before building the tree.
- The APP DATA header comment describes the new layout.

### Data layout now

```
app.js                                   APP_DATA.artistFiles → artist.js files
assets/AnlunHuang/artist.js              artist info + workFiles → work.js files
assets/HuangAnlun/ChineseRequiem/work.js work info + movements (audio, thumbnail)
assets/HuangAnlun/ChineseRequiem/ChapterN.timing.js   lyrics + timing per movement
```

All paths inside these files are relative to `index.html`.

### To add an artist

Create `assets/<Artist>/artist.js` (with its `workFiles`) and the `work.js` files, then add the `artist.js` path to
`APP_DATA.artistFiles`.

### Also updated

`workItems/draft/0003-20260222-add-mahler-mozart.md`: step 3 now creates `artist.js` and lists it in
`APP_DATA.artistFiles`.

### Verified

Headless Chrome, both `file://` and `http://`: the artist and its work load, the tree shows 8 movements, Chapter 1
lyrics load (55 lines), Next goes to "II. 深处祷告", and Maximize/Esc still work. A missing file and an artist.js loaded
as a work each return `null` with a warning, and there are no other errors.
