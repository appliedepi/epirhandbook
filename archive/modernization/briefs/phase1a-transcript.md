# Phase 1a transcript: cross-language code and chunk-header checker

Repo: `/home/raw996/ae/epiRhandbook_eng`
File added: `utils/check-language-consistency.R`
Discriminator: `Rscript utils/check-language-consistency.R`

Round 1 SNAPSHOT: `1d94ba0a84b062ba72cb1205a1fb99bbc600caee`
Round 1 SHA_FIXED: `1d94ba0a84b062ba72cb1205a1fb99bbc600caee`
Round 2 SNAPSHOT: `5af803c31028db78ecf93e8cf67776803bf4496d`
Round 2 SHA_FIXED: `723d744e2d72c906ea0701d7312c7ec4f5017610`
Round 2 tree: `05b525733e2d9256a85479502c1793ab263fd714`
Round 2 blob of the fixed file: `75b61607a0ce9a4f85f1153927f6edfbbf9de3c6`

`git stash create` writes a new commit object on every call, so the tree hash and the blob
hash are the stable references. The `air format` Stop hook reformats the file after this
report, so all three references go stale at that point.

Round 2 fixes three extraction defects in the same file. Round 2 changes no other file.
The pre-fix checker is saved to `/tmp/gate/checker-prefix.R`. Its source is
`git show cb1b60a0d36d91924ddc332d906429df7e73602e:utils/check-language-consistency.R`.

Every mutation and every fixture lives outside the repo. No tracked file changed.

- body mutation copy: `/tmp/gate/scratch-body/chapters`
- header mutation copy: `/tmp/gate/scratch-header/chapters`
- engine boundary fixture: `/tmp/gate/fx-engine/chapters`
- fence length fixture: `/tmp/gate/fx-fence/chapters`
- get_data scope fixture: `/tmp/gate/fx-getdata/chapters`

Round 4 changed no code. Round 4 reorganised this transcript and added one section. This
transcript now holds exactly six `###` proof sections, and all six are round 3's versions.
The superseded sections moved to `/tmp/gate/phase1a-transcript-archive.md`.

## round 2: the whole report is byte-identical to round 1

COMMAND: `Rscript utils/check-language-consistency.R`

The run before the three fixes and the run after them were both saved, then compared in full.

```
$ diff /tmp/gate/r2-baseline.txt /tmp/gate/r2-after.txt
(no output)
```

The two reports agree byte for byte. That covers the eight pinned numbers, the `get_data`
axis, every FAIL line and every per-row line.

```
--- get_data(name = ) call sites inside R chunks ---

differs   match
      2     334

--- FAIL: get_data(name = ) call-site counts ---
[differs] cleaning.fr  en=4 tr=3
[differs] grouping.es  en=2 tr=1
```

Both divergent pairs are still `grouping.es` and `cleaning.fr`.

Round 4 moved the section `why no number moved: the three variants were measured on the corpus`
to `/tmp/gate/phase1a-transcript-archive.md`.

## ground-truth run (no mutation)

COMMAND: `Rscript utils/check-language-consistency.R`

```
pairs: 336

--- chunk bodies ---

chunk-count       clean   code-diff
         26         227          83
differing chunks inside code-diff pairs: 260

--- chunk headers ---

count-differs     identical  text-differs
           26           276            34
text-differs split: cosmetic 9 / semantic 25

--- dataset names against appliedepidata::list_data() ---
files scanned whole-file: 384
catalogue entries: 207
name literals found: 1227
dataset names outside catalogue: 8
  benign placeholder "...": 8
  unknown names: 0
```

All eight ground-truth numbers reproduce exactly.

| ground truth | required | observed |
|---|---|---|
| pairs | 336 | 336 |
| body: chunk-count | 26 | 26 |
| body: code-diff | 83 (260 chunks) | 83 (260 chunks) |
| body: clean | 227 | 227 |
| header: identical | 276 | 276 |
| header: count-differs | 26 | 26 |
| header: text-differs | 34 (9 cosmetic, 25 semantic) | 34 (9 cosmetic, 25 semantic) |
| dataset names outside catalogue | 8 | 8 |

The four reader-visible header rows the brief names all land in the semantic set.

```
  basics.tr  chunk 31
    en line 755: ```{r out.width = "100%", fig.align = "center", echo=F}
    tr line 764: ```{r fig.align="center", out.width="100%"}
  survival_analysis.jp  chunk 3
    en line 49: ```{r, echo=F, message=FALSE, warning=FALSE}
    tr line 49: ```{r, message=FALSE, warning=FALSE}
  ggplot_tips.fr  chunk 26
    en line 660: ```{r, eval=T, warning=F}
    tr line 642: ```{r, warning=F, message=F}
  phylogenetic_trees.fr  chunk 2
    en line 53: ```{r, phylogenetic_trees_loading_packages}
    tr line 51: ```{r, phylogenetic_trees_loading_packages, warning=FALSE, message=FALSE}
```

Round 4 moved round 1's five proof sections to `/tmp/gate/phase1a-transcript-archive.md`.
Round 3 re-ran all five, and the round-3 versions are under "six proof sections" below.

## method note: how the two load-bearing normalisation rules were confirmed

This section is informational. It is not a proof and it does not count toward the proof total.

The brief states two body-axis rules and one header-axis sub-class. Each choice was measured, not
assumed. Six normalisation variants ran against the same extracted chunks.

```
keepdelim_carry      chunk-count=26 code-diff=80 clean=230 chunks=262
keepdelim_nocarry    chunk-count=26 code-diff=83 clean=227 chunks=267
nodelim_carry        chunk-count=26 code-diff=80 clean=230 chunks=255
nodelim_nocarry      chunk-count=26 code-diff=83 clean=227 chunks=260   <- ground truth
naive                chunk-count=26 code-diff=83 clean=227 chunks=267
naive_nodelim        chunk-count=26 code-diff=83 clean=227 chunks=260   <- ground truth
```

`nodelim_nocarry` is a per-line scanner that tracks the quote character. `naive_nodelim` is a
plain regex pass. The two are independent implementations. They agree on all four numbers, and
they name the same 83 pairs. `identical()` on the two pair vectors returns TRUE, and `setdiff()`
in both directions returns `character(0)`.

Two further measured choices:

1. Header lines are compared after `trimws()`. Without `trimws()` the counts are 272 identical
   and 38 text-differs. Four pairs differ only by trailing whitespace: `basics.es`,
   `tables_presentation.fr`, `tables_presentation.jp` and `transmission_chains.vn`.
2. The cosmetic sub-class removes all whitespace and rewrites `'` as `"`. That yields 9 cosmetic.
   A stronger canonicalisation that also collapses empty comma fields yields 15, which does not
   match the ground truth.

## method note: `command grep`

Every shell search in this unit used `command grep`. The brief warns that `grep` in this shell is
a function wrapping ugrep, whose output carries no `./` path prefix.

## input-number disagreement, reported not silently fixed

The brief describes `book.chapters` as "112 entries, of which 64 are `part:` title strings in 9
languages". The measured split is different, and the measurement base is `unlist(cfg$book$chapters)`.

```
total unlisted entries : 112   (agrees with the brief)
part title strings     :  63   (7 parts x 9 language keys)  -- the brief says 64
.qmd entries           :  49   (48 under chapters/, plus index.qmd at the repo root)
```

The brief's 48 declared stems and 336 pairs are both correct. The route to them differs. The
brief reaches 48 as 112 minus 64. The checker reaches 48 by keeping the `.qmd` entries and then
keeping the ones under `chapters/`. `index.qmd` sits at the repo root, so the checker skips it and
prints that it did.

## round 2 deviation: the get_data count uses the body normaliser

The brief says the get_data fix MUST NOT reuse the body normaliser. It gives a reason: the
normaliser replaces string-literal contents with `<string>`, which destroys the dataset name.
The fix uses the normaliser anyway. Here is why.

1. The reviewer's finding names two forms, not one. It says text in R comments **or string
   literals** counts as a call site. Comment stripping alone fixes half of it. A call inside a
   string literal would still count.
2. The brief's own pass criterion needs both halves. It requires the fixture to move from 3 to
   1. The fixture's third call sits inside a string literal. Comment stripping alone gives 2.
3. The stated reason does not apply to this script. The script never extracts dataset names
   from chunk text. `get_data_names_in_file()` scans the whole file, prose included, and that
   is deliberate. The file header says so, and the pinned count of 8 depends on it.
4. Nothing is lost. `count_get_data_calls()` needs the call opener `get_data(name =`, which
   sits outside the literal. A masked argument cannot hide a real call.

An intermediate function that strips comments and keeps literals was written first, then
removed. Nothing in production called it, and dead code is worse than no code.

`get_data_names_in_file()` is unchanged. An R comment stripper MUST NOT run over the whole
file, because every markdown heading starts with `#`.

## flagged, not touched

The `get_data(name = )` call-site axis is not one of the eight pinned numbers. It reports 2
divergent pairs out of 336. Both are real and both are reader-visible. Neither is in the file
list for this unit, so nothing was changed.

1. `chapters/grouping.es.qmd`, lines 60 to 62. The whole `eval=F` display chunk is commented
   out. Each of the three lines starts with `#`, including the two fences.

```
#```{r, eval=F}
#linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
#```
```

   `chapters/grouping.qmd` lines 62 to 64 carry the same chunk without the `#`. A Spanish reader
   never sees the load command that an English reader sees.

2. `chapters/cleaning.fr.qmd`, line 136. The `eval=F` display chunk shows the old file-based
   load, and English shows the package load.

```
en chapters/cleaning.qmd    line 130: linelist_raw <- appliedepidata::get_data(name = "case_linelists_linelist_raw")
fr chapters/cleaning.fr.qmd line 136: linelist_raw <- import("linelist.xlsx")
```

   The body axis catches this one as well. `cleaning.fr` is a `code-diff` pair.

---

# Round 3: dataset-name validation at two scopes

Round 3 SNAPSHOT: `5a22148eb8ec646a0780ac04e901831fab3c58ec`
Round 3 SHA_FIXED: `95343968b146e5d755514a03b27d76941a2bc7e8`
Round 3 tree: `7023c184673ffdf453989302a65305eeaa442089`
Round 3 blob of the fixed file: `1804bbf47af944eceb0ca5e353b0c907ae3b23b7`

`git stash create` writes a new commit object on every call. The tree hash and the blob hash
are the stable references. `air format` already ran over the file, and the report did not
change. See the section "air format ran, and the report did not move".

Round 3 changes one file: `utils/check-language-consistency.R`. Round 3 changes no other file.
Every fixture lives outside the repo.

The pre-round-3 checker is `/tmp/gate/prechecker.R`. Its source is
`git show dc9e526db66fc6749ff192bd814f769af1a60e2d:utils/check-language-consistency.R`.
Its md5 is `e71b55f44ad9b5631dbb3463f2d1e180`, and that is the md5 of the round-2 file.

The pre-round-2 checker is `/tmp/gate/checker-prefix.R`. Its source is
`git show cb1b60a0d36d91924ddc332d906429df7e73602e:utils/check-language-consistency.R`.
Its md5 is `0536dca25eb9b1544edd9094d3fd2bff`.

Fixtures:

- body mutation copy: `/tmp/gate/scratch-body/chapters`
- header mutation copy: `/tmp/gate/scratch-header/chapters`
- engine boundary fixture: `/tmp/gate/fx-engine/chapters`
- fence length fixture: `/tmp/gate/fx-fence/chapters`
- get_data scope fixture: `/tmp/gate/fx-getdata/chapters`
- name scope fixture: `/tmp/gate/fx-namescope/chapters`   (new in round 3)

## what round 3 changes

1. `scan_code_line(s, keep_strings)` replaces the body of `strip_code_line()`.
   `strip_code_line(s)` is `scan_code_line(s, keep_strings = FALSE)`. It masks every string
   literal, and axis 1 keeps its old behaviour.
   `strip_comment_tail(s)` is `scan_code_line(s, keep_strings = TRUE)`. It keeps every string
   literal whole, so a dataset name survives.
2. `get_data_names_in_chunks(path)` is new. It reads the `{r}` chunk bodies, removes the R
   comment tails, and extracts every `get_data(name = "X")` literal.
3. `get_data_names_in_file(path)` keeps the whole-file scope. Round 3 does not narrow it.
4. The report prints both scopes, labelled, and it prints the scopes that hold each name
   outside the catalogue.
5. `count_get_data_calls()` still uses `normalise_body()`. Round 3 does not change it.

## every non-name section of the report is byte-identical to round 2

COMMAND: `Rscript utils/check-language-consistency.R`

The pre-change run is `/tmp/gate/r3-baseline.txt`, produced by the round-2 file. The post-change
run is `/tmp/gate/r3-postformat.txt`. Both hold 2974 lines.

```
$ diff <(sed '/--- dataset names/,/^--- FAIL: chunk body/d' /tmp/gate/r3-baseline.txt) \
       <(sed '/--- dataset names/,/^--- FAIL: chunk body/d' /tmp/gate/r3-postformat.txt)
(no output)
```

That comparison deletes the dataset-name block from both files, and nothing else differs. It
covers `pairs: 336`, the body axis, the header axis, the `get_data` call-site axis, every FAIL
block and all 336 per-row result lines.

The whole-report diff touches the dataset-name block only.

```
=== Cross-language code and chunk-header consistency ===
chapters directory: chapters 
declared .qmd entries in _quarto.yml book.chapters: 49 
  under chapters/ and checked: 48 
  outside chapters/ and skipped: 1 (index.qmd) 
languages from babelquarto.languages: 7 (fr, es, vn, jp, pt, tr, ru) 
pairs: 336 
missing files: 0 

--- chunk bodies ---

chunk-count       clean   code-diff 
         26         227          83 
differing chunks inside code-diff pairs: 260 

--- chunk headers ---

count-differs     identical  text-differs 
           26           276            34 
text-differs split: cosmetic 9 / semantic 25 

--- get_data(name = ) call sites inside R chunks ---

differs   match 
      2     334 

--- dataset names against appliedepidata::list_data() ---
files scanned: 384 
catalogue entries: 207 

[whole-file scope] every literal in the file, prose included
  name literals found: 1227 
  dataset names outside catalogue: 8 
    benign placeholder "...": 8 
    unknown names: 0 

[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 1030 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
    unknown names: 0 

```

| pinned number | required | observed |
|---|---|---|
| pairs | 336 | 336 |
| body: chunk-count | 26 | 26 |
| body: code-diff | 83 (260 chunks) | 83 (260 chunks) |
| body: clean | 227 | 227 |
| header: identical | 276 | 276 |
| header: count-differs | 26 | 26 |
| header: text-differs | 34 (9 cosmetic, 25 semantic) | 34 (9 cosmetic, 25 semantic) |
| get_data call sites | differs 2 / match 334 | differs 2 / match 334 |
| whole-file: files scanned | 384 | 384 |
| whole-file: name literals | 1227 | 1227 |
| whole-file: outside catalogue | 8, all "..." | 8, all "..." |
| in-chunk: name literals | 1030 | 1030 |
| in-chunk: outside catalogue | 0 | 0 |

The two divergent `get_data` pairs are still `cleaning.fr` and `grouping.es`.

```
--- FAIL: get_data(name = ) call-site counts ---
[differs] cleaning.fr  en=4 tr=3
[differs] grouping.es  en=2 tr=1

```

## six proof sections

### body-mutation

MUTATION: `/tmp/gate/scratch-body/chapters/age_pyramid.tr.qmd`, line 48, inside an R chunk.

```
48c48
< linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
---
> linelist <- import("data/linelist_cleaned.rds")
```

`diff chapters/age_pyramid.tr.qmd /tmp/gate/scratch-body/chapters/age_pyramid.tr.qmd` reports
that one line and nothing else. The pair `age_pyramid.tr` is `clean` on the body axis and
`identical` on the header axis before the mutation.

RED COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/scratch-body/chapters`

RED:

```
--- chunk bodies ---

chunk-count       clean   code-diff 
         26         226          84 
differing chunks inside code-diff pairs: 261 

--- chunk headers ---

count-differs     identical  text-differs 
           26           276            34 
text-differs split: cosmetic 9 / semantic 25 

--- get_data(name = ) call sites inside R chunks ---
--- dataset names against appliedepidata::list_data() ---
files scanned: 384 
catalogue entries: 207 

[whole-file scope] every literal in the file, prose included
  name literals found: 1226 
  dataset names outside catalogue: 8 
    benign placeholder "...": 8 
    unknown names: 0 

[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 1029 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
    unknown names: 0 

prose-only name literals (whole-file minus in-chunk): 197 

names outside the catalogue, and the scopes that hold each one:
```

FAILED-LABEL: `--- chunk bodies ---`, the `code-diff` cell of `table(results$body)`.

RED names the mutated pair:

```
[code-diff] age_pyramid.tr  chunks en=39 tr=39  differing=1
  age_pyramid.tr  chunk 3  (en line 54, tr line 46)
    en only: linelist<-appliedepidata::get_data(name=<string>)
    tr only: linelist<-import(<string>)
```

`code-diff` moves 83 to 84, `clean` moves 227 to 226, and the differing-chunk total moves 260
to 261. The header axis does not move.

The mutation removes one `get_data(name = "linelist_cleaned_rds")` from an R chunk. Both name
scopes drop by exactly one: whole-file 1227 to 1226, and in-chunk 1030 to 1029. The prose-only
figure stays at 197. That is a causal witness that the in-chunk scope tracks chunk code.

REVERT: not needed. The mutation lives in `/tmp/gate/scratch-body/chapters`, outside the repo.

GREEN COMMAND: `Rscript utils/check-language-consistency.R`

GREEN:

```
--- chunk bodies ---

chunk-count       clean   code-diff 
         26         227          83 
differing chunks inside code-diff pairs: 260 

--- chunk headers ---

count-differs     identical  text-differs 
           26           276            34 
text-differs split: cosmetic 9 / semantic 25 

--- get_data(name = ) call sites inside R chunks ---
--- dataset names against appliedepidata::list_data() ---
files scanned: 384 
catalogue entries: 207 

[whole-file scope] every literal in the file, prose included
  name literals found: 1227 
  dataset names outside catalogue: 8 
    benign placeholder "...": 8 
    unknown names: 0 

[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 1030 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
    unknown names: 0 

prose-only name literals (whole-file minus in-chunk): 197 

names outside the catalogue, and the scopes that hold each one:
```

The body FAIL block of the GREEN run does not name `age_pyramid.tr`.

```
$ grep -c 'age_pyramid.tr' /tmp/gate/r3-postformat.txt
0
```

That count is the per-row results line, and nothing else. The mutated pair is absent from every
FAIL block.

### header-mutation

MUTATION: `/tmp/gate/scratch-header/chapters/regression.ru.qmd`, line 65, a chunk header.

```
65c65
< ```{r, message=FALSE, echo=F}
---
> ```{r, message=FALSE}
```

`diff chapters/regression.ru.qmd /tmp/gate/scratch-header/chapters/regression.ru.qmd` reports
that one line and nothing else. The pair `regression.ru` is `identical` on the header axis and
`clean` on the body axis before the mutation.

RED COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/scratch-header/chapters`

RED:

```
--- chunk bodies ---

chunk-count       clean   code-diff 
         26         227          83 
differing chunks inside code-diff pairs: 260 

--- chunk headers ---

count-differs     identical  text-differs 
           26           275            35 
text-differs split: cosmetic 9 / semantic 26 

--- get_data(name = ) call sites inside R chunks ---
--- dataset names against appliedepidata::list_data() ---
files scanned: 384 
catalogue entries: 207 

[whole-file scope] every literal in the file, prose included
  name literals found: 1227 
  dataset names outside catalogue: 8 
    benign placeholder "...": 8 
    unknown names: 0 

[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 1030 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
    unknown names: 0 

prose-only name literals (whole-file minus in-chunk): 197 

names outside the catalogue, and the scopes that hold each one:
```

FAILED-LABEL: `--- chunk headers ---`, the `text-differs` cell of `table(results$header)`, and
the `semantic` half of the `text-differs split` line.

RED names the mutated pair:

```
[text-differs/semantic] regression.ru  headers en=41 tr=41  differing=1
  regression.ru  chunk 4
    en line 65: ```{r, message=FALSE, echo=F}
    tr line 65: ```{r, message=FALSE}
```

`text-differs` moves 34 to 35, and the new row is semantic, not cosmetic. The body axis does not
move. A header change touches no dataset name, so both name scopes hold at 1227 and 1030.

REVERT: not needed. The mutation lives in `/tmp/gate/scratch-header/chapters`, outside the repo.

GREEN COMMAND: `Rscript utils/check-language-consistency.R`

GREEN: the header block of the GREEN run reads `count-differs 26, identical 276,
text-differs 34`, and `cosmetic 9 / semantic 25`. The raw block is quoted under `body-mutation`
GREEN above, in the same run file `/tmp/gate/r3-postformat.txt`.

The header FAIL block of the GREEN run does not name `regression.ru`.

```
$ grep -c 'regression.ru' /tmp/gate/r3-postformat.txt
0
```

That count is the per-row results line, and nothing else.

### fence-engine-boundary

DEFECT: the pre-round-2 `FENCE_OPEN` is `` "^[ \t]*`{3,}\\{r" ``. It has no engine boundary, so
it opens a chunk on `{rust}` and on `{ruby}`.

FIX: `` FENCE_OPEN <- "^[ \t]*`{3,}\\{r[},[:space:]]" ``. The engine name r must end at `}`, at
a comma, or at whitespace. Round 3 does not change this line.

FIXTURE: `/tmp/gate/fx-engine/chapters`. Two files hold three R chunks and two non-R chunks.
The three R chunk headers cover the three legal boundary characters. `grouping.fr.qmd` differs
from `grouping.qmd` in the rust body and the ruby body only.

RED COMMAND: `Rscript /tmp/gate/checker-prefix.R /tmp/gate/fx-engine/chapters`

RED:

```
--- chunk bodies ---

code-diff 
        1 
differing chunks inside code-diff pairs: 2 

--- chunk headers ---

identical 
        1 
text-differs split: cosmetic 0 / semantic 0 

--- get_data(name = ) call sites inside R chunks ---

match 
    1 

--- dataset names against appliedepidata::list_data() ---
files scanned whole-file: 2 
catalogue entries: 207 
name literals found: 0 
dataset names outside catalogue: 0 
  benign placeholder "...": 0 
  unknown names: 0 

--- FAIL: chunk body divergences ---
[code-diff] grouping.fr  chunks en=5 tr=5  differing=2

  per differing chunk (normalised lines):
  grouping.fr  chunk 4  (en line 15, tr line 15)
    en only: leta=1;
    tr only: letzz=9;
  grouping.fr  chunk 5  (en line 19, tr line 19)
    en only: a=1
    tr only: zz=9

--- FAIL: chunk header divergences ---
(none)

--- FAIL: get_data(name = ) call-site counts ---
(none)

--- full per-row results ---
  chapter lang chunks_en chunks_tr      body chunks_differing    header
 grouping   fr         5         5 code-diff                2 identical
 header_kind headers_differing get_data_en get_data_tr get_data
                             0           0           0    match
```

FAILED-LABEL: `--- FAIL: chunk body divergences ---`, the `[code-diff] grouping.fr` row.

The pre-round-2 checker counts 5 R chunks in a file that holds 3. It reads the Rust body and the
Ruby body as R code, and it reports two false divergences.

GREEN COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/fx-engine/chapters`

GREEN:

```
--- chunk bodies ---

clean 
    1 
differing chunks inside code-diff pairs: 0 

--- chunk headers ---

identical 
        1 
text-differs split: cosmetic 0 / semantic 0 

--- get_data(name = ) call sites inside R chunks ---

match 
    1 

--- dataset names against appliedepidata::list_data() ---
files scanned: 2 
catalogue entries: 207 

[whole-file scope] every literal in the file, prose included
  name literals found: 0 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
    unknown names: 0 

[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 0 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
    unknown names: 0 

prose-only name literals (whole-file minus in-chunk): 0 

names outside the catalogue, and the scopes that hold each one:
  whole-file+in-chunk: the name sits in R chunk code. Treat it as live.
  whole-file only: the name sits in prose, or in an R comment.
  in-chunk only: the chunk scope reads it and the whole-file scope does not.
(none)

--- FAIL: chunk body divergences ---
(none)

--- FAIL: chunk header divergences ---
(none)

--- FAIL: get_data(name = ) call-site counts ---
(none)

--- full per-row results ---
  chapter lang chunks_en chunks_tr  body chunks_differing    header header_kind
 grouping   fr         3         3 clean                0 identical            
 headers_differing get_data_en get_data_tr get_data
                 0           0           0    match
```

The chunk count moves from 5 to 3, and the two false divergences are gone. The three R chunks
still open, so `{r}`, `{r,` and `{r ` all still work.

### fence-close-length

DEFECT: the pre-round-2 closing fence is `` "^[ \t]*`{3,}[ \t]*$" ``. It is a fixed pattern. A
chunk opened with four backticks therefore closes on a three-backtick line, and the rest of the
chunk becomes prose.

FIX: `read_chunks()` reads the opening backtick count with `fence_length()`, then builds the
closing pattern with `fence_close(n)`, which is `` sprintf("^[ \t]*`{%d,}[ \t]*$", n) ``.
Round 3 does not change these two functions.

FIXTURE: `/tmp/gate/fx-fence/chapters`. Each file holds one four-backtick R chunk. The chunk
contains a three-backtick line, and it contains one line after that line. `grouping.qmd` reads
`y <- 2` and `grouping.fr.qmd` reads `y <- 99`.

RED COMMAND: `Rscript /tmp/gate/checker-prefix.R /tmp/gate/fx-fence/chapters`

RED:

```
--- chunk bodies ---

clean 
    1 
differing chunks inside code-diff pairs: 0 

--- chunk headers ---

identical 
        1 
text-differs split: cosmetic 0 / semantic 0 

--- get_data(name = ) call sites inside R chunks ---

match 
    1 

--- dataset names against appliedepidata::list_data() ---
files scanned whole-file: 2 
catalogue entries: 207 
name literals found: 0 
dataset names outside catalogue: 0 
  benign placeholder "...": 0 
  unknown names: 0 

--- FAIL: chunk body divergences ---
(none)

--- FAIL: chunk header divergences ---
(none)

--- FAIL: get_data(name = ) call-site counts ---
(none)

--- full per-row results ---
  chapter lang chunks_en chunks_tr  body chunks_differing    header header_kind
 grouping   fr         1         1 clean                0 identical            
 headers_differing get_data_en get_data_tr get_data
                 0           0           0    match
```

FAILED-LABEL: `--- chunk bodies ---`, the `clean` cell, and `differing chunks inside code-diff
pairs: 0`.

The pre-round-2 checker truncates both chunks at the three-backtick line. Each body holds one
line, `x <- 1`. The checker calls the pair clean. The real divergence, `y <- 2` against
`y <- 99`, is invisible.

GREEN COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/fx-fence/chapters`

GREEN:

```
--- chunk bodies ---

code-diff 
        1 
differing chunks inside code-diff pairs: 1 

--- chunk headers ---

identical 
        1 
text-differs split: cosmetic 0 / semantic 0 

--- get_data(name = ) call sites inside R chunks ---

match 
    1 

--- dataset names against appliedepidata::list_data() ---
files scanned: 2 
catalogue entries: 207 

[whole-file scope] every literal in the file, prose included
  name literals found: 0 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
    unknown names: 0 

[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 0 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
    unknown names: 0 

prose-only name literals (whole-file minus in-chunk): 0 

names outside the catalogue, and the scopes that hold each one:
  whole-file+in-chunk: the name sits in R chunk code. Treat it as live.
  whole-file only: the name sits in prose, or in an R comment.
  in-chunk only: the chunk scope reads it and the whole-file scope does not.
(none)

--- FAIL: chunk body divergences ---
[code-diff] grouping.fr  chunks en=1 tr=1  differing=1

  per differing chunk (normalised lines):
  grouping.fr  chunk 1  (en line 3, tr line 3)
    en only: y<-2
    tr only: y<-99

--- FAIL: chunk header divergences ---
(none)

--- FAIL: get_data(name = ) call-site counts ---
(none)

--- full per-row results ---
  chapter lang chunks_en chunks_tr      body chunks_differing    header
 grouping   fr         1         1 code-diff                1 identical
 header_kind headers_differing get_data_en get_data_tr get_data
                             0           0           0    match
```

The differing-chunk count moves from 0 to 1. The post-fix checker keeps the chunk whole and
names the divergence.

### get-data-comment-scope

DEFECT: the pre-round-2 `count_get_data_calls()` runs the call regex over raw chunk text. A call
in an R comment counts as a call site. A call inside a string literal counts as a call site.

FIX: the count runs over `normalise_body()`, the axis 1 normaliser. Normalisation drops the R
comment tail and masks every string literal. Both non-executable forms disappear, and the count
keeps every real call. Round 3 does not change `count_get_data_calls()`.

FIXTURE: `/tmp/gate/fx-getdata/chapters`. The English chunk holds one real call, one commented
call and one call inside a string literal. The French chunk holds the real call only.

`grouping.qmd`:

````
# Fixture: get_data scope

```{r}
d <- appliedepidata::get_data(name = "x")
# appliedepidata::get_data(name = "y")
s <- 'appliedepidata::get_data(name = "z")'
```
````

RED COMMAND: `Rscript /tmp/gate/checker-prefix.R /tmp/gate/fx-getdata/chapters`

RED:

```
--- get_data(name = ) call sites inside R chunks ---

differs 
      1 

--- dataset names against appliedepidata::list_data() ---
files scanned whole-file: 2 
catalogue entries: 207 
name literals found: 4 
dataset names outside catalogue: 4 
  benign placeholder "...": 0 
  unknown names: 4 
                                          file name       status
    /tmp/gate/fx-getdata/chapters/grouping.qmd    x unknown-name
    /tmp/gate/fx-getdata/chapters/grouping.qmd    y unknown-name
    /tmp/gate/fx-getdata/chapters/grouping.qmd    z unknown-name
 /tmp/gate/fx-getdata/chapters/grouping.fr.qmd    x unknown-name

--- FAIL: chunk body divergences ---
[code-diff] grouping.fr  chunks en=1 tr=1  differing=1

  per differing chunk (normalised lines):
  grouping.fr  chunk 1  (en line 3, tr line 3)
    en only: s<-<string>

--- FAIL: chunk header divergences ---
(none)

--- FAIL: get_data(name = ) call-site counts ---
[differs] grouping.fr  en=3 tr=1

--- full per-row results ---
  chapter lang chunks_en chunks_tr      body chunks_differing    header
 grouping   fr         1         1 code-diff                1 identical
 header_kind headers_differing get_data_en get_data_tr get_data
                             0           3           1  differs
```

FAILED-LABEL: `--- FAIL: get_data(name = ) call-site counts ---`, the row
`[differs] grouping.fr  en=3 tr=1`.

The pre-round-2 checker counts 3 call sites in the English chunk. Only 1 of the 3 is executable
code.

GREEN COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/fx-getdata/chapters`

GREEN:

```
--- get_data(name = ) call sites inside R chunks ---

match 
    1 

--- dataset names against appliedepidata::list_data() ---
files scanned: 2 
catalogue entries: 207 

[whole-file scope] every literal in the file, prose included
  name literals found: 4 
  dataset names outside catalogue: 4 
    benign placeholder "...": 0 
    unknown names: 4 

[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 3 
  dataset names outside catalogue: 3 
    benign placeholder "...": 0 
    unknown names: 3 

prose-only name literals (whole-file minus in-chunk): 1 

names outside the catalogue, and the scopes that hold each one:
  whole-file+in-chunk: the name sits in R chunk code. Treat it as live.
  whole-file only: the name sits in prose, or in an R comment.
  in-chunk only: the chunk scope reads it and the whole-file scope does not.
                                          file name       status
    /tmp/gate/fx-getdata/chapters/grouping.qmd    x unknown-name
    /tmp/gate/fx-getdata/chapters/grouping.qmd    y unknown-name
    /tmp/gate/fx-getdata/chapters/grouping.qmd    z unknown-name
 /tmp/gate/fx-getdata/chapters/grouping.fr.qmd    x unknown-name
               scope
 whole-file+in-chunk
     whole-file only
 whole-file+in-chunk
 whole-file+in-chunk

--- FAIL: chunk body divergences ---
[code-diff] grouping.fr  chunks en=1 tr=1  differing=1

  per differing chunk (normalised lines):
  grouping.fr  chunk 1  (en line 3, tr line 3)
    en only: s<-<string>

--- FAIL: chunk header divergences ---
(none)

--- FAIL: get_data(name = ) call-site counts ---
(none)

--- full per-row results ---
  chapter lang chunks_en chunks_tr      body chunks_differing    header
 grouping   fr         1         1 code-diff                1 identical
 header_kind headers_differing get_data_en get_data_tr get_data
                             0           1           1    match
```

The call-site count moves from 3 to 1, and the pair moves from `differs` to `match`.

This GREEN also shows the two name scopes on the same fixture, and the scopes tell the three
names apart.

| name | where it sits | scope reported |
|---|---|---|
| x | executable chunk code | whole-file+in-chunk |
| y | R comment inside the chunk | whole-file only |
| z | inside a string literal | whole-file+in-chunk |

The `y` row is the load-bearing one. The in-chunk scope removes the R comment tail, so a
commented-out name reports as prose only. The `z` row records a limit of the in-chunk scope at
its real size: the scope keeps string literal contents, because masking the literal would
destroy the dataset name, so a name inside a string literal reads as in-chunk. Axis 3a does not
have this limit, because it masks the literals and needs no name.

### name-scope-split

This section is new in round 3. The corpus holds no dataset name outside the catalogue except
the placeholder `"..."`, so the corpus cannot exercise a split. The fixture supplies one.

FIXTURE: `/tmp/gate/fx-namescope/chapters`. Two names sit outside the catalogue. One sits in a
prose sentence only. One sits inside a live `{r}` chunk.

`grouping.qmd`:

````
# Fixture: name scope split

To load the grouped extract, run `appliedepidata::get_data(name = "zz_prose_only")`
in your console. That sentence is prose. No chunk runs it.

```{r}
d <- appliedepidata::get_data(name = "zz_in_chunk")
```
````

`grouping.fr.qmd`:

````
# Fixture: name scope split (fr)

```{r}
d <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```
````

The catalogue membership of the three names was measured, not assumed.

```
$ Rscript -e 'x <- appliedepidata::list_data()$name; ...'
catalogue n = 207 
linelist_cleaned_rds in catalogue: TRUE 
zz_prose_only in catalogue: FALSE 
zz_in_chunk in catalogue: FALSE 
```

RED COMMAND: `Rscript /tmp/gate/prechecker.R /tmp/gate/fx-namescope/chapters`

`/tmp/gate/prechecker.R` is the pre-round-3 checker, md5 `e71b55f44ad9b5631dbb3463f2d1e180`.

RED:

```
--- dataset names against appliedepidata::list_data() ---
files scanned whole-file: 2 
catalogue entries: 207 
name literals found: 3 
dataset names outside catalogue: 2 
  benign placeholder "...": 0 
  unknown names: 2 
                                         file          name       status
 /tmp/gate/fx-namescope/chapters/grouping.qmd zz_prose_only unknown-name
 /tmp/gate/fx-namescope/chapters/grouping.qmd   zz_in_chunk unknown-name

--- FAIL: chunk body divergences ---
```

FAILED-LABEL: `--- dataset names against appliedepidata::list_data() ---`, the line
`name literals found: 3` and the line `dataset names outside catalogue: 2`.

The pre-round-3 checker reports one count for the two names. It prints `3` literals and `2`
outside the catalogue. The printed table carries `file`, `name` and `status` and no scope. A
reader cannot tell that `zz_in_chunk` runs and `zz_prose_only` does not.

GREEN COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/fx-namescope/chapters`

GREEN:

```
--- dataset names against appliedepidata::list_data() ---
files scanned: 2 
catalogue entries: 207 

[whole-file scope] every literal in the file, prose included
  name literals found: 3 
  dataset names outside catalogue: 2 
    benign placeholder "...": 0 
    unknown names: 2 

[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 2 
  dataset names outside catalogue: 1 
    benign placeholder "...": 0 
    unknown names: 1 

prose-only name literals (whole-file minus in-chunk): 1 

names outside the catalogue, and the scopes that hold each one:
  whole-file+in-chunk: the name sits in R chunk code. Treat it as live.
  whole-file only: the name sits in prose, or in an R comment.
  in-chunk only: the chunk scope reads it and the whole-file scope does not.
                                         file          name       status
 /tmp/gate/fx-namescope/chapters/grouping.qmd zz_prose_only unknown-name
 /tmp/gate/fx-namescope/chapters/grouping.qmd   zz_in_chunk unknown-name
               scope
     whole-file only
 whole-file+in-chunk

--- FAIL: chunk body divergences ---
```

The post-change checker reports whole-file 2 outside the catalogue and in-chunk 1 outside the
catalogue. The scope column names which one is executable.

| name | scope column | meaning |
|---|---|---|
| zz_prose_only | whole-file only | prose, and it does not run |
| zz_in_chunk | whole-file+in-chunk | live R chunk code |

#### source mutation A: the in-chunk scope must keep the string literals

The two fixture proofs above compare two checker files. This mutation and the next one change
the round-3 source itself, so the production path is proven reachable.

MUTATION: `strip_comment_tail()`, `keep_strings = TRUE` becomes `keep_strings = FALSE`.

```
@@ -183,3 +183,3 @@ strip_code_line <- function(s) {
-  scan_code_line(s, keep_strings = TRUE)
+  scan_code_line(s, keep_strings = FALSE)
```

FAILED-LABEL: `[in-chunk scope] literals inside {r} chunks, R comment tails removed`, the line
`name literals found:`.

RED COMMAND: `Rscript utils/check-language-consistency.R`

RED:

```
[whole-file scope] every literal in the file, prose included
  name literals found: 1227 
  dataset names outside catalogue: 8 
    benign placeholder "...": 8 
    unknown names: 0 

[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 0 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
    unknown names: 0 

prose-only name literals (whole-file minus in-chunk): 1227 
```

The in-chunk literal count collapses from 1030 to 0. Masking the literals destroys every
dataset name, and the pinned 1030 disappears.

REVERT: `cp /tmp/gate/r3-keep.R utils/check-language-consistency.R`

GREEN:

```
[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 1030 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
```

#### source mutation B: the in-chunk scope must read chunks, not the whole file

MUTATION: `get_data_names_in_chunks()` reads the whole file instead of the chunk bodies.

```
-  bodies <- read_chunks(path)$bodies
+  bodies <- list(read_lines_utf8(path))
```

FAILED-LABEL: `[in-chunk scope] literals inside {r} chunks, R comment tails removed`, the lines
`name literals found:` and `dataset names outside catalogue:`.

RED COMMAND: `Rscript utils/check-language-consistency.R`

RED:

```
[whole-file scope] every literal in the file, prose included
  name literals found: 1227 
  dataset names outside catalogue: 8 
    benign placeholder "...": 8 
    unknown names: 0 

[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 1226 
  dataset names outside catalogue: 8 
    benign placeholder "...": 8 
    unknown names: 0 

prose-only name literals (whole-file minus in-chunk): 1 
```

Both in-chunk numbers move. The literal count moves from 1030 to 1226, and the outside-catalogue
count moves from 0 to 8. The eight prose placeholders leak into the in-chunk scope, which is the
exact collapse the two scopes exist to prevent.

REVERT: `cp /tmp/gate/r3-keep.R utils/check-language-consistency.R`

GREEN COMMAND: `Rscript utils/check-language-consistency.R`

GREEN: the full report after the revert is byte-identical to the report before mutation A.

```
$ md5sum utils/check-language-consistency.R /tmp/gate/r3-keep.R
e1bab53e0a269ebd8d7f8549d133934f  utils/check-language-consistency.R
e1bab53e0a269ebd8d7f8549d133934f  /tmp/gate/r3-keep.R

$ diff /tmp/gate/r3-postformat.txt /tmp/gate/r3-green.txt
(no output)

$ git status --porcelain
A  utils/check-language-consistency.R
```

```
[in-chunk scope] literals inside {r} chunks, R comment tails removed
  name literals found: 1030 
  dataset names outside catalogue: 0 
    benign placeholder "...": 0 
    unknown names: 0 

prose-only name literals (whole-file minus in-chunk): 197 
```

## reviewer finding refuted: raw grep results

The round-3 review raised a second finding, and that finding is wrong. It said that two GREEN
results in this transcript are impossible:

> `grep -c 'age_pyramid.tr'` and `grep -c 'regression.ru'` both return `0`, and the report's
> per-row table contains each pair.

Round 4 re-ran the commands against `/tmp/gate/r3-postformat.txt`. The output below is the
round-4 run, not a transcription of an earlier run.

```
$ command grep -c 'age_pyramid.tr' /tmp/gate/r3-postformat.txt
0
$ command grep -c 'regression.ru' /tmp/gate/r3-postformat.txt
0
$ command grep -oE '[a-z_]+\.(es|fr|jp|pt|ru|tr|vn)' /tmp/gate/r3-postformat.txt | sort -u | wc -l
120
```

Both zeros are correct. Two independent facts make them correct.

1. The report writes a dotted token in two places, and in no other place. The first place is the
   three FAIL blocks, which name the divergent pairs only. The second place is the file-path
   column of the outside-catalogue table, which holds 8 rows, all of them `data_used`.
   `age_pyramid.tr` and `regression.ru` are clean on all three axes in the GREEN run, so no FAIL
   block names them. Neither file holds a name outside the catalogue, so that table omits them
   too.
2. The per-row table writes no dotted token at all. It prints `chapter` and `lang` as two
   columns. All 336 pairs sit in that table. A search for `age_pyramid.tr` cannot match a row
   that reads `age_pyramid   tr`.

Both pairs are present in the per-row table, in column form.

```
$ command grep -nE '^ *(regression|age_pyramid) +(ru|tr) ' /tmp/gate/r3-postformat.txt
2448:           regression   tr        41        41       clean                0
2449:           regression   ru        41        41       clean                0
2532:          age_pyramid   tr        39        39       clean                0
2533:          age_pyramid   ru        39        39       clean                0
```

Both facts were measured, not assumed. The probe is `/tmp/gate/r4-probe-dotted.R`. It parses
`/tmp/gate/r3-postformat.txt` and loads no checker code. The per-row table holds 336 rows in two
column blocks, because `print.data.frame` wraps the columns.

COMMAND: `Rscript /tmp/gate/r4-probe-dotted.R`

```
per-row block 1 lines            : 2317 to 2652 
per-row block 2 lines            : 2654 to 2989 
rows                             : 336 
distinct pairs                   : 336 
pairs divergent on >= 1 axis     : 119 
distinct dotted tokens in report : 120 
dotted tokens NOT pair names     : data.fr 
divergent pairs absent from tokens:  
pair-name tokens NOT divergent   :  
age_pyramid.tr   body=clean      header=identical    get_data=match
regression.ru    body=clean      header=identical    get_data=match
source of the token data.fr:
  [code-diff] missing_data.fr  chunks en=42 tr=42  differing=6
      en only: case_table<-data.frame(
      tr only: caso_tabela<-data.frame(

lines holding a dotted token, by report section:
     7  --- dataset names against appliedepidata::list_data() ---
   387  --- FAIL: chunk body divergences ---
   188  --- FAIL: chunk header divergences ---
     2  --- FAIL: get_data(name = ) call-site counts ---
last line holding a dotted token : 2313 
per-row table starts at line     : 2315 
dotted tokens inside the per-row table: 0 
```

Read the section table first. It lists every report section that holds a dotted token. Three of
the four are FAIL blocks. The fourth is the outside-catalogue table, and its 7 lines are file
paths of the form `chapters/data_used.fr.qmd`. The last dotted token in the whole report sits at
line 2313, and the per-row table starts at line 2315. The per-row table therefore holds none.

The 120 tokens split into 119 plus 1. The 119 are exactly the pairs that diverge on the body
axis, the header axis or the `get_data` axis. Neither set difference holds a member, in either
direction. The 120th token is `data.fr`, and it is not a pair name. It comes from the quoted
code line `case_table<-data.frame(` inside the `missing_data.fr` FAIL block.

The count of divergent pairs is therefore 119, not 120. The command output `120` is correct.
The reading "120 divergent pairs" is off by one, because the regex also matches `data.frame(`.

One sentence inside the two proof sections is misleading, and it produced the finding. Both
`### body-mutation` and `### header-mutation` say "That count is the per-row results line, and
nothing else" directly after the grep. A count of `0` counts nothing, so that sentence reads as
a claim that the pair appears once. The pair does not appear at all in the dotted form, because
the per-row table uses two columns. Round 4 leaves both sections at their round-3 text, so every
pinned number stays pinned. Read this section together with them.

The two zeros MUST stay `0`. A later round MUST NOT change them to satisfy the finding.

## method note: the two scope numbers were measured independently

This section is informational. It is not a proof and it does not count toward the proof total.

The brief supplies 1227/8 for the whole-file scope and 1030/0 for the in-chunk scope. Round 3
re-measured both with a probe that does not load the checker. The probe re-implements the two
scopes from scratch, including its own comment stripper. It is at
`/tmp/gate/r3-probe-scope.R`.

COMMAND: `Rscript /tmp/gate/r3-probe-scope.R`

```
files scanned                : 384 
catalogue entries            : 207 
WHOLE-FILE literals          : 1227 
WHOLE-FILE outside catalogue : 8 
  the outside names          : ... 
IN-CHUNK  literals           : 1030 
IN-CHUNK  outside catalogue  : 0 
prose-only literals (whole - in-chunk): 197 
```

The probe agrees with the brief on all five numbers, and it agrees with the checker.

## method note: the scan_code_line refactor changed no axis 1 behaviour

This section is informational. It is not a proof and it does not count toward the proof total.

Round 3 rewrote `strip_code_line()` as `scan_code_line(s, keep_strings = FALSE)`. That is a
refactor of a reviewed function, so it was measured. The probe holds the pre-round-3 body of
`strip_code_line()` verbatim, and it compares the two on every chunk body line in the corpus.
The probe is at `/tmp/gate/r3-probe-strip.R`.

COMMAND: `Rscript /tmp/gate/r3-probe-strip.R`

```
chunk body lines compared: 97145 
identical(old, new): TRUE 
differing lines: 0 

edge cases: identical(old, new) = TRUE 

  raw: x <- 1  # a comment                        | strip_code_line: x <- 1                           | strip_comment_tail: x <- 1  
  raw: s <- "a # not a comment"                   | strip_code_line: s <- <string>                    | strip_comment_tail: s <- "a # not a comment"
  raw: s <- 'single # quoted'                     | strip_code_line: s <- <string>                    | strip_comment_tail: s <- 'single # quoted'
  raw: s <- "escaped \" quote" # tail             | strip_code_line: s <- <string>                    | strip_comment_tail: s <- "escaped \" quote" 
  raw: s <- "unterminated                         | strip_code_line: s <- <string>                    | strip_comment_tail: s <- "unterminated
  raw: s <- "trailing backslash at end \          | strip_code_line: s <- <string>                    | strip_comment_tail: s <- "trailing backslash at end \
  raw: # whole line comment                       | strip_code_line:                                  | strip_comment_tail: 
  raw:                                            | strip_code_line:                                  | strip_comment_tail: 
  raw: get_data(name = "x") # get_data(name = "y") | strip_code_line: get_data(name = <string>)        | strip_comment_tail: get_data(name = "x") 
  raw: s <- "a\\" ; y <- 2                        | strip_code_line: s <- <string> ; y <- 2           | strip_comment_tail: s <- "a\\" ; y <- 2
```

The two definitions agree on all 97145 chunk body lines in the corpus, and on 10 hand-built edge
cases. The edge cases cover an escaped quote, an unterminated string, a trailing backslash at
end of line, a `#` inside a single-quoted string and a `#` inside a double-quoted string.

## air format ran, and the report did not move

`air` is installed at `/usr/local/bin/air`. Round 3 ran `air format
utils/check-language-consistency.R` before it staged the file, so the Stop hook has nothing left
to change.

```
$ diff /tmp/gate/r3-final.txt /tmp/gate/r3-postformat.txt
(no output)
```

`/tmp/gate/r3-final.txt` is the run before `air format`. `/tmp/gate/r3-postformat.txt` is the run
after it. The two reports agree byte for byte.

## round 3 scope: one file, and the working tree is clean beside it

```
$ git status --porcelain
A  utils/check-language-consistency.R
```

No `.qmd` file changed. No `_quarto.yml` change. Every fixture and every probe lives under
`/tmp/gate/`, outside the repo.
