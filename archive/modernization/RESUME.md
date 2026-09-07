# Prose sweep: resume record

## 1. What this is, and what state it is in

The prose sweep reads every translated chapter of the handbook against its English source.
It records each place where the translation says something the English does not say.

**The sweep is COMPLETE. All 336 chapter-language pairs are read.**
Phase C closed on 2026-09-01.

The corpus is 48 declared chapters in 7 languages: `es`, `fr`, `jp`, `pt`, `ru`, `tr`, `vn`.
48 chapters times 7 languages is 336 pairs. Every one has a JSON file in
`modernization/findings/prose-sweep/`, and no file there is outside that set.

The chapter list comes from `_quarto.yml` `book.chapters`, where the entries sit nested under
`part:` blocks. Match `^\s*-\s*chapters/([A-Za-z0-9_]+)\.qmd` over the whole file. A parser
that stops at the first unindented line finds 20 of the 48 and then reports no missing pairs,
because it also shrinks what it expects. `index.qmd` is a top-level entry rather than a
`chapters/` one, and it carries no sweep pair.

Three runs produced the 336 pairs. A session quota limit stopped the first run on 2026-08-09
at 98 pairs. That run did not stop by design. The second run added 133 pairs in five planned
batches, and each batch stopped at a size the owner set in advance. The third run, on
2026-09-01, added the last 105 pairs in four batches: waves 6, 7, 8 and 9 read 28, 35, 28 and
14. All four returned every pair, and no batch was killed.

Phase A, the deterministic segmenter, is SKIPPED rather than deferred. Section 5 gives the
reason: it cannot touch the fixed per-agent overhead, which is about half the per-pair cost,
and adopting it mid-sweep would have read the last pairs by a method the first 231 were not
read by. That objection expires now that the sweep is complete, so a future sweep or the
Phase D verification may use one freely.

## 2. Chapters

All 48 declared chapters are complete in all 7 languages. Nothing is partial.

| State | Chapters | Pairs |
|---|---|---|
| Complete, all 7 languages read | 48 | 336 |
| Remaining | 0 | 0 |
| Partial | 0 | 0 |

## 3. What the findings say so far

**Read the base before you read any number in this section.**
Every count below is over all 336 pairs in all 48 chapters. The base is now the whole corpus,
which it was not in any earlier revision of this record.

Total: **1617 findings over 336 pairs in 48 chapters**. Mean 4.81 findings per pair.

| Kind | Findings | Meaning |
|---|---|---|
| untrue | 702 | The translation asserts something the English does not assert. |
| missing | 463 | The English asserts something the translation drops. |
| code_mismatch | 260 | The prose describes an output that the chunk beside it does not produce. |
| added | 168 | The translation adds a claim with no English source. |
| alignment_mismatch | 24 | The segments pair up, but the pairing is wrong. |

By language. Each language contributed 48 pairs, one per chapter, so these 7 counts are
directly comparable:

| Language | Findings |
|---|---|
| tr | 335 |
| jp | 270 |
| pt | 241 |
| fr | 237 |
| vn | 180 |
| es | 177 |
| ru | 177 |

Turkish leads by 24% over Japanese and carries 89% more than the three-way floor. It led at
98 pairs, at 231, and it leads at 336. **That is the one per-language conclusion the sweep
supports.** The middle of the table moved at nearly every wave, and Portuguese crossed French
twice, so do not read a one-place gap as real.

323 of the 336 pairs carry at least one finding. Thirteen pairs carry none:
`combination_analysis.es`, `data_table.ru`, `directories.ru`, `errors.ru`,
`moving_average.pt`, `network_drives.ru`, `packages_suggested.es`, `packages_suggested.tr`,
`r_projects.fr`, `r_projects.ru`, `reportfactory.tr`, `stat_tests.ru` and `survey_analysis.ru`.
Those thirteen pairs are read, and they are covered in
`modernization/findings/language-prose-coverage.tsv`.
A pair absent from `modernization/findings/language-prose-drift.tsv` is therefore not proof of
a pair that nobody read. Use the coverage file to decide what was read.

Seven of the thirteen are Russian, against a Russian share of one seventh. Russian also sits at
the floor of the per-language table. Both facts are consistent with the Russian translation
being the closest to its source, and neither establishes it: nothing has verified a single
finding, so a lower count may equally mean a less thorough read.

## 4. How the sweep was run

Phase C is complete, so nothing here is a pending instruction. Keep it as the method, because
Phase D fans out the same way and a future sweep will reuse it.

The batch script is at `modernization/workflows/epirhandbook-prose-drift-batch.js`.
The Workflow tool runs the file directly. Pass it as `scriptPath`.

Each batch set `STEMS` to that batch's chapters alone, never the 48-stem corpus. That is the
hard slice. It cannot overshoot, because the pair count is fixed before dispatch. Nine batches
used it across two sessions, all nine returned every pair, and none was killed.

The agents write to `/tmp/gate/prose/`, which does not survive a reboot.

**Every batch ended with a disk reconciliation, and so must every future one:**

```bash
ls /tmp/gate/prose/*.json | wc -l
```

Do not report a completion count taken from the agent return values. Section 6 explains why.

**Reconcile by NAME, not by count.** Wave 9 put 106 files in that directory where 105 pairs had
run. The extra was `_segs.json`, an agent's own scratch segment map. A count alone reads that as
a surplus and a `cp *.json` copies it into the record, where it has no `chapter` key and breaks
the rebuild. Check that every filename matches `<chapter>.<lang>.json` and that each chapter has
exactly 7, then copy by explicit name.

Then copy the JSON files into `modernization/findings/prose-sweep/` and rebuild the two TSVs:

```bash
python3 modernization/rebuild-tsv.py
```

## 5. Cost, and how to predict it

**The 2026-09-01 session spent 10,062,583 subagent tokens on its 105 pairs**, across four
waves. That figure is exact, and it is the only session total this record can state.

The 2026-08-19 session's five waves sum to 10,644,259 for 133 pairs, but wave 5 contributes a
derived figure rather than a logged one. The 2026-08-09 run of 98 pairs never logged a total at
all: only a per-pair figure of 54,820, measured on 2 of its 14 chapters. **There is therefore no
trustworthy whole-sweep cost, and this record does not give one.**

Cost per pair rises with the size of the English chapter, on a large fixed overhead per agent.
Two rules govern any prediction, and both were learned by getting it wrong.

**Rule 1: fit the line per session. Never carry one across sessions.**

| Session | Model | Points | R2 |
|---|---|---|---|
| 2026-08 | `tokens_per_pair ~= 45,801 + 1,197 * KB` | 6 | 0.994 |
| 2026-09-01 | `tokens_per_pair ~= 57,767 + 1,159 * KB` | 4 | 0.979 |

Between the two sessions the fixed overhead rose about 26%. Each session's own line fits its
own points closely; neither predicts the other's.

**Rule 2: a session line is valid only across the sizes it was fitted on.**

Fitted on waves 6, 7 and 8, which span 24.4 to 40.6 KB, the 2026-09-01 line was
`62,936 + 975 * KB` and it predicted those three waves to within 0.04%. Extrapolated to wave 9
at 46.1 KB, 5 KB past its range, it came in 4.7% low. The 4-point line above includes wave 9
and is the one to reuse.

The measured points, with the session that produced each:

| Session | Mean English chapter | Tokens per pair | Batch |
|---|---|---|---|
| 2026-08 | 5,418 bytes | 52,020 | wave 1, 2 chapters |
| 2026-08 | 8,644 bytes | 55,885 | wave 4, 4 chapters |
| 2026-08 | 9,599 bytes | 54,820 | 2026-08-09, 2 chapters |
| 2026-08 | 18,976 bytes | 70,117 | wave 5, 7 chapters |
| 2026-08 | 56,607 bytes | 115,244 | wave 3, 4 chapters |
| 2026-08 | 66,580 bytes | 120,616 | wave 2, 2 chapters |
| 2026-09-01 | 25,022 bytes | 86,729 | wave 6, 4 chapters |
| 2026-09-01 | 29,368 bytes | 90,928 | wave 7, 5 chapters |
| 2026-09-01 | 41,606 bytes | 102,527 | wave 8, 4 chapters |
| 2026-09-01 | 47,199 bytes | 112,923 | wave 9, 2 chapters |

**How a scale correction went wrong, and why it could not have worked.**

Wave 6 came in 18.3% above the 2026-08 model and wave 7 came in 16.5% above it. Two waves
agreeing that closely looked like a measurement, so this record carried a flat multiplier of
1.173 for one commit. Wave 8 came in at 1.121 and broke it.

The multiplier was the wrong SHAPE, not the wrong number. A single factor scales the intercept
and the slope together. What actually happened is that the intercept went up while the slope
went down, so the two waves that set the multiplier both sat at 25 to 29 KB, where the two
errors cancelled. Wave 8 sat at 41.6 KB, far enough out for them to stop cancelling.

**A correction that fits at one size is not a model.** Before you trust one, test it well
outside the points that produced it. Waves 6 and 7 were 4 KB apart and agreed to 1.8 points,
which felt conclusive and was not.

**To size a batch:** fit this session's line on its first two batches, choosing one small and
one large chapter set so the two points are far apart, then sum `intercept + slope * KB` over
the batch chapters and multiply by 7.

**Findings per token does not favour either end.** The nine waves returned 45, 60, 53, 48, 53,
58, 53, 56 and 57 findings per million tokens. Cheap chapters complete more chapters per token.
Large chapters cover more of the corpus per token.

## 6. Two defects in the original run

The 2026-08-09 run carried both. The later batches avoided both. Keep avoiding them.

**Defect 1: no budget guard.** The workflow called `parallel()` on all 336 pairs at once.
Nothing checked the remaining quota between dispatches. The session limit then killed 253
agents mid-flight. The run stopped at an arbitrary point instead of at a clean boundary.
A hard slice turns a kill into a planned stop. Section 4 gives the rule.

**Defect 2: the run counted agent returns, not artifacts on disk.** The workflow built its
totals from the array that `parallel()` returned. It reported 83 completed pairs while 94
JSON files sat in `/tmp/gate/prose/`. Eleven agents wrote their JSON file and then died
before they returned a value. That work was nearly discarded as failed.
A resumed run MUST reconcile against the files on disk. The file is the artifact. The
return value is only a report about the artifact.

A workflow script cannot read the filesystem, so the reconciliation cannot live inside the
script. The orchestrator runs it. The script logs a reminder and labels its own count
`RETURN-BASED`.

## 7. Where the data is

`modernization/findings/prose-sweep/` holds the durable copy: 336 JSON files, one per chapter-language pair,
named `<chapter>.<lang>.json`. Each file holds `chapter`, `lang`, `coverage` and `findings`.
These files are byte-identical to the originals.

`/tmp/gate/prose/` holds the volatile originals. `/tmp` does not survive a reboot.
Treat `/tmp/gate/prose/` as scratch space, and `modernization/findings/prose-sweep/` as the record.

Two derived tables sit beside the JSON copies. Both are tab-separated with a header row.
Both were built from the 336 JSON files and from nothing else, by
`modernization/rebuild-tsv.py`.

| File | Rows | One row is |
|---|---|---|
| `modernization/findings/language-prose-drift.tsv` | 1617 | one finding |
| `modernization/findings/language-prose-coverage.tsv` | 16288 | one segment pairing |

`modernization/findings/language-prose-drift.tsv` columns:
`chapter`, `lang`, `heading`, `segment_index`, `kind`, `en_span`, `tr_span`, `proposition`,
`reader_consequence`, `confidence`.

`modernization/findings/language-prose-coverage.tsv` columns:
`chapter`, `lang`, `en_segment_id`, `tr_segment_id`, `relation`, `confidence`, `reviewed`.

Read them with `quote=""`, because the text fields contain quotation marks:

```r
d  <- read.delim("modernization/findings/language-prose-drift.tsv", sep = "\t", quote = "")
cv <- read.delim("modernization/findings/language-prose-coverage.tsv", sep = "\t", quote = "")
```

Three notes on the TSV encoding:

1. A JSON `null` is written as the literal `NA`, which R reads as a missing value.
   `en_segment_id` is `NA` on 32 rows. `tr_segment_id` is `NA` on 11 rows.
2. `reviewed` is written as `TRUE` or `FALSE`, which R reads as a logical column.
   It is `TRUE` on all 16288 coverage rows.
3. No field needed whitespace cleaning. No value in the 336 source files contained a tab,
   a newline or a carriage return. The rebuild checks this and exits non-zero if any did.

**Rebuild both TSVs from the JSON files after every batch.** Do not append to them.
Run `python3 modernization/rebuild-tsv.py`, which reads the JSON and nothing else.

**The rebuild is verified against the record, and the check was proved red.**
Restricted to the 231 pairs read before wave 6, via `--only-pairs`, it reproduces the
1054 drift rows and 10474 coverage rows **byte-identically**, not merely as sets.
The check was then proved red by dropping one pair from that list, which lost 5 drift
rows and which `cmp` detected. Re-run both before you trust a future rebuild.

**There are no unread pairs left, so this rule now protects a different thing.**
Thirteen pairs are read and carry zero findings. They appear in the coverage file and not in
the drift file. Do not add a placeholder drift row for any of them: absence from the drift file
is how the record says "read, nothing found", and a placeholder would destroy that.

## 8. What this record does NOT tell you

**No verification pass ran. Not one of the 1617 findings is verified.**

Each finding is one agent's unverified claim about one segment pair. The agent read the
English chapter and the translated chapter, and it wrote what it believed it saw.
Nothing checked that belief.

The agents self-rated 784 findings `high`, 672 `medium` and 161 `low`. Nothing checked
any of those three ratings either.

The plan requires two blind verifiers per finding before a finding is eligible for a fix.
That step ran for 0 of the 1617 findings.

Three consequences follow.

1. Do NOT edit a `.qmd` file on the strength of a row in `modernization/findings/language-prose-drift.tsv`.
2. Do NOT report a count from this record as a defect count. It is a claim count.
3. Do NOT read `confidence` as a measured quantity. It is the finding agent's own rating.

The coverage file records what an agent claims it read. It is not independent evidence of
reading either.
