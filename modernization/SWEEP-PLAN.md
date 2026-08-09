# Cross-language consistency sweep — epiRhandbook (v3)

## Context

v2 was approved and partly executed. Two things changed and force an amendment.

**Phase 1b cannot pass its own criterion.** It required all 336 chapter-language pairs. A session
quota limit killed the run at 98. The remaining 238 pairs have never been read. Leaving the phase
open indefinitely is dishonest bookkeeping, so v3 closes it at what was actually done and makes the
rest an explicit, separately-scoped phase.

**Two measurements now exist that v2 could only guess at.** A model A/B and a cost figure. Both
change the design, and both are recorded below as evidence rather than assumption.

The owner's three standing decisions are unchanged: read all 336 pairs, English is the reference so
translator additions are removed, and Phase 3 drafts and ships the translated prose.

---

## What is done

**Phase 1a — COMPLETE and reviewed.** `utils/check-language-consistency.R` compares 336 pairs on
four axes. `codex-review.py` returned ALLOW at round 4. Cost: four implementer rounds, four reviews.

**Phase 1b — 98 of 336 pairs, artifacts built and verified, NOT reviewed.**

```
chapters complete (7/7 languages)  14   = 98 pairs
chapters never started             34   = 238 pairs
partial chapters                    0   clean boundary
findings                          493   untrue 205, missing 155, code_mismatch 69, added 55, alignment 9
coverage rows                    5561
findings by language              tr 112, jp 85, fr 74, pt 62, vn 60, es 57, ru 43
```

Artifacts, all verified by an independent run: `utils/language-prose-drift.tsv` (493 rows),
`utils/language-prose-coverage.tsv` (5561 rows), `utils/prose-sweep/` (98 JSON, sha256-matched),
`utils/PROSE-SWEEP-RESUME.md` (the resume record).

Three of the 98 pairs have zero findings, so the drift file names 95 distinct pairs, not 98.
Recorded explicitly, because "absent from drift" must never be read as "never examined".

**The sweep is finding severe defects.** From `basics.tr` alone:
- English says do not put parentheses after `?functionname`; Turkish says do not use an apostrophe.
- English names the R package `leaflet`; Turkish names `brosur`, the Turkish word for "brochure".
  No such package exists.
- The Turkish class table gives R's logical values as `DOGRU`/`YANLIS`. They are `TRUE`/`FALSE`.

A Turkish reader following that chapter types code that cannot run. This answers the reviewer's
challenge that a full sweep was disproportionate to three confirmed defects.

---

## Measured evidence that changes the design

**Model A/B, four pairs, identical prompt, Sonnet medium against the Opus baseline.**

| | Opus | Sonnet medium |
|---|---|---|
| tokens per pair | 54,820 | **118,244** (2.2x MORE) |
| findings over the 4 pairs | 48 | 21 (44%) |
| `basics.tr` | 20 | 3 (15%) |
| `basics.tr` untrue | 11 | 0 |
| clean control `data_table.ru` | 0 | 1 |

Sonnet also wrote `data_table.json` instead of `data_table.ru.json`, which across 7 languages
silently overwrites, and reported 8 findings for `collaboration.fr` while writing 9.

**DECISION: Opus, not Sonnet.** Cheaper per token, more tokens used, and it missed all three severe
Turkish defects.

**The root cause is segmentation, not judgement.** Opus split `basics.tr` into 139 segments, Sonnet
into 80. They are not judging the same material. Every agent currently re-derives the segment map
by hand: splitting on headings, stripping `{#anchor}` attributes, finding fence boundaries, counting
line ranges. One agent literally wrote out a `_seg_en.json` map, which is the artifact a script
should produce once.

---

## Phase A — deterministic segmenter, and measure what it saves

**Invariant.** `utils/segment-chapters.R` produces one authoritative segment map per chapter file,
and a re-run of the same four A/B pairs using it costs measurably less per pair.

**Agent.** `implementer-high`. **Files.** May create `utils/segment-chapters.R`. Nothing else in
the repo.

**Requirements.**
- Reuse the chunk-fence logic already written and reviewed in `utils/check-language-consistency.R`:
  `{r}`-only opening fences, closing fence matching the opening backtick count. Do not write a
  second fence parser.
- Read declared chapters from `_quarto.yml` `book.chapters` filtered on `.qmd`; languages from
  `babelquarto.languages`. Do not hard-code 48 or 7.
- Emit per file: an ordered list of sections (heading text with the trailing `{#anchor}` /
  `{.unnumbered}` attribute block STRIPPED, heading level, start and end line) and, within each
  section, segments — runs of prose between code-chunk boundaries — each with a stable id, start
  line, end line, and the text.
- Write to `utils/segments/<chapter>[.<lang>].json`. These are build artifacts of the source, so
  they are reproducible and may be regenerated.
- No LLM, no network. Pure text processing.

**Discriminator.**
```
Rscript utils/segment-chapters.R && Rscript -e 'f <- list.files("utils/segments", full.names=TRUE); cat("files", length(f), "\n"); j <- lapply(f, jsonlite::fromJSON); cat("segments", sum(sapply(j, function(x) nrow(x$segments))), "\n")'
```

**Ground truth to assert.** 384 declared chapter files (48 stems x 8 languages). English carries
1,202 headings. The segmenter MUST produce a file for every one of the 384 and MUST NOT error on
any. Report the segment total; it is a new number, so measure it, do not predict it.

**Causally-red proof, required.** Two sections.
- `fence-aware`: a fixture chapter where a heading appears INSIDE a code chunk. RED: a naive
  splitter counts it as a section. GREEN: the segmenter does not.
- `attribute-strip`: a fixture with `## Title {#anchor .unnumbered}`. RED: unstripped heading text
  fails to match its translation. GREEN: stripped text matches.

**Pass/fail.** PASS when all 384 files segment without error, both proofs are red then green, and
the English heading count reconciles to 1,202. FAIL on any file erroring, or on a heading count
that disagrees with 1,202 without an explanation naming the base.

---

## Phase B — measure the saving on the same four pairs

**Invariant.** The four A/B pairs are re-swept using the pre-computed segment maps, and the
per-pair token cost is reported against the 54,820 baseline.

**Run by the orchestrator via the Workflow tool**, because it is agent fan-out, not an
implementation unit.

**Method.** Same finder prompt as the 98-pair run, with one change: the agent receives the
pre-computed segment pairs as text and is told NOT to segment anything itself. It does semantic
comparison only. Model Opus, default effort, output to `/tmp/gate/prose-seg/`.

**Pairs.** `basics.tr`, `basics.jp`, `collaboration.fr`, `data_table.ru` — the same four, so the
comparison is against a known baseline rather than a new one.

**What to report.** Tokens per pair against 54,820. Findings against the Opus baseline of 20, 14,
14, 0. Specifically whether the three severe `basics.tr` defects survive: the parentheses/apostrophe
instruction, the `brosur` package name, and `DOGRU`/`YANLIS`.

**Pass/fail.** This phase MEASURES; it does not gate. PASS when all four pairs return, the token
cost is reported, and the three named defects are checked by name. A cost increase is a valid
result and MUST be reported as one, not buried.

**STOP HERE.** The orchestrator reports the measurement and does not proceed to Phase C without
the owner's decision. Committing 238 pairs on an unmeasured assumption is what produced the quota
failure.

---

## Phase C — sweep the remaining 238 pairs. DEFERRED.

Not started, and MUST NOT start without a fresh quota window and an explicit decision.

**Two defects in the original run that the resumed run MUST fix**, both recorded in
`utils/PROSE-SWEEP-RESUME.md`:
1. **No budget guard.** 336 agents were launched at once and the session limit killed 253. The
   resumed run MUST drain a queue under `while (queue.length && budget.total && budget.remaining()
   > 200_000)`. Note that predicate never runs when `budget.total` is unset, and that failure looks
   identical in the log to a completed run, so the run MUST also log the queue length it stopped at.
2. **Return-based accounting.** The workflow reported 83 completed pairs when 94 files existed on
   disk; eleven agents wrote their JSON and died before returning. The resumed run MUST reconcile
   against files on disk, not against its own return values.

**Cost.** ~55k tokens per pair measured, so ~13M for 238, before any saving Phase B demonstrates.

---

## Phase D — verify the findings. NOT STARTED.

No verification has run on any of the 493 findings. Each is one agent's unverified claim, and 47
are self-rated `low` confidence with nothing checking the rating.

Per v2, every finding goes to **two blind verifiers** who see both source spans and classify
independently, without seeing the finder's verdict or each other's. Eligible for fixing only on
2-of-2 agreement with the finder. This covers `added` as well, because `added` now produces
deletions.

Batched per pair, not per finding: ~1000 findings at two verifiers each exceeds the 1000-agent
workflow cap.

---

## Phases E onward — unchanged from v2

E. Consolidated defect list, batched at most 20 edits per batch, one language and one kind each.
F. Fix, one `implementer-xhigh` dispatch per batch.
G. Local structural render gate, `quarto render --no-execute`, all 8 languages, excluding the 36
   inline-`r` files.
H. Verification by a fresh agent, then commit, push and CI. **A push to `main` deploys to staging
   automatically.**

---

## Forbidden list — unchanged from v2

No `git push`/`tag`, nothing under `.github/`. No `quarto render` without `--no-execute`. No
installs, formatters, `renv.lock`. Nothing under `_excluded/`, `data/`, `html_outputs/`, `renv/`,
`site_libs/`, no `*.de.qmd`, not `_quarto.yml:60`. No renaming translated identifiers. No reflowing
lines not otherwise changed. **Never bare `grep`** — it is a ugrep-backed shell function whose
output has no `./` prefix, so `^\./` filters are silently inert; use `command grep`. In every phase
before F: flag, do not fix; no agent may edit a `.qmd`.

## Execution

Phases A, E, F, G via `/implement-subagents-with-codex-review`.
Phases B, C, D via the Workflow tool, run by the orchestrator.
Phase B ends in a STOP for an owner decision.
