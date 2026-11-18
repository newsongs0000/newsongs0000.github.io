# Session 2026-11-08 22:50 — Correct values for Mozart Symphony No. 40, movement I

## Ask

now do that same for this file
(file: `assets/Mozart/Symphony40/work.js`; same as the previous ask: replace the movement's values with correct ones)

## Answer

Movement I of Mozart's Symphony No. 40 in G minor, K. 550, is the *Molto allegro*, in G minor, for orchestra only (no
singers). The file is written in Chinese, so the key and performers are in Chinese. The tempo marking stays in
Italian, as is usual.

| Field | Before | After |
|---|---|---|
| `title` | `Movement 1` | `Molto allegro` |
| `subtitle` | `诗篇116:7,9` (copied from the Requiem) | `G小调` (G minor) |
| `voicing` | `合唱` (chorus; copied from the Requiem) | `管弦乐` (orchestra) |

`id` (`ch1`), `number` (`I`), `audio` and `thumbnail` were already right, so they are unchanged. The heading above the
lyrics now reads:

```
I. Molto allegro [G小调]
管弦乐
```

The values come from my own knowledge of the score; I did not look them up online.

### Notes (not changed)

- As with Mahler, `Chapter1.mp3` here is a byte-for-byte copy of the Requiem's Chapter 1, and `Chapter1.timing.js`
  holds Requiem lyrics. This symphony is purely orchestral, so none of its movements has lyrics.
- The work-level fields are right: 1788 (completed 25 July 1788), K. 550, G minor. One exception:
  `premiered: "Vienna, 1788"` is not documented. No record of a first performance survives, and a performance in
  1788 is only a guess.
