# Compact now-playing titles on mobile

## Q1

Which html element displays the translation of movement title?

## A1

`<span id="np-title-translation">` in `index.html` (inside `#now-playing` → `#np-translation`). `updateNowPlaying()` in
`app.js` sets it to `"<number>. <movement.titleTranslation>"`; its sibling `#np-label-translation` holds the work title's
translation. The `#np-translation` wrapper is shown only when both Original and Translation are checked and a translation
exists; with Translation alone, the translated movement title goes into `#np-title` instead.

## Q2

The text set in np-title and np-title-translation spans are too crowded on mobile devices, do not include the work title
and limit to the first 16 characters

## A2

Changed `app.js` (`updateNowPlaying` and new helpers just above it):

- `compactNowPlaying = matchMedia('(max-width: 700px), (pointer: coarse) and (hover: none)')`: the same media query as
  the CSS rule that hides the timing panel (a touch device without a mouse, or a window as narrow as a phone's).
- When it matches:
  - `#np-label` and `#np-label-translation` (the work titles) are left empty, so the `:not(:empty)` margin rules in
    `common.css` don't add a gap either.
  - `#np-title` and `#np-title-translation` get `nowPlayingTitle(...)`: the text including the movement number,
    cut to its first 16 characters (`Array.from`, so no character is split; trailing space trimmed). No ellipsis is added.
  - `#np-translation` is hidden when the movement has no `titleTranslation` (there is no work translation left to show).
- A `change` listener on the media query re-runs `updateNowPlaying`, so resizing a desktop window across 700px switches
  between the full and the compact titles.

Verified in headless Chrome with `?movement=mozart/mozart-requiem/ch6`:

| Width | `#np-label` | `#np-title` | `#np-label-translation` | `#np-title-translation` |
|---|---|---|---|---|
| 400 | (empty) | `VI. Agnus Dei, L` | (empty) | `VI. 羔羊经、永恒之光` |
| 1280 | `Requiem` | `VI. Agnus Dei, Lux aeterna` | `安魂曲` | `VI. 羔羊经、永恒之光` |

`show=original` and `show=translation` at 400px also gave the expected single title.

## Q3

on mobile devices, reduce the space between btn-prev and np-title, and reduce the space between np-title-translation
and btn-next

## A3

Cause: in bilingual mode `#now-playing` is a grid split at `--lyrics-original-width` (each title centered in its share
of the bar, with 12px padding on both sides), so short titles left wide gaps next to Prev / Next (landscape), and long
ones were cut with an ellipsis well before using the room (portrait).

Changed `common.css` (new block after the bilingual `#now-playing` rules), under the same media query as
`compactNowPlaying` in `app.js` — `(max-width: 700px), (pointer: coarse) and (hover: none)`:

- `#song-nav { gap: 6px; }` (was 12px on a phone in landscape; already 6px at ≤700px).
- When both titles are shown (bilingual lyrics, or `#np-translation` not hidden): `#now-playing` is a grid of
  `minmax(0, auto) minmax(0, auto)` with `justify-content: space-between` and a 12px column gap, children without
  padding or margin. The original title sits 6px after Prev, the translation 6px before Next; when they don't both fit
  they share the room and get an ellipsis.
- Bilingual lyrics but no title translation: the lone original title is centered (one column, `justify-content: center`).
- Desktop layout unchanged.

Measured in headless Chrome emulating a touch phone (`?movement=mozart/mozart-requiem/ch6`, and the first movement):

| Viewport | Prev → title before | after | translation → Next before | after |
|---|---|---|---|---|
| 390×844 portrait | ~35px (title cut "VI. Agnus De…") | 6px ("VI. Agnus Dei, L" in full) | — (cut "VI. 羔羊…") | translation shows "VI. 羔羊经、…" |
| 844×390 landscape | 55px | 6px | ~16px+ | 6px |
| 390×844, "I. Overture / I. 序曲" | centered | 6px | centered | 6px |

## Q4

on mobile devices, reduce the padding and size of btn-prev and btn-next

## A4

Changed `common.css`, in the same mobile block as A3 (`(max-width: 700px), (pointer: coarse) and (hover: none)`):

```css
#song-nav #btn-prev,
#song-nav #btn-next { padding: 3px 6px; font-size: 0.66rem; }
```

The same size as the phone-sized playback buttons (`#playback-controls > .ctrl-btn` in "Smartphone sizes"). Was
`7px 10px` / `0.82rem` at ≤700px and `7px 14px` / `0.82rem` on a phone in landscape. The ID selectors outrank
`#song-nav .ctrl-btn`, so the rule doesn't depend on its place in the file.

Measured in headless Chrome emulating a touch phone, 390×844, `?movement=mozart/mozart-requiem/ch6`: Prev / Next went
from about 65×33px to 48×22px, the song-nav bar from about 50px to 36px tall, and the freed width lets the translation
show `VI. 羔羊经、永恒之…` (was `VI. 羔羊…`). Gaps to the titles stay at about 6px. Landscape (844×390) checked too.

## Q5

on mobile devices, limit the text set in np-title and np-title-translation to the first 20 characters

## A5

Changed `app.js`: `COMPACT_TITLE_CHARS` 16 → 20 (and the comment above `compactNowPlaying`). Still counts the movement
number ("VI. " is 4 of the 20), no "…" added by the cut itself.

Headless Chrome, touch-phone emulation, `?movement=mozart/mozart-requiem/ch6`:

- `#np-title` = `VI. Agnus Dei, Lux a` (20 chars), `#np-title-translation` = `VI. 羔羊经、永恒之光` (under 20, unchanged).
- 844×390 landscape: both shown in full, Prev 6px → title, translation 6px → Next.
- 390×844 portrait: the two don't both fit in the bar, so the CSS ellipsis cuts them further: `VI. Agnus Dei, L…` and
  `VI. 羔羊经、永…`.
