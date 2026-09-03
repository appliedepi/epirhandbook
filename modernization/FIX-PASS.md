# Fix pass: verify and fix the 1617 prose-sweep findings in one read

Run on 2026-09-01 and 2026-09-02 from commit `52442a79`. This replaces Phase D, E and F of
`SWEEP-PLAN.md` under the owner's amendment: verification and fixing are one pass, and each
agent reads only the extracted spans, never a whole chapter.

## Result

| Verdict | Findings | Meaning |
|---|---|---|
| fixed | 1511 | The finding was correct. The translated file is edited. |
| deferred | 76 | The finding was correct, but the fix is outside the pass's permissions. `findings/fix-pass/deferred.tsv`. |
| rejected | 30 | The finding was wrong or not a defect. Nothing edited. `findings/fix-pass/rejected.tsv`. |

1511 + 76 + 30 = 1617. Every finding has exactly one of the three outcomes. The 26 findings whose
spans did not parse ran last, as nine `odd-*` batches, after the owner said to do the whole set:
23 fixed, 3 deferred. `findings/fix-pass/unextractable-spans.tsv` records how each span was read.

By language, over the 1591 extractable findings:

| Language | fixed | deferred | rejected |
|---|---|---|---|
| tr | 323 | 5 | 6 |
| jp | 253 | 11 | 6 |
| pt | 208 | 22 | 7 |
| fr | 204 | 19 | 3 |
| ru | 171 | 2 | 3 |
| es | 166 | 10 | 1 |
| vn | 163 | 4 | 4 |

The diff from `52442a79` touches 317 translated chapter files: 1637 insertions, 1519 deletions.
No English chapter, no `*.de.qmd` and no file outside `chapters/` changed. No existing `{r` chunk was edited; `basics.fr.qmd` gained two chunks copied verbatim from the English, and `errors.tr.qmd` had two error-output fences corrected to R's literal English error text.
Nothing is pushed.

## Two named sets that need the owner, and a third for the English

**Deferred, 76 findings plus 5 review rows.** 65 name a defect inside a code chunk, which this pass may not edit:
a wrong package name in `p_load()`, a misspelled argument, a French translation of an R keyword.
7 name a defect in the English source. 6 need a structural change. Each row carries the agent's
one-sentence reason. These are the highest-value residue: a code-chunk defect makes a reader
type code that cannot run.

**Rejected, 30 findings.** Read them before you trust the drift file's counts. Several are
places where the translation is right and the English is wrong, such as `%M` for minutes in
the Portuguese and Vietnamese date chapters.

**Source defects, 11 English places.** `findings/fix-pass/source-defects.tsv`. Every one was
found because a translation was made to match the English and a reviewer then showed the
English contradicts its own code chunk, its own figure, or has a dead link. Nothing in this pass
edits an English file.

## Method

1. `extract-spans.py` reads every finding's spans from the files at `52442a79` with `git show`,
   never from the working tree, with 8 lines of context each side. Deterministic. Proved red:
   a span corrupted to line 9999 lands in `unextractable.tsv` and drops out of the evidence.
2. `make-batches.py` groups by language and kind, at most 20 findings per batch, and schedules
   waves in which no two batches share a file. 97 batches.
3. `workflows/epirhandbook-fix-pass-wave.js` runs one wave. One opus agent at xhigh per batch.
   The agent reads only its evidence file, edits with exact string replacement, and writes
   `findings/fix-pass/<batch>.json` with a verdict and the exact old and new text per finding.
4. `reconcile-fix-pass.py` checks every result file against the working tree: ids by name,
   new text present, old text absent, no change outside the batch's files. Proved red three ways.
5. `commit-batch.sh` commits one batch, signed, after the checker passes. 97 batches, 97 commits.

**Count artifacts, not returns.** Every wave was reconciled from the result files on disk.
No agent died after writing in this run, but the wave-2 quota kill left two partial edits with
no result file; they were stashed and the wave re-run from a clean tree.

## Cost

| Item | Value |
|---|---|
| Subagent tokens, 97 completed agents | 9,617,128 |
| Subagent tokens lost to the quota kill on wave 2 | 976,612 |
| Per completed agent, mean | 99,145 |
| Wall clock per wave of 14 | 8 to 11 minutes |
| Subagent tokens, 9 odd-span batches | 506,954 |
| Subagent tokens, 18 review agents | 2,913,765 |
| Codex, Turkish, two calls | 375,699 and 199,301 tokens |

The owner's estimate of 2.5M tokens assumed about 30,000 per agent. The fixed overhead of an
agent that reads a 40 to 60 KB evidence file and makes 15 to 20 edits is about three times that.
On this session's first two batches, in the harness's token unit,
`tokens ~= 64,000 + 600 * evidence_KB`, fitted on 39 and 63 KB. It predicted wave 1 8% low.

## Independent check: codex, one language per call

The diff is where a wrong edit is visible. Codex read each language's diff with the verdicts
and the current chapter files, read-only, at reasoning effort high. Verdicts are in `reviews/`.

| Call | Hunks | Verdict | Verified repairs | Rejected claims |
|---|---|---|---|---|
| tr part 1 | 165 | BLOCK, 22 | 24, see commit `4a05d937` | 2 |
| tr part 2 | 131 | BLOCK, 26 | 1, see commit `ada77630` | 5, and 20 were the part-1 repairs |
| jp | 228 | none: cut off by the codex usage limit after 320,388 tokens | n/a | n/a |
| pt | 179 | none: cut off by the codex usage limit | n/a | n/a |
| es, fr, ru, vn | 150, 174, 154, 147 | not started: the owner chose not to wait for codex | n/a | n/a |

Four defect classes came out of the Turkish review, and each was then swept mechanically across
all seven languages: an inserted link that points at the English chapter, a translated R literal,
a lost trailing hard break, and a literal folder name translated. The sweep found one more
Portuguese literal and 13 lost hard breaks in three languages. The wave brief gained one rule
per class before the last three waves ran.

Two codex runs died with "Selected model is at capacity" when four ran at once. Two at a time
was stable until the owner's codex usage limit tripped at about 02:15 on 2026-09-02; it resets
at 06:14. `codex-bundle.sh <lang> 52442a79 HEAD <lang>` rebuilds any language's workspace, and
`codex-prompt.txt` is the prompt. The owner decides whether to fund the six remaining calls.

**Claude review of the six other languages.** With codex blocked, the owner said to do it
without codex. Eighteen opus agents at xhigh, one per diff part of about 90 KB, read all 1032
hunks of es, fr, jp, pt, ru and vn with the codex brief, flag-only. `reviews/claude-fixpass/`
holds the 18 result files. They flagged 62 hunks: 21 broken markup, 20 not fluent, 16 wrong
meaning, 3 wrong insertions, 2 wrong removals. Every flag was verified against the current file
and the English. 52 were applied in commits `b01db9d6` and `f6e8ced4`. 10 were rejected: 6
match the English source word for word and are in `source-defects.tsv`; 4 name a defect
inside a code chunk and are appended to `deferred.tsv`. This is one model family reviewing its
own family's work, which the owner's standing rule says not to trust alone; it stands in for
the codex calls the usage limit blocked, and the owner chose it.

**Structural sweep, all languages, no codex.** For every one of the 317 changed files, the
counts of fence lines, `{r` chunk openers, headings and `{#anchor}` attributes before and after.
Fifteen files changed a count. Fourteen are alignment fixes that add or remove a section the
English has or lacks, one anchor restored from the English, and two English code chunks the
French `basics` chapter had dropped. One was a defect: a repaired link in `help.es.qmd`
targeted an in-page anchor where the English targets `collaboration.qmd`. Fixed in commit
`afc3b69e`. Fence counts stay even in every file.

## What this pass did not do

- Phase G ran as `render-gate.sh`: `quarto render --no-execute` per changed translated file,
  plus a fence-parity check, because pandoc renders an unclosed fence with exit 0. First run,
  before the review repairs: 287 pass, 0 fail, 32 skipped for inline R, of 319 files.
  Second run, on the 45 files the review repairs touched: 40 pass, 0 fail, 5 skipped. Verified by `modernization/render-gate.sh`.
- No push. A push to `main` deploys to staging.
- The English source defects that the agents and codex identified are recorded in
  `rejected.tsv` and `deferred.tsv` and are not fixed.
- The translated `DOĞRU`/`YANLIŞ` for `TRUE`/`FALSE` occurs on about 12 more Turkish lines that
  no finding named. They are untouched.
