# epiRhandbook 2.6 → 2.7: what changes for readers and authors

**Status: the content forward-port is COMPLETE and render-verified in all 9 languages.**
This document covers the *content* migration only. Building the 2.7 product images and pinning
the package set for shipping are a separate release step, deliberately out of scope here — see
"What is and is not verified" below before quoting this document. `epidemic_models` is cut (see
C5). Backing data: `BREAKAGE.tsv` (what errored), `DIFFERENCES.tsv` (what rendered differently),
`forward-port.patch` (every source change), `FORWARD-PORT.tsv` (per-change accounting),
`verify_render_26.04.tsv` (49 English chapters), `verify_render_multiling.tsv` (136 non-English).
Run on **Ubuntu 26.04 LTS / R 4.6.0**: **49 of 49 English chapters render**, the **17 edited
chapters render in all 8 other languages (136/136)**, and 468 of 473 packages load. Earlier
22.04 and 24.04 builds are superseded. Written for stakeholders, not as build output.

### What is and is not verified

| Claim | Status |
|---|---|
| The 4 fixes + 2 section cuts reach all 9 languages | **Verified by patch inspection AND by render** — see below |
| 49 English chapters render without error | **Verified by render** (`verify_render_26.04.tsv`, 49/49 rc=0) |
| The 17 edited chapters render in all 8 non-English languages | **Verified by render** (`verify_render_multiling.tsv`, 136/136 rc=0, 136 HTML files produced) |
| The content changes are complete and correct | **Verified** |
| The 2.7 per-chapter product images work | **OUT OF SCOPE for this phase.** Building them is a separate release step |
| The 2026 package set is reproducible for shipping | **OUT OF SCOPE for this phase.** 7 GitHub deps resolve at branch HEAD — correct for discovery, must be pinned before release |

The last two rows are release-phase work, deliberately not part of this content forward-port.
They are real and they are not small.

## What this upgrade is

2.6 is the handbook frozen on its 2024 package stack (R 4.3.2), split into per-chapter
images. **2.7 moves the same content onto 2026 packages** (R 4.6.0). The content is
deliberately unchanged except where a package forces our hand — the goal is the smallest
possible edit, not a rewrite.

## Executive summary

| | |
|---|---|
| Chapters in the 2.7 book | **49** (was 50; `epidemic_models` cut) |
| Chapters rendering successfully | **49 of 49** |
| Chapters edited for a hard break | **4** |
| Chapters edited only to clear deprecations (C3) | **13** |
| Chapters edited, total | **17** |
| Chapters needing no edit at all | **32** |
| Chapters cut | **1** (`epidemic_models`) |
| Sections cut | **2** (`dsr`, `sitrep` — see C1/C2) |
| Packages that no longer exist | **5** of 473 — 468 upgraded cleanly |
| Source diff | **154 files, +478 / −1881 lines** — 153 `.qmd` (+477/−1880) plus `_quarto.yml` (+1/−1) |

The headline: **the handbook survives two years of package churn largely intact.** 32 of the 49
shipping chapters needed no edit whatsoever. Four were fixed for hard breaks, and 13 more were
touched only to clear deprecation warnings (C3, an owner-approved decision). One
(`epidemic_models`) could not be salvaged without rewriting it, and is cut. Nearly every page
shows small cosmetic differences, and one new warning box appears on 28 pages.

**72% of all removed lines are the two approved section cuts** — the deprecation fixes themselves
are small (+477 / −522 across 9 languages).

---

## Part A — Content we had to change (5 chapters)

These **errored out** on 2026 packages. All five are now resolved: four fixed, one cut.

| Chapter | Why it breaks | Fix |
|---|---|---|
| `writing_functions` | `flextable::set_formatter_type()` is now defunct | **Mechanical** — use `colformat_*` |
| `tables_descriptive` | dplyr 1.2 rejects `quantile()` inside `summarise()` (returns 5 values, not 1) | **Mechanical** — use `reframe()` |
| `standardization` | The **`dsr` package no longer exists on CRAN** | **Needs a decision — see Part C** |
| `survey_analysis` | `sitrep::tab_survey()` no longer exists. The package still exists but its entire tabulation API was removed | **Needs a decision — see Part C** |
| `epidemic_models` | EpiNow2 removed the result accessors the chapter is built on | **CUT — see C5** |

✅ **This list is now final, not a floor.** The original scan could only report each chapter's
*first* error, so more problems could have been hiding behind them. Every chapter has since been
rendered end-to-end on the real 2026 stack: **49 of 49 pass**. Nothing new surfaced behind the
first errors — the four mechanical fixes were genuinely the whole cost.

### Warnings that will become breakages later
These still work but are formally deprecated — worth fixing while we're in here:

| Deprecated | Chapters |
|---|---|
| `forcats::fct_explicit_na()` → `fct_na_value_to_level()` | `cleaning`, `factors`, `missing_data` |
| `across(...)` argument form | `missing_data`, `regression` |
| ggplot2 `size=` on lines → `linewidth=` | `moving_average` |
| `feasts::autoplot.tbl_cf()` — moved to the new `{ggtime}` package | `time_series` |

**Not a miss: `survival_analysis`.** An earlier draft of this table also listed
`survival_analysis` here, and it was deliberately not changed. Its `size = 1` is an argument to
`survminer::ggsurvplot()`, which has its own `size` parameter — it is not the ggplot2 aesthetic
and it is not deprecated. Changing it would have been wrong. The table entry was the error, not
the code.

---

## Part B — What readers will notice (no source change)

None of these are errors. They are the visible cost of two years of package updates, and
they will appear on the published site whether or not we touch the source.

**1. Every page title is reordered.** Caused by the Quarto upgrade, not by R packages:
```
2024:  The Epidemiologist R Handbook - 46 Common errors
2026:  46 Common errors – The Epidemiologist R Handbook
```

**2. A new warning box appears on most pages.** (Measured as 28 of the 45 pages that rendered
during the initial discovery scan, before the fixes landed; the ratio, not the count, is the
point.) The single most widespread change, on
every page that imports data:
> `Warning: Missing 'trust' will be set to FALSE by default for RDS in 2.0.0.`

This is noisy and reader-visible. **Silencing it is a source change** — a deliberate choice,
not something to drift into.

**3. Tables look different.** In gtsummary/gt tables the group size moves onto its own line
(`Death` / `N = 2,582` instead of `Death, N = 2,582`), and a footnote about missing values
was dropped by gtsummary. Affects `stat_tests`, `regression`, `tables_descriptive` and others.

**4. Console messages are longer.** dplyr's grouping message went from one line to five,
and it prints into the page.

**5. Some warnings appear, others vanish.** `iteration` gains a repeated ggplot2 warning
about a stray `color=` argument. `transmission_chains` loses its "cycles detected" warning.

**6. Figures shift — but far less than the numbers suggest.** 154 of 258 figures differ
byte-wise, yet inspection shows most are *not* redesigns:
- Largest diff (23%, `phylogenetic_trees`): the same tree, drawn slightly larger.
- 13.85% (`ggplot_basics` jitter): identical plot — the jitter is **unseeded**, so points land
  differently on every render, in 2024 too.
- Typical 1–3%: sub-pixel font and margin shifts.

Most-affected chapters: `phylogenetic_trees`, `ggplot_tips`, `time_series`, `ggplot_basics`,
`epicurves`, `age_pyramid`, `contact_tracing`.

**Text similarity to the 2024 render: median 0.9966, lowest 0.9562** — i.e. the prose and
computed values are essentially unchanged.

---

## Part C — Decisions (all resolved)

These could not be resolved by engineering. All have been decided by the owner;
the forward-port implements them.

**A note on scale:** every code change is applied across **all 9 languages**. Translated
chapters (`<chapter>.fr.qmd`, `.es.qmd`, …) carry the same R code, so an English-only fix
would leave the other 8 sites still broken or still warning. E.g. `fct_explicit_na()` appears
in 6 English files and **46 translated ones**.

### C1. `standardization` — the `dsr` package is gone — **DECIDED: CUT**
`dsr` (directly standardised rates) was removed from CRAN and is not coming back. The chapter
teaches it directly. Options:

1. **Rewrite that section** using a maintained alternative (e.g. `PHEindicatormethods`,
   or compute the rates manually). Best for readers; largest diff.
2. **Vendor the last `dsr` release** into the image. Preserves the text exactly; means shipping
   an unmaintained, CRAN-removed package indefinitely.
3. **Cut the section**, leaving the rest of the chapter.

### C2. `survey_analysis` — `sitrep`'s tabulation API was removed — **DECIDED: CUT**
`sitrep` still exists but no longer provides `tab_survey()` or the related functions; the
current release exports only six helper functions. This is a larger hole than a renamed
function. Options:

1. **Rewrite** using `srvyr`/`gtsummary`, which the handbook already uses elsewhere.
2. **Pin the old `sitrep`** from GitHub at the 2024 commit — fragile, and it may not build
   against 2026 dependencies.
3. **Cut the affected section.**

### C3. Deprecation warnings printing into the published pages — **DECIDED: UPDATE**
Four warning classes now render into reader-visible output (Part B, items 2 and 5). Silencing
them means editing the source beyond what's strictly required to build. **Do we accept noisier
pages, or accept a larger diff?**

### C4. `gis` — **DECIDED: CUT**
`gis` fetches live OpenStreetMap tiles while rendering, so it cannot be built in a hermetic CI
job and has no 2.7 image. It is commented out of `_quarto.yml` as of this release.

An earlier draft of this section said `gis` "was already excluded before this upgrade". That was
true of the 2.6 baseline but not of the branch this release was cut from, where `gis` was still a
declared chapter — which is why it surfaced late, as a chapter with no image to render it.

**Its published URL stops resolving.** A chapter absent from `book.chapters` is never rendered, so
it emits no redirect stub either. 31 links from six other chapters (`basics`, `data_used`,
`flexdashboard`, `importing`, `rmarkdown`, `survey_analysis`, across en/jp/pt/ru/tr/vn) point at
it; they are deliberately left in place and start working again the moment the chapter returns.
Bringing it back needs a render that does not reach an external service.

### C5. `epidemic_models` — EpiNow2's result API was removed — **DECIDED: CUT**
The chapter does not merely *plot* an EpiNow2 result — it reads the fitted object's internals
throughout. Those accessors were removed in the 1.4 → 1.9 rewrite. This is not a plotting fix;
restoring the chapter means re-teaching the chapter against EpiNow2's new interface, which is a
rewrite by a subject-matter author, not an upgrade task.

**Decision: cut `epidemic_models` from 2.7.** The 2.7 book has **49 chapters, not 50.**

This is the one piece of teaching content the upgrade loses outright. If the handbook wants
EpiNow2 back, it needs a newly authored chapter — that work is out of scope here and should be
tracked separately.

---

## Part D — What is unchanged

- **32 of the 49 shipping chapters carry no source edit at all.**
- **468 of 473 packages** upgraded cleanly to 2026 versions.
- Structure and navigation. Chapter ordering is unchanged except that
  `epidemic_models` is removed (C5).
- Teaching prose, except in the 4 chapters we edited — and note the stale passages in
  **Part E**, which still need a translator's attention.
- Computed values and statistical results, apart from the genuinely random ones
  (unseeded simulations, which differed between any two renders in 2024 as well).

---

## Part E — Translator backlog

**Moved to [TRANSLATION-BACKLOG.md](TRANSLATION-BACKLOG.md).**

The upgrade fixed the *code* in all 9 languages, but some surrounding *prose* still explains code
that no longer exists — 5 passages, roughly 54 edits once every language is counted. Nothing there
breaks the build; all 49 chapters render. It is a translator's job, not an engineering one.

`TRANSLATION-BACKLOG.md` carries the full list with a search token per item, what each currently
says and what it should say, a list of things that look related but are already correct, and an
appendix of the site's pre-existing dead anchors. It is kept there so the work list has one home
and cannot drift from this document.

## Appendix — the 5 packages that no longer exist

| Package | Last version | Used by |
|---|---|---|
| `dsr` | 0.2.2 | `standardization` (see C1) |
| `Quandl` | 2.11.0 | not used by any book chapter |
| `i2extras` | 0.2.1 | not used by any book chapter |
| `plogr` | 0.2.0 | transitive dependency only |
| `survMisc` | 0.5.6 | transitive dependency only |

Only `dsr` affects published content.

**Not in this list, despite earlier appearances — now resolved.** `terra`, `tmap`, `raster`,
`leafem` and `OpenStreetMap` are all alive on CRAN. They failed only because our build image was
based on Ubuntu 22.04, whose GDAL (3.4.1) is too old for the 2026 geospatial stack. We rebuilt the
base on **Ubuntu 26.04 LTS (GDAL 3.12.2)** and all five now install and load:
`terra` 1.9.34, `raster` 3.6.32, `tmap` 4.4.1, `leafem` 0.2.5, `OpenStreetMap` 0.4.1.
This was a build-image problem, never a content problem.

**Why 26.04 and not 24.04.** Both install the same 468 of 473 packages, so this is a longevity
choice rather than a correctness one. 24.04 shipped in April 2024; pairing it with a 2026 package
set would repeat, in miniature, the very mismatch that broke `terra` — an operating system
meaningfully older than the packages it must compile. 26.04 is the LTS contemporary with these
packages, which pushes the next "system library too old" problem out by roughly two more years.
