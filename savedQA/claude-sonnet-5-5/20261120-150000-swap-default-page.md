# Session: make the sound page the default, rename the silent page to index1.html

## Ask

Rename index.html as index1.html, switch index-sound.html as default.

## Response

- `git mv index.html index1.html` (the silent page) and `git mv index-sound.html index.html` (the sound page, now the
  default). `index-sound.html` no longer exists.
- Page titles follow: `index.html` is "Player with Lyrics", `index1.html` is "Player with Lyrics (silent)".
- Comments and docs updated to the new names: the CONFIGURATION, VIEW OPTIONS IN URL and MUTE comments in `app.js`,
  the Mute box comment in `common.css`, and `README.md` (Audio row, "Silent and sound pages", project structure).
  `mute` in URLs now matters only on `index.html`.
- Not changed: app code (the Mute check box is `disabled` on `index1.html`, which is what locks it silent); other
  mentions of `index.html` (relative paths, `?movement=` examples) are still correct.
- Not committed.
