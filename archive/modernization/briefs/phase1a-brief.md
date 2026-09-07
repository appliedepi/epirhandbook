# Phase 1a — cross-language code and chunk-header checker

Repo: /home/raw996/ae/epiRhandbook_eng  (Quarto book, 9 languages. NOT an R package: no
DESCRIPTION, no test suite, no R CMD check.)

## Invariant

`utils/check-language-consistency.R` reports every divergence between an English declared
chapter's R code AND chunk headers and each translation's.

## Files

You MAY create exactly one file: `utils/check-language-consistency.R`.
You MUST NOT touch anything else. No `.qmd`. No `_quarto.yml`. No `.github/`.

## What to build

Follow the shape of the existing `utils/check-data-equivalence.R`: a results `data.frame`, a
`table()` summary, a FAIL block, then the full per-row listing. Same register. Its header
comment block documents its own entry point (`# Run from the repo root: Rscript utils/...`);
do the same. Header prose follows the `rw-technical-prose` skill.

Nothing runs `utils/*.R` automatically in this repo. A human types the command. That is the
intended reachability; do not add a CI step, and do not edit `.github/`.

### Inputs, and three traps that each produced a wrong number during planning

1. Read the declared chapter list from `_quarto.yml` `book.chapters`. That structure holds 112
   entries, of which 64 are `part:` title strings in 9 languages. **Filter on `.qmd`** or you
   get 112 stems, 64 of which resolve to no file.
2. Read the language list from `_quarto.yml` `babelquarto.languages` (7 entries).
   **NOT `babelquarto.languagecodes`** (9 entries, including `de` and `en`). Reading the wrong
   key picks up German, whose files live under `_excluded/de/`, and reports 384 pairs.
3. MUST NOT hard-code 48 or 7.

### Body axis

Extract R chunks. Fence opening matches `^[ \t]*` + three-or-more backticks + `{r` — **`{r}`
chunks only, not any-engine `{...}`**. Then normalise: strip comments, replace string-literal
CONTENTS with a fixed placeholder, remove all whitespace, drop lines that become empty.

**A chunk that normalises to zero lines still counts as a chunk.** Do not drop it.

Both bolded rules are load-bearing. Any-engine extraction yields 26/86/224 and dropping
zero-line chunks yields 26/82/228. Either fails this phase for a reason that is not a defect.

Classify each chapter-language pair: `chunk-count`, `code-diff`, or `clean`. For `code-diff`,
report the chunk index and the differing normalised lines on both sides.

### Header axis (new, and the reason this phase is not just a body diff)

Compare the ordered list of chunk-header lines. Classify each pair `identical`,
`count-differs`, `text-differs`.

Within `text-differs`, canonicalise whitespace and quote style (`'` vs `"`) and report a
separate `cosmetic` sub-class, so the semantic rows are not buried. There are 9 cosmetic and 25
semantic among the 34.

The four rows that matter, all reader-visible, all invisible to a body-only check:
- `basics.tr` — English `echo=F`, Turkish drops it, so Turkish readers see source English hides
- `survival_analysis.jp` line 49 — same, `echo=F` dropped
- `ggplot_tips.fr` — English `eval=T`, French drops it and adds `message=F`
- `phylogenetic_trees.fr` — French adds `warning=FALSE, message=FALSE` English does not have

### get_data and dataset names

Count `get_data(name = )` call sites **INSIDE R chunks only**, English vs translation.
Whole-file counting is wrong and produced four false defects during planning: for example
`standardization.qmd:55` names `appliedepidata::get_data()` in prose, which makes all 7
languages look short by one when all 11 code call sites in fact match.

Validate every `get_data(name = "X")` against `appliedepidata::list_data()$name`. The literal
`"..."` is a benign placeholder present identically in English; do not report it as a defect.

## Ground truth — the checker MUST reproduce these exactly

Measured twice, by two independent implementations.

```
pairs                     336        (48 declared stems x 7 languages, zero missing)
body: chunk-count          26
body: code-diff            83        (260 differing chunks)
body: clean               227
header: identical         276
header: count-differs      26        (the same 26 pairs the body check catches)
header: text-differs       34        (9 cosmetic, 25 semantic)
dataset names outside catalogue: 8   (all the literal "...", one per data_used.*.qmd incl. English)
```

## Discriminator

```
Rscript utils/check-language-consistency.R
```

## Causally-red proof — REQUIRED, two sections

Copy `chapters/` to a scratch directory OUTSIDE the repo. The script takes the chapters
directory as an optional first argument (default `chapters`) precisely so this is possible
without touching a tracked file.

### section `body-mutation`
In the copy, change one `appliedepidata::get_data(name = "linelist_cleaned_rds")` call in one
translated chapter to `import("data/linelist_cleaned.rds")`.
RED: run against the copy. body `code-diff` MUST be 84, and the mutated pair MUST be named.
GREEN: run against the unmodified `chapters`. body `code-diff` MUST be 83.

### section `header-mutation`
In the copy, delete `echo=F` from one chunk header in one translated chapter that is currently
header-identical to English.
RED: run against the copy. header `text-differs` MUST be 35, and the mutated pair MUST be named.
GREEN: run against the unmodified `chapters`. header `text-differs` MUST be 34.

Write both sections to `/tmp/gate/phase1a-transcript.md`, each as `### <name>` with `RED:` and
`GREEN:` lines carrying the raw numbers.

## Pass/fail

PASS when:
- all eight ground-truth numbers reproduce exactly, AND
- the body mutation moves `code-diff` 83 -> 84 and nothing on the header axis, AND
- the header mutation moves `text-differs` 34 -> 35 and nothing on the body axis.

FAIL on any other outcome, including a number that is close. A number that is close means the
normalisation differs from the specified one, which is exactly the defect this pass criterion
exists to catch.

## Forbidden

- Bare `grep` in anything you write or run. `grep` in this shell is a function wrapping ugrep,
  whose output carries NO `./` path prefix, so every `^\./` filter is silently inert. Use
  `command grep`.
- `quarto render` without `--no-execute`, `quarto preview`, `renv::restore()`, `pak::pak()`,
  any install, any formatter, any linter.
- Editing `renv.lock`, `_excluded/`, `data/`, `html_outputs/`, `renv/`, `site_libs/`, any
  `*.de.qmd`, or anything under `.github/`.
- `git push`, `git tag`, `git commit`.
