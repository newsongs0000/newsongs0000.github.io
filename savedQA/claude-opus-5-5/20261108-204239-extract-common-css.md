# Session 2026-11-08 20:42 — Move CSS into a separate file

## Ask

Carve out common CSS into a separate .css file

## Answer

- The whole `<style>` block of `index.html` (about 500 lines, the app's only CSS) moved to a new file **`common.css`**
  next to `index.html`, with the indentation shifted left by 4 spaces. No rules were changed: comparing the removed
  block with `common.css` while ignoring leading whitespace shows no differences.
- `index.html` `<head>` now has `<link rel="stylesheet" href="common.css">` in place of the `<style>` block
  (index.html: 1670 → 1167 lines).
- The URL-parameter colors still work: JS sets the `--lyrics-*` custom properties on `<html>`, and `common.css`
  keeps their defaults in `:root`.

Verified in headless Chrome opened from `file://` (no server): `common.css` loads (79 rules), and the layout
matches the earlier screenshot. Maximize and Esc still work.

Note: the app is now two files (`index.html` + `common.css`) plus `assets/`. It still works offline. When copying
or deploying the app, `common.css` must go with `index.html`.
