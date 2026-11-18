# Work title translation in the top panel

## Ask

Added titleTranslation field to the work.js files, display it after title on the top panel

## Answer

- `app.js` (`loadMovement`): the now-playing label (`#np-label`) in the top panel now shows
  `title (titleTranslation)`, or just `title` when a work has no `titleTranslation`.
  - 安魂曲 (Requiem)
  - Symphony No. 2 (第2交响曲)
  - Symphony No. 40 (交响曲第40号)
- `README.md`: the `work.js` example now has `title: "安魂曲"` plus the optional `titleTranslation: "Requiem"`.
- The tree and the info pane still show only `title`. Since "(Requiem)" was moved out of `title`, they no
  longer show the translation.
