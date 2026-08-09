# Prose sweep: resume record

## 1. What this is, and what state it is in

The prose sweep reads every translated chapter of the handbook against its English source.
It records each place where the translation says something the English does not say.
The sweep is **98 of 336 chapter-language pairs complete**.
The other **238 pairs were never read**.
Nothing is half-read. Every one of the 14 complete chapters has all 7 languages.
Every one of the 34 remaining chapters has none.
A session quota limit stopped the run. The run did not stop by design.

The corpus is 48 declared chapters in 7 languages: `es`, `fr`, `jp`, `pt`, `ru`, `tr`, `vn`.
48 chapters times 7 languages is 336 pairs.

## 2. Chapters

| State | Chapters | Pairs |
|---|---|---|
| Complete, all 7 languages read | 14 | 98 |
| Remaining, 0 languages read | 34 | 238 |
| Partial | 0 | 0 |

**Complete (14).** Every one has 7 of 7 languages on disk.

```
age_pyramid  basics  characters_strings  cleaning  collaboration
combination_analysis  contact_tracing  data_table  data_used  dates
deduplication  diagrams  directories  editorial_style
```

**Remaining (34).** Not one language of these was read.

```
epicurves  errors  factors  flexdashboard  ggplot_basics  ggplot_tips
grouping  heatmaps  help  importing  interactive_plots  iteration
joining_matching  missing_data  moving_average  network_drives
packages_suggested  phylogenetic_trees  pivoting  r_projects  regression
reportfactory  rmarkdown  shiny_basics  standardization  stat_tests
survey_analysis  survival_analysis  tables_descriptive  tables_presentation
time_series  transition_to_r  transmission_chains  writing_functions
```

## 3. What the findings say so far

**Read the base before you read any number in this section.**
Every count below is over the 98 pairs in the 14 complete chapters.
No count below is over the 336-pair corpus, and none is over the 48 declared chapters.

Total: **493 findings over 98 pairs in 14 chapters**. Mean 5.03 findings per pair.

By kind, over those same 98 pairs:

| Kind | Findings | Meaning |
|---|---|---|
| untrue | 205 | The translation asserts something the English does not assert. |
| missing | 155 | The English asserts something the translation drops. |
| code_mismatch | 69 | The prose describes an output that the chunk beside it does not produce. |
| added | 55 | The translation adds a claim with no English source. |
| alignment_mismatch | 9 | The segments pair up, but the pairing is wrong. |

By language, over those same 98 pairs. Each language contributed 14 pairs, one per complete
chapter, so these 7 counts are comparable to each other:

| Language | Findings |
|---|---|
| tr | 112 |
| jp | 85 |
| fr | 74 |
| pt | 62 |
| vn | 60 |
| es | 57 |
| ru | 43 |

95 of the 98 pairs carry at least one finding. Three pairs carry none:
`combination_analysis.es`, `data_table.ru` and `directories.ru`.
Those three pairs are read, and they are covered in `modernization/findings/language-prose-coverage.tsv`.
A pair absent from `modernization/findings/language-prose-drift.tsv` is therefore not proof of a pair that
nobody read. Use the coverage file to decide what was read.

If the rate holds, 336 pairs give roughly 1690 findings. Treat 1690 as an estimate, not a
measurement.

## 4. How to resume

The repository holds a copy of the workflow script at this path:

```
modernization/workflows/epirhandbook-prose-drift-find-wf_549a2da0-bec.js
```

The Claude Code workflow store holds the live original at this path:

```
/home/raw996/.claude/projects/-home-raw996-ae/5d0394ed-b037-40d5-b069-f1722bddc6a4/workflows/scripts/epirhandbook-prose-drift-find-wf_549a2da0-bec.js
```

Edit the live original, not the repository copy. The Workflow tool runs the live original.

Do these four things before you start the run.

1. Cut the `STEMS` array down to the 34 remaining chapters listed in section 2.
   `STEMS` currently holds all 48 chapters. Leaving it whole re-reads 98 finished pairs and
   overwrites their JSON.
2. Add a budget guard. The original run had none. Section 6 explains what that cost.
3. Change the completion count to read files on disk. The original counted agent returns.
   Section 6 explains what that cost.
4. Confirm that `/tmp/gate/prose/` exists and is writable. The agents write there.

The guard MUST stop the run while quota remains. Use one of these two shapes.

Shape A, a running check. Dispatch pairs while the budget holds, and stop above a floor:

```js
const queue = [...PAIRS]
while (queue.length && budget.total && budget.remaining() > 200_000) {
  await runPair(queue.shift())
}
if (queue.length) log(`BUDGET FLOOR reached: ${queue.length} pairs undispatched`)
```

Verify that `budget.total` is non-zero before you use shape A.
The loop body never runs when `budget.total` is 0 or undefined.
A run that dispatches nothing looks the same in the log as a run that finished everything.

Shape B, a hard slice. Pick a pair count you can pay for, and run only that many:

```js
const BATCH = 40                       // 40 pairs x ~55k tokens = ~2.2M tokens
const PAIRS_THIS_RUN = PAIRS.slice(0, BATCH)
```

Shape B is the safer choice for an unattended run, because it cannot overshoot.
Shape A gets more work done per quota window, because it uses the real remaining budget.

Whichever shape you use, the run MUST end by listing `/tmp/gate/prose/*.json` and counting
the files. Do not report a completion count taken from the agent return values.

## 5. Cost

One clean 5-pair run used 274,099 tokens. That is about **55,000 tokens per pair**.
The remaining 238 pairs therefore cost about **13 million tokens**.

Plan for a fresh quota window. This is not a spare half hour of work.
Section 4 shape B lets you split the 238 pairs across several windows.

## 6. Two defects in the original run

Fix both before you resume. Each one already cost real work.

**Defect 1: no budget guard.** The workflow called `parallel()` on all 336 pairs at once.
Nothing checked the remaining quota between dispatches. The session limit then killed 253
agents mid-flight. The run stopped at an arbitrary point instead of at a clean boundary.
A guard turns a kill into a planned stop. Section 4 gives the guard shape.

**Defect 2: the run counted agent returns, not artifacts on disk.** The workflow built its
totals from the array that `parallel()` returned. It reported 83 completed pairs while 94
JSON files sat in `/tmp/gate/prose/`. Eleven agents wrote their JSON file and then died
before they returned a value. That work was nearly discarded as failed.
A resumed run MUST reconcile against the files on disk. The file is the artifact. The
return value is only a report about the artifact.

## 7. Where the data is

`modernization/findings/prose-sweep/` holds the durable copy: 98 JSON files, one per chapter-language pair,
named `<chapter>.<lang>.json`. Each file holds `chapter`, `lang`, `coverage` and `findings`.
These files are byte-identical to the originals.

`/tmp/gate/prose/` holds the volatile originals. `/tmp` does not survive a reboot.
Treat `/tmp/gate/prose/` as scratch space, and `modernization/findings/prose-sweep/` as the record.
`/tmp/gate/prose/` also holds `build.py`, `build_cov.py` and `_seg_en.json`. Those three
are one agent's scratch files, not pair data, and they are not copied into the repo.

Two derived tables sit beside the JSON copies. Both are tab-separated with a header row.
Both were built from the 98 JSON files and from nothing else.

| File | Rows | One row is |
|---|---|---|
| `modernization/findings/language-prose-drift.tsv` | 493 | one finding |
| `modernization/findings/language-prose-coverage.tsv` | 5561 | one segment pairing |

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
   `en_segment_id` is `NA` on the 26 rows with `relation` `unmatched-tr`.
   `tr_segment_id` is `NA` on the 3 rows with `relation` `unmatched-en`.
2. `reviewed` is written as `TRUE` or `FALSE`, which R reads as a logical column.
   It is `TRUE` on all 5561 coverage rows.
3. No field needed whitespace cleaning. No `proposition` or `reader_consequence` value in
   the 98 source files contained a tab, a newline or a carriage return.

**Neither TSV holds a row for any of the 238 unread pairs.**
That absence is deliberate, and it is the record.
Do not add a placeholder row for an unread pair. A placeholder would later read as
"somebody read this pair and found nothing", which is false.

## 8. What this record does NOT tell you

**No verification pass ran. Not one of the 493 findings is verified.**

Each finding is one agent's unverified claim about one segment pair. The agent read the
English chapter and the translated chapter, and it wrote what it believed it saw.
Nothing checked that belief.

The plan requires two blind verifiers per finding before a finding is eligible for a fix.
That step ran for 0 of the 493 findings.

Three consequences follow.

1. Do NOT edit a `.qmd` file on the strength of a row in `modernization/findings/language-prose-drift.tsv`.
2. Do NOT report a count from this record as a defect count. It is a claim count.
3. Do NOT read `confidence` as a measured quantity. It is the finding agent's own rating.

The coverage file records what an agent claims it read. It is not independent evidence of
reading either.
