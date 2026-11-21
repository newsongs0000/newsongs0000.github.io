# Configurable lyrics background (graphics or static image)

## Ask

> Enable configuring background, either by graphics or static image

## Response

Added a configurable background behind the lyrics panel with three choices: **None**, **Graphics** and **Image**.

### How to use it

- **View Options → Background: None | Graphics | Image** (a new last row in the left pane, on `index.html` and
  `index1.html`). It's also in the phone layout's collapsible View Options panel.
- URL parameters:

| Parameter | Meaning | Default |
|---|---|---|
| `bg` | `none`, `graphics` or `image`; rewritten when a button is clicked | `none` |
| `bg-image` | One picture for every movement (path relative to `index.html`, or a URL) | — |
| `bg-dim` | Percent of the page color laid over the background (0–95) | `75` |
| `bg-blur` | Blur of the picture in px (0–40) | `10` |

- `work.js` accepts an optional per-movement `background: "file.jpg"` (relative to `work.js`, like `thumbnail`).

### Behavior

- **Graphics**: three soft radial lights (two in a per-movement hue between cyan and magenta, one in the accent gold)
  that drift only while the audio plays. Only transforms are animated, so it is cheap. They stand still when the
  system's reduce-motion setting is on.
- **Image**: the picture is chosen in this order: `bg-image`, then the movement's `background`, then its `thumbnail`.
  It is cover-fitted, blurred and dimmed. A movement with no picture, or one that fails to load, gets the graphics
  instead. When the next movement uses the same picture (e.g. Handel.jpg for all of Messiah), it is kept and doesn't
  flash.
- Readability: the page color covers the background at `bg-dim`, and the lyric lines get a soft text shadow in
  graphics and image modes. The default dimming went from 65% to 75% after testing: Chapter2.jpg (a white score page)
  left the lighter lyric lines at only about 3:1 contrast at 65%.

### Files changed

- `index.html`, `index1.html`: the `#background-toggle` row and the `#lyrics-bg` layer in `#song-display`.
- `common.css`: `--bg-dim` and `--bg-blur` defaults; the background layer (an isolated stacking context with
  `z-index: -1`), the graphics and keyframes, the text shadow and the toggle row styles.
- `app.js`: a new BACKGROUND section (`setBackground`, `updateBackground`, `backgroundHue`, bg-dim and bg-blur parsing).
  `loadMovement` calls `updateBackground()`, `showPlaying` toggles `.playing`, `resolveWorkPaths` resolves
  `background`, and the URL docs list the new parameters.
- `README.md`: the screen layout diagram, the left pane and Background descriptions, the configuration table, the
  `work.js` example and the relative-path note.

### Verified (headless Chrome)

- All three modes at 1280×800, including bilingual Messiah with the Handel portrait, maximized lyrics on
  `index1.html`, and a 390×844 phone layout.
- A missing `bg-image` falls back to the graphics, `bg=bogus` falls back to `none`, an invalid `bg-dim` keeps the
  default, and `bg-blur=999` is clamped to 40px.
- The URL's `bg` parameter follows the buttons.

---

## Ask

> Make image background option as default

## Response

Image is now the default background. A URL without `bg`, or with an invalid value, starts in Image mode and writes
`bg=image` to the URL. `bg=none` and `bg=graphics` still pick the other modes.

- `app.js`: `setBackground(...)` at the end of the BACKGROUND section now falls back to `'image'`. The comments in
  BACKGROUND, VIEW OPTIONS IN URL and CONFIGURATION say so.
- `README.md`: the Background description and the `bg` row of the configuration table give `image` as the default.

Verified in headless Chrome: a plain `index.html` loads with `bg=image`, the Image button pressed and Handel.jpg
showing. `?bg=none` still gives a plain background.

---

## Ask

> On mobile devices, the style of the first 5 buttons in the playback-controls panel are different from desktop, make
> them as desktop

## Response

The five playback buttons (◀◀, −15s, ▶ / ❚❚, +15s, ▶▶) now look the same on a phone as on a computer.

- **Size**: removed the smartphone overrides in `common.css`. On a phone, portrait or landscape, they had 3px 6px
  padding and 0.66rem text, with 3px 8px and 0.78rem for play. They now use the desktop size: 4px 8px and 0.72rem,
  with 4px 12px and 0.88rem for play. The row's slightly tighter spacing on a phone (3px gap, less side padding) stays.
- **Glyphs**: iPhone Safari tends to draw ◀ (U+25C0) and ▶ (U+25B6) as emoji, in a colored box. Each triangle in these
  buttons is now followed by U+FE0E (text presentation), in `index.html`, `index1.html` and the ▶ icon that
  `showPlaying` in `app.js` writes, which the maximized play button shares. A computer already drew them as text, so
  nothing changes there.
- `README.md`: says the smartphone buttons look as they do on a computer.

Verified in headless Chrome with touch emulation (pointer: coarse). The buttons have the desktop font size and padding
at 390, 360 and 320 px portrait and at 844×390 landscape. At 390 and 360 px the buttons, time and Max fit on one row.
At 320 px the time and Max wrap to their own row, as the README already describes. In landscape the progress bar keeps
225 px.

Not changed: Prev / Next keep their smaller phone size, and their ◀ ▶ could still show as emoji on an iPhone.

---

## Ask

> Find different background image for different movements if you can find on internet; if you can't find any more,
> just use the same ones.

(Mid-way: "downloading is stuck?")

## Response

Every movement now has its own Image background. That's 23 pictures for 32 movements: the Chinese Messiah reuses the
English Messiah's, movement for movement. Each is a painting from Wikimedia Commons whose subject fits the movement's
text. All are public domain except El Greco's *Christ Healing the Blind*, which the Met released as CC0.

| Movement | Picture |
|---|---|
| Messiah I Overture | Holman Hunt, *The Light of the World* |
| Messiah II Comfort ye (Isaiah 40) | Michelangelo, *Isaiah* (Sistine ceiling) |
| Messiah III Nos. 7–15 (the shepherds) | Govert Flinck, *Angels Announcing the Birth of Christ to the Shepherds* |
| Messiah IV the eyes of the blind | El Greco, *Christ Healing the Blind* |
| Messiah V Behold the Lamb of God | Zurbarán, *Agnus Dei* |
| Messiah VI the Passion | Velázquez, *Christ Crucified* |
| Messiah VII Hallelujah | Christ Pantocrator, Deesis mosaic, Hagia Sophia |
| Messiah VIII I know that my Redeemer liveth | Piero della Francesca, *Resurrection* |
| Messiah IX Worthy is the Lamb | van Eyck, *Adoration of the Mystic Lamb* |
| Mozart I Dies irae … Lacrimosa | Michelangelo, *The Last Judgment* |
| Mozart II Domine Jesu (St Michael) | Guido Reni, *St Michael* |
| Mozart III Hostias (prayers) | Dürer, *Praying Hands* |
| Mozart IV Sanctus | Doré, *Paradiso* Canto 31 (the heavenly rose) |
| Mozart V Benedictus | Giotto, *Entry into Jerusalem* |
| Mozart VI Lux aeterna | Bosch, *Ascent of the Blessed* |
| 安魂曲 I 永远安息 | 黄公望《富春山居图》 |
| 安魂曲 II 深处祷告 | 范宽《溪山行旅图》 |
| 安魂曲 III 称颂耶稣 | 王希孟《千里江山图》 |
| 安魂曲 IV 圣洁颂歌 | 郭熙《早春图》 |
| 安魂曲 V 羔羊赞颂 | 赵孟頫《二羊图》 |
| 安魂曲 VI 永享自由 | 宋徽宗《瑞鹤图》 |
| 安魂曲 VII 永远照耀 | 马远《水图·云生苍海》 |
| 安魂曲 VIII 诗篇二十三 | 赵孟頫《鹊华秋色图》 |

- Files: `assets/<Artist>/<Work>/ChapterN-bg.jpg`, each cropped to 3:2 around its subject (a face, the Lamb, the
  light) and saved 1024 px wide at JPEG quality 50. They total 3.5 MB; a blurred background needs no more.
- `work.js`: every movement has a `background`. `MessiahChinese` uses `../Messiah/ChapterN-bg.jpg`.
- Credits: a `backgrounds.md` in each work folder lists every file with the movement text it illustrates, the Commons
  page, the artist, the date and the license.
- `README.md`: the Background section and the project structure mention the new pictures.

On "downloading is stuck?": yes. Commons kept answering HTTP 429 (too many requests) for non-standard thumbnail sizes
(e.g. 1098 px) and for downloads of original files, and the script kept waiting and retrying. Changing it to request
only Wikimedia's standard thumbnail widths fixed it. A second problem: `sips` treats a crop offset of 0 as "center",
which cut Isaiah's head off. The crop now starts at 1 px.

Verified in headless Chrome: all 32 movements load their own picture, and Messiah V and 安魂曲 VI stay readable behind
the lyrics.

---

## Ask

> New background images are not showing, both local server and remote, I also restarted local server

## Response

Both servers did serve the new pictures, and the page loaded them: in headless Chrome `Chapter1-bg.jpg` loaded
(1024 px) on GitHub Pages and on the local `npx serve`. They weren't visible in practice:

1. **Before playback** the "▶ Click to play" overlay covered the lyrics area with an opaque panel holding the
   movement's `thumbnail`. That is still the same composer portrait for every movement, so the new pictures never
   showed there.
2. **During playback** the picture showed, but darkened 75% and blurred 10 px, which made a painting like *The Light of
   the World* an unrecognizable dark blur.

Changes:

- **Image mode before playback** (`common.css`): the overlay becomes see-through (no thumbnail, no opaque panel), so
  the movement's painting fills the lyrics area, sharp and not dimmed, with "▶ Click to play" centered over it. The
  lyrics stay hidden until playback, as before. When the music starts the painting blurs and dims over 0.8 s while
  the lyrics fade in. In None and Graphics modes, and for a movement without a picture, the usual thumbnail overlay
  shows.
- **Lighter defaults**: `--bg-dim` went from 0.75 to 0.7 and `--bg-blur` from 10px to 4px, so the painting stays
  recognizable behind the lyrics. Checked on a dark painting (Holman Hunt), a light silk painting (Huang Gongwang)
  and Dürer's blue paper: the current and nearby lines stay clearly readable. `app.js` comments and the README table
  were updated to match.
- The "Click to play" pill is now 80% black (was 55%), so it stays readable over a light painting.
- README: the Picture and Background descriptions explain the pre-play view. A note under "Running an HTTP server"
  explains that `npx serve` redirects `/index.html?…` to `/index` and drops the parameters (confirmed with `curl -I`:
  `301 Location: /index`), so local links should leave out `index.html` or use `http-server`.

The remote (GitHub Pages) needs these changes committed and pushed.

---

## Ask

> After I asked you "On mobile devices, the style of the first 5 buttons in the playback-controls panel are different
> from desktop, make them as desktop", you fix 4 of them, only the btn-play-pause button is still different

## Response

The play button's CSS was already the same on desktop and phones: same rules, and the same measured size in headless
Chrome at phone sizes. What still differed was the device:

1. **Its icons were font characters.** ▶ (U+25B6) and the pause bars ▮▮ (U+25AE) are not in Georgia, so every device
   draws them from its own fallback font. The play button shows them larger than the other buttons (0.88rem) and
   swaps them while playing. On a phone the fallback glyphs can differ in shape, weight and width. Even on desktop the
   button jumped from 38 px wide (▶) to 43 px (▮▮).
2. **Touch screens keep `:hover` after a tap**, so the play button stayed in its lighter hover gold after being tapped.

Fix:

- The play and pause icons are now inline SVG drawings (`PLAY_ICON` / `PAUSE_ICON` in `app.js`, written by
  `showPlaying`; the initial ▶ in `index.html` and `index1.html`), the same approach as the Max button's icon. No
  font is involved, so every device draws them the same. Both are 1em square, filled with the text color. The
  triangle is sized to match the old desktop ▶.
- The padding went from 12px to 11px, so the button is 38 × 26 px in both states on every device. It no longer widens
  when playback starts.
- `@media (hover: none)`: after a tap, the play buttons keep their normal gold, as on a computer once the mouse moves
  off.
- The maximized view's play button (`#btn-play-pause-max`) gets the same icons and hover rule.

Verified in headless Chrome on desktop and an emulated touch phone (390 px, hover: none), paused and playing: the
button is 38.1 × 26 px everywhere with the icon centered, and after a tap its background stays rgb(201, 162, 39).
