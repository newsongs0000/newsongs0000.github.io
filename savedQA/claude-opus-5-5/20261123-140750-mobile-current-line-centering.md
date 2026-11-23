# Keep the current lyrics line centered on mobile

## Ask

On mobile devices, sometime the lyrics line that is currently being played is not displayed at the center or not
visible

## Answer

The lyrics were centered only when the highlight moved to another line. Anything that changed the layout between
two lines left the current line where the scroll position happened to put it, until the next line started. On a
phone this happens often, because the Songs tree and View Options sit above the lyrics in the same column.

Reproduced in headless Chrome at 390×844 (phone emulation), measuring the current line's distance from the
middle of the lyrics panel:

| Action                                   | Before                    | After |
|------------------------------------------|---------------------------|-------|
| Collapse the Songs tree                  | 198px above center        | 0px   |
| Reopen the Songs tree (line 20)          | 198px below, **not visible** | 0px |
| Open View Options                        | 36px off                  | 0px   |
| A+ ×5                                    | 49px off                  | 0px   |
| Rotate to landscape                      | 10–208px off (not visible) | 0px  |
| Max / restore, desktop size              | (re-centered after 350ms) | 0px   |

### Changes

[app.js](../../app.js):

- `centerCurrentLine(smooth = true)`: can now scroll at once (`behavior: 'instant'`; `'auto'` would follow the CSS
  `scroll-behavior: smooth`).
- New section **KEEP THE CURRENT LINE CENTERED**: a `ResizeObserver` on `#lyrics-container` (panel size: tree,
  View Options, rotation, Max, browser toolbars) and `#lyrics-inner` (content size: A+ / A−, Show, bilingual divider
  drag) re-centers the current line at once, at most once a frame, so it stays pinned even through the 0.3s
  font-size transition. It also re-centers when the page becomes visible again (phone unlocked, back from another
  app), since smooth scrolling may not run while the page is hidden.
- Removed the now-redundant re-centering in `setLyricsMaximized` (`setTimeout(centerCurrentLine, 350)`) and in the
  bilingual divider's `lostpointercapture` / `dblclick` handlers.

[common.css](../../common.css):

- `#app` height `100vh` → `100dvh` (with `100vh` as fallback), matching `body`. On a phone, `100vh` is the height
  with the browser toolbars hidden, so with them shown the bottom of the app sat under the toolbar and the lyrics
  were centered lower than their visible middle.

Normal line-to-line scrolling is unchanged (smooth); verified with auto-mode playback.

### Not changed

The first and last few lines of a movement still can't reach the center: the spacers above and below the lyrics
are only 40px, so the panel can't scroll further. This is by design and the same on desktop.
