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
