# Draggable divider between the lyrics columns

## Ask

Make the divider adjustable

## Answer

The line between the original and translation columns can now be dragged.

- **Drag** it left or right to resize the columns. The original column can be 20% to 80% of the width, and the
  translation gets the rest. The cursor shows `↔` (col-resize) over it, and the line turns gold under the mouse and
  while dragging.
- **Double-click** it to go back to the default, 40%.
- The width is **remembered in this browser** (`localStorage` key `onepagemp3.lyricsOriginalWidth`) and applies to
  every movement with translations, in normal and maximized view. After a drag the current line is re-centered,
  because lines may wrap differently.

Changes:

- `app.js`: new section **BILINGUAL LYRICS DIVIDER**. It creates one divider element, which `renderLyrics()` adds to
  bilingual lyrics. Dragging uses pointer events with pointer capture and sets `--lyrics-original-width` on the page.
  The value is saved when the drag ends, removed on double-click, and restored at startup (ignored unless it is between
  20 and 80).
- `common.css`: the decorative `::before` line became `.lyrics-divider`: a 13px-wide invisible grab area at
  `--lyrics-original-width`, with the 1px line drawn in its middle. The default is still `--lyrics-original-width: 40%`
  in `:root`.
- `README.md`: a "Divider" bullet under the song playing section, and the CSS setting is now described as the
  default.

### Verification

Headless Chrome over `npx http-server -c-1`, Chapter 1, with real mouse events (CDP `Input.dispatchMouseEvent`):

| Step | Result |
|---|---|
| Start | Line at 40.0%, cursor `col-resize`, nothing stored |
| Drag to 55% | Line at 55.0%, columns meet at the line (within 1px), stored `55` |
| Drag far left | Stopped at 20% |
| Drag back to 55%, reload | Still 55% |
| Single click on the divider at 0:30 (Auto mode) | No seek: still 0:30 |
| Double-click | Back to 40%, stored value removed |
| Chapter 2 (no translations) | No divider |

The picture shown before playback covers the lyrics, so the divider can be dragged once the music has started (or
after the picture is dismissed).
