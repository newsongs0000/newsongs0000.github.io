# Lyrics mode is Manual by default

- Session: 2026-11-17 00:28
- Model: claude-fable-5-2

## Ask

> Lyrics mode is manual by default

## Response

The player now starts in **Manual** lyrics mode: the highlight moves only when you press ↓ / → (next), ↑ / ← (back)
or click a line. The audio position no longer moves it unless you switch to Auto.

### Behavior

- On load the **Manual** button is active, the `↓→ next ↑← back` hint shows, and no line is highlighted until the
  first key press or click.
- Click **Auto** to have the highlight follow the audio; it jumps to the line at the current audio position.
- The URL parameter is reversed: `?highlight-mode=auto` starts in Auto. Any other value, or none, starts in Manual,
  so old links with `highlight-mode=manual` still work.
- Together with mute by default, the player now starts set up for a live performance. To listen to a recording,
  uncheck **Mute** and click **Auto**.

### Changes

| File | Change |
|---|---|
| `app.js` | `state.highlightMode` is `auto` only for `highlight-mode=auto`, else `manual`; CONFIGURATION comment |
| `README.md` | Lyrics highlight modes (default column, URL parameter), URL parameter table and example, left navigation pane list, and a note under "Playing music" about the muted / Manual start |

### Verification

Tested in headless Chrome against a local Range-capable HTTP server (`npx http-server`), Chinese Requiem chapter 1
from 0:08:

- No parameter: Manual is active and the hint shows. After 6 s of playback (to 0:14) no line is highlighted; pressing
  ↓ twice highlights line 2 (index 1). Clicking Auto moves the highlight to the line at the audio position (index 2)
  and hides the hint.
- `highlight-mode=auto`: Auto is active; the highlight follows the audio (index 1 at 0:08, index 2 at 0:14).
- `highlight-mode=manual`: Manual, as with no parameter.

Not tested in Firefox or Safari.
