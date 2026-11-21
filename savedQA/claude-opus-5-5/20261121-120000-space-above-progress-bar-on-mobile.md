# Space above progress bar on mobile

## Q1

On mobile devices, in normal lyrcx mode, add a little bit space above progress-bar

## A1

`common.css`, phone layout (`@media (max-width: 700px)`): `#progress-bar` margin changed from `-3px 0 -6px` to
`1px 0 -6px`.

- Before, the bar's 12px box reached 3px up into the 3px row gap, so the thumb sat right under the buttons.
- Now the box starts 1px below the row gap, so there are 4px more between the buttons and the bar; the playback
  controls get 4px taller.
- The bottom margin is unchanged (still reaches into the 6px bottom padding).
- Maximized mode hides `#playback-controls`, so only normal lyrics mode changes. Landscape phones and desktop
  (bar inline with the buttons) are unchanged.
