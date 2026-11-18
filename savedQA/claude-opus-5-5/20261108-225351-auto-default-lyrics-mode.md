# Session 2026-11-08 22:53 — Auto as the default lyrics mode

## Ask

set Auto as default Lyrics mode;

## Answer

In `app.js`, the page now starts in **Auto** mode. The lyric highlight follows the audio, using the times in the
`.timing.js` file, or linear interpolation where there are none.

```js
highlightMode: new URLSearchParams(window.location.search).get('highlight-mode') === 'manual'
               ? 'manual' : 'auto'
```

The URL option is flipped to match. `index.html?highlight-mode=manual` starts in Manual mode, and the CONFIGURATION
comment now says `(default: auto)`. `?highlight-mode=auto` still works and is now the same as no option. The
Auto/Manual buttons work as before, and pressing **Rec** still switches to Manual by itself.

### Verified (headless Chrome, file://)

| URL | Mode | Pressed button | Manual key hint |
|---|---|---|---|
| `index.html` | auto | Auto | hidden |
| `index.html?highlight-mode=manual` | manual | Manual | shown |
| `index.html?highlight-mode=auto` | auto | Auto | hidden |
