# Modernization work: index

This folder holds the durable record of the epiRhandbook cross-language modernization work.
The session that produced the work wrote its scratch files to `/tmp`, and `/tmp` is not preserved.

## State on 2026-08-19

| Phase | State |
|---|---|
| Phase 1a, the language checker | COMPLETE. Codex returned ALLOW at round 4. |
| Phase 1b, the prose sweep | PARTIAL. 154 of 336 chapter-language pairs read. |
| Phase A, the deterministic segmenter | NOT STARTED. |
| Phase B, the cost measurement | COMPLETE. A cost model replaced the flat per-pair rate. |
| Phase C, the remaining 182 pairs | NOT STARTED. |
| Phase D, verification of the findings | NOT STARTED. |

The corpus is 48 declared chapters in 7 languages, which is 336 chapter-language pairs.

The prose sweep read 154 of those 336 pairs. It produced these counts:

- 798 findings over the 154 pairs in 22 chapters.
- 8552 coverage rows over the same 154 pairs in the same 22 chapters.
- 22 of the 48 declared chapters complete, each in all 7 languages.
- 26 of the 48 declared chapters never started, in any language.
- 0 chapters half-read. The boundary is clean.

Two runs produced the 154 pairs. A session quota limit stopped the first run on 2026-08-09
at 98 pairs, and that run did not stop by design. The second run on 2026-08-19 added 56 pairs
in three planned batches. It used a hard slice, it reconciled against disk, and no batch was
killed. `RESUME.md` sections 4 to 6 hold the method.

**No verification ran on any of the 798 findings.**
Each of the 798 findings is one agent's unverified claim about one segment pair.
Do NOT edit a `.qmd` file on the strength of a finding.
Read `modernization/RESUME.md` section 8 before you use any finding.

## What to do first in the next session

1. Read `modernization/RESUME.md` sections 4 and 5. They give the batch method and the cost model.
2. Re-approve the plan with the owner.
3. Continue Phase C with a batch sized against the quota you hold.

Phase A creates `utils/segment-chapters.R` and changes nothing else in the repository.
Phase A exists because segmentation, not judgement, drove the model difference below.

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

The 2026-08-09 record put the remaining work at 55,000 tokens per pair. That rate was measured
on `directories` and `editorial_style`, the two smallest complete chapters at about 9.4 KB.
Applied to the whole corpus it is too low, because cost rises with chapter size.

The 2026-08-19 batches measured both ends. A 5.4 KB chapter cost 52,020 tokens per pair.
A 66.6 KB chapter cost 120,616. Fitting those two points gives this model:

```
tokens_per_pair  ~=  45,900  +  1,121 * (English chapter size in KB)
```

The model predicts the older 9.4 KB run within 3.4%, and it predicted a later 28-pair batch
within 2.7%. About 46,000 tokens is fixed overhead per agent, and the rest is the reading.

The 26 remaining chapters hold 675,256 bytes of English source, which the model puts at
**13.7M tokens** for 182 pairs. `RESUME.md` section 5 shows how to size one batch.

Findings per token favour the large chapters. Wave 2 returned 60 findings per million tokens
against wave 1's 45, even though wave 2 cost 2.3 times more per pair.

## The two defects the resumed run MUST avoid

**Defect 1: no budget guard.** The workflow dispatched all 336 pairs at once.
Nothing checked the remaining quota between dispatches.
The session limit then killed 253 of the 336 agents in flight.
The resumed run MUST drain a queue under a remaining-budget check.
The resumed run MUST also log the queue length it stopped at.
`modernization/RESUME.md` section 4 gives two guard shapes and names the safer one.

**Defect 2: return-based accounting.** The workflow counted agent return values.
It reported 83 completed pairs while 94 JSON files sat on disk.
Eleven agents wrote a JSON file, then died before they returned a value.
The resumed run MUST count the JSON files on disk, not the return values.

## Folder map

| Entry | What it holds |
|---|---|
| `README.md` | This index. |
| `SWEEP-PLAN.md` | The approved plan, version 3. A faithful copy, see "Provenance" below. |
| `RESUME.md` | How to resume the prose sweep, the cost model, and what the 798 findings do not tell you. |
| `STAKEHOLDERS.md` | Release notes for readers, authors, translators and contributors. |
| `TRANSLATION-BACKLOG.md` | Open translation work only, with a search token per item. |
| `archive/PLAN-translated-data-used.md` | The method record for the `data_used` page alignment. |
| `findings/language-prose-drift.tsv` | 798 rows. One row is one finding. |
| `findings/language-prose-coverage.tsv` | 8552 rows. One row is one segment pairing. |
| `findings/prose-sweep/` | 154 JSON files. One file is one completed chapter-language pair. |
| `findings/sonnet-ab/` | 4 JSON files from the Sonnet medium A/B run. |
| `workflows/` | 5 Claude Code workflow scripts. See the table below. |
| `reviews/` | 4 Codex verdicts on Phase 1a. See the table below. |
| `briefs/` | 6 subagent briefs and 3 implementer transcripts. |

### `workflows/`

| Script | What it does |
|---|---|
| `epirhandbook-prose-drift-batch.js` | **The current script.** One batch of whole chapters, hard-sliced. Set `STEMS` and run it. `RESUME.md` section 4 names this one. |
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
  `findings/prose-sweep/` holds a byte-identical durable copy of all 98 JSON files.
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
