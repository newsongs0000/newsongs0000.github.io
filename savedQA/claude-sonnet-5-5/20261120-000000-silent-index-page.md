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

---

## Ask (follow-up)

make index-silent.html default

## Response (follow-up)

Interpreted "default" as the page the site root serves, i.e. `index.html`. Swapped the two pages:

- `index-silent.html` became `index.html` (always muted, Mute box hidden and locked; title "Player with Lyrics").
- The old `index.html` became `index-sound.html` (visible Mute box; title "Player with Lyrics (with sound)").
- Updated the comments in `app.js` and `common.css`, and `README.md` (new "Silent and sound pages" section, layout diagram,
  Mute bullet, project structure). `mute` in URLs now only matters on `index-sound.html`.
- Verified in headless Chrome: `index.html` (also with `?mute=0`) is muted, label hidden; `index-sound.html` is unmuted by
  default and muted with `?mute=1`.
- Left alone: the old draft work items in `workItems/draft` that mention `index.html` for their own purposes.
