# Session 2026-11-08 22:49 — Correct values for Mahler Symphony No. 2, movement I

## Ask

Replace the values in the movement (lines 11 - 19) with correct values
(file: `assets/Mahler/Symphony2/work.js`)

## Answer

Movement I of Mahler's Symphony No. 2 is the *Allegro maestoso*, marked "Mit durchaus ernstem und feierlichem
Ausdruck" ("with a thoroughly serious and solemn expression"). It is purely orchestral, with no singers. It grew out of
Mahler's 1888 symphonic poem *Totenfeier*.

| Field | Before | After |
|---|---|---|
| `title` | `Move 1` | `Allegro maestoso` |
| `subtitle` | `subtitle for Movement 1` | `Mit durchaus ernstem und feierlichem Ausdruck` |
| `voicing` | `orchestra` | `Orchestra` |

`id` (`ch1`), `number` (`I`), `audio` and `thumbnail` were already right for the files in that folder, so they are
unchanged. The heading above the lyrics now reads:

```
I. Allegro maestoso [Mit durchaus ernstem und feierlichem Ausdruck]
Orchestra
```

The values come from my own knowledge of the score; I did not look them up online.

### Notes (not changed)

- `Chapter1.mp3` in that folder is a byte-for-byte copy of the Requiem's Chapter 1. `Chapter1.timing.js` and
  `Chapter1-Lyrics.txt` also hold Requiem lyrics. The real movement I has no lyrics. In this symphony only IV
  (*Urlicht*, alto solo) and V (finale: soprano, alto, chorus) are sung.
- The work-level fields above the movement (outside lines 11–19) are also placeholders that are wrong for this
  symphony:
  - `year: 1902`: composed 1888–1894, first performed complete in 1895
  - `opusNumber: "Op. 63"`: copied from the Requiem; Mahler's symphonies have no opus numbers
  - `premiered: "Berlin, December 1903"`: the complete premiere was in Berlin on 13 December 1895, conducted by
    Mahler
