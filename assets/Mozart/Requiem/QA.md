# Requirem by Mozart

## Ask

Add Requirem by Mozart from here: https://archive.org/details/lp_requiem_volfgang-amadeus-mozart-karl-bhm-viener-ph

## Opus 5.5 Extra high

I've added Mozart's Requiem, K. 626, from that Internet Archive recording, under the existing Mozart artist. It loads and plays in Chrome with no console warnings. Only the section headings are timed so far; you'll need to record the timing of the lyric lines yourself.

**The recording:** Karl Böhm conducting the Wiener Philharmoniker, with Mathis, Hamari, Ochman and Ridderbusch (Deutsche Grammophon LP, 1971). The performers come from the booklet's track listing.

**Movements (six, one per LP track, as with Messiah):**

| Movement | Contents | Length |
|---|---|---|
| I. Introitus, Kyrie, Sequentia | Nos. 1–7 (the whole of side 1, which the archive has as one track) | 34:13 |
| II. Domine Jesu | No. 8 | 4:44 |
| III. Hostias | No. 9 | 5:06 |
| IV. Sanctus | No. 10 | 1:59 |
| V. Benedictus | No. 11 | 6:55 |
| VI. Agnus Dei, Lux aeterna | No. 12 | 11:35 |

**Files:**
- [assets/Mozart/Requiem/work.js](assets/Mozart/Requiem/work.js) is the new work, and [artist.js](assets/Mozart/artist.js) now lists it.
- The six MP3s are the archive's files, unchanged. The largest is 48 MB, just under GitHub's 50 MB warning size.
- The picture is Barbara Krafft's 1819 portrait of Mozart, which is public domain.
- The lyrics files have the Latin text with a Chinese translation I wrote, in the same 和合本 wording as the Messiah files (神, 米迦勒, 亚伯拉罕, 高高在上和散那). Where a soloist or a section of the choir takes over, the line starts with a marker such as `(Bass)` / `（男低音）`.
- I updated the project-structure section of the [README](README.md).

**Timing:** each number's heading line is timed, and every lyric line is `null`, as in the first Messiah files. Side 1 has no silent gaps because of vinyl surface noise, so I placed its headings at dips in the loudness. They agree with the track lengths printed on the sleeve. In Auto mode at 11:40 the "No. 3 · Tuba mirum" heading was highlighted, as expected. I left the "Lux aeterna" heading in movement VI untimed. It follows the Agnus Dei without a clear gap, and I couldn't tell whether it starts at about 4:05 or 4:41.

I haven't committed anything. The session is saved in [savedQA/claude-opus-5-5/](savedQA/claude-opus-5-5/20261118-001233-add-mozart-requiem.md).