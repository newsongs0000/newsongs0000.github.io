# Requiem by Verdi

## Ask

Add Requiem by Verdi

## Opus 5.5

Verdi's Requiem is added as a new artist, **Verdi 威尔第**, with the work **Requiem 安魂曲**. It loads and plays
in Chrome with no console warnings. As with Mozart's Requiem, only the section headings are timed; the lyric lines
are untimed.

**Recording:** no source was given, so I chose the 1960 recording by Fritz Reiner and the Wiener Philharmoniker, with
Leontyne Price, Rosalind Elias, Jussi Björling and Giorgio Tozzi (RCA Victor Red Seal LD 6091, 2 LPs, 1961). It comes
from the same Internet Archive LP collection as the Mozart:
https://archive.org/details/lp_verdi-requiem_fritz-reiner-wiener-philharmoniker

**Movements:** eight, one per LP band, as with Mozart and Messiah.

| Movement | Contents | Length |
|---|---|---|
| I. Requiem e Kyrie | No. 1 | 11:57 |
| II. Dies irae (1) | No. 2: Dies irae, Tuba mirum, Mors stupebit, Liber scriptus, Quid sum miser | 14:26 |
| III. Dies irae (2) | No. 2 concluded: Rex tremendae, Recordare, Ingemisco, Confutatis, Lacrymosa | 25:00 |
| IV. Offertorio | No. 3: Domine Jesu Christe, Hostias | 12:01 |
| V. Sanctus | No. 4 | 2:48 |
| VI. Agnus Dei | No. 5 | 5:33 |
| VII. Lux aeterna | No. 6 | 7:10 |
| VIII. Libera me | No. 7 | 15:48 |

**Files:**
- `assets/Verdi/artist.js` and `Verdi.jpg` (Boldini's 1886 portrait); `app.js` lists the new artist.
- `assets/Verdi/Requiem/work.js`, `Chapter1..8.mp3`, `Chapter1..8.timing.js`, `Chapter1..8-bg.jpg`, `work.jpg`
  (the 1874 Ricordi title page), `backgrounds.md` (sources and licenses), and the generated `work.txt` and
  `work.pdf`.
- `README.md`: the project-structure section.

**Audio:** the archive's MP3s had the same LP hiss as the Mozart and Messiah files before they were cleaned. I used
the same filter (`afftdn=nr=18:nf=-48:nt=w:tn=1`, with its 25 ms delay removed) and re-encoded as LAME VBR q2. The
quietest passages are 15–38 dB quieter above 4 kHz. The length is the same to the sample, there is no time shift,
and the tags and cover art are kept. The largest file, Chapter3.mp3, is 32 MB.

**Lyrics:** Verdi's Latin text with a Chinese translation in the same wording as the Mozart files. Where a soloist
or the chorus takes over, the line starts with a label such as `(Tenor)` / `（男高音）`.

**Timing:** 23 section headings are timed (Kyrie, Tuba mirum, Mors stupebit, Liber scriptus, Recordare, Hostias,
and so on), and all other lines are `null`. I placed them using the Decca CD of the same recording, whose track
lengths are listed on MusicBrainz (about 2% longer than the LP bands). I then moved each one to the nearest break in
the loudness, and checked it against Whisper where it heard the soloists (for example "Recordare, Jesu pie" and
"Ingemisco tamquam reus"). Whisper could not follow the Latin choruses, so it cannot draft the line timings the way
it did for Messiah; these will need to be recorded with ● Rec. In a headless Chrome test, every heading was
highlighted at the expected moment in Auto mode.

**Pictures:** all public domain, from Wikimedia Commons. The LP's own booklet is illustrated with Luca Signorelli's
Last Judgment frescoes at Orvieto, so I used those for I–IV (Lamentation, Resurrection of the Flesh, The Damned, The
Elect). The others are van Eyck's Singing Angels (V) and Adoration of the Mystic Lamb (VI), Fra Angelico's Paradise
(VII), and John Martin's The Great Day of His Wrath (VIII).

Nothing is committed.
