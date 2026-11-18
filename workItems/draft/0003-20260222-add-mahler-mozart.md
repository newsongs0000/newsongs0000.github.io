# Add Mahler and Mozart Works to APP_DATA

**Created:** 2026-02-22

## Description

Add Mahler and Mozart (an `artist.js` per artist and a `work.js` per work, in their assets folders, with each `artist.js` listed in `APP_DATA.artistFiles` in `app.js`) once their audio files and lyrics are available. The `assets/` directory already has subdirectories for these composers (currently empty).

## Pre-requisites

- Audio MP3 files sourced and placed under `assets/Mahler/` and `assets/Mozart/`
- Lyrics text for each work obtained

## Steps

1. Populate `assets/Mahler/` and `assets/Mozart/` with MP3 files
2. For each work, create `work.js` in its assets folder (e.g. `assets/Mozart/<Work>/work.js`), following
   `assets/AnlunHuang/ChineseRequiem/work.js`:
   ```js
   onePageMp3Work({
     id: "...",
     title: "...",
     movements: [{
       id: "ch1",
       number: "I",
       title: "...",
       audio: "assets/Mozart/<Work>/Chapter1.mp3"
     }]
   });
   ```
   Each movement's lyrics go in `Chapter1.timing.js` next to its MP3, not in `work.js`.
3. For each artist, create `artist.js` in the artist's assets folder (e.g. `assets/Mozart/artist.js`) that lists
   those work files, following `assets/AnlunHuang/artist.js`:
   ```js
   onePageMp3Artist({
     id: "mozart",
     name: "Wolfgang Amadeus Mozart",
     nameSort: "Mozart, Wolfgang Amadeus",
     workFiles: ["assets/Mozart/<Work>/work.js"]
   });
   ```
   Then add `"assets/Mozart/artist.js"` to `APP_DATA.artistFiles` in `app.js`.
4. Verify the left nav tree lists all composers in ascending alphabetical order (the UI sorts automatically)
5. Test playback and lyrics display for each new work

## Acceptance Criteria

- Mahler and Mozart appear in the left navigation tree alongside Huang
- Their works and movements are selectable and playable
- Lyrics display correctly; highlighting works (with or without timestamps)
- Alphabetical ordering in the nav tree is correct
