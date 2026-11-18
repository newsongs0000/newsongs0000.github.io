# Session 2026-11-08 22:57 — Lyrics timing panel collapsed by default

## Ask

By default minimize the Lyrics timing panel at left-bottom, only shows a up arrow (^)

## Answer

The LYRICS TIMING panel at the bottom of the left pane now starts **collapsed**. Only a small up-arrow (^) button
shows, at the right of a thin strip, and the composer tree gets the freed space.

- Click **^**: the panel opens with the title, status and Rec/Save/Load/Clear/Export, and the arrow turns to point
  down.
- Click it again: the panel collapses back to the arrow.
- Hover text says "Show lyrics timing" / "Hide lyrics timing". `aria-expanded` is kept in sync for screen readers.

### Changes

- `index.html`: the panel gets `class="collapsed"`, a header row (`#timing-header`: the "LYRICS TIMING" title plus
  `#btn-timing-toggle`), and its status, buttons and file input are wrapped in `#timing-body`.
- `common.css`: `#timing-panel.collapsed` hides the title and `#timing-body` and shrinks the padding. The arrow is a
  small inline SVG chevron, rotated 180° while the panel is open. The text glyph ⌃ sat off-center in the button, so I
  replaced it.
- `app.js`: a click handler on `#btn-timing-toggle` toggles `collapsed`, updates `aria-expanded` and the tooltip, and
  blurs the button so Space still plays/pauses.

It always starts collapsed on page load; the open/closed state is not remembered.

### Verified (headless Chrome, file://)

On load the panel is collapsed (35px tall, body hidden). One click opens it (165px, status shows
"I. 永远安息 · 55 / 55 lines timed"), and a second click collapses it again. No errors. Screenshots were checked for
both states.
