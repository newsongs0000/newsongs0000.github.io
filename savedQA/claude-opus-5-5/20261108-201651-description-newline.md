# Session 2026-11-08 20:16 — Newline in work description

## Ask

When the value of the description field of line 626 is displayed, insert a newline before "词：唐佑之（根据圣经）"

## Answer

Two changes in `index.html`:

1. The Chinese Requiem `description` string now has a `\n` before `词：唐佑之（根据圣经）`.
2. `#info-description` CSS gets `white-space: pre-line;`, so newlines in a description are shown as line breaks.
   It still wraps long lines and collapses runs of spaces as before.

The description is still rendered with `textContent` (no HTML injection). Any other work's description can use `\n` the same way.
