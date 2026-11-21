# Hide the timing panel on mobile devices

## Ask

On mobile devices, always hide the timing-panel panel.

## Answer

Until now the LYRICS TIMING panel (`#timing-panel`) was hidden only inside the `@media (max-width: 700px)` block.
That covered a phone in portrait, but not a phone in landscape (wider than 700px, so it gets the two-pane layout)
or a tablet. On those, the panel still appeared at the bottom of the left pane.

Change in `common.css`:

- Removed `#timing-panel { display: none; }` from the `max-width: 700px` block.
- Added a separate rule after the timing panel's own styles:

```css
@media (max-width: 700px), (pointer: coarse) and (hover: none) {
  #timing-panel { display: none; }
}
```

`(pointer: coarse) and (hover: none)` matches touch-screen devices that have no mouse: phones in either orientation,
and tablets. `max-width: 700px` still hides the panel in a desktop window as narrow as a phone, as before.
When the panel is hidden, the Songs tree (`flex: 1`) takes the freed height, and View Options stays docked at the
bottom of the left pane.
