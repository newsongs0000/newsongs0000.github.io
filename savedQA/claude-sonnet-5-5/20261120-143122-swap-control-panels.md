# Session: move playback controls above navigation controls, rename both panels

## Ask

Move the bottom-controls panel to the top, before the current top-controls panel, and rename these two panels.

## Answer / Response

The names `top-controls` / `bottom-controls` stop being true once the panels swap, so both were renamed to position-neutral names:

| Old                         | New                  | Contents                                  |
|-----------------------------|----------------------|-------------------------------------------|
| `#bottom-controls`          | `#playback-controls` | ◀◀ −15s ▶ +15s ▶▶, progress bar, time     |
| `#top-controls`             | `#song-nav`          | ◀ Prev, now playing, Next ▶ (+ maximized-mode buttons) |

Right pane order is now: playback controls → song navigation → lyrics → info pane.

Changes:

- `index.html`, `index1.html`: moved the playback block above the navigation block; renamed ids and section comments.
- `common.css`: renamed selectors (incl. maximized-mode and smartphone rules); `#right-pane` grid rows
  `auto 1fr auto 100px` → `auto auto 1fr 100px` (smartphone: `auto auto minmax(0,1fr) auto`);
  playback panel's separator border moved from `border-top` to `border-bottom`.
- `README.md`: screen-layout diagram, section order and wording updated.
- `app.js` needed no change (it uses the button ids, not the panel ids).

Verified with headless Chrome screenshots at 1280px and 420px widths.
`CLAUDE.md` (the layout spec) still describes the old top/bottom order; not changed.
