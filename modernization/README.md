# Modernization work: index

This folder holds the durable record of the epiRhandbook cross-language modernization work.
The session that produced the work wrote its scratch files to `/tmp`, and `/tmp` is not preserved.

## State on 2026-09-02

| Phase | State |
|---|---|
| Phase 1a, the language checker | COMPLETE. Codex returned ALLOW at round 4. |
| Phase 1b / C, the prose sweep | **COMPLETE. All 336 chapter-language pairs read.** |
| Phase A, the deterministic segmenter | SKIPPED. See "Why Phase A is skipped" below. |
| Phase B, the segmenter saving | SKIPPED with Phase A. It exists only to measure Phase A. |
| Phases D, E, F, verify and fix | **COMPLETE on 2026-09-02, as one pass.** Of 1617 findings: 1511 fixed, 76 deferred then 67 of those fixed in the deferred pass, 30 rejected. See `FIX-PASS.md`. |
| Phase G, the render gate | COMPLETE on 2026-09-02. `render-gate.sh` and `chunk-parse-gate.py`, both green after every pass. |
| Chunk sync, deferred pass, inline pass | COMPLETE on 2026-09-02. Every translated chapter carries the English code chunks. See `FIX-PASS.md`. |
| English source fixes and mirror | COMPLETE on 2026-09-02. 17 English defects fixed, translations follow. |
| Phase H, verification, commit, push, CI | PUSH_STATE_LINE |

The corpus is 48 declared chapters in 7 languages, which is 336 chapter-language pairs.
The sweep read all 336. It produced these counts:

- 1617 findings over 336 pairs in 48 chapters, a mean of 4.81 per pair.
- 16288 coverage rows over the same 336 pairs.
- 48 of 48 declared chapters complete, each in all 7 languages. Nothing partial.
- 13 pairs read with zero findings. Absence from the drift file records that.

Three runs produced the 336 pairs. A session quota limit stopped the first on 2026-08-09 at 98
pairs, and it did not stop by design. The second added 133 pairs in five planned batches. The
third, on 2026-09-01, added the last 105 in four batches of 28, 35, 28 and 14. Every batch
after the first used a hard slice, reconciled against disk, and none was killed.
`RESUME.md` sections 4 to 6 hold the method.

**Every extractable finding was verified and acted on in the fix pass of 2026-09-02.**
`FIX-PASS.md` holds the result. A finding's verdict is in `findings/fix-pass/<batch>.json`.
`RESUME.md` section 8 describes the state before that pass and stays as the record of it.

## What to do next

**The push, which is the owner's.** After it, `gh run watch` for CI, and staging.

The 17 English source defects are fixed and mirrored, the inline deferrals closed. One item
stays open: `editorial_style.ru#1` in `findings/fix-pass/deferred.tsv`. And every few months, or after an English chapter changes,
`modernization/check-sync.sh`; see `SYNC-CHECKS.md`.

## Why Phase A is skipped

Phase A builds a deterministic segmenter, and Phase B measures what it saves. Wave 6 skipped
both, and this is the reason, so a later reader can overturn it on evidence rather than guess
at it.

The measured cost model is `45,900 + 1,121 * KB` per pair. The 45,900 is fixed per-agent
overhead. Across the 105 pairs read on 2026-09-01 the fixed floor was 57,767 tokens against a
mean per-pair cost of 95,834, so it was 60% of the bill. A segment map cannot touch the floor,
and the agent still has to read both chapters to compare them semantically, so the saving is a
fraction of the remaining 40%. Phase B exists to measure that fraction, so Phase A plus Phase B
is a spend to find out whether a spend is worth it.

The second reason was the stronger one. The 231 pairs read before wave 6 were hand-segmented.
Adopting segment maps mid-sweep would have read the last 105 pairs by a method the first 231
were not read by, and re-unifying the corpus would have meant re-reading 231 pairs.

**That objection has now expired.** It was a decision about Phase C, and Phase C is complete.
A deterministic segmenter is the right tool for Phase D verification and for any future sweep,
where no comparability to the 231 is at stake.

## The measured facts that drive the plan

A model A/B ran the same 4 chapter-language pairs on Opus and on Sonnet medium.
Both runs used an identical prompt. The 4 pairs were `basics.tr`, `basics.jp`,
`collaboration.fr` and `data_table.ru`.

| Measure | Opus | Sonnet medium |
|---|---|---|
| tokens per pair | 54,820 | 118,244, which is 2.2 times more |
| findings over the 4 A/B pairs | 48 | 21, which is 44% of the Opus total |
| findings on `basics.tr` | 20 | 3 |
| findings on the clean control `data_table.ru` | 0 | 1 |

**The decision is Opus.** Sonnet medium cost more per pair and reported fewer findings.
Sonnet medium also missed all three severe Turkish defects that Opus found in `basics.tr`.
`SWEEP-PLAN.md` names those three defects, under "The sweep is finding severe defects".

Sonnet medium wrote `data_table.json` instead of `data_table.ru.json`.
Across 7 languages that filename overwrites 6 of the 7 output files.
`modernization/findings/sonnet-ab/data_table.json` keeps that defect as evidence.

## Cost is not flat per pair

`RESUME.md` section 5 holds the full measurement. Two rules matter, and both were learned by
getting them wrong on 2026-09-01.

**Fit the cost line per session. Never carry one across sessions.**

| Session | Model | Points | R2 |
|---|---|---|---|
| 2026-08 | `tokens_per_pair ~= 45,801 + 1,197 * KB` | 6 | 0.994 |
| 2026-09-01 | `tokens_per_pair ~= 57,767 + 1,159 * KB` | 4 | 0.979 |

**A session line is valid only across the sizes it was fitted on.** Fitted on waves 6 to 8,
spanning 24.4 to 40.6 KB, the 2026-09-01 line predicted those three to within 0.04%.
Extrapolated 5 KB past its range to wave 9 it came in 4.7% low.

The failed intermediate step is worth keeping, because it looked convincing. Waves 6 and 7 came
in 18.3% and 16.5% above the 2026-08 model, so this record briefly carried a flat 1.173
multiplier. Wave 8 came in at 1.121 and broke it. The multiplier was the wrong SHAPE: one factor
scales intercept and slope together, but the intercept had risen while the slope fell, and the
two waves that set it both sat at 25 to 29 KB where those errors cancelled. **A correction that
fits at one size is not a model. Test it well outside the points that produced it.**

The 2026-09-01 session spent 10,062,583 subagent tokens on 105 pairs, a mean of 95,834 per pair.

Findings per token favours neither end. The nine waves returned 45, 60, 53, 48, 53, 58, 53, 56
and 57 findings per million tokens, which is noise rather than a trend.

## The two defects the resumed run MUST avoid

**Defect 1: no budget guard.** The workflow dispatched all 336 pairs at once.
Nothing checked the remaining quota between dispatches.
The session limit then killed 253 of the 336 agents in flight.
A batch MUST fix its pair count before it dispatches, by setting `STEMS` to that batch alone.
`modernization/RESUME.md` section 4 gives the rule. Five batches used it and none was killed.

**Defect 2: return-based accounting.** The workflow counted agent return values.
It reported 83 completed pairs while 94 JSON files sat on disk.
Eleven agents wrote a JSON file, then died before they returned a value.
The resumed run MUST count the JSON files on disk, not the return values.

## Folder map

| Entry | What it holds |
|---|---|
| `README.md` | This index. |
| `SWEEP-PLAN.md` | The approved plan, version 3. A faithful copy, see "Provenance" below. |
| `RESUME.md` | How to resume the prose sweep, the cost model, and what the 1617 findings do not tell you. |
| `STAKEHOLDERS.md` | Release notes for readers, authors, translators and contributors. |
| `TRANSLATION-BACKLOG.md` | Open translation work only, with a search token per item. |
| `archive/PLAN-translated-data-used.md` | The method record for the `data_used` page alignment. |
| `rebuild-tsv.py` | Rebuilds both TSVs from the JSON files. Run it after every batch. |
| `SYNC-CHECKS.md` | **How to check the translations are still in sync, and repair drift.** Run `check-sync.sh`. |
| `FIX-PASS.md` | The fix pass: method, result, cost, the codex verdicts, and the three named sets that need the owner. |
| `findings/fix-pass/` | One JSON per batch with a verdict and exact old/new text per finding, plus `deferred.tsv`, `rejected.tsv`, `unextractable-spans.tsv`, `batch-index.tsv`. |
| `extract-spans.py`, `make-batches.py`, `reconcile-fix-pass.py`, `commit-batch.sh`, `wave-args.py`, `codex-bundle.sh`, `codex-prompt.txt` | The fix-pass tooling. `FIX-PASS.md` names the order. |
| `findings/language-prose-drift.tsv` | 1617 rows. One row is one finding. |
| `findings/language-prose-coverage.tsv` | 16288 rows. One row is one segment pairing. |
| `findings/prose-sweep/` | 336 JSON files. One file is one completed chapter-language pair. |
| `findings/sonnet-ab/` | 4 JSON files from the Sonnet medium A/B run. |
| `workflows/` | 5 Claude Code workflow scripts. See the table below. |
| `reviews/` | 4 Codex verdicts on Phase 1a. See the table below. |
| `briefs/` | 6 subagent briefs and 3 implementer transcripts. |

### `workflows/`

| Script | What it does |
|---|---|
| `epirhandbook-prose-drift-batch.js` | **The current script.** One batch of whole chapters, hard-sliced. Set `STEMS` and run it. `RESUME.md` section 4 names this one. `STEMS` currently holds the wave 9 batch, the last of Phase C. |
| `epirhandbook-prose-drift-find-wf_549a2da0-bec.js` | The 336-pair finder. Holds the 48 stems inline. Superseded: it has no slice and no disk reconciliation. |
| `epirhandbook-prose-drift-find-wf_23d079e4-151.js` | An earlier revision of the same finder. Takes the stems from `args.stems`. |
| `epirhandbook-prose-drift-finish-started-wf_87695bbb-ca4.js` | The 5-pair finish run for `directories.tr` and 4 `editorial_style` pairs. |
| `epirhandbook-prose-ab-sonnet-wf_bfc014a5-a37.js` | The Sonnet medium A/B over the 4 pairs. |

### `reviews/`

| File | Verdict |
|---|---|
| `codex-round1.md` | BLOCK. Fence and call-site extraction can misclassify non-R text. |
| `codex-round2.md` | BLOCK. The checker does not extract dataset names from comment-stripped R chunks. |
| `codex-round3.md` | BLOCK. The proof transcript holds duplicated sections and impossible raw results. |
| `codex-round4.md` | ALLOW. The transcript repair satisfies the brief and changes no checker code. |

## What is NOT here

- **The gate state and the phase ledger.** Both were session-scoped under `/tmp/gate/`.
  They record one session's dispatch bookkeeping. They are deliberately not preserved.
- **The four Codex review logs.** Each of the 4 logs is between 206 KB and 263 KB.
  Each log is mostly prompt text and tool calls.
  `reviews/codex-round<N>.md` keeps only the final Codex answer, and names its source log.
- **The volatile prose-sweep originals under `/tmp/gate/prose/`.**
  `findings/prose-sweep/` holds a byte-identical durable copy of all 336 JSON files.
- **`utils/check-language-consistency.R`.** That file stays in `utils/`.
  It is a working tool beside `utils/check-data-equivalence.R`, and it is not bookkeeping.

## Provenance

`SWEEP-PLAN.md` is a byte-faithful copy of `/home/raw996/.claude/plans/noble-mixing-matsumoto.md`.
It was copied without edits, so a reader can diff it against that source.
Four distinct paths in `SWEEP-PLAN.md` still name the locations the artifacts held before this move.
This table maps each one:

| Path named in `SWEEP-PLAN.md` | Current path |
|---|---|
| `utils/language-prose-drift.tsv` | `modernization/findings/language-prose-drift.tsv` |
| `utils/language-prose-coverage.tsv` | `modernization/findings/language-prose-coverage.tsv` |
| `utils/prose-sweep/` | `modernization/findings/prose-sweep/` |
| `utils/PROSE-SWEEP-RESUME.md` | `modernization/RESUME.md` |

`SWEEP-PLAN.md` also names `utils/check-language-consistency.R`. That path is still correct.

Every file under `briefs/` and every file under `reviews/` is a byte-faithful copy.
Each one records a past dispatch, so none of them was edited for this move.
Three of them name pre-move paths: `briefs/phase1b-record-brief.md`,
`briefs/phase1b-record-transcript.md` and `briefs/modernization-brief.md`.
No file under `reviews/` names a pre-move path.
Read the table above when a brief names a path under `utils/`.

`RESUME.md` moved from `utils/PROSE-SWEEP-RESUME.md`. Its artifact paths were updated in place,
because `RESUME.md` section 4 is a set of instructions that a reader runs.

## Known broken links inside the moved documents

`TRANSLATION-BACKLOG.md` lines 185 to 191 link to 7 `data_used.<lang>.qmd` files.
`archive/PLAN-translated-data-used.md` line 160 links to `importing.qmd`.
All 8 links were broken before this move, because those 8 chapters live under `chapters/`.
The move did not create them, and this unit did not fix them.
Fix them with the other prose defects, in a phase that is allowed to edit content.
