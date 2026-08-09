# Phase 1a, round 4 — repair the proof transcript. NO CODE CHANGE.

Repo: /home/raw996/ae/epiRhandbook_eng
Artifact to repair: `/tmp/gate/phase1a-transcript.md`

## Why this round exists

Round 3's review said, verbatim: **"The checker's behavior and all pinned values pass."** It
confirmed whole-file `1227/8`, in-chunk `1030/0`, and unchanged body, header and call-site results.
It endorsed keeping `get_data_names_in_file()` at whole-file scope and `count_get_data_calls()` on
normalised executable code.

It blocked on the transcript, with two findings. One is real. One is not.

**REAL — the transcript holds 12 `###` sections where the brief requires 6.** The round-3 brief said
"Re-run and keep the five that exist", which was the orchestrator's wording error. The implementer
correctly appended round 3's five sections, and round 1's five remained above them, plus a
non-proof section `### why no number moved: the three variants were measured on the corpus`.
Current headings, by line: 57, 134, 241, 337, 427, 499, 824, 947, 1033, 1169, 1306, 1459.

**NOT REAL — the "impossible raw command results" finding.** The reviewer said
`grep -c 'age_pyramid.tr'` and `grep -c 'regression.ru'` returning `0` are impossible because the
report's per-row table contains each pair. The orchestrator reproduced both commands against
`/tmp/gate/r3-postformat.txt`, under `command grep` and under the shell function, and both return
`0`. The report names only DIVERGENT pairs, 120 of them, not all 336. A pair that is clean in the
GREEN run is correctly absent. The transcript already says this at line 937. **Do not change those
numbers. They are correct.**

## Invariant

`/tmp/gate/phase1a-transcript.md` contains exactly six `###` proof sections, each with `RED:` and
`GREEN:`, and `utils/check-language-consistency.R` is byte-identical to what it is now.

## What to do

1. Rewrite `/tmp/gate/phase1a-transcript.md` so it holds **exactly six `###` sections**, in this
   order, each being the ROUND 3 version (the later one in the current file):
   `body-mutation`, `header-mutation`, `fence-engine-boundary`, `fence-close-length`,
   `get-data-comment-scope`, `name-scope-split`.
2. Move everything superseded — round 1's five sections and the `### why no number moved` section —
   into a separate file `/tmp/gate/phase1a-transcript-archive.md`. Do not delete the content; it is
   the record of how the earlier rounds were settled. It MUST NOT contain any `###` heading; demote
   them to `##` in the archive so no parser counts them as proof sections.
3. Add a short section to the main transcript titled `## reviewer finding refuted: raw grep results`
   (note `##`, not `###`, so it is not counted as a proof). It MUST record: the finding as quoted
   above, the two commands, their reproduced output, and the reason the result is correct, namely
   that the report names only divergent pairs. Include the reproduction:
   ```
   $ command grep -c 'age_pyramid.tr' /tmp/gate/r3-postformat.txt   -> 0
   $ command grep -c 'regression.ru'  /tmp/gate/r3-postformat.txt   -> 0
   $ command grep -oE '[a-z_]+\.(es|fr|jp|pt|ru|tr|vn)' /tmp/gate/r3-postformat.txt | sort -u | wc -l  -> 120
   ```
   Re-run all three yourself and report what YOU get. If any disagrees with the above, say so
   loudly rather than transcribing these numbers.

## Absolutely forbidden

- **Any change to `utils/check-language-consistency.R`.** Not one byte. Its staged blob is
  `975fd6...` — read the real value with `git rev-parse :utils/check-language-consistency.R` and
  confirm it is unchanged at the end.
- Any change to any file in the repo. `git status --porcelain` MUST end at exactly
  `A  utils/check-language-consistency.R`, the same as now.
- Re-running `air format`, installs, `renv.lock`.
- Bare `grep`. Use `command grep`; the shell's `grep` is a ugrep-backed function whose output has
  no `./` path prefix.

## Discriminator

```
Rscript utils/check-language-consistency.R
```

Its output MUST be byte-identical to `/tmp/gate/r3-postformat.txt`. You are not changing code, so
this is a regression guard, not a proof.

## Pass/fail

PASS when:
- `command grep -c '^### ' /tmp/gate/phase1a-transcript.md` returns exactly `6`
- each of the six sections carries `RED:` and `GREEN:` with its raw numbers, unchanged from round 3
- the archive file exists and contains zero `###` headings
- `git rev-parse :utils/check-language-consistency.R` is unchanged
- the discriminator output is byte-identical to `/tmp/gate/r3-postformat.txt`

FAIL if the checker file changes at all, if any proof section's numbers differ from round 3, or if
the refuted finding's numbers are altered to match the reviewer's expectation.
