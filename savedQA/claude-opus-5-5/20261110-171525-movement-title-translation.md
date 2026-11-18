# Movement title translation in the top panel

## Ask

Added titleTranslation to the movements in work.js, display it after movement title at the top panel

## Answer

- `app.js`: a new helper, `translatedTitle(item)`, returns `title (titleTranslation)`, or just `title` when
  there is no translation. The top panel now uses it for the work title (`#np-label`) and for the movement
  title (`#np-title`), for example `安魂曲 (Requiem)   II. 深处祷告 (Prayer from the Depths)`.
- `README.md`: the movement in the `work.js` example now has `titleTranslation: "Eternal Rest"`.
- Checked in headless Chrome at 1400px and 1024px wide: the top panel showed the full text for movements I–III,
  including the longest translation, "Prayer from the Depths".
- The movements' `subtitleTranslation` field (also added in work.js) is not shown anywhere yet.
