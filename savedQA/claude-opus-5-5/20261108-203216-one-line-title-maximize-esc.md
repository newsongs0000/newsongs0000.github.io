# Session 2026-11-08 20:32 — One-line now-playing title, Maximize hides top buttons, Esc restores

## Ask

Display the movement title in the same line after Song name, separated with some spaces; When the Maximize button at top panel is clicked, also hide all buttons of top panel; since the Maximize button will also be hidden, exit the Maximization mode by Esc key

## Answer

Changes in `index.html`:

1. **One-line now-playing header** — `#np-label` (composer — work) and `#np-title` (movement) are now inline on one line,
   with a 2.5em gap between them (`#np-label:not(:empty) + #np-title`, so the placeholder text stays centered when no
   song is selected). The whole line truncates with an ellipsis if it doesn't fit.
   Example: `黄安伦 — 安魂曲 (Requiem)      I. 永远安息`
2. **Maximize hides all top-panel buttons** — new CSS rule
   `#app.lyrics-maximized #top-controls > :not(#now-playing) { display: none; }` hides Prev, the Auto/Manual toggle,
   Maximize and Next; the now-playing line stays.
3. **Esc exits maximized mode** — the click handler now calls `setLyricsMaximized(true)`; the global `keydown`
   handler calls `setLyricsMaximized(false)` on Escape. Since the button is never visible while maximized, its
   Restore label / pressed state were dropped. The button tooltip now says "Maximize lyrics panel (Esc to restore)",
   and the keyboard-shortcuts comment lists Esc.

Verified in headless Chrome: header shows on one line; when maximized only `#now-playing` is visible in the top
panel; pressing Esc removes `lyrics-maximized`.

Note: while maximized, Prev/Next and the Auto/Manual toggle are not reachable by mouse — press Esc first.
Keyboard shortcuts (Space, arrows) still work.
