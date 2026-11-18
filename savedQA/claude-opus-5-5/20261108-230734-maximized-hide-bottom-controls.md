# Session 2026-11-08 23:07 — Maximized mode also hides the bottom control panel

## Ask

In maximized mode, also hide the bottom panel

## Answer

In maximized mode, the bottom control section (⏮ −15s ▶ +15s ⏭ and the progress bar) is now hidden too. Only the
now-playing title line at the top and the lyrics remain.

### Changes

- `common.css`: `#app.lyrics-maximized #bottom-controls` is added to the `display: none` rule. The right pane's grid
  in maximized mode is now `grid-template-rows: auto 1fr` (title line + lyrics), so the lyrics take the whole rest of
  the screen. The section comment is updated.
- `app.js`: the MAXIMIZE LYRICS PANEL comment now lists the bottom control section among the hidden parts, and notes
  that Space and the arrow keys still control playback.

While maximized, playback is controlled from the keyboard. Space plays or pauses. In Auto mode, ←/→ seek 5 s and
Shift+←/→ seek 15 s. In Manual mode, the arrows step through the lyric lines. Esc restores the normal layout.

### Verified (headless Chrome)

| State | Visible | Lyrics area height |
|---|---|---|
| Normal | left pane, top controls, lyrics, bottom controls, info pane | 506px |
| Maximized | top controls (title only), lyrics | 678px |
| Space while maximized | (unchanged) | audio paused, as expected |
| Esc | everything back | 506px |

No errors. Checked with a screenshot.
