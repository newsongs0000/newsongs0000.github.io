# The Chinese lyrics column takes 40% of the width, on either side

- Session: 2026-11-17 00:19
- Model: claude-fable-5-2

## Ask

> Added language and translationLanguage fields to all work.js files; currently the program displqys the lyrics in
> original language in the left lyris panel, and the lyrics in translation language in the right, and the left panel
> takes 40% width, while the right takes the rest (60%). Change the program to let the panel that displays Chinese
> lrycs takes 40% of the width, even if it is in the right panel

## Response

The 40% now belongs to the column with the Chinese lyrics instead of the left column. The original lyrics stay on
the left and the translation on the right; only the widths change.

| Work | `language` | `translationLanguage` | Left (original) | Right (translation) |
|---|---|---|---|---|
| 安魂曲 | `zh` | `en` | 40% | 60% |
| Messiah | `en` | `zh` | 60% | 40% |

### Behavior

- The translation column is the Chinese one when `translationLanguage` starts with `zh` (`zh`, `zh-Hant`, ...) and
  `language` does not. In every other case (Chinese original, or no Chinese at all) the original column gets the 40%,
  as before.
- The top bar titles split at the same place as the lyrics.
- Dragging the divider sets the Chinese column's width (20% to 80%). It keeps that width when you go to a work with
  the Chinese lyrics on the other side. Double-click goes back to 40%. As before, it is not saved.
- With only Original or only Translation checked there is one full-width column, unchanged.

### Changes

| File | Change |
|---|---|
| `common.css` | `--lyrics-chinese-width: 40%` is the setting now; `--lyrics-original-width` (the left column) is derived from it, and is `100% - chinese width` under `#right-pane:has(#lyrics-inner.chinese-translation)` |
| `app.js` | `translationIsChinese(work)`; `renderLyrics` sets the `chinese-translation` class; the divider sets `--lyrics-chinese-width` (`setOriginalWidth` renamed `setChineseWidth`) |
| `README.md` | Translation, Divider and default-width paragraphs; `language` / `translationLanguage` in the `work.js` example and the file table |

### Verification

Measured in headless Chrome (1400 px wide) against a local HTTP server:

- Messiah No. 1: original 60%, Chinese translation 40%, top bar split at 60%.
- 安魂曲 I: Chinese original 40%, translation 60%.
- Dragging the divider in Messiah to 70% makes the Chinese column 30%; going to 安魂曲 keeps the Chinese column at 30%
  (now on the left). Dragging past the limit stops at 20%.
- Double-click restores 40% for the Chinese column in both works.
- Translation only: one column, no split.

Not tested in Firefox or Safari.
