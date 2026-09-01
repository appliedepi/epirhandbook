# Prose sweep: resume record

## 1. What this is, and what state it is in

The prose sweep reads every translated chapter of the handbook against its English source.
It records each place where the translation says something the English does not say.
The sweep is **259 of 336 chapter-language pairs complete**.
The other **77 pairs were never read**.
Nothing is half-read. Every one of the 37 complete chapters has all 7 languages.
Every one of the 11 remaining chapters has none.

The corpus is 48 declared chapters in 7 languages: `es`, `fr`, `jp`, `pt`, `ru`, `tr`, `vn`.
48 chapters times 7 languages is 336 pairs.

Three runs produced the 259 pairs. A session quota limit stopped the first run on 2026-08-09
at 98 pairs. That run did not stop by design. The second run added 133 pairs in five planned
batches, and each batch stopped at a size the owner set in advance. The third run, wave 6 on
2026-09-01, added 28 pairs in one batch and returned all 28.

Phase A, the deterministic segmenter, is SKIPPED rather than deferred. Section 5 gives the
reason: it cannot touch the fixed per-agent overhead, which is most of the per-pair cost, and
adopting it now would read the last pairs by a method the first 231 were not read by.

## 2. Chapters

| State | Chapters | Pairs |
|---|---|---|
| Complete, all 7 languages read | 37 | 259 |
| Remaining, 0 languages read | 11 | 77 |
| Partial | 0 | 0 |

**Complete (37).** Every one has 7 of 7 languages on disk.

```
age_pyramid  basics  characters_strings  cleaning  collaboration
combination_analysis  contact_tracing  data_table  data_used  dates
deduplication  diagrams  directories  editorial_style  epicurves
errors  factors  ggplot_basics  ggplot_tips  grouping
heatmaps  help  interactive_plots  moving_average  network_drives
packages_suggested  pivoting  r_projects  reportfactory  shiny_basics
standardization  stat_tests  tables_descriptive  time_series  transition_to_r
transmission_chains  writing_functions
```

**Remaining (11).** Not one language of these was read.

```
flexdashboard  importing  iteration  joining_matching  missing_data
phylogenetic_trees  regression  rmarkdown  survey_analysis
survival_analysis  tables_presentation
```

## 3. What the findings say so far

**Read the base before you read any number in this section.**
Every count below is over the 259 pairs in the 37 complete chapters.
No count below is over the 336-pair corpus, and none is over the 48 declared chapters.

Total: **1196 findings over 259 pairs in 37 chapters**. Mean 4.62 findings per pair.

By kind, over those same 259 pairs:

| Kind | Findings | Meaning |
|---|---|---|
| untrue | 501 | The translation asserts something the English does not assert. |
| missing | 359 | The English asserts something the translation drops. |
| code_mismatch | 180 | The prose describes an output that the chunk beside it does not produce. |
| added | 134 | The translation adds a claim with no English source. |
| alignment_mismatch | 22 | The segments pair up, but the pairing is wrong. |

By language, over those same 259 pairs. Each language contributed 37 pairs, one per complete
chapter, so these 7 counts are comparable to each other:

| Language | Findings |
|---|---|
| tr | 266 |
| jp | 190 |
| pt | 169 |
| fr | 167 |
| ru | 141 |
| vn | 136 |
| es | 127 |

Turkish led the count at 98 pairs and it still leads at 259 pairs. Russian is no longer the
lowest: wave 6 moved Russian above Vietnamese and Spanish, and Portuguese above French.
Read a per-language rank as unstable until the corpus is complete.

247 of the 259 pairs carry at least one finding. Twelve pairs carry none, and wave 6 added
none to that list:
`combination_analysis.es`, `data_table.ru`, `directories.ru`, `errors.ru`,
`moving_average.pt`, `network_drives.ru`, `packages_suggested.es`, `packages_suggested.tr`,
`r_projects.fr`, `r_projects.ru`, `reportfactory.tr` and `stat_tests.ru`.
Those twelve pairs are read, and they are covered in `modernization/findings/language-prose-coverage.tsv`.
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

| English chapter, mean size | Measured tokens per pair | Batch |
|---|---|---|
| 5,418 bytes | 52,020 | wave 1, 2 chapters |
| 8,644 bytes | 55,885 | wave 4, 4 chapters |
| 9,599 bytes | 54,820 | 2026-08-09, `directories` and `editorial_style` |
| 18,976 bytes | 70,117 | wave 5, 7 chapters |
| 25,022 bytes | 86,729 | wave 6, 4 chapters |
| 56,607 bytes | 115,244 | wave 3, 4 chapters |
| 66,580 bytes | 120,616 | wave 2, 2 chapters |

Fit a line to the wave 1 and wave 2 points and you get this model:

```
tokens_per_pair  ~=  45,900  +  1,121 * (English chapter size in KB)
```

The model was fitted on two points and tested against four others. Its errors are 3.4%, 2.7%,
0.5% and 4.4%.

**The model under-predicts, and wave 6 shows the 5% headroom is not enough.**

Wave 6 read 4 chapters of mean 24.4 KB. The model predicted 2,052,198 tokens.
The measured cost was **2,428,408**, which is **18.3% above the prediction**.
That is four times the largest error in the original fit, whose tests were 3.4%, 2.7%,
0.5% and 4.4%.

**Multiply any model estimate by 1.18 before you use it.** Do not use the bare model, and do
not use the old 5% headroom. One point does not re-fit a slope, so 1.18 is a correction and
not a new model. Re-measure it on the next batch and revise it.

**Do not use a flat per-pair rate.** Two earlier estimates did, and both were low.
The 13M figure in the 2026-08-09 record and a later 11.7M figure both extrapolated a
small-chapter rate across the whole corpus.

The 11 remaining chapters hold 407,760 bytes of English source, at a mean of 36.2 KB.
They are larger than the 6 waves read so far, so the correction matters more, not less.
The model puts them at 6.66M tokens for 77 pairs. Corrected by 1.18 that is **7.88M**,
and **8.27M** with a further 5%.

To size one batch, sum `45,900 + 1,121 * KB` over its chapters, multiply by 7, then
multiply by 1.18.

**Findings per token does not favour either end.** The six waves returned 45, 60, 53, 48, 53
and 58 findings per million tokens. Order a batch by whichever you need: cheap chapters complete
more chapters per token, large chapters cover more of the corpus.

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

`modernization/findings/prose-sweep/` holds the durable copy: 259 JSON files, one per chapter-language pair,
named `<chapter>.<lang>.json`. Each file holds `chapter`, `lang`, `coverage` and `findings`.
These files are byte-identical to the originals.

`/tmp/gate/prose/` holds the volatile originals. `/tmp` does not survive a reboot.
Treat `/tmp/gate/prose/` as scratch space, and `modernization/findings/prose-sweep/` as the record.

Two derived tables sit beside the JSON copies. Both are tab-separated with a header row.
Both were built from the 259 JSON files and from nothing else, by
`modernization/rebuild-tsv.py`.

| File | Rows | One row is |
|---|---|---|
| `modernization/findings/language-prose-drift.tsv` | 1196 | one finding |
| `modernization/findings/language-prose-coverage.tsv` | 11772 | one segment pairing |

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
   `en_segment_id` is `NA` on 30 rows. `tr_segment_id` is `NA` on 11 rows.
2. `reviewed` is written as `TRUE` or `FALSE`, which R reads as a logical column.
   It is `TRUE` on all 11772 coverage rows.
3. No field needed whitespace cleaning. No value in the 259 source files contained a tab,
   a newline or a carriage return. The rebuild checks this and exits non-zero if any did.

**Rebuild both TSVs from the JSON files after every batch.** Do not append to them.
Run `python3 modernization/rebuild-tsv.py`, which reads the JSON and nothing else.

**The rebuild is verified against the record, and the check was proved red.**
Restricted to the 231 pairs read before wave 6, via `--only-pairs`, it reproduces the
1054 drift rows and 10474 coverage rows **byte-identically**, not merely as sets.
The check was then proved red by dropping one pair from that list, which lost 5 drift
rows and which `cmp` detected. Re-run both before you trust a future rebuild.

**Neither TSV holds a row for any of the 77 unread pairs.**
That absence is deliberate, and it is the record.
Do not add a placeholder row for an unread pair. A placeholder would later read as
"somebody read this pair and found nothing", which is false.

## 8. What this record does NOT tell you

**No verification pass ran. Not one of the 1196 findings is verified.**

Each finding is one agent's unverified claim about one segment pair. The agent read the
English chapter and the translated chapter, and it wrote what it believed it saw.
Nothing checked that belief.

The agents self-rated 576 findings `high`, 496 `medium` and 124 `low`. Nothing checked
any of those three ratings either.

The plan requires two blind verifiers per finding before a finding is eligible for a fix.
That step ran for 0 of the 1196 findings.

Three consequences follow.

1. Do NOT edit a `.qmd` file on the strength of a row in `modernization/findings/language-prose-drift.tsv`.
2. Do NOT report a count from this record as a defect count. It is a claim count.
3. Do NOT read `confidence` as a measured quantity. It is the finding agent's own rating.

The coverage file records what an agent claims it read. It is not independent evidence of
reading either.
