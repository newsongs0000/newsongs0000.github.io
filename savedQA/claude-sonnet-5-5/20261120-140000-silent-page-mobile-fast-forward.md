# Session: silent page races to the end of the movement on mobile

## Ask

When the silent version is open on mobile devices and the play button is clicked, it fast-forwards very fast to the
end of the movement. The desktop does not do that.

## Response

- `index.html` and `index-sound.html` differ only in the Mute check box; the silent page sets `audio.muted = true`
  from the start, before any playback. That is the only difference, so the mobile-only runaway comes from a muted
  `<audio>` element: on mobile (WebKit especially) it has no audio output to keep time with, so `currentTime` is
  not paced by real time.
- Fix in `app.js` (MUTE section): the silent page no longer mutes the element. It routes the element through a Web
  Audio `GainNode` with gain 0 (`silenceAudioViaWebAudio`), which keeps a real audio output and clock running while
  nothing is heard. The `AudioContext` is resumed on the first user gesture, on `play`, and when the page becomes
  visible again. Without Web Audio it falls back to `audio.muted`.
- `index-sound.html` and its Mute box are unchanged.
- Checked in headless desktop Chrome: after 4.02 s of wall-clock time, `currentTime` was 4.004 s, `muted` false.
  Not verified on a real phone; the cause on mobile is inferred, not reproduced.
- README updated (Silent and sound pages).
