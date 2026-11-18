# Session 2026-11-08 23:02 — Artist folders collapsed on first load

## Ask

When the app is loaded first, collapse all artist folders

## Answer

In `app.js` `buildTree()`, each artist folder is now created as `class="tree-composer"` instead of
`"tree-composer open"`. `buildTree()` runs only once, at startup, so when the app first loads the left pane shows just
the artist names (黄安伦, Mahler, 沃尔夫冈·阿马德乌斯·莫扎特), each with a ► arrow.

Clicking an artist opens it as before. Its works are still created open, so all of that artist's movements show at
once. Folders the user opens stay open until clicked again.

### Verified (headless Chrome, file://)

On load, all 3 artists are closed with 0 movements visible. After clicking 黄安伦, it is open with all 8 movements
visible, and the other two stay closed. No errors. Checked with a screenshot.

### Side note (not changed)

Prev/Next can move into another artist (e.g. Next after the Requiem's last movement goes to Mahler). If that artist's
folder is collapsed, the now-playing movement's highlighted tree item is hidden until the folder is opened. The app
could open the folder of the playing movement automatically.
