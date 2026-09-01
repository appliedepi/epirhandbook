# Prose sweep: resume record

## 1. What this is, and what state it is in

The prose sweep reads every translated chapter of the handbook against its English source.
It records each place where the translation says something the English does not say.
The sweep is **322 of 336 chapter-language pairs complete**.
The other **14 pairs were never read**.
Nothing is half-read. Every one of the 46 complete chapters has all 7 languages.
Both remaining chapters have none.

The corpus is 48 declared chapters in 7 languages: `es`, `fr`, `jp`, `pt`, `ru`, `tr`, `vn`.
48 chapters times 7 languages is 336 pairs.

Three runs produced the 322 pairs. A session quota limit stopped the first run on 2026-08-09
at 98 pairs. That run did not stop by design. The second run added 133 pairs in five planned
batches, and each batch stopped at a size the owner set in advance. The third run, on
2026-09-01, added 91 pairs in three batches: wave 6 read 28, wave 7 read 35 and wave 8 read
28. All three returned every pair.

Phase A, the deterministic segmenter, is SKIPPED rather than deferred. Section 5 gives the
reason: it cannot touch the fixed per-agent overhead, which is most of the per-pair cost, and
adopting it now would read the last pairs by a method the first 231 were not read by.

## 2. Chapters

| State | Chapters | Pairs |
|---|---|---|
| Complete, all 7 languages read | 46 | 322 |
| Remaining, 0 languages read | 2 | 14 |
| Partial | 0 | 0 |

**Complete (46).** Every one has 7 of 7 languages on disk.

```
age_pyramid  basics  characters_strings  cleaning  collaboration
combination_analysis  contact_tracing  data_table  data_used  dates
deduplication  diagrams  directories  editorial_style  epicurves
errors  factors  flexdashboard  ggplot_basics  ggplot_tips
grouping  heatmaps  help  interactive_plots  joining_matching
missing_data  moving_average  network_drives  packages_suggested  phylogenetic_trees
pivoting  r_projects  regression  reportfactory  rmarkdown
shiny_basics  standardization  stat_tests  survey_analysis  survival_analysis
tables_descriptive  tables_presentation  time_series  transition_to_r
transmission_chains  writing_functions
```

**Remaining (2).** Neither language of these was read. They are the two largest chapters
in the corpus.

```
importing  iteration
```

## 3. What the findings say so far

**Read the base before you read any number in this section.**
Every count below is over the 322 pairs in the 46 complete chapters.
No count below is over the 336-pair corpus, and none is over the 48 declared chapters.

Total: **1527 findings over 322 pairs in 46 chapters**. Mean 4.74 findings per pair.

By kind, over those same 322 pairs:

| Kind | Findings | Meaning |
|---|---|---|
| untrue | 668 | The translation asserts something the English does not assert. |
| missing | 438 | The English asserts something the translation drops. |
| code_mismatch | 232 | The prose describes an output that the chunk beside it does not produce. |
| added | 166 | The translation adds a claim with no English source. |
| alignment_mismatch | 23 | The segments pair up, but the pairing is wrong. |

By language, over those same 322 pairs. Each language contributed 46 pairs, one per complete
chapter, so these 7 counts are comparable to each other:

| Language | Findings |
|---|---|
| tr | 323 |
| jp | 254 |
| pt | 228 |
| fr | 220 |
| vn | 172 |
| ru | 170 |
| es | 160 |

Turkish led the count at 98 pairs and it still leads at 322 pairs. Spanish has been lowest
throughout. The middle of the table is not stable: Portuguese has crossed French twice, and
wave 8 moved Russian below Vietnamese. **Read only the Turkish lead and the Spanish floor as
settled.**

309 of the 322 pairs carry at least one finding. Thirteen pairs carry none. Wave 8 added
`survey_analysis.ru`, which is the first zero-finding pair since 2026-08-19:
`combination_analysis.es`, `data_table.ru`, `directories.ru`, `errors.ru`,
`moving_average.pt`, `network_drives.ru`, `packages_suggested.es`, `packages_suggested.tr`,
`r_projects.fr`, `r_projects.ru`, `reportfactory.tr`, `stat_tests.ru` and
`survey_analysis.ru`.
Those thirteen pairs are read, and they are covered in `modernization/findings/language-prose-coverage.tsv`.
A pair absent from `modernization/findings/language-prose-drift.tsv` is therefore not proof of a pair that
nobody read. Use the coverage file to decide what was read.

## 4. How to resume

The repository holds the batch script at this path:

```
modernization/workflows/epirhandbook-prose-drift-batch.js
```

The Workflow tool runs this file directly. Pass it as `scriptPath`. Do not copy it elsewhere.

Do these three things before you start a batch.

1. Set `STEMS` to the chapters this batch reads. Take them from the remaining list in section 2.
   `STEMS` MUST NOT hold the 48-stem corpus. A whole-corpus run is what defect 1 below describes.
2. Size the batch with the cost model in section 5. Convert the token estimate to a share of
   your quota before you dispatch.
3. Confirm that `/tmp/gate/prose/` exists and is writable. The agents write there.
   `/tmp` does not survive a reboot, so this directory is usually empty.

The batch is a hard slice, which this record earlier called shape B. It cannot overshoot,
because the pair count is fixed before dispatch. The five 2026-08-19 batches used it, all five
returned every pair, and none was killed.

**Every batch MUST end with a disk reconciliation.** Run this, and report its count:

```bash
ls /tmp/gate/prose/*.json | wc -l
```

`/tmp/gate/prose/` accumulates across batches within one session, so that count is the running
total and not the batch. List the batch chapters by name when you need the batch count.

Do not report a completion count taken from the agent return values. Section 6 explains why.
Then copy the new JSON files into `modernization/findings/prose-sweep/`, and rebuild the two
TSVs described in section 7:

```bash
python3 modernization/rebuild-tsv.py
```

## 5. Cost, and how to predict it

Cost per pair rises with the size of the English chapter. It does not rise in proportion,
because a large fixed overhead sits under every agent.

**The fit is per session. Do not carry a model across sessions.** This is the single most
important thing in this section, and 2026-09-01 is what established it.

| Session | Model | Points | R2 |
|---|---|---|---|
| 2026-08 | `tokens_per_pair ~= 45,801 + 1,197 * KB` | 6 | 0.994 |
| 2026-09-01 | `tokens_per_pair ~= 62,936 + 975 * KB` | 3 | 0.99998 |

Between the two sessions the fixed overhead rose 37% and the per-KB slope fell 19%. Each
session's own line fits its own points almost exactly. The 2026-09-01 fit predicts its three
waves to within 0.04%.

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

**How a scale correction went wrong, and why it could not have worked.**

Wave 6 came in 18.3% above the 2026-08 model and wave 7 came in 16.5% above it. Two waves
agreeing that closely looked like a measurement, so this record carried a flat multiplier of
1.173 for one commit. Wave 8 then came in at 1.121 and broke it.

The multiplier was the wrong SHAPE, not the wrong number. A single factor scales the intercept
and the slope together. What actually happened is that the intercept went up while the slope
went down, so the two waves that set the multiplier were both near 25 to 29 KB, where the two
errors happened to cancel. Wave 8 sat at 41.6 KB, far enough out for them to stop cancelling.

Two rules follow, and the second is the general one:

1. **Fit a fresh line per session.** Two batches at different sizes give you the line. Run a
   small batch and a large one early, not two of similar size.
2. **A correction that fits at one size is not a model.** Before you trust one, check it at a
   size well outside the points that produced it. Waves 6 and 7 were 4 KB apart and agreed to
   1.8 points, which felt conclusive and was not.

**To size a batch:** fit this session's line on its first two batches, then sum
`intercept + slope * KB` over the batch chapters and multiply by 7. Until you have two points,
use the 2026-09-01 line and treat it as provisional.

The 2 remaining chapters hold 94,397 bytes of English source, at a mean of 46.1 KB.
The 2026-09-01 line puts them at **1.51M tokens** for 14 pairs.

**Findings per token does not favour either end.** The eight waves returned 45, 60, 53, 48, 53,
58, 53 and 56 findings per million tokens.

### Converting tokens to a share of the weekly quota

The 2026-08-19 session measured this against the owner's meter. 5,643,732 subagent tokens moved
it 8 percentage points, which is about **705,000 tokens per point**. Orchestrator work sits
inside that denominator already, so do not add a separate reserve for it.

Re-measure this on the first batch of any new session. The rate is a property of the plan and
the model in use, not of this repository.

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

`modernization/findings/prose-sweep/` holds the durable copy: 322 JSON files, one per chapter-language pair,
named `<chapter>.<lang>.json`. Each file holds `chapter`, `lang`, `coverage` and `findings`.
These files are byte-identical to the originals.

`/tmp/gate/prose/` holds the volatile originals. `/tmp` does not survive a reboot.
Treat `/tmp/gate/prose/` as scratch space, and `modernization/findings/prose-sweep/` as the record.

Two derived tables sit beside the JSON copies. Both are tab-separated with a header row.
Both were built from the 322 JSON files and from nothing else, by
`modernization/rebuild-tsv.py`.

| File | Rows | One row is |
|---|---|---|
| `modernization/findings/language-prose-drift.tsv` | 1527 | one finding |
| `modernization/findings/language-prose-coverage.tsv` | 15243 | one segment pairing |

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
   It is `TRUE` on all 15243 coverage rows.
3. No field needed whitespace cleaning. No value in the 322 source files contained a tab,
   a newline or a carriage return. The rebuild checks this and exits non-zero if any did.

**Rebuild both TSVs from the JSON files after every batch.** Do not append to them.
Run `python3 modernization/rebuild-tsv.py`, which reads the JSON and nothing else.

**The rebuild is verified against the record, and the check was proved red.**
Restricted to the 231 pairs read before wave 6, via `--only-pairs`, it reproduces the
1054 drift rows and 10474 coverage rows **byte-identically**, not merely as sets.
The check was then proved red by dropping one pair from that list, which lost 5 drift
rows and which `cmp` detected. Re-run both before you trust a future rebuild.

**Neither TSV holds a row for any of the 14 unread pairs.**
That absence is deliberate, and it is the record.
Do not add a placeholder row for an unread pair. A placeholder would later read as
"somebody read this pair and found nothing", which is false.

## 8. What this record does NOT tell you

**No verification pass ran. Not one of the 1527 findings is verified.**

Each finding is one agent's unverified claim about one segment pair. The agent read the
English chapter and the translated chapter, and it wrote what it believed it saw.
Nothing checked that belief.

The agents self-rated 733 findings `high`, 641 `medium` and 153 `low`. Nothing checked
any of those three ratings either.

The plan requires two blind verifiers per finding before a finding is eligible for a fix.
That step ran for 0 of the 1527 findings.

Three consequences follow.

1. Do NOT edit a `.qmd` file on the strength of a row in `modernization/findings/language-prose-drift.tsv`.
2. Do NOT report a count from this record as a defect count. It is a claim count.
3. Do NOT read `confidence` as a measured quantity. It is the finding agent's own rating.

The coverage file records what an agent claims it read. It is not independent evidence of
reading either.
