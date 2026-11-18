# Subtitle and voicing translations in the lyrics translation panel

## Ask

Added subtltleTranslation and voicingTranslation to the movements in work.js, display them at the top of the lyrics translation panel

## Answer

- `app.js` (`renderLyrics`): when a movement has translated lyrics (two columns), the movement heading is now split into
  two columns as well:
  - Left, over the original lyrics: `I. 永远安息 [诗篇116:7,9]` / `合唱` (unchanged).
  - Right, over the translation: `I. Eternal Rest [Psalm 116:7,9]` / `Chorus`, made from `titleTranslation`,
    `subtitleTranslation` and `voicingTranslation`. The translated title is included so the right heading has the same
    shape as the left one. Missing parts are left out.
  - A new helper, `movementHeading()`, builds both headings. Movements without translated lyrics keep the old
    one-column heading.
- `common.css`: the bilingual heading uses the same two-column grid as the lyric lines. It also has the same invisible
  3px left border, so its columns line up exactly with the lines and stay level with the divider when it is dragged.
- `README.md`: documented `subtitleTranslation` / `voicingTranslation` in the `work.js` example, described the
  translation column's heading, and mentioned the translations in the top bar ("Now playing").
- Checked in headless Chrome: Chapter 1 shows both headings, with their columns at the same x positions as the lyric
  lines (343px / 740px). Chapter 2 has no translated lyrics yet, so it still shows the one-column heading.
