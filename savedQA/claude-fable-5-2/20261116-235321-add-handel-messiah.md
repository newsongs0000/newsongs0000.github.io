# Add Handel's Messiah

- Date: 2026-11-16
- Model: claude-fable-5-2

## Ask 1

> Add Handell's Messiah https://archive.org/details/lp_messiah_georg-friedrich-hndel-the-london-symphony/disc1/01.01.+Overture.mp3

## Ask 2 (while the first was in progress)

> find English lyrics as original and Chinese translation

## Response

Added Handel's *Messiah* as a new artist and work, from the Internet Archive item
`lp_messiah_georg-friedrich-hndel-the-london-symphony` (Philips PHS 3-992, 1966: Colin Davis, London Symphony
Orchestra and Choir; Heather Harper, Helen Watts, John Wakefield, John Shirley-Quirk).

### Files

| File | What it is |
|---|---|
| `assets/Handel/artist.js` | Artist `handel` ("Handel 亨德尔") |
| `assets/Handel/Messiah/work.js` | Work `messiah` (HWV 56, 1741), 9 movements `ch1`..`ch9` |
| `assets/Handel/Messiah/Chapter1..9.mp3` | The item's 9 VBR MP3 tracks, unchanged (223 MB) |
| `assets/Handel/Messiah/Chapter1..9.timing.js` | Lyrics: English text, Chinese translation, some start times |
| `assets/Handel/Messiah/Handel.jpg` | Picture for all 9 movements: Thomas Hudson's 1749 portrait (Wikimedia Commons, public domain) |
| `app.js` | `assets/Handel/artist.js` in `APP_DATA.artistFiles` (the line was already there when I went to add it) |
| `README.md` | artistFiles example and project structure mention Handel |

### Movements

One movement per band of the LP set, named as on the LP:

| Movement | LP band | Part | Length |
|---|---|---|---|
| I. Overture | disc 1, side 1 | I | 4:05 |
| II. Nos. 1–6 | disc 1, side 1 | I | 17:24 |
| III. Nos. 7–15 | disc 1, side 2 | I | 22:52 |
| IV. Nos. 16–19 | disc 2, side 3 | I | 11:57 |
| V. Nos. 20–21 | disc 2, side 3 | II | 12:36 |
| VI. Nos. 22–34 | disc 2, side 4 | II | 25:55 |
| VII. Nos. 35–42 | disc 3, side 5 | II | 15:46 |
| VIII. Nos. 43–44 | disc 3, side 5 | III | 8:23 |
| IX. Nos. 45–52 | disc 3, side 6 | III | 24:18 |

The numbering (Overture, then Nos. 1–52) is the one printed in the LP's booklet.

### Lyrics

- **English (`text`)**: the libretto as printed in the LP's booklet (read from the item's OCR text, OCR errors
  corrected). Each number starts with a heading line, e.g. `No. 3 · Chorus [Isaiah 40:5]`. Scripture references use
  King James verse numbers; the booklet's differ in a few psalms and Isaiah 9.
- **Chinese (`translation`)**: 和合本 (Chinese Union Version, simplified), fetched from api.getbible.net (`cus`) and
  split to match the English lines.
- 282 lines in all.
- Text is written once per number, as in a libretto, not once per sung repetition. Whole sections that return are
  written out: No. 5 (A B A B), No. 16 (A B A), No. 21 and No. 46 (da capo), Nos. 8–9 (air, then chorus) and No. 31.

Where the Chinese is not 和合本 word for word:

| Where | Change |
|---|---|
| Nos. 18, 19, 21, 25, 27, 28, 29, 30 | 我 changed to 他, because the libretto puts these verses in the third person |
| Nos. 1, 4, 34, 36, 47, 48 | Clauses reordered to follow the English line order |
| Nos. 1, 4, 15 | 和合本's alternative reading (its bracketed note) used, because it matches the King James text |
| Nos. 12, 35, 51 | Shortened or split to match the English ("奇妙、策士", no "妇女", Rev 5:9 condensed) |
| Throughout | "甚么" written as "什么"; no space before "神" |

Left as 和合本 although it differs from the English: No. 43 "我必在肉体之外得见神" (English: "in my flesh"),
No. 26 "耶和华" (English: "God"), No. 48 "死啊" for "O grave".

### Start times

64 of the 282 lines have a start time: the heading of every number, and the first line of some sections inside a
number. All other lines are `null`, to be timed with Rec.

- Found from the silences between numbers in the audio, and checked against Whisper transcriptions of the first
  minute after each one.
- Three section starts come from the transcription alone and can be a second or so off: "(Soprano) Come unto Him"
  in No. 18, and the vocal re-entries in Nos. 21 and 46.
- No. 28's start (814.5 s in movement VI) is the least certain: two isolated chords precede it, taken to be the end
  of No. 27.
- Effect in Auto mode: the highlight sits on the heading of the number being played, not on each sung line.

### Checked

In headless Chrome over a local server: all 9 movements load audio, lyrics (two columns) and picture with no
errors; at 11:58 in movement VII the highlighted line is "No. 42 · Chorus"; clicking an untimed line seeks to an
interpolated position.

### To know

- Handel sorts first in the tree, so with no `movement` in the URL the app now opens on Messiah I. Overture
  instead of Chinese Requiem I.
- The recording is a 1966 Philips release. The Internet Archive offers it for download, but it is not public
  domain. The lyrics (1741 libretto, 和合本 of 1919) and the portrait are.
- Nothing is committed.
