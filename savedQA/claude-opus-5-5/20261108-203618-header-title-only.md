# Session 2026-11-08 20:36 — Top header shows work title only

## Ask

Do not display the value of name in the "name - title" at top, display title only; for example instead of displaying "黄安伦 — 安魂曲 (Requiem)", display "安魂曲 (Requiem)" only

## Answer

In `index.html` (`selectMovement`), the now-playing label is now set to `work.title` only:

```js
document.getElementById('np-label').textContent = work.title;
```

The header now reads e.g. `安魂曲 (Requiem)      I. 永远安息`. The composer name is still shown in the left tree and
the bottom-right info pane. The old `escHtml(...)` wrapper was dropped: `textContent` does not interpret HTML, so
escaping would have shown characters like `&` as `&amp;`.
