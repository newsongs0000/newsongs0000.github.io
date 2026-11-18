# Session 2026-11-08 22:34 — Lyrics missing for dummy Mahler and Mozart works

## Ask

Created dummy data under artists Mahler and Mozart, but their lyrics do not show up

## Answer

There were two causes: one in the new data files, and one bug in `app.js` that the new data exposed.

### 1. Data: the timing files name a different work id (why the lyrics were blank)

A `.timing.js` file is only used for a movement if its `"composer"`, `"work"` and `"movement"` match that movement's
artist id, work id and movement id. The new files did not match:

| File | `"work"` in timing file | `id` in work.js |
|---|---|---|
| `assets/Mahler/Symphony2/Chapter1.timing.js` | `symphony2` | `mahler-symphony2` |
| `assets/Mozart/Symphony40/Chapter1.timing.js` | `symphony40` | `mozart-symphony40` |

The app rejected both files with only a console warning ("Chapter1.timing.js is not the timing of
mahler/mahler-symphony2/ch1"), so no lyrics appeared.

**Fix:** set `"work"` in the two timing files to `mahler-symphony2` and `mozart-symphony40`.

### 2. Code bug: movements were looked up by movement id alone

All three works have a movement with id `ch1`. `app.js` found the clicked movement with `m.data.id === movement.id`,
which always matched the Requiem's `ch1` first. Clicking Mahler's or Mozart's movement showed its title and audio,
but the player state pointed at Requiem ch1. Prev/Next, Auto-mode highlighting, Rec and Save would have used the
wrong movement, and three tree items were highlighted at once.

**Fix (`app.js`):**
- `loadMovement` finds its entry with `movementEntry(movement)` (matches the movement object).
- `currentFlatIdx` matches by object: `e.data === m`.
- Tree items carry the full key, `data-key="artist/work/movement"` (via `movementKey`), instead of `data-id="ch1"`,
  and the active highlight compares that key.

### Verified

Headless Chrome, both `http://` and `file://`. Clicked all 10 movements in the tree. Each one loads its own movement
(Mahler → `mahler/mahler-symphony2/ch1`, Mozart → `mozart/mozart-symphony40/ch1`), shows 55 lyric lines for the
dummies, highlights exactly one tree item, and logs no warnings.

### Tip

When copying a `.timing.js` file for a new work, change its `"composer"`, `"work"` and `"movement"` to the new ids.
If lyrics don't show, the browser console names the mismatched file.

### Side note (not changed)

Prev/Next follow the order of `artistFiles` and `workFiles`, while the tree is sorted alphabetically. They match today
(Huang, Mahler, Mozart). If an artist is added out of alphabetical order, Next would jump differently than the tree
suggests.
