# Session: silent version of index.html

## Ask

Create a version of index.html that does not play sound, basically it is same as the current version with the Mute checkbox
checked but the user won't see the Mute checkbox.

## Response

- Added `index-silent.html`: a copy of `index.html` whose Mute checkbox is `checked disabled` inside a `hidden` label.
  The title is "Player with Lyrics (silent)", and the "Audio:" row label (the row also holds the font-size buttons) is now "Font:".
- `app.js` (MUTE section): when the Mute box is disabled it is treated as locked, so `audio.muted` is always true, the `mute`
  URL parameter is ignored and not written, and the change handler does nothing. `index.html` behaves as before.
- `common.css`: `#audio-options label[hidden] { display: none; }`, because `display: flex` on that label overrides the
  `hidden` attribute.
- `README.md`: documented the silent page and listed it in the project structure.
- Verified in headless Chrome: `index-silent.html` (also with `?mute=0`) gives `audio.muted === true`, the label is not displayed,
  and `mute` does not appear in the URL; `index.html` still honours `?mute=1` / the default unmuted state.
