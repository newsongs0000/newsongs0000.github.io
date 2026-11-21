# MP3 Song Player with Lyrics Highlighting

OnePageMP3 is an MP3 song player built with plain HTML and JavaScript. While a song plays, it shows several lines of
lyrics and highlights the line being sung.

- **One page, offline.** No server, build step, framework or internet connection is needed: open `index.html` and play.
- **No dependencies.** It is plain HTML5, CSS Grid and ES6+ JavaScript, using the browser's `<audio>` element.
- **Lyrics follow the music.** Each lyric line can have a start time, which you record in the app as the music
  plays. Lines with no times are spread evenly over the song as an approximation.

## Contents

- [MP3 Song Player with Lyrics Highlighting](#mp3-song-player-with-lyrics-highlighting)
  - [Contents](#contents)
  - [Running the app](#running-the-app)
    - [Running an HTTP server](#running-an-http-server)
  - [Screen layout](#screen-layout)
  - [Playing music](#playing-music)
  - [Lyrics highlight modes](#lyrics-highlight-modes)
  - [Maximized lyrics](#maximized-lyrics)
  - [Keyboard shortcuts](#keyboard-shortcuts)
  - [Configuration (URL parameters)](#configuration-url-parameters)
  - [Flow: timing the lyrics](#flow-timing-the-lyrics)
    - [1. Record](#1-record)
    - [2. Check](#2-check)
    - [3. Save to the project](#3-save-to-the-project)
    - [4. Tidy up and commit](#4-tidy-up-and-commit)
    - [Other timing buttons](#other-timing-buttons)
  - [Flow: modifying lyrics](#flow-modifying-lyrics)
  - [Flow: adding an artist, work or movement](#flow-adding-an-artist-work-or-movement)
    - [1. Put the media in place](#1-put-the-media-in-place)
    - [2. Describe the artist — `assets/<Artist>/artist.js`](#2-describe-the-artist--assetsartistartistjs)
    - [3. Describe the work — `assets/<Artist>/<Work>/work.js`](#3-describe-the-work--assetsartistworkworkjs)
    - [4. Register a new artist in `app.js`](#4-register-a-new-artist-in-appjs)
    - [5. Add the lyrics — `<mp3 name>.timing.js`](#5-add-the-lyrics--mp3-nametimingjs)
    - [6. Check](#6-check)
  - [Data files reference](#data-files-reference)
  - [Project structure](#project-structure)
  - [Browser notes](#browser-notes)
  - [Development workflow](#development-workflow)

## Running the app

**From disk (the usual way).** Double-click `index.html`, or open it as `file:///…/one-page-mp3/index.html`. Every
data file (artists, works, lyrics) is a `.js` file loaded with a `<script>` tag because browsers block `fetch` of
local files.

**Over HTTP (optional).** You can also serve the project folder with a local web server. This is useful when you:

- edit data files often. Over HTTP the app adds a cache-busting query to every data file, so a plain reload picks up
  your edits;
- want to open the app from another device on the same network, such as a tablet or the computer that drives a
  projector.

### Running an HTTP server

Any static file server works, as long as it supports HTTP **Range requests**. Without them the browser cannot seek
in the audio: rewind, fast-forward, the progress bar and clicking a lyric line all jump back to 0:00.

> **Do not use `python3 -m http.server`.** It does not support Range requests, so seeking does not work.
>
> **Do not use `ruby -run -e httpd`.** In Chrome the music starts and then stops at once, or does not start at all,
> after the first time an MP3 is loaded. Chrome keeps the part of the MP3 it has downloaded, and when it asks for the
> next part, this server answers `304 Not Modified` instead of sending the audio.

Run one of these commands in the project folder (the folder that contains `index.html`), then open the URL shown:

| Needs | Command | Open |
|---|---|---|
| Node.js (recommended) | `npx http-server -c-1` | http://localhost:8080/ |
| Node.js | `npx serve` | http://localhost:3000/ |
| Python 3 | `python3 -m pip install rangehttpserver` (once), then `python3 -m RangeHTTPServer` | http://localhost:8000/ |

- **`npx`** comes with Node.js. The first run downloads the server package, so it needs an internet connection once.
- **`-c-1`** turns off `http-server`'s caching, so edited MP3s and pictures are also picked up on reload. Add
  `-p 9000` to use another port, or `-a 127.0.0.1` to accept connections from this computer only.
- **Other devices.** `http-server` lists the addresses it listens on, including the network one (e.g.
  `http://192.168.1.20:8080`). Open that address on the other device. Your firewall may ask whether to allow it.
- Press **Ctrl+C** in the terminal to stop the server.

To check that a server supports Range requests, ask it for part of an MP3. It should answer `206`, not `200`:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -H 'Range: bytes=0-99' \
  http://localhost:8080/assets/HuangAnlun/ChineseRequiem/Chapter1.mp3
```

Passing this check is not enough on its own: the Ruby server above passes it and still fails in Chrome. Play an MP3,
reload the page, and play it again to be sure.

Browser recordings of lyrics timing are stored per origin, and the port is part of the origin. A recording made at
`http://localhost:8080` is not visible at `http://localhost:3000` or from `file://`. Use the same server and port each
time, or Save the recording to its `.timing.js` file (see [Flow: timing the lyrics](#flow-timing-the-lyrics)).

## Screen layout

```
┌───────────────┬─────────────────────────────────────────────────────────────┐
│ ♫ / Lyrics    │ ◀◀  −15s  ▶  +15s  ▶▶  ━━━━━━━●━━━━━━━  1:23 / 5:40   ⤢ Max │  playback controls
│ SONGS       ˄ ├─────────────────────────────────────────────────────────────┤
│ ▾ Artist      │ ◀ Prev               Work · Movement                 Next ▶ │  song navigation
│   ▾ Work      ├────────────────────────┬────────────────────────────────────┤
│     1. Mvt    │   lines above (dimmed) │   their translations               │
│     2. Mvt    │ ▌ CURRENT LINE         │   ITS TRANSLATION (highlighted)    │  lyrics
│ ▸ Artist      │   lines below (dimmed) │   their translations               │
│ ▸ Artist      │                        │                                    │
│               ├────────────────────────┴────────────────────────────────────┤
│ LYRICS TIMING │ Artist · Work Op. (year) · Premiere: … │ Description        │  info pane
│   (collapsed) │                                                             │
│ Lyrics:[Auto| │                                                             │
│ Manual]       │                                                             │
│ Show: ☑ Orig. │                                                             │
│   ☑ Transl.   │                                                             │
│ Font: A− A+   │                                                             │
└───────────────┴─────────────────────────────────────────────────────────────┘
```

- **Left navigation pane**
  - **Tree.** Artists, then works, then movements. Artists are sorted alphabetically by `nameSort` and works by
    `titleSort`. Movements keep the order they have in `work.js`. Artist and work folders start collapsed; click one
    to open or close it. The movement that is playing is highlighted. The tree is under a **SONGS** title bar, whose
    arrow button collapses the whole tree to that bar and opens it again. It is open by default; the state is kept in
    the `songs` URL parameter (`open` or `collapsed`). On a wider window the panels below the tree stay at the bottom of
    the pane when it is collapsed.
  - **LYRICS TIMING panel.** Docked near the bottom of the pane and collapsed by default, showing its title and a `^`
    button; open it with the button. Not shown on a smartphone. See [Flow: timing the lyrics](#flow-timing-the-lyrics).
  - **Lyrics: Auto | Manual** (below the LYRICS TIMING panel) switches the
    [highlight mode](#lyrics-highlight-modes). The player starts in Manual.
  - **Show: ☑ Original ☑ Translation** (under them) chooses which lyrics the panel shows, and which titles the top
    bar shows. See **Translation** below.
  - **Audio: ☑ Mute** (the last row; not on `index1.html`, see [Silent and sound pages](#silent-and-sound-pages))
    silences the audio without stopping it. The music keeps playing with no sound, so the lyrics are highlighted, the
    progress bar moves and the keyboard works exactly as usual. This suits showing the timed lyrics while the music is
    performed live. Your choice stays when you go to another movement, and is kept in the `mute` URL parameter. On
    `index1.html` the row is just **Font:** (the lyrics size buttons), because the audio is always silent.
  - **Smartphone layout** (window 700 px wide or narrower). The playback controls are at the top of the screen, then
    the navigation pane, then the rest of the player (song navigation, lyrics, info pane). The navigation pane is as
    tall as its content (the tree and the View Options panel) up to 64% of the height, then the tree scrolls. The
    lyrics take the rest, so the song navigation and lyrics move up when you collapse tree folders or the whole
    **SONGS** panel. The **SONGS** title bar stays at the top of the pane while the tree scrolls. The LYRICS TIMING panel is not shown. The panel with **Lyrics: Auto | Manual**,
    **Show** and the last row (**Audio:** or **Font:**) is titled **VIEW OPTIONS** and is collapsible there: it starts
    collapsed to its title and an arrow button, and the arrow opens it. The state is kept in the `view-options` URL
    parameter (`open` or `collapsed`). On a wider window the panel is always shown and has no title or arrow.
- **Playback control section** (the top bar of the right pane). These are the playback buttons: ◀◀ rewind to the
  beginning, −15s, ▶ / ❚❚ play/pause, +15s, and ▶▶ fast-forward to the end. Next to them are a draggable progress bar
  and the elapsed / total time, then, a little apart at the right end, **⤢ Max**, which shows only the lyrics (see
  [Maximized lyrics](#maximized-lyrics)). In the smartphone layout the buttons are smaller, the time and **⤢ Max** are at
  the right end of the button row (on a row of their own on a very narrow screen, about 320 px), and the progress bar
  is always on a row of its own below them.
- **Song navigation section** (below the playback controls)
  - **◀ Prev / Next ▶** go to the previous or next movement. If music is playing, the new movement starts playing.
  - **Now playing** shows the work title and the movement number and title, then both translations (if any)
    after them, without parentheses, e.g. "安魂曲 I. 永远安息  Requiem I. Eternal Rest". It follows the **Show**
    check boxes: with only Original checked it shows "安魂曲 I. 永远安息", and with only Translation checked
    "Requiem I. Eternal Rest" (a title without a translation shows its original). While the lyrics panel shows two
    columns, the song navigation bar is split the same way: the original titles are centered over the original lyrics and the
    translations over the translations. Dragging the divider moves both.
- **Song playing section (lyrics)**
  - **Movement heading.** The number and title, then the subtitle (e.g. the Bible references) and the voicing.
  - **Lyric lines.** The current line has a gold left border, a tinted background and a larger font. Up to 4 lines
    above and 4 below it use the "above" and "below" colors. Lines further away are faded. The current line is kept
    centered vertically. In the smartphone layout the lines are half the size they are in a wider window (maximized
    too); **A− / A+** scale them from there.
  - **Translation.** If any line of the movement has a `"translation"` (see
    [Flow: modifying lyrics](#flow-modifying-lyrics)), the panel is divided into two columns: the original lyrics on
    the left and the translation on the right. The column with the Chinese lyrics gets 45% of the width and the other
    column the remaining 55%, since Chinese usually needs less room. The work's `language` and `translationLanguage`
    in `work.js` tell which column that is: for 安魂曲 (`language: "zh"`) the left one, for Messiah
    (`translationLanguage: "zh"`) the right one. If neither is Chinese, the original gets the 45%.
    Each line and its translation share one row, so they are highlighted
    together and stay level even when one of them wraps. The translation column has its own movement heading, made from
    the movement's `titleTranslation`, `subtitleTranslation` and `voicingTranslation` in `work.js`. Movements without
    translations keep one full-width column.
  - **Original / Translation check boxes.** Both are checked by default, which gives the two columns above. Uncheck
    **Translation** to show only the original lyrics, or **Original** to show only the translation, each in one
    full-width column. With only Translation checked, a line without a translation shows its original text, and so
    does a movement with no translations at all. At least one box must stay checked, so the last checked box is
    disabled. The highlighted line stays the same when you change them. The choice applies to every movement and is
    not saved: reloading the page checks both again.
  - **Divider.** Drag the line between the two columns to change their widths (from 20% to 80% for each column).
    It turns gold under the mouse. Double-click it to go back to 45% for the Chinese column. The new width belongs to
    the Chinese column, so it keeps it when you go to a work that has its Chinese lyrics on the other side. It is kept in the
    URL parameter `chinese-width` (a percent, 20 to 80), so reloading or sharing the link restores it.
  - **Picture.** The movement's picture (`thumbnail`) covers the lyrics until playback starts, with "▶ Click to play".
    It is a placeholder for the lyrics panels: it has exactly their size (the same side margins) and, while the lyrics
    are bilingual, the same two columns and divider, with the picture in the original-language column and the hint in
    the other. It is hidden while the music plays so it never makes the lyrics hard to read.
- **Bottom info pane.** Shows the artist's name, the work's title with its opus number and year, the premiere
  (`Premiere: …`) and the work's description.

## Playing music

1. In the left tree, open an artist and then a work, and click a movement. Its lyrics, picture and work information
   appear.
2. Click the picture, or press ▶ or Space, to play.
3. When a movement ends, the next one starts automatically.

The default page, `index.html`, plays the recording's sound (see below). To show the timed lyrics with no sound,
open `index1.html` instead.

### Silent and sound pages

- **`index.html` (default)** is the player with the visible **Mute** check box, unchecked by default. Check it to
  silence the audio, or open the page with `?mute=1`.
- **`index1.html`** is the player with the audio always silent. The Mute check box is hidden and locked, the
  `mute` URL parameter is ignored, and the music still plays silently, so the lyrics, progress bar and keyboard work
  as usual. This suits showing the timed lyrics while the music is performed live. The audio is not muted at the
  element level: on phones a muted `<audio>` element has no audio output to keep time with, and its position races to
  the end of the movement when ▶ is pressed. So the page plays the audio normally into a Web Audio gain node set to
  0, which keeps a real output clock running while nothing is heard (it falls back to muting where Web Audio is
  missing).

The two pages differ only in that check box (and the page title); both use the same `app.js` and `common.css`.

Prev, Next and auto-advance use the **data order**: artists as listed in `APP_DATA.artistFiles` in `app.js`, works
as listed in each artist's `workFiles`, then movements as listed in `work.js`. This order can differ from the
alphabetical order of the tree.

If a movement's MP3 file is missing, its lyrics still display. The browser console logs a warning.

## Lyrics highlight modes

Choose a mode with **Lyrics: Auto | Manual** at the bottom of the left pane. The player starts in Manual; to start in
Auto, add the URL parameter `?highlight-mode=auto`.

| | **Auto** | **Manual** (default) |
|---|---|---|
| What moves the highlight | The audio position | The operator: ↓ / → for the next line, ↑ / ← for the previous one, or a click on any line |
| Clicking a lyric line | Jumps the audio to that line's start (see below) | Highlights that line and jumps the audio to its start (not while recording) |
| ← / → keys | Seek 5 s (15 s with Shift) | Previous / next line |
| Typical use | Listening to a recording | Live singing, or [recording the timing](#flow-timing-the-lyrics) |

How Auto mode chooses the current line:

1. If the movement has times (from its `.timing.js` file or recorded in this browser), the current line is the one
   with the latest start time at or before the audio position. Lines without a time are skipped. Before the first
   timed line, no line is highlighted.
2. If the movement has no times at all, the lines are spread evenly over the length of the audio. This is a rough
   approximation.

Clicking a lyric line (in either mode) jumps the audio to where that line starts: its time if it has one. A line without
a time is placed evenly between the nearest timed lines before and after it, or the start and end of the audio where
there are none. With no times at all, that is the same even spread as rule 2.

On a touch screen, Manual mode has no arrow keys, so **swipe** on the lyrics instead: up or left for the next
line, down or right for the previous one (at least 40 px). Tapping a line still highlights it. The lyrics do not
scroll by touch in Manual mode; the highlighted line is kept centered.

In Manual mode, a hint (`↓→ next ↑← back`) shows in the corner of the lyrics. The movement starts with no line
highlighted, and the first ↓ highlights line 1; if you press play first, the line being played is highlighted
instead (not while recording), and from then on you move the highlight. Holding a key down advances only one line. ◀◀ (rewind to the
beginning) clears the highlight. Stepping through lines also hides the picture, so lyrics can be shown without any
audio, for example for live singing. When you switch back to Auto, the highlight returns to the audio position.

## Maximized lyrics

**⤢ Max** (in the playback controls) hides the left pane, the playback controls, the info pane and the song navigation buttons. Only the "now playing"
title and the lyrics remain, in a larger font. This suits projecting lyrics for an audience. The keyboard still works:
Space plays and pauses, and the arrow keys seek or step through lines. **Esc**, or the **Norm** button (arrows
pointing in, at the top right), restores the normal layout.

## Keyboard shortcuts

| Key | Auto mode | Manual mode |
|---|---|---|
| Space | Play / pause | Play / pause |
| ← / → | Back / forward 5 s | Previous / next lyric line |
| Shift + ← / → | Back / forward 15 s | Previous / next lyric line |
| ↑ / ↓ | — | Previous / next lyric line |
| Esc | Leave maximized lyrics | Leave maximized lyrics |

The shortcuts also work after you have dragged the progress bar. They do not apply while you are typing in a text
field.

## Configuration (URL parameters)

Add parameters to the page URL. Colors are any CSS color, and `#` must be written as `%23`.

| Parameter | Sets | Default |
|---|---|---|
| `above-color` | Text color of the lines above the current line | `#7f94b0` |
| `above-bg` | Background of the lines above the current line | `transparent` |
| `below-color` | Text color of the lines below the current line | `#7f94b0` |
| `below-bg` | Background of the lines below the current line | `transparent` |
| `highlight-mode` | `auto` starts in Auto mode; anything else starts in Manual | `manual` |
| `movement` | The movement selected on load, as `<artist id>/<work id>/<movement id>` (the `id`s in `artist.js` and `work.js`). The app rewrites it whenever you select a movement, so reloading or sharing the URL opens that movement | the first movement in the tree |
| `t` | The audio position of the `movement` above, in whole seconds (rounded down), e.g. `83` (used only with `movement`). The app rewrites it about once a second while the audio plays or you seek, so reloading or sharing the URL continues from there; it is removed when you select another movement | `0` |

For example:

```
index.html?above-color=%238888aa&below-color=%23aaaaaa&below-bg=rgba(0,0,0,0.2)&highlight-mode=auto
```

Three settings have no URL parameter yet, so you change them in the source:

- **Current line colors.** `--lyrics-current-color`, `--lyrics-current-bg` and `--lyrics-current-border` at the top
  of [common.css](common.css).
- **Default width of the Chinese-lyrics column** when a movement has translations. `--lyrics-chinese-width` at the
  top of [common.css](common.css), `45%`, and `DEFAULT_CHINESE_WIDTH` in [app.js](app.js), which must match. The other column gets the rest. To change
  it for one link only, use `?chinese-width=` or [drag the divider](#screen-layout).
- **Number of lines above and below.** This is the `4` in `highlightLyricLine()` in [app.js](app.js). Lines further
  away are faded.

## Flow: timing the lyrics

Timing means giving each lyric line the moment it starts in the MP3. Auto mode then highlights the lines exactly. You
record the times in the app by pressing a key as each line starts.

### 1. Record

1. Open the **LYRICS TIMING** panel with the `^` button near the bottom of the left pane.
2. Select the movement. The panel shows how many lines are timed (for example `22 / 37 lines timed`) and where the
   times come from: the `.timing.js` file or `this browser`.
3. Click **● Rec**. This switches to Manual mode, and `● REC` appears in the lyrics corner.
4. Play the audio. As each line **starts** to be sung, press **↓** (or **→**). The highlight moves to that line, and
   the line gets the current audio time.
5. Made a mistake? Press **↑** to go back. Going back records nothing, and advancing again overwrites the time.
6. Click **■ Stop** to end recording. Switching to Auto also stops it.

Recording rules:

- A time is recorded only while the audio is **playing**, and only when you move **forward**.
- Clicking a line works like the keys: it moves the highlight there and records that line's time. While recording,
  a click does not move the audio.
- Each recording builds on the existing times, so you can redo just part of a movement. Use ↑ to put the highlight
  on the line before the part, move the audio to a little before it with the progress bar or −15s, press play, and
  continue with ↓.
- Each recording is saved immediately in the browser's `localStorage`, so it survives a reload.
- A browser recording **overrides the file's times** (never its text) until you **Clear** it.

### 2. Check

Switch to **Auto** and play. Clicking a timed line jumps the audio to that line's start time, which is a quick way to
check single lines.

### 3. Save to the project

Only the `.timing.js` file beside the MP3 goes into the project. A browser recording stays in that one browser.

- **Save** writes the **current** movement's timing as `<mp3 name>.timing.js`, e.g. `Chapter3.timing.js`.
  - In Chrome or Edge, a save dialog opens. Choose the MP3's folder and replace the existing file.
  - In other browsers, the file is downloaded. Move it next to the MP3 yourself.
- **Export to MP3 folders** writes **every** movement that has a timing in this browser in one go. The button shows
  how many there are.
  - In Chrome or Edge, pick the app folder (the one that contains `index.html`) or the MP3's folder. Each file is
    written next to its MP3, and the folder is remembered until the page is reloaded.
  - In other browsers, each file is downloaded. Move each one next to its MP3.
- Saving keeps the text of the lyrics as it is in the file and writes only the new times.

### 4. Tidy up and commit

1. Click **Clear** for the movement. This discards the browser recording, so the app goes back to the file you just
   saved. If you skip it, the old browser recording keeps overriding any later edits to the file's times.
2. Reload the page and confirm that the panel shows `… lines timed · ChapterN.timing.js`.
3. Commit the `.timing.js` file.

### Other timing buttons

- **Load** imports one or more `.timing.js` files (or the older `.timing.json` files) into this browser as
  recordings. You might use it for files a collaborator sent you. Each file names its own movement, so it does not
  matter which movement is selected. After loading, Save or Export them as above.
- **Clear** discards this browser's recording for the current movement and goes back to the times in the file. It
  asks for confirmation first.
- **Clear all** does the same for **every** movement that has a recording in this browser. It asks for confirmation
  first, and is disabled when there is nothing to clear. Use Export first if you want to keep the recordings.

## Flow: modifying lyrics

A movement's lyrics exist in only one place: the `.timing.js` file next to its MP3, e.g.
`assets/HuangAnlun/ChineseRequiem/Chapter1.timing.js`. The app has no other copy. Files such as `Lyrics.txt` are
source material only, and the app does not read them.

1. Edit the text in the `.timing.js` file. Each lyric line is one row:

   ```javascript
       {"time":0.1,"text":" ( Prayerfully 以祷告的心 )"},
       {"time":2.2,"text":"求主"},
       {"time":null,"text":"赐他们永远"},
   ```

   - `"time"` is the line's start in seconds, or `null` if the line has not been timed yet.
   - Each time belongs to the row it is on. When you add or remove a line, add or remove its time with it. A new line
     can start as `"time":null`.
   - Each row is a JavaScript object, and everything inside `onePageMp3Timing(...)` must be valid **JSON**: Save
     writes it with `JSON.stringify`, and **Load** reads it with `JSON.parse`. So put names and strings in double
     quotes (`"time"`, not `time` or `'time'`), separate rows with commas but put none after the last row, and do not
     add comments. A file that breaks these rules may still play, but **Load** rejects it.
   - To show a translation beside a line, add `"translation"` to its row. Rows without one leave the right column
     empty:

     ```javascript
         {"time":2.2,"text":"求主","translation":"O Lord,"},
     ```

     **Save** and **Export** keep the translations.
2. If this browser has a recording for the movement (the panel says `· this browser`), click **Clear**. A recording
   matches times to lines by **position**, so after lines are added or removed its times would land on the wrong
   lines.
3. Reload the page and check the lyrics.
4. Time any new or changed lines as described in [Flow: timing the lyrics](#flow-timing-the-lyrics).

## Flow: adding an artist, work or movement

The paths to `artist.js` files (`artistFiles` in `app.js`) are relative to `index.html`. The `workFiles` in an
`artist.js` file are relative to that `artist.js` file, a movement's `audio` and `thumbnail` in a `work.js` file
are relative to that `work.js` file, and the `audio` in a `.timing.js` file is relative to that `.timing.js` file, so
they are short when the files sit next to each other.

### 1. Put the media in place

```
assets/<Artist>/artist.js
assets/<Artist>/<Work>/work.js
assets/<Artist>/<Work>/Chapter1.mp3        # audio
assets/<Artist>/<Work>/Chapter1.jpg        # picture shown before playback (optional)
assets/<Artist>/<Work>/Chapter1.timing.js  # lyrics + timing (optional: no file = no lyrics)
```

### 2. Describe the artist — `assets/<Artist>/artist.js`

```javascript
/* Artist data for OnePageMP3: loaded by app.js from APP_DATA.artistFiles */
onePageMp3Artist({
  id: "anlun-huang",              // unique; used in each .timing.js "composer" field
  name: "黄安伦",                  // shown in the tree and info pane
  nameSort: "Huang, An-Lun",      // tree sort key (optional; defaults to name)
  bio: "黄安伦（1949–），加拿大华人作曲家。",  // kept with the data; not displayed yet
  workFiles: [
    "ChineseRequiem/work.js"
  ]
});
```

### 3. Describe the work — `assets/<Artist>/<Work>/work.js`

```javascript
/* Work data for OnePageMP3: loaded by app.js from its artist's workFiles list */
onePageMp3Work({
  id: "chinese-requiem",          // unique; used in each .timing.js "work" field
  title: "安魂曲",                 // shown in the tree, top bar and info pane
  titleTranslation: "Requiem",    // top bar: "安魂曲 I. 永远安息  Requiem I. Eternal Rest" (optional)
  titleSort: "Chinese Requiem",   // tree sort key (optional; defaults to title)
  language: "zh",                 // language of the lyrics' "text"; the "zh" column gets 45% of the lyrics width
  translationLanguage: "en",      // language of the lyrics' "translation"
  year: 2004,                     // info pane: "title Op. 63 (2004)"
  opusNumber: "Op. 63",
  premiered: "Toronto, May 2004", // info pane: "Premiere: Toronto, May 2004"
  description: "…",               // info pane; "\n" starts a new line
  movements: [
    {
      id: "ch1",                  // unique within the work; used in the .timing.js "movement" field
      number: "I",
      title: "永远安息",
      titleTranslation: "Eternal Rest",  // top bar, after the original titles; translation column's heading (optional)
      subtitle: "诗篇116:7,9",     // lyrics heading, in [brackets] (optional)
      subtitleTranslation: "Psalm 116:7,9",  // translation column's heading (optional)
      voicing: "合唱",             // lyrics heading, second line (optional)
      voicingTranslation: "Chorus",          // translation column's heading (optional)
      audio: "Chapter1.mp3",
      thumbnail: "Chapter1.jpg"   // optional
    }
  ]
});
```

### 4. Register a new artist in `app.js`

Add the artist's `artist.js` to `APP_DATA.artistFiles` at the top of [app.js](app.js). A new work only needs adding to
its artist's `workFiles`, and a new movement only to its work's `movements`.

```javascript
artistFiles: [
  "assets/AnlunHuang/artist.js",
  "assets/Handel/artist.js",
  "assets/Mahler/artist.js",
  "assets/Mozart/artist.js",
  "assets/<Artist>/artist.js"
],
```

### 5. Add the lyrics — `<mp3 name>.timing.js`

Create the file next to the MP3 with every line untimed, then
[record the timing](#flow-timing-the-lyrics):

```javascript
onePageMp3Timing({
  "format": "onepagemp3-lyrics-timing",
  "version": 1,
  "composer": "anlun-huang",
  "work": "chinese-requiem",
  "movement": "ch1",
  "audio": "Chapter1.mp3",
  "lines": [
    {"time":null,"text":"first line"},
    {"time":null,"text":"second line"}
  ]
});
```

`"audio"` is the MP3's name, relative to the `.timing.js` file beside it. It is for information only: the app finds
the `.timing.js` file from the movement's `audio` in `work.js`.

> **The three ids must match exactly.** `"composer"`, `"work"` and `"movement"` must equal the `id` in `artist.js`,
> the `id` in `work.js` and the movement's `id`. If any of them differs, the app ignores the file, shows **no
> lyrics**, and logs only a console warning (`… is not the timing of …`).

### 6. Check

Reload the page. The new entries should appear in the tree. If something is missing, open the browser console. A file
that is missing or broken is skipped with a warning (`Cannot load …`, `… did not call onePageMp3Work(...)`, and so
on), and the rest of the app keeps working.

## Data files reference

| File | Wrapper call | Holds | Loaded |
|---|---|---|---|
| `assets/<Artist>/artist.js` | `onePageMp3Artist({...})` | Artist: id, name, nameSort, bio, workFiles | At startup, from `APP_DATA.artistFiles` |
| `assets/<Artist>/<Work>/work.js` | `onePageMp3Work({...})` | Work: id, title, titleSort, language, translationLanguage, year, opusNumber, premiered, description, movements | At startup, from the artist's `workFiles` |
| `<mp3 name>.timing.js` | `onePageMp3Timing({...})` | The movement's lyrics, one `{time, text, translation}` per line (`translation` optional) | When the movement is first selected |

Each file contains one call to a function that `app.js` defines, so it can be loaded with a `<script>` tag. This works
from `file://`, where `fetch` does not.

Precedence for times is: the browser recording (`localStorage` key `onepagemp3.timing:<artist id>/<work id>/<movement id>`),
then the `.timing.js` file, then even spacing. The lyrics **text** and **translations** always come from the `.timing.js` file.

## Project structure

```
index.html                 page markup only; the default page, with the visible Mute box, for listening
index1.html                same page with the audio always silent (the Mute box is hidden and locked)
common.css                 all styles; color variables at the top
app.js                     all behavior; APP_DATA.artistFiles at the top
assets/
  AnlunHuang/              黄安伦 — Chinese Requiem (安魂曲, Op. 63), 8 movements
    artist.js
    ChineseRequiem/
      work.js
      Chapter1..8.mp3      audio
      Chapter1..8.jpg      pictures
      Chapter1..8.timing.js  lyrics + timing
      Lyrics.txt, *.pdf, *.md  source material and notes (not read by the app)
  Handel/                  亨德尔 — Messiah (弥赛亚, HWV 56), 9 movements: one per band of the 1966 Philips LP set
    artist.js              (Colin Davis, London Symphony Orchestra), from the Internet Archive
    Messiah/
      work.js
      Chapter1..9.mp3      audio: Overture, then Nos. 1–52 in 8 tracks
      Handel.jpg           picture shared by all movements (Thomas Hudson's 1749 portrait, public domain)
      Chapter1..9.timing.js  lyrics: English libretto as sung (repeats included) + 和合本 translation, a heading
                           line per number; timed from a Whisper transcription of the recording
    MessiahChinese/        弥赛亚（中文版）: the same oratorio sung in Chinese (performers unknown), from
      work.js              https://www.bilibili.com/video/BV1eb4y1h7Va/, in the same 9 chapters as Messiah/
      Chapter1..9.mp3      audio: Nos. 1–55 as numbered in the video (Sinfonia = No. 1, Amen = No. 55)
      Chapter1..9.timing.js  lyrics: Chinese as sung + English libretto, timed from the video's subtitles;
                           the picture is Messiah/Handel.jpg
  Mozart/                  莫扎特 — Requiem (安魂曲, K. 626), 6 movements: one per band of the 1971 Deutsche
    artist.js              Grammophon LP (Karl Böhm, Wiener Philharmoniker), from the Internet Archive
    Requiem/
      work.js
      Chapter1..6.mp3      audio: Nos. 1–7 (side 1) in one track, then Nos. 8–12 one track each
      Mozart.jpg           picture shared by all movements (Barbara Krafft's 1819 portrait, public domain)
      Chapter1..6.timing.js  lyrics: Latin text + Chinese translation, a heading line per number
    Symphony40/            example entry (its audio and lyrics are a placeholder copy of Chinese Requiem I)
  Mahler/                  example entry that shows the layout for more artists
                           (its audio and lyrics are a placeholder copy of Chinese Requiem I)
workItems/                 work items: draft / todo / wip / completed / blocked / archived
CLAUDE.md, CLAUDE_engineering.md   instructions for the AI assistant
```

## Browser notes

- Use a current version of Chrome, Edge, Firefox or Safari.
- **Save** straight into a folder, and **Export to MP3 folders**, need the File System Access API (Chrome or Edge).
  Other browsers download the files instead.
- Browser recordings are stored **per browser and per origin**. A recording made with the page opened as `file://`
  is not visible at `http://localhost:…`, and the other way round. It is also not visible in another browser. Save or
  Export a recording to keep it.
- Some browsers block audio until you interact with the page. If playback does not start on its own, click ▶.

## Development workflow

Tasks are tracked as Markdown work items under `workItems/` (`draft` → `todo` → `wip` → `completed`, plus `blocked` and
`archived`). See [CLAUDE_engineering.md](CLAUDE_engineering.md) for the conventions.
