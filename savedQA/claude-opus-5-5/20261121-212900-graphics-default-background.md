# Graphics as the default background

## Ask

> Use Grahpics as defult background

## Answer

Changed the lyrics background's default from **None** to **Graphics** (used when the URL has no valid `bg`
parameter). `?bg=none` and `?bg=image` still pick the other modes.

- `app.js`: `setBackground(...)` at startup falls back to `'graphics'` instead of `'none'`; the VIEW OPTIONS IN URL
  list and the BACKGROUND comment now say Graphics is the default (the BACKGROUND comment had wrongly said Image).
- `README.md`: the Background section and the `bg` row of the URL parameter table say `graphics` by default; the
  `serve` note's example link uses `bg=image`, since `bg=graphics` would no longer differ from the default.
- Both `index.html` and `index1.html` use `app.js`, so both pages get the new default.

Checked in headless Chrome: no `bg` → Graphics button active and `data-bg="graphics"`; `?bg=none` and `?bg=image`
still select None and Image.

## Ask

> use the 80% of the current lyrics font size as default

## Answer

The lyrics font size now starts at **80%** (`--lyrics-font-scale: 0.8`) when the URL has no `font` parameter, and
clicking the percentage resets it to 80% rather than 100%. A− / A+ still step by 10% (10%–250%), and `?font=100`
gives the old size.

- `app.js` (LYRICS FONT SIZE): a `DEFAULT_PCT = 80` constant for the starting value, the reset and the URL fallback;
  the comments and the VIEW OPTIONS IN URL list say default 80.
- `index.html`, `index1.html`: the label's initial text is `80%`.
- `README.md`: the Lyric lines item gives the 80% default, the reset and the `font` URL parameter.

Checked in headless Chrome: no `font` → 80% and scale 0.8; `?font=120` → 120% and scale 1.2.

## Ask

> When a movement is selected, currently the background of the movement is displayed in the left lyrics panel, extend
> to right panel (use the full width of the lyrics area)

## Answer

The picture shown before playback (the thumbnail overlay, in the None and Graphics background modes) now spans the
full width of the lyrics area. With bilingual lyrics it used to sit in the original-language column only, with the
caption and "▶ Click to play" in the translation column. Now it is centered across both columns, scaled to fit whole
(scaled up too, so e.g. a 909×606 painting fills the height), with the caption and hint centered at the bottom, as
with one column. Image mode is unchanged: there the movement's picture already filled the whole song area.

- `common.css`: removed the overlay's two-column grid, its second panel and divider, and the bilingual offset of the
  caption/hint (plus Image mode's override of that offset, no longer needed). The overlay `img` is now
  `width/height: 100%` with `object-fit: contain` instead of `max-width/max-height: 100%`.
- `index.html`, `index1.html`: removed the empty `.thumbnail-panel-2` and updated the overlay comment.
- `README.md`: the Picture item describes the full-width picture.

Checked in headless Chrome (1400×900) on 安魂曲 I, image sets 1 and 2: the picture spans both columns with the
caption and hint centered under it. A browser that cached the old `common.css` may need a hard reload.
