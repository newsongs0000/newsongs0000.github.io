# Song starts playing, then stops immediately

## Ask

I added translation in assets/HuangAnlun/ChineseRequiem/Chapter1.timing.js, but the song started playing, then
stopped immediately

## Answer

The translation edit was not the cause. `Chapter1.timing.js` loads fine: unquoted `translation:` keys are valid
JavaScript, and the panel shows both columns. The cause is the HTTP server, `ruby -run -e httpd . -p 8000`
(macOS's built-in Ruby 2.6, WEBrick 1.9.1), together with Chrome's cache:

1. Chrome downloads the start of the MP3, cancels that request, and keeps the part it got in its cache.
2. When it asks for more (`Range: bytes=…`), WEBrick answers `304 Not Modified` with no audio data.
3. The `<audio>` element fails (`MEDIA_ERR_NETWORK` on the first load, then `Format error` on every reload), so the
   music starts and stops at once, or never starts.

`curl` shows WEBrick answering Range requests correctly with `206`, which is why it passed last session's check and was
listed in the README.

Fix: use `npx http-server -c-1` (http://localhost:8080/). It sends `Cache-Control: no-store`, so Chrome keeps no
partial copy.

Changes:

- `README.md` (Running an HTTP server): removed the Ruby row and note, added a "Do not use `ruby -run -e httpd`"
  warning, and noted that a `206` from curl is not enough (play, reload, play again).
- `app.js`: the audio `error` handler now logs `Cannot play audio: <url> <error message>` instead of always
  `Audio file not found`.

Also noted about `Chapter1.timing.js`:

- It now has 10 lines; the other 45 lines (from 1:32 on) were removed. Restore them from git if that was not intended.
- Quote the key as `"translation"`. The panel works either way, but **Load** reads files as JSON and rejects unquoted
  keys. **Save** writes them quoted.

### Verification

Headless Chrome with its cache on, opening Chapter 1 from the tree and clicking the picture to play:

| Server | Result |
|---|---|
| `ruby -run -e httpd . -p 8000` | Failed 6 of 6 runs: `error 2` on the first, `error 4 Format error` after. The network log showed `304` for `Range: bytes=0-` |
| `npx http-server -c-1` | Played 4 of 4 runs (6.9 s after 6 s, lines highlighted, both languages) |
| `npx serve` | Played 3 of 3 runs |
| `python3 -m RangeHTTPServer` (rangehttpserver 1.x, in a scratch venv) | Played 3 of 3 runs |

The new console message was checked with a missing MP3: `Cannot play audio: …/missing.mp3 MEDIA_ELEMENT_ERROR: Format
error`.

## Follow-up ask

When server is run by the two npx command, song is playing well, on when the server is started by ruby command doesn't
work

## Answer

That matches the tests: both `npx http-server -c-1` and `npx serve` play, and `ruby -run -e httpd` fails in Chrome. The
README now lists only the servers that work. Use `npx http-server -c-1` (http://localhost:8080/).
