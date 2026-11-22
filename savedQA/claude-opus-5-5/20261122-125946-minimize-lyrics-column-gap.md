# Minimize the space between the two lyrics panels

## Ask

Minimie the space between the two lyrics panels

## Answer

The two panels are the bilingual lyrics columns (original | translation). Each cell had 24px of padding on its
divider side, so the text in the two columns was 48px apart, plus the 1px divider.

Changed in [common.css](../../common.css) (the "Bilingual lyrics" section):

```css
/* Little space between the columns: 8px each side of the divider, just clear of its 13px grab area */
#lyrics-inner.bilingual .lyric-original    { padding: 0 8px 0 14px; }
#lyrics-inner.bilingual .lyric-translation { padding: 0 14px 0 8px; }
```

- The gap at the divider is now 16px, down from 48px. The outer side margins (14px) are unchanged.
- 8px keeps the text just outside the divider's drag area (6px each side of the line), so clicking a line near the
  divider still selects the line instead of starting a drag.
- Checked in headless Chrome: 安魂曲 I (Chinese on the left), Messiah III (Chinese on the right, long lines that
  wrap), and the phone layout (390px wide).

Note: when the Chinese lines are short, most of the visible blank space comes from the unused part of the 45%
Chinese column, not from the padding. To reduce that, drag the divider, or set `?chinese-width=`.
