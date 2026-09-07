# Phase 1a, round 2 — fix three extraction defects in the checker

Repo: /home/raw996/ae/epiRhandbook_eng
File: `utils/check-language-consistency.R` (already exists, staged, not committed)

Round 1 was BLOCKED by adversarial review. The pinned numbers and both causal proofs passed.
Three extraction defects did not. Fix exactly those three. Change nothing else.

## The prior verdict, verbatim

> - `utils/check-language-consistency.R:51` uses `\\{r` without a boundary. It therefore treats
>   engines such as `{ruby}` or `{rust}` as R chunks, contrary to the explicit R-only requirement.
>   The pinned corpus does not expose this defect.
> - `utils/check-language-consistency.R:134-136` counts `get_data(name=...)` with a regex over raw
>   chunk text. Text in R comments or string literals counts as a call site, although it is not
>   executable code. The required causal proofs do not test this assertion.
> - `utils/check-language-consistency.R:52,77` accepts any three-backtick closing fence, even for an
>   opening fence with four or more backticks. A valid four-backtick R chunk containing a
>   three-backtick line will be truncated.

## Measured: none of the three has a live instance in this corpus

The orchestrator measured this before writing the brief. Do not re-litigate it; use it.

```
4+ backtick fences in chapters/            0
engines present                            r 13652, bash 64, =html 1   (nothing else starts with r)
get_data(name= inside an R comment in a real chunk   0
```
The single commented `get_data` is `chapters/grouping.es.qmd:61`, and its fence lines are commented
too (`#```{r, eval=F}`), so no chunk ever opens there and the line is already outside chunk scope.
That pair's `get_data` divergence is a REAL finding and MUST survive this fix.

## Invariant

The three defects are fixed AND every pinned number is unchanged.

## The three fixes

1. **`FENCE_OPEN`.** Must match an R chunk only: `r` followed by `}`, `,`, or whitespace. Must NOT
   match `{ruby`, `{rust`, `{rmd` or any other engine beginning with `r`.

2. **Closing fence length.** A chunk opened with N backticks closes only on a fence of N or more
   backticks. Track the opening length per chunk. `FENCE_CLOSE` as a fixed `` `{3,} `` is wrong.

3. **`get_data(name = )` scope.** Count call sites and extract names from chunk text with **R
   comments removed**, so a commented-out call is not a call site.

   **Careful, and this is the trap:** the body axis normaliser replaces string-literal CONTENTS with
   `<string>`, which would destroy the dataset name you must extract. So do NOT reuse the body
   normaliser here. You need comment-stripping WITHOUT string-content replacement: strip comments
   using the existing string-aware scanner (a `#` inside a string literal is not a comment), keep
   the literals intact, then count call sites and extract names from that text.

## Pass criterion — the whole point of this round

Run the discriminator. **All eight pinned numbers MUST be byte-identical to round 1:**

```
pairs                     336
body: chunk-count          26
body: code-diff            83     (260 differing chunks)
body: clean               227
header: identical         276
header: count-differs      26
header: text-differs       34     (9 cosmetic, 25 semantic)
dataset names outside catalogue: 8   (all the literal "...")
```

The `get_data` call-site axis MUST still report `differs 2 / match 334`, and both divergent pairs
MUST still be `grouping.es` and `cleaning.fr`.

**If any number moves, the fix is wrong.** The three defects have no live instance, so a correct fix
cannot change any result on this corpus. A moved number means you changed behaviour on real content.
Report the movement; do not adjust a threshold to absorb it.

## Discriminator

```
Rscript utils/check-language-consistency.R
```

## Proof — FIVE sections required in /tmp/gate/phase1a-transcript.md

Keep the two existing sections. They are still valid; re-run them and confirm they still hold.

- `### body-mutation`   (existing, re-run)
- `### header-mutation` (existing, re-run)

Add three, each proving one fix. The corpus cannot exercise these, so build a **fixture directory
outside the repo** holding a few small `.qmd` files that do. The script already takes the chapters
directory as its first argument.

The PRE-FIX checker is available without touching the repo:
`git show cb1b60a0d36d91924ddc332d906429df7e73602e:utils/check-language-consistency.R > /tmp/gate/checker-prefix.R`

For each: RED = pre-fix checker on the fixture gives the wrong answer, with the number. GREEN =
post-fix checker on the same fixture gives the right answer, with the number.

- `### fence-engine-boundary` — fixture with a `{rust}` or `{ruby}` chunk. RED: pre-fix counts it as
  an R chunk. GREEN: post-fix does not.
- `### fence-close-length` — fixture with a 4-backtick R chunk containing a 3-backtick line. RED:
  pre-fix truncates the chunk. GREEN: post-fix keeps it whole.
- `### get-data-comment-scope` — fixture with a real `get_data(name = "x")` call and a commented
  `# get_data(name = "y")` inside the SAME chunk, plus one `get_data(name = "z")` inside a string
  literal. RED: pre-fix counts 3. GREEN: post-fix counts 1, and the extracted name is `x`.

## Pass/fail

PASS when all eight pinned numbers are unchanged, the `get_data` axis still reports 2/334 naming
`grouping.es` and `cleaning.fr`, and all five transcript sections carry RED and GREEN with the raw
numbers.

FAIL if any pinned number moves, or if a fixture proof cannot be made red against the pre-fix
checker — that would mean the defect it claims to fix was never there.

## Forbidden

- Any file other than `utils/check-language-consistency.R`. No `.qmd`. No `_quarto.yml`.
- Fixtures MUST live outside the repo. `git status --porcelain` MUST end showing only
  `A  utils/check-language-consistency.R`.
- Bare `grep`. It is a ugrep-backed shell function emitting paths with no `./` prefix, so `^\./`
  filters are silently inert. Use `command grep`.
- `git commit`, `git push`, `git tag`, installs, formatters run by hand, `renv.lock`.
