# Session: mobile navigation height and collapsible audio options

## Ask

On mobile devices, double the height of the movement navigation panel, make audio-options panel collapsible and being
collapsed by default.

## Response

- **Navigation pane height.** In the smartphone media query (`max-width: 700px`) of `common.css`, the left pane's grid
  row went from `minmax(0, 32%)` to `minmax(0, 64%)`.
- **Collapsible audio-options row** (`index.html` and `index-sound.html`):
  - Added a `collapsed` class to `#audio-options` and an arrow button `#btn-audio-toggle` at the end of the row.
  - `common.css`: the button is hidden by default, so on a wide window the row is always shown. In the smartphone media
    query the button shows, and a collapsed row hides everything except its label and the button. The arrow is rotated
    while open (same look as the LYRICS TIMING arrow).
  - `app.js`: `setAudioOptionsOpen()` toggles the state, starts collapsed unless the URL says `audio-options=open`, and
    writes `audio-options=open|collapsed` into the URL like the `timing` parameter. Documented in the VIEW OPTIONS IN
    URL comment.
  - `README.md`: new "Smartphone layout" bullet.
- **Checked** with headless Chrome at 500 px (collapsed, `?audio-options=open`) and at 1280 px (no arrow, row shown).
- **Caveat.** 64% of the height leaves little room for the lyrics area below on a phone; the percentage is the one value
  to tune in the media query.
