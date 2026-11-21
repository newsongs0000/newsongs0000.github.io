# Work thumbnail, movement background

## Ask

Verify that all movements of the same work have the same thumbnai, if so move thumbnail one level up to work level,
and display the work thumbnail when a work is selected, dispaly the movement background when a movement is selected

## Answer

### Verification

| Work | Movement thumbnails | Result |
|---|---|---|
| Handel / Messiah | `Handel.jpg` in all 9 movements | Same: moved to the work |
| Handel / 弥赛亚 (MessiahChinese) | `../Messiah/Handel.jpg` in all 9 movements | Same: moved to the work |
| Mozart / Requiem | `Mozart.jpg` in all 6 movements | Same: moved to the work |
| Huang An-Lun / 安魂曲 (ChineseRequiem) | ch1 `HuangAnlun.jpg`, ch2–ch8 `Chapter2.jpg` … `Chapter8.jpg` | Different: left on the movements |

### Changes

- **work.js** (Messiah, MessiahChinese, Mozart Requiem): the 24 identical movement `thumbnail` lines were removed and
  replaced by one work-level `thumbnail`.
- **app.js**
  - `resolveWorkPaths` also resolves the work's `thumbnail` relative to its `work.js`.
  - A movement without a `thumbnail` uses its work's. A work without a `thumbnail` (安魂曲) uses its first movement's
    (`HuangAnlun.jpg`).
  - New section **SELECT WORK**: opening a work in the tree selects it, unless music is playing, so browsing the tree
    never stops the music. Closing a work changes nothing. A selected work shows its thumbnail over the lyrics area
    with "▶ Click to play", its titles in the top bar, its information in the info pane, and a highlighted header in the
    tree. Nothing is loaded to play yet. ▶, Space or a click on the picture plays the work's first movement, **Next**
    selects that movement and **Prev** the movement before it.
  - New section **PICTURE BEFORE PLAYBACK**: a selected movement's overlay picture is now its `background`
    (`background2` in image set 2), then its own `thumbnail`, then the work's. If a picture fails to load, the next
    one is tried. Changing the image set also updates the overlay.
  - The URL keeps a selected work as `?work=<artist id>/<work id>` in place of `movement`.
- **common.css**: `.tree-work-header.active` is highlighted like the selected movement.
- **README.md**: updated the tree, picture, background and `work.js` format sections, and added the `work` URL
  parameter.

### Verified in headless Chrome

- Default load: Messiah I is selected and the overlay shows `Chapter1-bg.jpg`.
- Opening Mozart / Requiem shows `Mozart.jpg`, highlights the work header, writes `work=mozart/mozart-requiem` to the
  URL, unloads the audio and enables Prev and Next.
- Clicking movement II shows `Chapter2-bg.jpg`.
- Opening 安魂曲 shows `HuangAnlun.jpg`. Closing it keeps the selection. **Next** selects ch1 (`Chapter1-bg.jpg`), and
  image set 2 switches the overlay to `Chapter1-bg2.jpg`.
- Clicking the picture with a work selected plays its first movement. While music plays, opening another work only
  opens it. Space with a work selected plays its first movement.
- `index1.html?work=handel/messiah-zh&bg=image` opens the work with `Handel.jpg`. Selecting a movement then shows its
  background, sharp and full-size, as Image mode does.
- No console errors.

### Not changed

- 安魂曲 ch1 has `thumbnail1: "An-lun Huang.png"`, which nothing uses, and that file doesn't exist (the folder has
  `HuangAnlun1.png`).
- `assets/HuangAnlun/artist.js` has a `thumbnail` that app.js doesn't use.

## Ask

Can we display the work level thumbnail when a work is selected only when no music is being played?

## Answer

It already works that way, so no code changed. In the tree's work-header click handler (`buildTree` in app.js), the
guard is `if (opened && !state.isPlaying) loadWork(composer, work);`.

- **Music playing:** opening a work only opens it in the tree. The selection, the music and the display stay as they
  are, and the work's thumbnail is not shown.
- **Nothing playing (stopped, paused, or not started):** opening a work selects it, and its thumbnail shows over the
  lyrics area. A movement that was paused is unloaded.
- **Work selected, then playback starts** (▶, Space, or a click on the picture): the work's first movement loads
  and plays, and the picture is hidden, as it always is during playback. So the work's thumbnail is never on screen
  while music plays.

The headless-Chrome test in the first answer covered the playing case: opening Messiah while 安魂曲 I played left
`activeWork` null and the audio playing.

## Ask

Use HuangAnlun.jpg as the work level thumbnail for the work HuangAnlun.jpg,

## Answer

This was taken to mean the 安魂曲 (ChineseRequiem) work, the one whose `work.js` holds `HuangAnlun.jpg`.

- Added `thumbnail: "HuangAnlun.jpg"` at the work level in `assets/HuangAnlun/ChineseRequiem/work.js`.
- Removed the same `thumbnail: "HuangAnlun.jpg"` from movement ch1, which now inherits it from the work. Movements
  ch2–ch8 keep their own thumbnails (`Chapter2.jpg` … `Chapter8.jpg`).

Nothing on screen changes: selecting the work already showed `HuangAnlun.jpg` through the first-movement fallback,
and ch1 still shows `Chapter1-bg.jpg` first, then `HuangAnlun.jpg`. The work's picture is now stated in its own
`work.js` instead of borrowed from ch1. `thumbnail1: "An-lun Huang.png"` on ch1 is left as it was.

## Ask

remove all movement level thumbnail in 安魂曲 (Chinese Requiem),

## Answer

- Removed `thumbnail` from movements ch2–ch8 (`Chapter2.jpg` … `Chapter8.jpg`) in
  `assets/HuangAnlun/ChineseRequiem/work.js`. ch1's had already been moved to the work.
- Also removed ch1's unused `thumbnail1: "An-lun Huang.png"`, which pointed to a file that doesn't exist.
- No movement of 安魂曲 has a thumbnail now. Each shows its `background` (`background2` in image set 2) before
  playback and falls back to the work's `HuangAnlun.jpg`. Selecting the work shows `HuangAnlun.jpg`.
- README: the media list in "Put the media in place" now shows the work's thumbnail and the movement's `-bg.jpg`
  picture, not a movement `Chapter1.jpg`.
- `Chapter1.jpg` … `Chapter8.jpg` are still in the folder and tracked by git, but nothing uses them now. They were not
  deleted.
