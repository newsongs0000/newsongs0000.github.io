# Session 2026-11-20 22:04 — Arrow direction of the collapse button on mobile

## Ask

> On mobile devices, the icon of the button btn-timing-toggle is opposite

## Answer

On a smartphone (window 700 px wide or narrower) the LYRICS TIMING panel, and with it `#btn-timing-toggle`, is hidden
(`#timing-panel { display: none; }`). The arrow you see on the phone is the VIEW OPTIONS button, `#btn-view-toggle`,
which uses the same `^` markup and the same "rotate 180° while open" rule.

The two panels open in different directions:

- **LYRICS TIMING, wider window:** docked at the bottom of the left pane, so opening it moves the title up. `^` while
  collapsed and `˅` while open is correct, so this is unchanged.
- **VIEW OPTIONS, smartphone:** the left pane is only as tall as its content, so the title stays where it is and the
  options appear below it, pushing the lyrics down. `^` while collapsed pointed the wrong way.

### Fix (`common.css`, smartphone media query)

```css
/* was: #view-panel:not(.collapsed) #btn-view-toggle { transform: rotate(180deg); } */
#view-panel.collapsed #btn-view-toggle { transform: rotate(180deg); }
```

On a phone the arrow now points down (`˅`) while collapsed and up (`˄`) while open. The comment above the rule
explains why it is the reverse of the timing arrow. I checked both states in headless Chrome at phone width
(`?view-options=collapsed` and `?view-options=open`).
