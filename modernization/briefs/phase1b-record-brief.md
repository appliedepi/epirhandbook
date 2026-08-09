# Phase 1b, partial — assemble the artifacts and write the resume record

Repo: /home/raw996/ae/epiRhandbook_eng

## Situation

The 336-pair prose sweep was cut off by a session quota limit after 98 pairs. The owner asked
for two things: finish the chapters that had been started (DONE, all 98 pairs are on disk), and
**record the state well enough that resuming later is easy**. The record is the deliverable.

Source data: 98 JSON files in `/tmp/gate/prose/`, one per chapter-language pair, all valid JSON.
**`/tmp` is volatile. Preserving this data in the repo is part of the job.**

## Measured state, verified by the orchestrator. Use these numbers; do not re-derive them silently.

```
declared chapters                48
chapters COMPLETE (7/7 langs)    14   = 98 pairs
chapters REMAINING (0/7 langs)   34   = 238 pairs
partial chapters                  0   (clean boundary, nothing half-read)

pair files on disk               98   all valid JSON
findings                        493
coverage rows                  5561

findings by kind   untrue 205, missing 155, code_mismatch 69, added 55, alignment_mismatch 9
findings by lang   tr 112, jp 85, fr 74, pt 62, vn 60, es 57, ru 43
findings per pair  5.03  ->  336 pairs would give roughly 1690

cost measured on the clean 5-pair run: 274,099 tokens / 5 = ~55k tokens per pair
remaining 238 pairs therefore ~13M tokens
```

COMPLETE: age_pyramid, basics, characters_strings, cleaning, collaboration, combination_analysis,
contact_tracing, data_table, data_used, dates, deduplication, diagrams, directories, editorial_style

REMAINING: epicurves, errors, factors, flexdashboard, ggplot_basics, ggplot_tips, grouping,
heatmaps, help, importing, interactive_plots, iteration, joining_matching, missing_data,
moving_average, network_drives, packages_suggested, phylogenetic_trees, pivoting, r_projects,
regression, reportfactory, rmarkdown, shiny_basics, standardization, stat_tests, survey_analysis,
survival_analysis, tables_descriptive, tables_presentation, time_series, transition_to_r,
transmission_chains, writing_functions

## Files you MAY create. Nothing else.

```
utils/language-prose-drift.tsv        one row per finding
utils/language-prose-coverage.tsv     one row per coverage entry
utils/PROSE-SWEEP-RESUME.md           the resume record
utils/prose-sweep/<chapter>.<lang>.json   copies of all 98 source files
```

You MUST NOT touch any `.qmd`, `_quarto.yml`, `.github/`, or `utils/check-language-consistency.R`.

## 1. The two TSVs

`language-prose-drift.tsv` columns, tab-separated, header row:
`chapter  lang  heading  segment_index  kind  en_span  tr_span  proposition  reader_consequence  confidence`

`language-prose-coverage.tsv` columns:
`chapter  lang  en_segment_id  tr_segment_id  relation  confidence  reviewed`

Rules:
- Row counts MUST be exactly 493 and 5561. If your count differs, STOP and report the difference
  with the file that caused it. Do not silently drop or dedupe a row.
- Tabs, newlines and carriage returns inside any field MUST be replaced with a single space, or
  the TSV is unreadable. Say in your report how many fields you had to clean.
- Do not translate, reword or truncate `proposition` or `reader_consequence`.
- Add NO rows for the 238 unread pairs. Absence is the record; a placeholder row would later read
  as "read, nothing found", which is the single most dangerous thing this file could say.

## 2. `utils/PROSE-SWEEP-RESUME.md`

Written for someone picking this up cold in a week, possibly not the orchestrator. Follow
`rw-technical-prose`. It MUST contain, in this order:

1. **What this is and what state it is in.** One short paragraph. Say plainly that the sweep is
   98 of 336 pairs complete and that the other 238 have never been read.
2. **The two tables above** — complete and remaining chapters, with counts.
3. **What the findings say so far**, with the by-kind and by-lang tables. State the base with
   every number: these counts are over 98 pairs in 14 chapters, NOT over the corpus.
4. **How to resume.** The workflow script is at
   `/home/raw996/.claude/projects/-home-raw996-ae/5d0394ed-b037-40d5-b069-f1722bddc6a4/workflows/scripts/epirhandbook-prose-drift-find-wf_549a2da0-bec.js`
   Say that the resumer MUST edit the `STEMS` array down to the 34 remaining chapters, and MUST
   add a budget guard. Give the exact guard shape:
   `while (budget.total && budget.remaining() > 200_000) { ... }` or a hard slice, and explain
   that the original run had none, which is why it died mid-sweep instead of stopping cleanly.
5. **Cost.** ~55k tokens per pair measured, ~13M for the remaining 238. Enough that it needs a
   fresh quota window, not a spare half hour.
6. **Two defects in the original run, so the next one does not repeat them.**
   - No budget guard. 336 agents were launched at once; the session limit killed 253 of them.
   - The workflow reported 83 completed pairs when 94 files existed on disk. It counted agent
     RETURNS, not artifacts. Eleven agents wrote their JSON and then died before returning, and
     that data was nearly discarded. A resumed run MUST reconcile against files on disk, not
     against its own return values.
7. **Where the data is**, naming `utils/prose-sweep/` as the durable copy and noting that
   `/tmp/gate/prose/` is the volatile original.
8. **What this does NOT tell you.** No verification pass has run. Every finding is a single
   agent's unverified claim. The plan requires two blind verifiers per finding before anything
   is eligible to be fixed, and that has not happened for any of the 493.

## 3. Copy the JSON

Copy all 98 files from `/tmp/gate/prose/` into `utils/prose-sweep/`. Skip the stray `_seg_en.json`,
which is a scratch artifact from one agent, not a pair file. Confirm 98 files copied and that each
is valid JSON after the copy.

## Discriminator

```
Rscript -e 'd <- read.delim("utils/language-prose-drift.tsv", sep="\t", quote=""); c2 <- read.delim("utils/language-prose-coverage.tsv", sep="\t", quote=""); stopifnot(nrow(d) == 493); stopifnot(nrow(c2) == 5561); stopifnot(length(unique(paste(d$chapter, d$lang))) <= 98); stopifnot(length(unique(paste(c2$chapter, c2$lang))) == 98); stopifnot(!any(is.na(d$kind) | d$kind == "")); print(table(d$kind)); print(table(d$lang)); cat("chapters covered:", length(unique(c2$chapter)), "\n")'
```

It MUST print 493 rows split across the five kinds, 5561 coverage rows, and 14 chapters covered.

## Pass/fail

PASS when: both TSVs parse in R with the exact row counts; coverage names exactly 98 distinct
pairs across 14 chapters; `utils/prose-sweep/` holds 98 valid JSON files; `PROSE-SWEEP-RESUME.md`
contains all eight required elements including the two named defects; and `git status --porcelain`
shows only the new files plus the already-staged `utils/check-language-consistency.R`.

FAIL if a row count differs and is not reported, if any placeholder row exists for an unread pair,
or if any `.qmd` appears in the diff.

## Forbidden

- Bare `grep`. It is a ugrep-backed shell function whose output has no `./` prefix. Use `command grep`.
- `git commit`, `git push`, `git tag`, installs, formatters, `renv.lock`.
- Spawning subagents. This is deterministic data assembly and documentation.
