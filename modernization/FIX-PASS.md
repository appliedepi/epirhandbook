# Fix pass: verify and fix the 1617 prose-sweep findings in one read

Run on 2026-09-01 and 2026-09-02 from commit `52442a79`. This replaces Phase D, E and F of
`SWEEP-PLAN.md` under the owner's amendment: verification and fixing are one pass, and each
agent reads only the extracted spans, never a whole chapter.

## Result

| Verdict | Findings | Meaning |
|---|---|---|
| fixed | 1488 | The finding was correct. The translated file is edited. |
| deferred | 73 | The finding was correct, but the fix is outside the pass's permissions. `findings/fix-pass/deferred.tsv`. |
| rejected | 30 | The finding was wrong or not a defect. Nothing edited. `findings/fix-pass/rejected.tsv`. |
| unextractable | 26 | The finding's spans do not parse or lie outside the file. Not attempted. `findings/fix-pass/unextractable-spans.tsv`. |

1488 + 73 + 30 + 26 = 1617. Every finding has exactly one of the four outcomes.

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
No English chapter, no `*.de.qmd`, no code chunk and no file outside `chapters/` changed.
Nothing is pushed.

## Three named sets that need the owner

**Unextractable, 26 findings.** 24 carry a single line number, `file:N`, instead of a range.
1 names `chapters/diagrams.vn.vn.qmd`, which does not exist. 1 lies past the end of both files.
Recommended decision: read `file:N` as `N-N` and run those 24 as one extra batch. The other 2
need the finder's evidence re-read by hand.

**Deferred, 73 findings.** 60 name a defect inside a code chunk, which this pass may not edit:
a wrong package name in `p_load()`, a misspelled argument, a French translation of an R keyword.
7 name a defect in the English source. 6 need a structural change. Each row carries the agent's
one-sentence reason. These are the highest-value residue: a code-chunk defect makes a reader
type code that cannot run.

**Rejected, 30 findings.** Read them before you trust the drift file's counts. Several are
places where the translation is right and the English is wrong, such as `%M` for minutes in
the Portuguese and Vietnamese date chapters.

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

Four defect classes came out of the Turkish review, and each was then swept mechanically across
all seven languages: an inserted link that points at the English chapter, a translated R literal,
a lost trailing hard break, and a literal folder name translated. The sweep found one more
Portuguese literal and 13 lost hard breaks in three languages. The wave brief gained one rule
per class before the last three waves ran.

Two codex runs died with "Selected model is at capacity" when four ran at once. Two at a time
was stable.

## What this pass did not do

- No `quarto render`. Phase G, the structural render gate, has not run.
- No push. A push to `main` deploys to staging.
- The English source defects that the agents and codex identified are recorded in
  `rejected.tsv` and `deferred.tsv` and are not fixed.
- The translated `DOĞRU`/`YANLIŞ` for `TRUE`/`FALSE` occurs on about 12 more Turkish lines that
  no finding named. They are untouched.
