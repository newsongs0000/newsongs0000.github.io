# Same size for the Max and Restore icons

## Ask

The icon for Norm is smaller than the icon for maz

## Answer

Both icons were sized `0.9em`, which is relative to the button's own font size:

- Max (`#btn-maximize`): 1rem (0.9rem on phones), so the icon was 14.4px (13px on phones).
- Restore (`#btn-restore`, in the song navigation row): 0.82rem, so the icon was about 11.8px.

The shared rule in `common.css` (`#btn-maximize svg, #btn-restore svg`) now sizes them in `rem`: `width: 0.9rem;
height: 0.9rem` (14.4px), so both icons are the same size on every screen. On phones the Max icon grows slightly,
from 13px to 14.4px.

The result was not checked in a browser (the DevTools browser was in use by another session).
