# Lyrics font sizes: current line vs other lines

## Question

what's the difference between the font sizes of selected lyrics and other lines?

## Answer

Defined in `common.css`:

| View | Other lines (`.lyric-line`) | Current line (`.lyric-line.current`) | Difference |
|---|---|---|---|
| Normal | 1.95rem (31.2px) | 2.15rem (34.4px) | +0.2rem (3.2px), about 10% larger |
| Maximized (`#app.lyrics-maximized`) | 2.7rem (43.2px) | 3.1rem (49.6px) | +0.4rem (6.4px), about 15% larger |

(px values assume the browser default root size of 16px.)

- Lines above (`.before`) and below (`.after`) share the base size; they differ from each other only in color/background (and opacity 0.9). `.distant` lines are also the same size, just faded to opacity 0.28.
- The size change animates over 0.3s (`transition: font-size 0.3s ease`).
- In bilingual mode, the original and translation columns inherit the line's size, so both columns of the current line grow together.
- Font size is not one of the URL-param settings; only colors/backgrounds are configurable.

---

## Question

make the difference of font size of current line only 5% larger than other lines

## Answer

Changed the current-line sizes in `common.css`, writing each as base × 1.05 so the 5% ratio is clear:

| View | Other lines | Current line (before) | Current line (now) |
|---|---|---|---|
| Normal | 1.95rem (31.2px) | 2.15rem (34.4px) | `calc(1.95rem * 1.05)` = 2.0475rem (32.76px) |
| Maximized | 2.7rem (43.2px) | 3.1rem (49.6px) | `calc(2.7rem * 1.05)` = 2.835rem (45.36px) |

No JavaScript depends on these sizes; the 0.3s size transition and re-centering after it are unchanged.

---

## Question

default width of the left lyrics panel is 40%, right is 60%; change them to 50% by default

## Answer

Changed `--lyrics-original-width` in `common.css` `:root` from 40% to 50%; the translation column takes the remaining `1fr`, so it is now 50% too. The double-click reset in `app.js` just removes the inline override, so it falls back to the new 50% with no JS change.

Note: a browser that already has a dragged width saved (localStorage `onepagemp3.lyricsOriginalWidth`) keeps showing that width until the divider is double-clicked.

---

## Question

I tryed to insert &nbsp; and "\n" in lines 24 and 25 to insert a newline when the lyric lines are displayed, but it does work as expected

## Answer

Why neither worked:

- `app.js` puts lyric text on the page with `textContent`, not `innerHTML`, so `&nbsp;` is never treated as HTML. It shows up as the literal six characters. (Even as HTML, `&nbsp;` is a non-breaking space, which *prevents* a line break.)
- `"\n"` does become a real newline character, but `.lyric-line` used the default `white-space: normal`, which collapses newlines into a space.

Fix: added `white-space: pre-line;` to `.lyric-line` in `common.css`. Now a `\n` in `text` or `translation` starts a new line (extra spaces are still collapsed, so `"whom\n the Lord"` works too). Replaced the `&nbsp;` on lines 24–25 of `Chapter1.timing.js` with `\n`.

Verified in headless Chrome: in a line with `\n`, "Only those whom" is on the first row and "the Lord loves" on the second; lines without `\n` are unchanged. The in-app timing export uses `JSON.stringify`, so `\n` survives re-recording and saving.

---

## Question

I inserted two spaces after the \n sign, change css style to respect that

## Answer

Changed `.lyric-line` in `common.css` from `white-space: pre-line` to `white-space: pre-wrap`. `pre-line` keeps newlines but collapses spaces; `pre-wrap` keeps both newlines and spaces exactly as written and still wraps long lines.

Verified in headless Chrome: in "Only those whom\n  the Lord loves, [F]", "the" starts 15px right of "Only", the width of two spaces.

Side effect: spaces at the start or end of a line, and runs of spaces, now show everywhere. Three existing lines start with a space and are now shifted right by one space: line 10 of `Chapter1.timing.js` in `AnlunHuang/ChineseRequiem` (`" ( 以祷告的心 )"` / `" ( Prayerfully )"`), `Mozart/Symphony40` and `Mahler/Symphony2`. Left unchanged.

---

## Question

use the same font size for current lyrics line and other lines

## Answer

Removed the `font-size` from `.lyric-line.current` and deleted the `#app.lyrics-maximized .lyric-line.current` rule in `common.css`. The current line now uses the same size as every other line: 1.95rem normally and 2.7rem when maximized. It is still marked by its color, background and gold left border. The `font-size` transition on `.lyric-line` stays, because toggling Maximize still resizes all lines.

---

## Question

let left lyrics panel take 45% width, the right 55%

## Answer

Changed `--lyrics-original-width` in `common.css` `:root` from 50% to 45%; the translation column takes the rest (55%). As before, a width saved by dragging the divider still wins until the divider is double-clicked.

---

## Question

what's the difference: rest in Your embrace vs rest in Your arm?

## Answer

"Rest in Your arm" (singular) doesn't work: the idiom is plural, "in Your arms". In the Bible, "the arm of the Lord" (e.g. Isaiah 53:1) usually means God's power or strength, not tenderness. So the real choice is **embrace** vs **arms**:

- **Arms**: a concrete picture of being held and carried, like a child. It's common in hymns ("Safe in the arms of Jesus", "the everlasting arms", Deut 33:27). It's also the wording in `NewVersionAndEnglishTranslation.pdf`: "Give them eternal rest, O Lord, rest in your arms".
- **Embrace**: names the act of holding. It feels a bit more abstract, more literary, and more about closeness and love than safety.

The Chinese 怀里 literally means "in the bosom" (cf. "Abraham's bosom", Luke 16:22). Both are fair renderings. "Arms" is the more common hymn wording and matches the source translation; "embrace" is a little more intimate. "Bosom" is the most literal but sounds archaic.

---

## Question

Verify if the default 45% left lyrics panel width is taking effect; I want it to be 40% now.

## Answer

Verified in headless Chrome with a fresh profile (nothing in localStorage): the 45% default worked. The columns measured 45% / 55%, and the divider line sat at 45% (its 13px grab area starts 6px to the left, so its box reads 44.5%).

A width saved by dragging the divider (localStorage `onepagemp3.lyricsOriginalWidth`) overrides the CSS default. With 55 stored, the columns measured 55% / 45%. If a browser shows a different split than the default, double-click the divider to clear the saved width.

Changed `--lyrics-original-width` in `common.css` to 40% and re-measured in a fresh profile: 40% / 60%.

---

## Question

The width changed by moving the divider should be temporary, don't save it.

## Answer

Removed the divider's localStorage saving from `app.js`: the `DIVIDER_STORAGE_KEY` constant, `storeOriginalWidth()`, the `restoreOriginalWidth()` startup step, the calls in the drag-end and double-click handlers, and the `draggedPct` variable they needed. Dragging still sets the width for the current page; double-click still resets to the default; reloading the page always starts from `--lyrics-original-width` (40%). Updated the two README passages that said the width is remembered.

Verified in headless Chrome (fresh profile):

| Step | Original / translation |
|---|---|
| Fresh load | 40% / 60% |
| Load with an old saved `55` in localStorage | 40% / 60% (ignored) |
| Drag the divider to 60% | 60% / 40%, nothing saved |
| Reload | 40% / 60% |

An old saved value left by the previous version stays in the browser's localStorage but is never read.
