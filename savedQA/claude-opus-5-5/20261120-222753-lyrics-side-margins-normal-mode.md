# Lyrics side margins in normal mode

## Ask

When lyrics mode is Max, the spaces at both sides are smaller than the normal mode, make them same(small) as the Max mode for normal mode

## Answer

The side margins of the lyrics panel come from the CSS variable `--lyrics-side-pad` on `#song-display` in `common.css`.
It was `60px` in normal mode, and maximized mode overrode it to `0px`.

Changes in `common.css`:

- `#song-display { --lyrics-side-pad: 0px; }`: normal mode now has the same (zero) side margins as Max mode.
- Removed the now-redundant `#app.lyrics-maximized #song-display { --lyrics-side-pad: 0px; }` override.

The thumbnail overlay uses the same variable (`inset: 0 var(--lyrics-side-pad)`), so it still lines up with the lyrics.
