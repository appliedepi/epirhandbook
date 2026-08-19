# Prose sweep: resume record

## 1. What this is, and what state it is in

The prose sweep reads every translated chapter of the handbook against its English source.
It records each place where the translation says something the English does not say.
The sweep is **154 of 336 chapter-language pairs complete**.
The other **182 pairs were never read**.
Nothing is half-read. Every one of the 22 complete chapters has all 7 languages.
Every one of the 26 remaining chapters has none.

The corpus is 48 declared chapters in 7 languages: `es`, `fr`, `jp`, `pt`, `ru`, `tr`, `vn`.
48 chapters times 7 languages is 336 pairs.

Two runs produced the 154 pairs. A session quota limit stopped the first run on 2026-08-09
at 98 pairs. That run did not stop by design. The second run on 2026-08-19 added 56 pairs in
three planned batches, and it stopped with quota still remaining.

## 2. Chapters

| State | Chapters | Pairs |
|---|---|---|
| Complete, all 7 languages read | 22 | 154 |
| Remaining, 0 languages read | 26 | 182 |
| Partial | 0 | 0 |

**Complete (22).** Every one has 7 of 7 languages on disk.

```
age_pyramid  basics  characters_strings  cleaning  collaboration
combination_analysis  contact_tracing  data_table  data_used  dates
deduplication  diagrams  directories  editorial_style  epicurves
errors  ggplot_basics  ggplot_tips  r_projects  shiny_basics
tables_descriptive  time_series
```

**Remaining (26).** Not one language of these was read.

```
factors  flexdashboard  grouping  heatmaps  help  importing
interactive_plots  iteration  joining_matching  missing_data
moving_average  network_drives  packages_suggested  phylogenetic_trees
pivoting  regression  reportfactory  rmarkdown  standardization
stat_tests  survey_analysis  survival_analysis  tables_presentation
transition_to_r  transmission_chains  writing_functions
```

## 3. What the findings say so far

**Read the base before you read any number in this section.**
Every count below is over the 154 pairs in the 22 complete chapters.
No count below is over the 336-pair corpus, and none is over the 48 declared chapters.

Total: **798 findings over 154 pairs in 22 chapters**. Mean 5.18 findings per pair.

By kind, over those same 154 pairs:

| Kind | Findings | Meaning |
|---|---|---|
| untrue | 344 | The translation asserts something the English does not assert. |
| missing | 232 | The English asserts something the translation drops. |
| code_mismatch | 115 | The prose describes an output that the chunk beside it does not produce. |
| added | 94 | The translation adds a claim with no English source. |
| alignment_mismatch | 13 | The segments pair up, but the pairing is wrong. |

By language, over those same 154 pairs. Each language contributed 22 pairs, one per complete
chapter, so these 7 counts are comparable to each other:

| Language | Findings |
|---|---|
| tr | 190 |
| jp | 125 |
| fr | 116 |
| pt | 108 |
| es | 92 |
| vn | 90 |
| ru | 77 |

Turkish led the count at 98 pairs and it still leads at 154 pairs.

148 of the 154 pairs carry at least one finding. Six pairs carry none:
`combination_analysis.es`, `data_table.ru`, `directories.ru`, `errors.ru`,
`r_projects.fr` and `r_projects.ru`.
Those six pairs are read, and they are covered in `modernization/findings/language-prose-coverage.tsv`.
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

The batch is a hard slice, which `RESUME.md` earlier called shape B. It cannot overshoot,
because the pair count is fixed before dispatch. The three 2026-08-19 batches used it and none
was killed.

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
| 5,418 bytes | 52,020 | 2026-08-19 wave 1, `r_projects` and `errors` |
| 9,599 bytes | 54,820 | 2026-08-09, `directories` and `editorial_style` |
| 56,607 bytes | 115,244 | 2026-08-19 wave 3, four chapters |
| 66,580 bytes | 120,616 | 2026-08-19 wave 2, `epicurves` and `shiny_basics` |

Fit a line to the wave 1 and wave 2 points and you get this model:

```
tokens_per_pair  ~=  45,900  +  1,121 * (English chapter size in KB)
```

The model was fitted on two points and tested against the other two.
It predicts the 9,599-byte run at 56,700 against a measured 54,820, an error of 3.4%.
It predicts wave 3 at 3.14M against a measured 3.23M, an error of 2.7%.

**Do not use a flat per-pair rate.** Two earlier estimates did, and both were low.
The 13M figure in the 2026-08-09 record and a later 11.7M figure both extrapolated a
small-chapter rate across the whole corpus.

The 26 remaining chapters hold 675,256 bytes of English source.
The model puts them at **13.7M tokens**, for 182 pairs.

To size one batch, sum `45,900 + 1,121 * KB` over its chapters and multiply by 7.

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

`modernization/findings/prose-sweep/` holds the durable copy: 154 JSON files, one per chapter-language pair,
named `<chapter>.<lang>.json`. Each file holds `chapter`, `lang`, `coverage` and `findings`.
These files are byte-identical to the originals.

`/tmp/gate/prose/` holds the volatile originals. `/tmp` does not survive a reboot.
Treat `/tmp/gate/prose/` as scratch space, and `modernization/findings/prose-sweep/` as the record.

Two derived tables sit beside the JSON copies. Both are tab-separated with a header row.
Both were built from the 154 JSON files and from nothing else.

| File | Rows | One row is |
|---|---|---|
| `modernization/findings/language-prose-drift.tsv` | 798 | one finding |
| `modernization/findings/language-prose-coverage.tsv` | 8552 | one segment pairing |

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
   It is `TRUE` on all 8552 coverage rows.
3. No field needed whitespace cleaning. No value in the 154 source files contained a tab,
   a newline or a carriage return. The rebuild checks this and reports the count.

**Rebuild both TSVs from the JSON files after every batch.** Do not append to them.
The rebuild is verified: restricted to the original 98 pairs it reproduces the earlier
493 drift rows and 5561 coverage rows exactly, compared as sets.

**Neither TSV holds a row for any of the 182 unread pairs.**
That absence is deliberate, and it is the record.
Do not add a placeholder row for an unread pair. A placeholder would later read as
"somebody read this pair and found nothing", which is false.

## 8. What this record does NOT tell you

**No verification pass ran. Not one of the 798 findings is verified.**

Each finding is one agent's unverified claim about one segment pair. The agent read the
English chapter and the translated chapter, and it wrote what it believed it saw.
Nothing checked that belief.

The plan requires two blind verifiers per finding before a finding is eligible for a fix.
That step ran for 0 of the 798 findings.

Three consequences follow.

1. Do NOT edit a `.qmd` file on the strength of a row in `modernization/findings/language-prose-drift.tsv`.
2. Do NOT report a count from this record as a defect count. It is a claim count.
3. Do NOT read `confidence` as a measured quantity. It is the finding agent's own rating.

The coverage file records what an agent claims it read. It is not independent evidence of
reading either.
