# Prose sweep: resume record

## 1. What this is, and what state it is in

The prose sweep reads every translated chapter of the handbook against its English source.
It records each place where the translation says something the English does not say.
The sweep is **182 of 336 chapter-language pairs complete**.
The other **154 pairs were never read**.
Nothing is half-read. Every one of the 26 complete chapters has all 7 languages.
Every one of the 22 remaining chapters has none.

The corpus is 48 declared chapters in 7 languages: `es`, `fr`, `jp`, `pt`, `ru`, `tr`, `vn`.
48 chapters times 7 languages is 336 pairs.

Two runs produced the 182 pairs. A session quota limit stopped the first run on 2026-08-09
at 98 pairs. That run did not stop by design. The second run on 2026-08-19 added 84 pairs in
four planned batches, and it stopped at an owner-set quota ceiling with the record committed.

## 2. Chapters

| State | Chapters | Pairs |
|---|---|---|
| Complete, all 7 languages read | 26 | 182 |
| Remaining, 0 languages read | 22 | 154 |
| Partial | 0 | 0 |

**Complete (26).** Every one has 7 of 7 languages on disk.

```
age_pyramid  basics  characters_strings  cleaning  collaboration
combination_analysis  contact_tracing  data_table  data_used  dates
deduplication  diagrams  directories  editorial_style  epicurves
errors  ggplot_basics  ggplot_tips  help  network_drives
packages_suggested  r_projects  reportfactory  shiny_basics
tables_descriptive  time_series
```

**Remaining (22).** Not one language of these was read.

```
factors  flexdashboard  grouping  heatmaps  importing
interactive_plots  iteration  joining_matching  missing_data
moving_average  phylogenetic_trees  pivoting  regression  rmarkdown
standardization  stat_tests  survey_analysis  survival_analysis
tables_presentation  transition_to_r  transmission_chains
writing_functions
```

## 3. What the findings say so far

**Read the base before you read any number in this section.**
Every count below is over the 182 pairs in the 26 complete chapters.
No count below is over the 336-pair corpus, and none is over the 48 declared chapters.

Total: **873 findings over 182 pairs in 26 chapters**. Mean 4.80 findings per pair.

By kind, over those same 182 pairs:

| Kind | Findings | Meaning |
|---|---|---|
| untrue | 379 | The translation asserts something the English does not assert. |
| missing | 254 | The English asserts something the translation drops. |
| code_mismatch | 120 | The prose describes an output that the chunk beside it does not produce. |
| added | 106 | The translation adds a claim with no English source. |
| alignment_mismatch | 14 | The segments pair up, but the pairing is wrong. |

By language, over those same 182 pairs. Each language contributed 26 pairs, one per complete
chapter, so these 7 counts are comparable to each other:

| Language | Findings |
|---|---|
| tr | 199 |
| jp | 141 |
| fr | 125 |
| pt | 121 |
| vn | 102 |
| es | 98 |
| ru | 87 |

Turkish led the count at 98 pairs and it still leads at 182 pairs.
Russian has held the lowest count throughout.

172 of the 182 pairs carry at least one finding. Ten pairs carry none:
`combination_analysis.es`, `data_table.ru`, `directories.ru`, `errors.ru`,
`network_drives.ru`, `packages_suggested.es`, `packages_suggested.tr`,
`r_projects.fr`, `r_projects.ru` and `reportfactory.tr`.
Those ten pairs are read, and they are covered in `modernization/findings/language-prose-coverage.tsv`.
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
because the pair count is fixed before dispatch. The four 2026-08-19 batches used it, all four
returned every pair, and none was killed.

**Every batch MUST end with a disk reconciliation.** Run this, and report its count:

```bash
ls /tmp/gate/prose/*.json | wc -l
```

Do not report a completion count taken from the agent return values. Section 6 explains why.
Then copy the new JSON files into `modernization/findings/prose-sweep/`, and rebuild the two
TSVs described in section 7.

## 5. Cost, and how to predict it

Cost per pair rises with the size of the English chapter. It does not rise in proportion,
because a large fixed overhead sits under every agent.

| English chapter, mean size | Measured tokens per pair | Batch |
|---|---|---|
| 5,418 bytes | 52,020 | 2026-08-19 wave 1, 2 chapters |
| 8,644 bytes | 55,885 | 2026-08-19 wave 4, 4 chapters |
| 9,599 bytes | 54,820 | 2026-08-09, `directories` and `editorial_style` |
| 56,607 bytes | 115,244 | 2026-08-19 wave 3, 4 chapters |
| 66,580 bytes | 120,616 | 2026-08-19 wave 2, 2 chapters |

Fit a line to the wave 1 and wave 2 points and you get this model:

```
tokens_per_pair  ~=  45,900  +  1,121 * (English chapter size in KB)
```

The model was fitted on two points and tested against three others. It predicts the
9,599-byte run within 3.4%, wave 3 within 2.7%, and wave 4 within 0.5%.

**Do not use a flat per-pair rate.** Two earlier estimates did, and both were low.
The 13M figure in the 2026-08-09 record and a later 11.7M figure both extrapolated a
small-chapter rate across the whole corpus.

The 22 remaining chapters hold 640,680 bytes of English source.
The model puts them at **12.1M tokens**, for 154 pairs.

To size one batch, sum `45,900 + 1,121 * KB` over its chapters and multiply by 7.

**Findings per token does not favour either end.** The four waves returned 45, 60, 53 and 48
findings per million tokens. Order a batch by whichever you need: cheap chapters complete more
chapters per token, large chapters cover more of the corpus.

## 6. Two defects in the original run

The 2026-08-09 run carried both. The 2026-08-19 batches avoided both. Keep avoiding them.

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

`modernization/findings/prose-sweep/` holds the durable copy: 182 JSON files, one per chapter-language pair,
named `<chapter>.<lang>.json`. Each file holds `chapter`, `lang`, `coverage` and `findings`.
These files are byte-identical to the originals.

`/tmp/gate/prose/` holds the volatile originals. `/tmp` does not survive a reboot.
Treat `/tmp/gate/prose/` as scratch space, and `modernization/findings/prose-sweep/` as the record.

Two derived tables sit beside the JSON copies. Both are tab-separated with a header row.
Both were built from the 182 JSON files and from nothing else.

| File | Rows | One row is |
|---|---|---|
| `modernization/findings/language-prose-drift.tsv` | 873 | one finding |
| `modernization/findings/language-prose-coverage.tsv` | 8970 | one segment pairing |

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
   `en_segment_id` is `NA` on 27 rows. `tr_segment_id` is `NA` on 9 rows.
2. `reviewed` is written as `TRUE` or `FALSE`, which R reads as a logical column.
   It is `TRUE` on all 8970 coverage rows.
3. No field needed whitespace cleaning. No value in the 182 source files contained a tab,
   a newline or a carriage return. The rebuild checks this and reports the count.

**Rebuild both TSVs from the JSON files after every batch.** Do not append to them.
The rebuild is verified: restricted to the original 98 pairs it reproduces the earlier
493 drift rows and 5561 coverage rows exactly, compared as sets.

**Neither TSV holds a row for any of the 154 unread pairs.**
That absence is deliberate, and it is the record.
Do not add a placeholder row for an unread pair. A placeholder would later read as
"somebody read this pair and found nothing", which is false.

## 8. What this record does NOT tell you

**No verification pass ran. Not one of the 873 findings is verified.**

Each finding is one agent's unverified claim about one segment pair. The agent read the
English chapter and the translated chapter, and it wrote what it believed it saw.
Nothing checked that belief.

The plan requires two blind verifiers per finding before a finding is eligible for a fix.
That step ran for 0 of the 873 findings.

Three consequences follow.

1. Do NOT edit a `.qmd` file on the strength of a row in `modernization/findings/language-prose-drift.tsv`.
2. Do NOT report a count from this record as a defect count. It is a claim count.
3. Do NOT read `confidence` as a measured quantity. It is the finding agent's own rating.

The coverage file records what an agent claims it read. It is not independent evidence of
reading either.
