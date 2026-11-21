# Hide the Mute check box on mobile devices

## Ask

On mobile devices, hide the audio Mute checkbox

## Answer

"Mobile device" here means a touch screen without a mouse, `(pointer: coarse) and (hover: none)`. A narrow
desktop window keeps its Mute box.

**`common.css`:** in that media query, the label holding `#chk-mute` is hidden (`label:has(#chk-mute)`, the same
`:has` pattern the CSS already uses).

**`index.html`:** with Mute gone, the row would have read "Audio: A− 100% A+". index1.html already titles this row
"Font:" because its Mute box is always hidden, so index.html now does the same on mobile. The row label holds two
spans (`.label-audio` "Audio:", `.label-font` "Font:") and the CSS shows one of them. The group's name now comes from
the visible label (`aria-labelledby="audio-options-label"`) rather than a fixed `aria-label="Audio"`.

**`app.js`:** the box was hidden, so a URL with `mute=1` (for example, a link shared from a computer) would have
silenced the phone with no way to unmute it. On a mobile device the `mute` URL parameter is now ignored, the audio
starts unmuted, and the URL is rewritten to `mute=0`. A `matchMedia` check uses the same query as the CSS. The MUTE
section comment and the URL parameter docs are updated to match.

index1.html (the always-silent page) is unaffected: its box is already hidden and locked.

`node --check app.js` passes. Not verified in a browser emulation (the DevTools browser was in use by another
session).
