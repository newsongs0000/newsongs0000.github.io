# Scripts

Helper scripts for maintaining the assets. They need [Node.js](https://nodejs.org/) only (no `npm install`);
`make-work-pdf.js` also needs Google Chrome or Microsoft Edge. Run everything from the repository root.

| Script | Output (next to each `work.js`) |
| --- | --- |
| [make-work-txt.js](make-work-txt.js) | `work.txt`: plain text, each lyric line followed by its translation |
| [make-work-pdf.js](make-work-pdf.js) | `work.pdf`: original language on the left, translation on the right |

Both read the same input (a work's `work.js` and the `*.timing.js` of its movements, loaded by
[lib/load-work.js](lib/load-work.js)), and both overwrite an existing output file. Rerun them after editing
`work.js` or any `*.timing.js`. The times in the timing files are ignored.

Without arguments a script processes every directory under `assets/` that contains a `work.js`; or pass one or
more work directories:

```sh
node scripts/make-work-txt.js
node scripts/make-work-txt.js assets/Handel/Messiah
node scripts/make-work-pdf.js assets/Handel/Messiah
node scripts/make-work-pdf.js assets/Mozart/Requiem assets/HuangAnlun/ChineseRequiem
```

## make-work-txt.js

Generates a plain-text version of a work. It combines the titles and movement headers from `work.js` with the
lyrics (and translations) from every movement's `*.timing.js` (named after the movement's `audio`:
`Chapter1.mp3` → `Chapter1.timing.js`). Only `lines[].text` and the optional `lines[].translation` are used.

### Output layout

Blocks are separated by a blank line:

```text
Messiah                                  <- title
弥赛亚                                    <- translated title

I Overture                               <- movement header: number + title,
Orchestra                                   voicing, then the same two lines
I 序曲                                      in the translation language
管弦乐

Sinfony (Overture) · Grave               <- one block per lyric line:
序曲 · 庄板                                 text, then its translation

Allegro moderato
中庸的快板
```

- The main language comes first, as in `work.js` (`language` / `translationLanguage`): English for Messiah and
  Mozart's Requiem, Chinese for the Chinese Requiem.
- Lines without a translation (Chinese Requiem chapters 2–8) appear as a block of their own.
- Line breaks inside a lyric are kept; leading and trailing spaces are trimmed.
- A movement's `subtitle` and `description` are not included.

### Notes

The output is called `work.txt`, not `lyrics.txt`, because `assets/HuangAnlun/ChineseRequiem/Lyrics.txt` is the source
lyrics and the two names collide on case-insensitive file systems (macOS, Windows).

## make-work-pdf.js

Generates `work.pdf`, an A4 PDF with two columns: the original language on the left (`language` in `work.js`) and
the translation on the right (`translationLanguage`, in blue). Each lyric line is one row, so a line and its
translation sit side by side; rows are never split across pages. The work title and every movement header
(number, title, voicing) are laid out the same way, and pages are numbered.

The PDF is rendered by headless Chrome from a temporary HTML page, so the CJK text uses the fonts of the machine
running the script. The browser is found automatically on macOS, Linux and Windows (Chrome, Edge or Chromium);
otherwise point to it:

```sh
CHROME="/path/to/chrome" node scripts/make-work-pdf.js
```

- Lines without a translation (Chinese Requiem chapters 2–8) leave the right column empty.
- A movement's `subtitle` and `description` are not included.
- A PDF is about 1 MB because the CJK font is embedded.
