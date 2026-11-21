# Landscape: View Options doesn't move up when Songs is collapsed

## Ask

On mobile devices, normal lyrics mode and landscape orientation, when the tree-panel which contains the composer-tree
is collapsed, the view-panel is not moving up to occupy the space

## Answer

**Cause:** a phone in landscape is wider than 700px, so it gets the two-pane layout. There `#tree-panel` keeps
`flex: 1` even when collapsed — on a computer that keeps the LYRICS TIMING panel docked at the bottom of the left
pane. On a mobile device the timing panel is hidden, so the collapsed Songs panel just left empty space above
VIEW OPTIONS.

**Fix (`common.css`):** in the media query that hides the timing panel on mobile devices
(`(max-width: 700px), (pointer: coarse) and (hover: none)`), added

```css
#tree-panel.collapsed { flex: none; }
```

so the collapsed Songs panel shrinks to its title bar and VIEW OPTIONS sits right under it. Updated the comment on
`#tree-panel` to note the exception.

- Portrait phones: unchanged (`#tree-panel` was already `flex: none` there).
- Computers: unchanged (the timing panel stays docked at the bottom).
- Tablets (touch, no hover) get the same behavior as landscape phones, consistent with the timing panel being hidden
  there.

Not verified in a browser emulation (the DevTools browser was in use by another session).
