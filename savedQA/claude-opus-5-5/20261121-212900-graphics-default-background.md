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
