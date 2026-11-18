# Session 2026-11-18 00:12 — Add Mozart's Requiem

## Ask

Add Requirem by Mozart from here: https://archive.org/details/lp_requiem_volfgang-amadeus-mozart-karl-bhm-viener-ph

## Response

Added Mozart's Requiem, K. 626, as a new work under the existing Mozart artist, following the same pattern as Handel's
Messiah (also from an Internet Archive LP): one movement per band of the LP.

### Source

- Deutsche Grammophon 2530 143 (1 LP), 1971: Edith Mathis, soprano; Julia Hamari, alto; Wiesław Ochman, tenor;
  Karl Ridderbusch, bass; Konzertvereinigung Wiener Staatsopernchor (Norbert Balatsch); Hans Haselböck, organ;
  Wiener Philharmoniker; Karl Böhm.
- Performers and track list taken from the item's metadata and the booklet OCR (`_djvu.txt`).
- The item's six VBR MP3s were used unchanged (largest is 48 MB, under GitHub's 50 MB warning).

### Files

| File | Content |
|---|---|
| `assets/Mozart/artist.js` | `"Requiem/work.js"` added to `workFiles` |
| `assets/Mozart/Requiem/work.js` | Work `mozart-requiem`: `language: "la"`, `translationLanguage: "zh"`, 6 movements |
| `assets/Mozart/Requiem/Chapter1..6.mp3` | Side 1 (Nos. 1–7, 34:13) in one track; Nos. 8, 9, 10, 11, 12 one track each |
| `assets/Mozart/Requiem/Chapter1..6.timing.js` | Latin text + Chinese translation, a heading line per number |
| `assets/Mozart/Requiem/Mozart.jpg` | Barbara Krafft's 1819 portrait (public domain, Wikimedia Commons), 960 px wide |
| `README.md` | Project structure updated |

Movements: I. Introitus, Kyrie, Sequentia (Nos. 1–7) · II. Domine Jesu (No. 8) · III. Hostias (No. 9) ·
IV. Sanctus (No. 10) · V. Benedictus (No. 11) · VI. Agnus Dei, Lux aeterna (No. 12).

### Timing

Only the heading lines are timed; every lyric line is `"time":null`, ready to record in the app.

- Headings in Chapter 1 were placed from loudness dips in the audio (vinyl noise prevents a plain silence detector),
  which agree with the sleeve's durations: No. 1 0:00, Kyrie 6:23.5, No. 2 9:36.5, No. 3 11:37.5, No. 4 15:55.5,
  No. 5 19:08.5, No. 6 26:12, No. 7 30:00.5.
- Chapters 2–6 start their heading at 0.
- The "Communio: Lux aeterna" heading in Chapter 6 is untimed: Agnus Dei runs into it without a clear gap
  (candidates at about 4:05 and 4:41).

### Translation

The Chinese translation was written for this project, using the 和合本 wording that the Messiah files use
(神, 米迦勒, 亚伯拉罕, 高高在上和散那, 神的羔羊). Solo/chorus changes inside a number are marked at the start of the line,
e.g. `(Bass)` / `（男低音）`.

### Checked

- All six `.timing.js` files parse as JSON; ids match `artist.js` / `work.js`.
- In Chrome (file://): the tree, top bar, info pane, picture and two-column lyrics show correctly; at 11:40 Auto mode
  highlights the No. 3 heading; no console warnings.

Not committed.
