# Phase 1b record: proof transcript

SNAPSHOT = 0e10ff047b30abd06723d7f007e3c0622611c78b
SHA_FIXED = 0e10ff047b30abd06723d7f007e3c0622611c78b  (no R source changed)

Discriminator command, run from `/home/raw996/ae/epiRhandbook_eng`:

```
Rscript -e 'd <- read.delim("utils/language-prose-drift.tsv", sep="\t", quote=""); c2 <- read.delim("utils/language-prose-coverage.tsv", sep="\t", quote=""); stopifnot(nrow(d) == 493); stopifnot(nrow(c2) == 5561); stopifnot(length(unique(paste(d$chapter, d$lang))) <= 98); stopifnot(length(unique(paste(c2$chapter, c2$lang))) == 98); stopifnot(!any(is.na(d$kind) | d$kind == "")); print(table(d$kind)); print(table(d$lang)); cat("chapters covered:", length(unique(c2$chapter)), "\n")'
```

## Method note: where the mutations ran

The discriminator uses relative paths under `utils/`. Every mutation below ran in a scratch
copy at `/tmp/gate/mutate/utils/`, never against the repo. The repo copies were confirmed
unchanged by sha256 after the mutation sequence:

```
13eab1d3149c935db38601f512e8cf284621ebd6739181f3dc62f3d50a889c76  utils/language-prose-drift.tsv
5971222d69f580e0ba1b15a3e49fab9aed79705855940adcc6fbae3e46be2c67  utils/language-prose-coverage.tsv
```

## BEFORE: the discriminator on a clean export of HEAD

`git archive HEAD | tar -x -C /tmp/gate/before`, then the discriminator in that tree:

```
Error in file(file, "rt") : cannot open the connection
Calls: read.delim -> read.table -> file
In addition: Warning message:
In file(file, "rt") :
  cannot open file 'utils/language-prose-drift.tsv': No such file or directory
Execution halted
EXIT=1
```

## AFTER: the discriminator in the repo

```
             added alignment_mismatch      code_mismatch            missing
                55                  9                 69                155
            untrue
               205

 es  fr  jp  pt  ru  tr  vn
 57  74  85  62  43 112  60
chapters covered: 14
EXIT=0
```

## M0: baseline on the scratch copies

```
             added alignment_mismatch      code_mismatch            missing
                55                  9                 69                155
            untrue
               205

 es  fr  jp  pt  ru  tr  vn
 57  74  85  62  43 112  60
chapters covered: 14
EXIT=0
```

## Proof 1: the drift row count is pinned

MUTATION: delete line 7 of `utils/language-prose-drift.tsv` (one finding row).
FAILED-ASSERTION: `nrow(d) == 493`
RED:

```
Error: nrow(d) == 493 is not TRUE
Execution halted
EXIT=1
```

REVERT: `cp /tmp/gate/mutate/drift.orig /tmp/gate/mutate/utils/language-prose-drift.tsv`

## Proof 2: the coverage row count is pinned

MUTATION: delete line 3 of `utils/language-prose-coverage.tsv` (one coverage row).
FAILED-ASSERTION: `nrow(c2) == 5561`
RED:

```
Error: nrow(c2) == 5561 is not TRUE
Execution halted
EXIT=1
```

REVERT: `cp /tmp/gate/mutate/cov.orig /tmp/gate/mutate/utils/language-prose-coverage.tsv`

## Proof 3: a placeholder row for an UNREAD pair is detected

This is the failure mode the brief names as most dangerous, so it gets its own proof.

MUTATION: rewrite coverage row 1 as `epicurves	es	S1.P1	S1.P1	1-1	high	TRUE`.
`epicurves` is one of the 34 chapters that nobody read.
FAILED-ASSERTION: `length(unique(paste(c2$chapter, c2$lang))) == 98`
RED:

```
Error: length(unique(paste(c2$chapter, c2$lang))) == 98 is not TRUE
Execution halted
EXIT=1
```

REVERT: `cp /tmp/gate/mutate/cov.orig /tmp/gate/mutate/utils/language-prose-coverage.tsv`

## Proof 4: an embedded tab in a text field is detected

MUTATION: insert one raw tab at character 20 of the `proposition` field on drift row 1.
FAILED-ASSERTION: `read.delim` fails before any `stopifnot` runs, because the row now has 11
fields against a 10-column header.
RED:

```
Error in read.table(file = file, header = header, sep = sep, quote = quote,  :
  duplicate 'row.names' are not allowed
Calls: read.delim -> read.table
Execution halted
EXIT=1
```

REVERT: `cp /tmp/gate/mutate/drift.orig /tmp/gate/mutate/utils/language-prose-drift.tsv`

## GREEN after all four reverts

```
             added alignment_mismatch      code_mismatch            missing
                55                  9                 69                155
            untrue
               205

 es  fr  jp  pt  ru  tr  vn
 57  74  85  62  43 112  60
chapters covered: 14
EXIT=0
```

## Independent round-trip check, not a mutation proof

Parsed both TSVs with `csv.QUOTE_NONE` and compared every field against the source JSON:

```
rows drift 493 cov 5561
bad ncol drift 0 cov 0
per-pair count/content mismatches: []
pairs with zero findings (3): ['combination_analysis.es', 'data_table.ru', 'directories.ru']
```

All 493 findings match the source JSON field for field. All 5561 coverage rows match by
per-pair count.

## Whitespace cleaning: measured, not assumed

Scanned every string value in all 98 JSON files for `\t`, `\r` and `\n`:

```
dirty fields: {}
dirty char counts: {}
control/format/line-sep chars: {}
```

**0 fields needed cleaning.** The cleaning step is in the build script and never fired. The
scan also covered Unicode categories Cc, Cf, Zl and Zp, and found none.

## JSON copies

```
copied: 98
files: 98 invalid JSON: [] sha256 mismatches vs source: []
_seg_en present? False
```

All 98 files are byte-identical to `/tmp/gate/prose/`. `_seg_en.json`, `build.py` and
`build_cov.py` were not copied.

## Prose measurement of utils/PROSE-SWEEP-RESUME.md

Adapted splitter, three adaptations, all stated in the script comment:

- split after terminal punctuation even when a markdown `**` marker follows it;
- treat a line ending in `:` as a unit boundary, because a colon before a table or a code
  fence otherwise merges two authored units;
- keep `**bold**` lines and numbered list items, which the stock filter drops.

```
ADAPTED: units 133 mean 8.5 max 19 over25 0 over20 0
```

Stock unadapted snippet, for comparison:

```
units: 109 over 25: 2 max: 28
17 28  Each language contributed 14 pairs, one per complete chapter, so these 7 counts are comparable to ea
44 27  Pick a pair count you can pay for, and run only that many: Shape B is the safer choice for an unatte
```

Both stock readings decompose into units under the limit:

- reading 17 is `Each language contributed 14 pairs, one per complete chapter, so these 7
  counts are comparable to each other:` (18 words) merged across a table with
  `95 of the 98 pairs carry at least one finding.` (10 words);
- reading 44 is `Pick a pair count you can pay for, and run only that many:` (13 words)
  merged across a code fence with `Shape B is the safer choice for an unattended run,
  because it cannot overshoot.` (14 words).

Em dashes: 0. Non-ASCII characters: 0.

## Universals verified, not asserted

| Claim in the record | Check | Result |
|---|---|---|
| every complete chapter has all 7 languages | count langs per chapter | 14 chapters, all 7 |
| every language contributed 14 pairs | count pairs per language | es fr jp pt ru tr vn all 14 |
| no remaining chapter appears in either TSV | membership test on 34 names | 0 in drift, 0 in coverage |
| `reviewed` is TRUE on all 5561 rows | count | 5561 TRUE |
| `en_segment_id` is NA exactly on `unmatched-tr` | cross-tab | 26 of 26, 0 elsewhere |
| `tr_segment_id` is NA exactly on `unmatched-en` | cross-tab | 3 of 3, 0 elsewhere |
| text fields contain quotation marks, so `quote=""` is needed | count | 186 drift rows contain `"` |
| `STEMS` holds all 48 chapters | parse the workflow | 48 |
| the workflow calls `parallel()` on all 336 pairs | read the workflow | `parallel(PAIRS.map(...))` present |
| the workflow has no budget guard | string search for `budget` | 0 occurrences |
| the complete list in the record matches disk | set compare | identical, 14 |
| the remaining list in the record matches STEMS minus disk | set compare | identical, 34 |
