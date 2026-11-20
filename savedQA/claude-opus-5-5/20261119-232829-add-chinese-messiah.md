# Add a Chinese version of Handel's Messiah

## Ask

Create another version of Handel's Messiah whose original language is Chinese, translation language is English,
download MP3 audio from here: https://www.bilibili.com/en/video/BV1eb4y1h7Va/

## Answer

Added `assets/Handel/MessiahChinese/` and registered it in `assets/Handel/artist.js` (`"MessiahChinese/work.js"`).
It shows in the tree as **弥赛亚（中文版） Messiah (Chinese)** under Handel, next to the English Messiah.

### Source

- The Bilibili video is a single 2 h 22 min upload (no chapters, no CC subtitles). The uploader (发呆界小青瓜) restored
  the audio and burned in Chinese + English subtitles, notes and pictures; the performers are not named anywhere.
- `yt-dlp` failed with HTTP 403/567 from Bilibili's CDN (even the latest version), so the audio (AAC 320 kbps) and
  the 720p video were fetched with `curl` from the stream URLs that `yt-dlp -J` reported (Range requests worked).

### Audio

- Cut into 9 MP3s (`Chapter1..9.mp3`, LAME VBR `-q:a 3`, ~160 kbps, 169 MB total) at silences between numbers,
  in the **same grouping as the English Messiah**:

  | Chapter | Numbers (video numbering) | English Messiah equivalent |
  | --- | --- | --- |
  | I | 1 序曲 | Overture |
  | II | 2–7 | Nos. 1–6 |
  | III | 8–18 | Nos. 7–15 |
  | IV | 19–22 | Nos. 16–19 |
  | V | 23–24 | Nos. 20–21 |
  | VI | 25–37 | Nos. 22–34 |
  | VII | 38–45 (Hallelujah) | Nos. 35–42 |
  | VIII | 46–47 | Nos. 43–44 |
  | IX | 48–55 (Amen) | Nos. 45–52 |

### Lyrics and timing

- The lyrics were read from the video's burned-in subtitles with Apple Vision OCR (Chinese line and English line
  separately, 2 frames per second, majority vote per subtitle), then proofread by hand against the frames.
- Each lyric line's `time` is when its subtitle appears in the video, so the files are **already timed**
  (to about 0.5 s). Spot-check and fine-tune with the LYRICS TIMING panel if needed.
- `text` is the Chinese as sung, `translation` the English libretto as shown in the video.
- Each number starts with a heading line, e.g.
  `第2首 · 安慰我的百姓 · 宣叙调（男高音）[以赛亚书40:1–3]` / `No. 2 · Comfort ye my people · Recitative (tenor) [Isaiah 40:1–3]`.
  Numbers and Chinese titles follow the video's title cards (55 numbers; it numbers differently from the LP
  booklet used by the English Messiah). Voice types are the score's, since the performers are unknown.
- Obvious subtitle typos were corrected (e.g. 见朽壤 → 见朽坏).
- The video has no subtitle for the opening "Glory to God" phrase of No. 18; the timing follows the video.

### Other files

- `work.js`: `language: "zh"`, `translationLanguage: "en"`, parts as subtitles (第一部：预言与成就, 第二部：受难与得胜,
  第三部：复活与荣耀), description with source and credits. The picture reuses `../Messiah/Handel.jpg`; the
  video's paintings were not copied.
- `work.txt` and `work.pdf` generated with `scripts/make-work-txt.js` and `scripts/make-work-pdf.js`.
- `README.md` project structure lists the new folder.

### Checked

- All 9 `.timing.js` files parse as JSON and have increasing times.
- Loaded in headless Chrome over HTTP: the work appears in the tree, durations are right, lyrics show Chinese left /
  English right, and clicking a line seeks to its time.

Nothing was committed.
