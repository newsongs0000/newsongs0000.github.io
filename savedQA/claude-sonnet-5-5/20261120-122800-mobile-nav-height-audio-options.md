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

## Follow-up ask

Sorry, not audio-options, but I want to make its enclosing container view-panel collapsible, when it is collapsed,
display title; also display title for timing-panel when it's collapsed; on mobile devices, do not display timing-panel.

## Follow-up response

- **Undid the audio-options collapse** (HTML, CSS, `app.js`, README): no arrow button, no `audio-options` URL parameter.
- **View panel collapsible, smartphone only** (window 700 px wide or narrower):
  - `index.html` and `index-sound.html`: `#view-panel` got the class `collapsed`, a `#view-header` (title "VIEW OPTIONS"
    and the arrow `#btn-view-toggle`), and its old content moved into `#view-body`.
  - `common.css`: the flex layout moved from `#view-panel` to `#view-body`; the header is hidden by default and shown in
    the smartphone media query, where a collapsed panel hides `#view-body`.
  - `app.js`: `setViewPanelOpen()`, collapsed unless the URL says `view-options=open`, written back to the URL like
    `timing`.
- **LYRICS TIMING panel:** its title now shows while collapsed (only the body is hidden), and it is `display: none` on a
  smartphone.
- **Checked** with headless Chrome at 500 px (collapsed, `?view-options=open`) and 1280 px.
- **Mishap:** a Python edit of `app.js` corrupted it (the start marker came after the end marker, so `str.replace('', ...)`
  inserted text between every character). `app.js` was restored with `git checkout` (HEAD already held the committed
  audio-options change, so nothing was lost) and the edit redone with the Edit tool.
