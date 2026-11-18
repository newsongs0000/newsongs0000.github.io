# Session 2026-11-08 23:04 — Work folders collapsed on first load too

## Ask

also collapse work folders

## Answer

In `app.js` `buildTree()`, each work folder is now created as `class="tree-work"` instead of `"tree-work open"`,
like the artist folders in the previous change. The comment there now reads "artist and work folders start
collapsed".

When the app first loads, only the artist names show. Clicking an artist shows its work names, each collapsed with a
► arrow. Clicking a work shows its movements.

### Verified (headless Chrome, file://)

| Step | 黄安伦 | its work 安魂曲 (Requiem) | Movements visible |
|---|---|---|---|
| Load | closed | closed, hidden | 0 |
| Click 黄安伦 | open | closed, visible | 0 |
| Click 安魂曲 | open | open | 8 |

Mahler and Mozart stay closed throughout. No errors. Checked with a screenshot.

### Side note (not changed)

Same as before: when Prev/Next moves into a collapsed artist or work, the playing movement's highlighted tree item is
hidden until its folders are opened. This can now also happen when moving between works of the same artist. The app
could open the playing movement's folders automatically.
