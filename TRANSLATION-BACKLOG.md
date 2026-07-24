# Translation backlog: prose left stale by the 2.7 forward-port

## What this is

The 2.7 forward-port updated R code so chapters run on the 2026 package stack. It did
not reword the teaching prose around that code. Five passages now describe features
that no longer exist or no longer work the way the text says.

**This is not a build blocker.** All 49 chapters render. The code is correct. Only the
explanation is out of date.

**This is not a translation job in the usual sense.** The stale wording is present in
the English source too, and in all 8 translations of it — nobody has reworded any of
the 9 copies yet. A translator fixes it once the English wording is settled, so this
list stays as one shared backlog rather than 8 separate per-language tickets.

## How to fix an item

Each item below gives a **search token** — a package or function name. Search for the
token, not for translated words, because the token survives translation unchanged.

For each item, the token appears in all 9 of these files:

```
chapters/<chapter>.qmd        (English)
chapters/<chapter>.de.qmd
chapters/<chapter>.es.qmd
chapters/<chapter>.fr.qmd
chapters/<chapter>.jp.qmd
chapters/<chapter>.pt.qmd
chapters/<chapter>.ru.qmd
chapters/<chapter>.tr.qmd
chapters/<chapter>.vn.qmd
```

Open the file, find the token, reword the surrounding sentence to match "Should say."

## Do NOT touch these — they look related but are correct

- **`sitrep` the package.** It is still used for `find_start_date()`,
  `assert_positive_timespan()`, the install line, and two links in `survey_analysis`.
  Only the tabulation recommendation (item 4 below) is stale.
- **`survival_analysis`'s `size = 1`.** It is an argument to `survminer::ggsurvplot()`,
  which has its own `size` parameter. It is not the deprecated ggplot2 aesthetic in
  item 5 below, and it is not stale.

## The five items

### 1. `chapters/standardization.qmd` (+ 8 translations) — token: `two ways`

- Currently says: "This page will show you **two ways** to standardize an outcome..."
- Why stale: the `dsr`-package method was cut (the package no longer exists on CRAN).
  Only the `PHEindicatormethods` method remains, so "two ways" is no longer true.
- Should say: drop "two ways" — "This page will show you how to standardize..."

### 2. `chapters/standardization.qmd` (+ 8 translations) — token: `dsr`

- Two spots per language: a sentence, and a nearby code comment.
- Currently says: "the package **dsr** expects... the column... called `pop`"
- Why stale: `dsr` is gone. The `pop` column rename is still needed — the code still
  does `stdpop = pop` — but the reason given (the `dsr` package) no longer applies.
- Should say: attribute the `pop` requirement to **PHEindicatormethods** /
  `phe_dsr()`, not to `dsr`.

### 3. `chapters/standardization.qmd` (+ 8 translations) — token: `Another way`

- Currently says: "**Another way** of calculating standardized rates is with
  **PHEindicatormethods**..."
- Why stale: "Another" refers back to the `dsr` section, which is now cut. There is no
  longer a first way for this to be "another" of.
- Should say: drop "Another" — "We calculate standardized rates with
  **PHEindicatormethods**..."

### 4. `chapters/survey_analysis.qmd` (+ 8 translations) — token: `four different options`

- Currently says: "There are **four different options**... we recommend the
  **sitrep** function"
- Why stale: the sitrep tabulation section was cut (`sitrep::tab_survey()` no longer
  exists). Three options remain, and the one the text recommends is gone.
- Should say: "There are **three** options (**survey**, **srvyr**, **gtsummary**)...";
  drop the sitrep recommendation entirely.

### 5. `chapters/ggplot_basics.qmd` (+ 8 translations) — token: `assigned twice`

- Currently says: "the `size = ` aesthetic is **assigned twice**... both times a
  static value"
- Why stale: the code was updated to `size = 1` (points) and `linewidth = 2` (the
  smoothing line). `size` is no longer set twice — it is set once, plus a separate
  `linewidth`.
- Should say: reword to describe `size = 1` for the points and `linewidth = 2` for
  the smoothing line.

## Scope

5 passages × 9 languages. Item 2 is two edits per language (sentence + code comment),
so roughly 54 edits in total.

## How far this was checked

Items 1-5 above are quoted directly from the **English** source — read and confirmed
present at the quoted line. The other 8 languages were confirmed **structurally**: same
section present, same reference counts (e.g. the `dsr` token appears the same number of
times in every language), so the same stale passages exist in all of them. The
**translated wording itself was not read** — nobody who reads all 8 languages checked
whether the phrasing differs from the English. Treat "Should say" as the idea to
convey in each language, not a literal string to paste in.
