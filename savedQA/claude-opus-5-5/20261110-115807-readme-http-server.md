# README: how to run an HTTP server

## Ask

Update README.md to document how to run HTTP server to serve index.html and static files

## Answer

Expanded **Running the app** in `README.md` with a new subsection, **Running an HTTP server** (also added to the
table of contents). It covers:

- Why you might serve over HTTP: edits picked up on a plain reload (cache-busting query), and opening the app from
  another device on the network.
- The requirement for HTTP Range requests (otherwise seeking jumps back to 0:00), with a warning not to use
  `python3 -m http.server`.
- A table of tested commands, run in the folder that contains `index.html`:

  | Needs | Command | Open |
  |---|---|---|
  | Node.js (recommended) | `npx http-server -c-1` | http://localhost:8080/ |
  | Node.js | `npx serve` | http://localhost:3000/ |
  | Python 3 | `python3 -m pip install rangehttpserver`, then `python3 -m RangeHTTPServer` | http://localhost:8000/ |
  | Ruby | `ruby -run -e httpd . -p 8000` | http://localhost:8000/ |

- Notes on `npx` (one-time download), `-c-1` / `-p` / `-a 127.0.0.1`, opening from another device, Ruby 3+ needing
  `gem install webrick`, and stopping with Ctrl+C.
- A `curl` command to check Range support (expect `206`, not `200`).
- A reminder that browser timing recordings are per origin (port included), so use the same server and port, or
  Save the recording to its `.timing.js` file.

### Verification

- Sent `Range: bytes=100-199` for `Chapter1.mp3` to each server: `python3 -m http.server` answered `200 OK`; Ruby
  `httpd`, `npx http-server`, `npx serve` and `RangeHTTPServer` answered `206 Partial Content` with a correct
  `Content-Range`.
- Confirmed the default ports (8080, 3000, 8000) with the documented `curl` check.
- Loaded the app over `npx http-server -c-1` in headless Chrome: the tree showed 10 movements and all 3 artists, the
  first movement's MP3 loaded, and setting the audio to 120 s stayed at 120 s (duration 431 s), so seeking works.
