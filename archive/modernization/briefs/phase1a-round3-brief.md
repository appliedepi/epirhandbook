# Phase 1a, round 3 — report dataset-name validation at BOTH scopes

Repo: /home/raw996/ae/epiRhandbook_eng
File: `utils/check-language-consistency.R` (exists, staged, not committed)

## Why this round exists

Round 2 was BLOCKED. The block was correct against the round-2 brief, and the round-2 brief was
wrong. The owner has re-scoped the unit. Read this section, because it tells you what NOT to undo.

Round 2's reviewer found:
> - `count_get_data_calls()` uses `normalise_body()`, contrary to the explicit requirement.
> - `get_data_names_in_file()` still extracts names from the raw whole file, including prose,
>   comments, and string-contained text. It does not extract names from comment-stripped R chunks
>   as required.
> - The `get-data-comment-scope` GREEN proves only the call-site count. [...] the required
>   production property has no genuine RED/GREEN proof.

The round-2 implementer deviated from that brief and argued whole-file scanning was correct. The
orchestrator measured it and the implementer was right, so the brief changed rather than the code.

**Measured on the checker's real base, 384 declared chapter files (48 stems x 8 languages):**

```
WHOLE-FILE scope : 1227 name literals, 8 outside catalogue   (all the literal "...")
IN-CHUNK  scope  : 1030 name literals, 0 outside catalogue
prose-only literals (whole minus in-chunk): 197
```

The 8 placeholders live in PROSE. In-chunk scope cannot see them, so it reports 0 and the pinned 8
disappears. Whole-file is the STRONGER check: a chapter that prints `get_data(name = "typo")` in a
sentence is a defect, because a reader copies that sentence and runs it.

## Invariant

The checker reports dataset-name validation at BOTH scopes, separately and labelled, and every
previously pinned number is unchanged.

## What to change

Report name validation twice, clearly labelled:

1. **whole-file scope** — every `get_data(name = "...")` literal anywhere in the file, prose
   included. This is the existing `get_data_names_in_file()`. **Do not narrow it.** An R comment
   stripper MUST NOT run over a whole `.qmd`: every markdown heading starts with `#`.
2. **in-chunk scope** — literals inside `{r}` chunks only, with R comments removed and **string
   literal contents PRESERVED** (a `#` inside a string literal is not a comment; the file already
   has a string-aware scanner). This is a new number.

For any name outside the catalogue, say which scopes it appears in. A bad name that is executable
is more serious than one that is only mentioned in prose, and the output MUST let a reader tell
them apart.

## What to leave alone — all of this passed review

- The `FENCE_OPEN` engine boundary fix. Reviewer called the proof genuine.
- The closing-fence backtick-length fix. Reviewer called the proof genuine.
- `count_get_data_calls()` using `normalise_body()`. This is the per-pair CALL-SITE COUNT axis and
  it is correct: comparing languages needs executable code only, and the count does not need the
  name. Round 2's reviewer objected that it "destroys string contents instead of preserving dataset
  names" — irrelevant to a count. **Keep it.**

## Pinned numbers — all MUST be unchanged

```
pairs                     336
body: chunk-count          26
body: code-diff            83     (260 differing chunks)
body: clean               227
header: identical         276
header: count-differs      26
header: text-differs       34     (9 cosmetic, 25 semantic)
get_data call-site axis:  differs 2 / match 334, naming grouping.es and cleaning.fr
name validation, whole-file: 384 files, 1227 literals, 8 outside catalogue, all "..."
```

New, and MUST be reported:
```
name validation, in-chunk:   1030 literals, 0 outside catalogue
```

## Discriminator

```
Rscript utils/check-language-consistency.R
```

## Proof — SIX sections in /tmp/gate/phase1a-transcript.md

Re-run and keep the five that exist: `body-mutation`, `header-mutation`, `fence-engine-boundary`,
`fence-close-length`, `get-data-comment-scope`.

Add one. The corpus has no bad dataset name at all, so it cannot exercise this; build a fixture
outside the repo. The pre-change checker is at
`git show dc9e526db66fc6749ff192bd814f769af1a60e2d:utils/check-language-consistency.R`.

- `### name-scope-split` — fixture with TWO names that are not in the catalogue: one in a prose
  sentence only, one inside a live `{r}` chunk.
  RED: the pre-change checker reports both as a single undifferentiated count, with no way to tell
  which is executable.
  GREEN: the post-change checker reports whole-file 2 outside catalogue and in-chunk 1 outside
  catalogue, and names which one is executable.

## Pass/fail

PASS when every pinned number above is unchanged, the in-chunk name scope reports 1030 literals and
0 outside catalogue, the output distinguishes the two scopes for any bad name, and all six sections
carry RED and GREEN with raw numbers.

FAIL if any pinned number moves, or if the two scopes are reported as one number, or if
`get_data_names_in_file()` has been narrowed.

## Forbidden

- Any file other than `utils/check-language-consistency.R`. No `.qmd`. No `_quarto.yml`.
- Fixtures live outside the repo. `git status --porcelain` MUST end at exactly
  `A  utils/check-language-consistency.R`.
- Bare `grep`. It is a ugrep-backed shell function emitting paths with no `./` prefix, so `^\./`
  filters are silently inert. Use `command grep`.
- `git commit`, `git push`, `git tag`, installs, `renv.lock`.
