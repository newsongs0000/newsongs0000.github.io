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

## Second follow-up ask

What a fresh visitor sees: before the first click, the lyrics are covered by the "Click to play" thumbnail. That is by
design and happens on both sites. Change to display the placeholder of lyrics panels with the same size as the real
ones.

(Asked which placeholder was meant: skeleton columns, real lyrics with no cover, or the thumbnail in panels. Answer:
**Thumbnail in panels**.)

## Second follow-up response

- **Overlay = placeholder of the lyrics panels.** The thumbnail overlay now has exactly the box of the real lyrics (the
  song area less the same 60 px side margins, none when maximized) instead of the whole song area. A new CSS variable
  `--lyrics-side-pad` on `#song-display` is shared by `#lyrics-container` and `#thumbnail-overlay`.
- **Bilingual lyrics:** the overlay becomes two panels split at `--lyrics-original-width` with a 1 px divider where the
  real divider is. The picture is in the first (original-language) panel and "▶ Click to play" in the second. One panel
  otherwise.
- `index.html` and `index-sound.html`: overlay markup now holds two `.thumbnail-panel` divs, the hint stays inside the
  overlay. `common.css`: new overlay rules. No JS change. README "Picture" bullet updated.
- **Checked** with headless Chrome: bilingual (1280 px), `?show=original` (single panel) and 500 px. The hint was
  wrapping on two lines in the narrow mobile panel, fixed with `white-space: nowrap`.

## Third follow-up ask

On mobile devices, when the composer-tree is collapsed, the View Options panel moves up, but the lyrics panels
(right-pane) does not; make it also moves up as the View Options panel does.

## Third follow-up response

- The smartphone grid had a fixed `minmax(0, 64%)` row for the navigation pane, so collapsing the tree left an empty
  gap under the View Options panel. The row is now `fit-content(64%)`: the pane is as tall as its content, capped at
  64% (then the tree scrolls and the View Options panel stays at the bottom, sticky). The right pane takes the rest.
- Only `common.css` (smartphone media query) and the README "Smartphone layout" bullet changed.
- **Checked** with headless Chrome at 500 px using a scratch copy of the page that collapses or opens every tree node:
  collapsed (right pane moves up with the panel) and fully open (pane capped at 64%, the panel at its bottom).
