# Archive: superseded sections of the phase 1a transcript

Round 4 moved the sections below out of `/tmp/gate/phase1a-transcript.md`. Round 4 deleted
nothing. This file is the record of how rounds 1 and 2 were settled.

Every heading in this file is at level 2, written `##`. This file holds no level-3 heading, so
no parser counts a section here as a proof section of the current round.

The first section is round 2's explanation of why no pinned number moved. The five sections
after it are round 1's proof sections. Round 3 re-ran all five against the round-3 checker.
The round-3 versions live in `/tmp/gate/phase1a-transcript.md`, and they supersede these.

## why no number moved: the three variants were measured on the corpus

The `get_data` call-site count has three candidate scopes. Each one was run over the same
384 files.

| scope | total call sites | files where it disagrees with the others |
|---|---|---|
| raw chunk text (pre-fix) | 1030 | 0 |
| R comments removed | 1030 | 0 |
| normalised chunk code (post-fix) | 1030 | 0 |

The corpus holds no live instance of the defect. The 4+ backtick fence is also absent.

```
backtick run lengths over all 27866 fence lines in chapters/ : 3 -> 27866
character after {r over all 13652 openings : space 2856, comma 6224, } 4572
old FENCE_OPEN matches 13652, new FENCE_OPEN matches 13652, differing lines 0
```

## body-mutation

MUTATION: `/tmp/gate/scratch-body/chapters/age_pyramid.tr.qmd`, line 48, inside an R chunk.

```
48c48
< linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
---
> linelist <- import("data/linelist_cleaned.rds")
```

`diff -r chapters /tmp/gate/scratch-body/chapters` reports that one line and nothing else.
The pair `age_pyramid.tr` is `clean` on the body axis and `identical` on the header axis before
the mutation.

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
```

RED names the mutated pair:

```
[code-diff] age_pyramid.tr  chunks en=39 tr=39  differing=1
  age_pyramid.tr  chunk 3  (en line 54, tr line 46)
    en only: linelist<-appliedepidata::get_data(name=<string>)
    tr only: linelist<-import(<string>)
```

`code-diff` moves 83 to 84. The header axis does not move: `identical` stays 276,
`count-differs` stays 26, `text-differs` stays 34, cosmetic stays 9 and semantic stays 25.

The `get_data(name = )` call-site axis moves from 2 divergent pairs to 3, and names
`[differs] age_pyramid.tr  en=6 tr=5`. That is the same mutation seen on a third axis, not a
header effect.

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
```

The body FAIL block of the GREEN run does not name `age_pyramid.tr`.

ROUND 2 RE-RUN: the fixed checker was run against the same mutated copy.

COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/scratch-body/chapters`

```
--- chunk bodies ---

chunk-count       clean   code-diff
         26         226          84
differing chunks inside code-diff pairs: 261

--- chunk headers ---

count-differs     identical  text-differs
           26           276            34
text-differs split: cosmetic 9 / semantic 25
```

```
[code-diff] age_pyramid.tr  chunks en=39 tr=39  differing=1
  age_pyramid.tr  chunk 3  (en line 54, tr line 46)
    en only: linelist<-appliedepidata::get_data(name=<string>)
```

```
--- FAIL: get_data(name = ) call-site counts ---
[differs] cleaning.fr  en=4 tr=3
[differs] grouping.es  en=2 tr=1
[differs] age_pyramid.tr  en=6 tr=5

differs   match
      3     333
```

The red numbers match round 1 exactly. The proof still holds.

## header-mutation

MUTATION: `/tmp/gate/scratch-header/chapters/regression.ru.qmd`, line 65, a chunk header.

```
65c65
< ```{r, message=FALSE, echo=F}
---
> ```{r, message=FALSE}
```

`diff -r chapters /tmp/gate/scratch-header/chapters` reports that one line and nothing else.
The pair `regression.ru` is `identical` on the header axis and `clean` on the body axis before
the mutation.

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
```

RED names the mutated pair:

```
[text-differs/semantic] regression.ru  headers en=41 tr=41  differing=1
  regression.ru  chunk 4
    en line 65: ```{r, message=FALSE, echo=F}
    tr line 65: ```{r, message=FALSE}
```

`text-differs` moves 34 to 35, and the new row is semantic, not cosmetic. The body axis does not
move: `chunk-count` stays 26, `clean` stays 227, `code-diff` stays 83, and the differing-chunk
total stays 260. The `get_data(name = )` axis stays at 2 divergent pairs.

REVERT: not needed. The mutation lives in `/tmp/gate/scratch-header/chapters`, outside the repo.

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
```

The header FAIL block of the GREEN run does not name `regression.ru`.

ROUND 2 RE-RUN: the fixed checker was run against the same mutated copy.

COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/scratch-header/chapters`

```
--- chunk bodies ---

chunk-count       clean   code-diff
         26         227          83
differing chunks inside code-diff pairs: 260

--- chunk headers ---

count-differs     identical  text-differs
           26           275            35
text-differs split: cosmetic 9 / semantic 26
```

```
[text-differs/semantic] regression.ru  headers en=41 tr=41  differing=1
  regression.ru  chunk 4
    en line 65: ```{r, message=FALSE, echo=F}
    tr line 65: ```{r, message=FALSE}
```

The `get_data` axis stays at `differs 2 / match 334`, naming `cleaning.fr` and `grouping.es`.
The red numbers match round 1 exactly. The proof still holds.

## fence-engine-boundary

DEFECT: the pre-fix `FENCE_OPEN` is `` "^[ \t]*`{3,}\\{r" ``. It has no engine boundary, so it
opens a chunk on `{rust}` and on `{ruby}`.

FIX: `` FENCE_OPEN <- "^[ \t]*`{3,}\\{r[},[:space:]]" ``. The engine name r must end at `}`,
at a comma, or at whitespace.

FIXTURE: `/tmp/gate/fx-engine/chapters`. Two files hold three R chunks and two non-R chunks.
The three R chunk headers cover the three legal boundary characters.

`grouping.qmd`:

````
# Fixture: engine boundary

```{r}
a <- 1
```

```{r, echo=F}
b <- 2
```

```{r label}
d <- 3
```

```{rust}
let a = 1;
```

```{ruby}
a = 1
```
````

`grouping.fr.qmd` is the same file with two changed lines. The rust body reads `let zz = 9;`
and the ruby body reads `zz = 9`. The three R bodies are identical in both files.

RED COMMAND: `Rscript /tmp/gate/checker-prefix.R /tmp/gate/fx-engine/chapters`

RED:

```
--- chunk bodies ---

code-diff
        1
differing chunks inside code-diff pairs: 2

--- FAIL: chunk body divergences ---
[code-diff] grouping.fr  chunks en=5 tr=5  differing=2

  per differing chunk (normalised lines):
  grouping.fr  chunk 4  (en line 15, tr line 15)
    en only: leta=1;
    tr only: letzz=9;
  grouping.fr  chunk 5  (en line 19, tr line 19)
    en only: a=1
    tr only: zz=9

  chapter lang chunks_en chunks_tr      body chunks_differing
 grouping   fr         5         5 code-diff                2
```

The pre-fix checker counts 5 R chunks in a file that holds 3. It reads the Rust body and the
Ruby body as R code, and it reports two false divergences.

GREEN COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/fx-engine/chapters`

GREEN:

```
--- chunk bodies ---

clean
    1
differing chunks inside code-diff pairs: 0

--- FAIL: chunk body divergences ---
(none)

  chapter lang chunks_en chunks_tr  body chunks_differing    header
 grouping   fr         3         3 clean                0 identical
```

The count moves from 5 to 3. The three R chunks still open, so `{r}`, `{r,` and `{r ` all
still work. The two false divergences are gone.

## fence-close-length

DEFECT: the pre-fix `FENCE_CLOSE` is `` "^[ \t]*`{3,}[ \t]*$" ``. It is a fixed pattern. A
chunk opened with four backticks therefore closes on a three-backtick line, and the rest of the
chunk becomes prose.

FIX: `read_chunks()` reads the opening backtick count with `fence_length()`. It then builds the
closing pattern with `fence_close(n)`, which is `` sprintf("^[ \t]*`{%d,}[ \t]*$", n) ``.

FIXTURE: `/tmp/gate/fx-fence/chapters`. Each file holds one four-backtick R chunk. The chunk
contains a three-backtick line, and it contains one line after that line.

`grouping.qmd`:

`````
# Fixture: fence length

````{r}
x <- 1
```
y <- 2
````
`````

`grouping.fr.qmd` is the same file with one changed line. It reads `y <- 99` instead of
`y <- 2`. That line sits after the three-backtick line, so only a whole chunk exposes it.

RED COMMAND: `Rscript /tmp/gate/checker-prefix.R /tmp/gate/fx-fence/chapters`

RED:

```
--- chunk bodies ---

clean
    1
differing chunks inside code-diff pairs: 0

--- FAIL: chunk body divergences ---
(none)

  chapter lang chunks_en chunks_tr  body chunks_differing    header
 grouping   fr         1         1 clean                0 identical
```

The pre-fix checker truncates both chunks at the three-backtick line. Each body holds one
line, `x <- 1`. The checker reports 0 differing chunks and calls the pair clean. The real
divergence, `y <- 2` against `y <- 99`, is invisible.

GREEN COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/fx-fence/chapters`

GREEN:

```
--- chunk bodies ---

code-diff
        1
differing chunks inside code-diff pairs: 1

--- FAIL: chunk body divergences ---
[code-diff] grouping.fr  chunks en=1 tr=1  differing=1

  per differing chunk (normalised lines):
  grouping.fr  chunk 1  (en line 3, tr line 3)
    en only: y<-2
    tr only: y<-99
```

The differing-chunk count moves from 0 to 1. The post-fix checker keeps the chunk whole and
names the divergence.

## get-data-comment-scope

DEFECT: the pre-fix `count_get_data_calls()` runs the call regex over raw chunk text. A call in
an R comment counts as a call site. A call inside a string literal counts as a call site.

FIX: the count runs over `normalise_body()`, the axis 1 normaliser. Normalisation drops the R
comment tail and replaces every string literal with `<string>`. Both non-executable forms
disappear, and the count keeps every real call.

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

`grouping.fr.qmd` holds the same chunk with the first code line only.

RED COMMAND: `Rscript /tmp/gate/checker-prefix.R /tmp/gate/fx-getdata/chapters`

RED:

```
--- get_data(name = ) call sites inside R chunks ---

differs
      1

--- FAIL: get_data(name = ) call-site counts ---
[differs] grouping.fr  en=3 tr=1

  chapter lang get_data_en get_data_tr get_data
 grouping   fr           3           1  differs
```

The pre-fix checker counts 3 call sites in the English chunk. Only 1 of the 3 is executable
code.

GREEN COMMAND: `Rscript utils/check-language-consistency.R /tmp/gate/fx-getdata/chapters`

GREEN:

```
--- get_data(name = ) call sites inside R chunks ---

match
    1

--- FAIL: get_data(name = ) call-site counts ---
(none)

  chapter lang get_data_en get_data_tr get_data
 grouping   fr           1           1    match
```

The count moves from 3 to 1. The French file holds exactly one call, `get_data(name = "x")`.
The English count matches it, so the surviving English call site is the `x` call.

The next probe names it directly. It loads the production definitions out of the fixed
checker, and it runs `read_chunks()`, `strip_code_line()` and `count_matches()` on the fixture.
The probe script is `/tmp/gate/r2/probe-getdata.R`.

```
chunks found: 1

per source line of chunk 1 (production strip_code_line / count_matches):
  raw: d <- appliedepidata::get_data(name = "x")     | normalised: d<-appliedepidata::get_data(name=<string>)    | call sites: 1 | name literal in raw line: x
  raw: # appliedepidata::get_data(name = "y")        | normalised:                                               | call sites: 0 | name literal in raw line: y
  raw: s <- 'appliedepidata::get_data(name = "z")'   | normalised: s<-<string>                                   | call sites: 0 | name literal in raw line: z

count_get_data_calls(bodies) = 1
surviving call-site source lines: 1
  d <- appliedepidata::get_data(name = "x")  -> name = x
```

The extracted name is `x`. The commented `y` call and the in-string `z` call are both gone.
