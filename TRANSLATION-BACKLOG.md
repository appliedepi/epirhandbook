# Translation backlog

**This file holds OPEN translation work only.** When an item is done it comes out of here; the
record of what changed lives in [STAKEHOLDERS.md](STAKEHOLDERS.md) and in git history. That rule
exists because this file previously described work that had since been completed, which is worse
than saying nothing — a translator would have redone it.

The division of labour between the two files:

| | Purpose | Audience |
|---|---|---|
| `STAKEHOLDERS.md` | release notes — what changed, and why it matters to you | readers, authors, translators, contributors |
| `TRANSLATION-BACKLOG.md` | a work queue — what is still to do, with search tokens and target wording | whoever picks up translation work |

Covers items from the 2.7 forward-port and the 2.8 **appliedepidata** migration.

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


## Appendix: dead same-page anchors (not caused by the forward-port)

Separate from the five prose items above, the published site carries **106 dead
same-page anchors** — links of the form `(#something)` where no element on that page
has that id. They are long-standing content bugs, present in the current production
render, and unrelated to the 2.7 forward-port.

The largest groups:

| Anchor | Occurrences |
|---|---|
| `#gis` | 15 |
| `#contact_us` | 7 |
| `#objectstructure` | 6 |
| `#ggplot_basics_map_loc` | 6 |
| `#pivot_prep` | 6 |
| `#gis-basics` | 6 |

`#gis` and `#gis-basics` deserve a note. They look like they should point at the GIS
chapter, but a `#`-only link never leaves the page it is on. Excluding the GIS chapter
did not break them, and restoring it will not fix them. Each needs rewriting as a real
cross-page link, or removing.

To find them, render the site and check every `href="#x"` for a matching `id="x"` in
the same file. Percent-decode the fragment first — hrefs are URL-encoded and `id`
attributes are not, which otherwise inflates the count roughly fortyfold.


## appliedepidata migration — machine-written prose (Unit D)

The English handbook was migrated from reading `data/` files directly to calling
`appliedepidata::get_data()` / `save_data()` (commits `dbaa049` and `e4130b5`). This
section propagates the same code changes to the 7 translations (es, fr, jp, pt, ru, tr,
vn) and converts every `class='download-button'` (and equivalent markdown-link) button
that pointed at now-migrated data.

**All prose below was machine-written during this propagation.** It follows a fixed
per-language template (below) but was not reviewed by a native speaker for grammar,
register, or naturalness. Treat it as a first draft that needs a native-speaker pass,
same as the five items already logged above.

### LINKTEXT used per language, and where it came from

Each converted sentence links to that language's own "Download handbook and data" page
(`data_used.<lang>.qmd`), using link text native to that language. Per rule, this text
was extracted from the language's own files wherever it already existed as real inline
link text; where no such precedent existed, it was taken from the page's own `#` title
(also the language's own words, just not previously used as a link).

| Lang | LINKTEXT used | Source |
|---|---|---|
| es | "Descargando el manual y los datos" | `data_used.es.qmd` H1 title — **no existing inline link to this page anywhere in the ES corpus**, so no precedent to extract. Judgment call: reused the page's own title text. Flag for native review. |
| fr | "Télécharger le manuel et les données" | `data_used.fr.qmd` H1 title — only one weak precedent existed (`[chapitre sur les données](#data_used)` in `time_series.fr.qmd`, different wording, anchor-only). Judgment call: reused the page's own title text instead. Flag for native review. |
| jp | "ハンドブックとデータのダウンロード" | Already used as inline link text 16 times (bound to `#data-used` anchor); reused verbatim, target corrected to `data_used.jp.qmd`. |
| pt | "Baixar manual e dados" | Already used as inline link text 9 times (most common of 3 variants found; dominant over "Download do manual e dados" ×2 and "Baixar livro e dados" ×2), bound to `#data-used` anchor; reused verbatim, target corrected to `data_used.pt.qmd`. |
| ru | "Скачивание руководства и данных" | Already used as inline link text 8 times, **already** with the correct `data_used.ru.qmd` target; reused verbatim, nothing to fix. |
| tr | "El kitabı ve veri indirme" | Already used as inline link text once (of 2 variants found), with the correct `data_used.tr.qmd` target; reused verbatim. |
| vn | "Tải sách và dữ liệu" | Already used as inline link text 14 times, **already** with the correct `data_used.vn.qmd` target; reused verbatim, nothing to fix. |

### Sentence templates used (adapted per surrounding sentence's grammar where the lead
clause was kept; used verbatim where no lead clause existed to keep)

- **es**: Cárguelo directamente con `` `appliedepidata::get_data(name = "X")` `` (véase la página [LINKTEXT](data_used.es.qmd) para más detalles).
- **fr**: Chargez-les directement avec `` `appliedepidata::get_data(name = "X")` `` (voir la page [LINKTEXT](data_used.fr.qmd) pour plus de détails).
- **pt**: Carregue diretamente com `` `appliedepidata::get_data(name = "X")` `` (consulte a página [LINKTEXT](data_used.pt.qmd) para mais detalhes).
- **tr**: Doğrudan `` `appliedepidata::get_data(name = "X")` `` ile yükleyin (ayrıntılar için [LINKTEXT](data_used.tr.qmd) sayfasına bakın).
- **ru**: Загрузите их напрямую с помощью `` `appliedepidata::get_data(name = "X")` `` (подробности см. на странице [LINKTEXT](data_used.ru.qmd)).
- **vn**: Tải trực tiếp bằng `` `appliedepidata::get_data(name = "X")` `` (xem trang [LINKTEXT](data_used.vn.qmd) để biết chi tiết).
- **jp**: `` `appliedepidata::get_data(name = "X")` `` で直接読み込めます（詳細は[LINKTEXT](data_used.jp.qmd)のページを参照）。

Algorithm used: kept everything in the paragraph up to and including the last
sentence-ending period before the button (the "we import dataset X" lead clause, if one
existed); replaced everything from there through the button and its trailing "(as .ext
file). Import with `import()`..." clause with the template sentence above. Where no lead
clause existed (the button opened the paragraph), the template sentence stands alone.

### Every sentence written, by language (file:line → dataset)

All rows below use the template for that language shown above, substituting the dataset
name shown. 188 sentences total.

#### es (28)
`age_pyramid.es.qmd:47`, `characters_strings.es.qmd:55`, `combination_analysis.es.qmd:89`,
`descriptive_statistics.es.qmd:31`, `diagrams.es.qmd:42`, `factors.es.qmd:43`,
`flexdashboard.es.qmd:49`, `ggplot_basics.es.qmd:44`, `ggplot_tips.es.qmd:37`,
`grouping.es.qmd:54`, `heatmaps.es.qmd:57`, `interactive_plots.es.qmd:67`,
`iteration.es.qmd:43`, `joining_matching.es.qmd:39`, `missing_data.es.qmd:44`,
`moving_average.es.qmd:39`, `pivoting.es.qmd:76`, `plot_continuous.es.qmd:89`,
`plot_discrete.es.qmd:61`, `regression.es.qmd:49`, `relational_databases.es.qmd:24`,
`stat_tests.es.qmd:53`, `survival_analysis.es.qmd:71`, `tables_descriptive.es.qmd:53`,
`tables_presentation.es.qmd:135` → dataset `linelist_cleaned_rds`.
`cleaning.es.qmd:115` → `case_linelists_linelist_raw`.
`pivoting.es.qmd:53` → `malaria_facility_count_data`.
`time_series.es.qmd:61` → `campylobacter_germany`.

#### fr (28)
`age_pyramid.fr.qmd:41`, `characters_strings.fr.qmd:54`, `combination_analysis.fr.qmd:87`,
`descriptive_statistics.fr.qmd:31`, `diagrams.fr.qmd:43`, `factors.fr.qmd:43`,
`flexdashboard.fr.qmd:48`, `ggplot_basics.fr.qmd:43`, `ggplot_tips.fr.qmd:36`,
`grouping.fr.qmd:57`, `heatmaps.fr.qmd:59`, `interactive_plots.fr.qmd:67`,
`iteration.fr.qmd:46`, `joining_matching.fr.qmd:47`, `missing_data.fr.qmd:42`,
`moving_average.fr.qmd:41`, `pivoting.fr.qmd:82`, `plot_continuous.fr.qmd:87`,
`plot_discrete.fr.qmd:61`, `regression.fr.qmd:55`, `relational_databases.fr.qmd:24`,
`stat_tests.fr.qmd:54`, `survival_analysis.fr.qmd:69`, `tables_descriptive.fr.qmd:55`,
`tables_presentation.fr.qmd:130` → dataset `linelist_cleaned_rds`.
`cleaning.fr.qmd:123` → `case_linelists_linelist_raw`.
`pivoting.fr.qmd:56` → `malaria_facility_count_data`.
`time_series.fr.qmd:57` → `campylobacter_germany`.

#### jp (24 — jp has no translations of `basics_old`/`cleaning`/`plot_continuous`/`plot_discrete`/`relational_databases` buttons in this set; `cleaning.jp.qmd` had no button to begin with)
`age_pyramid.jp.qmd:52`, `characters_strings.jp.qmd:54`, `combination_analysis.jp.qmd:89`,
`descriptive_statistics.jp.qmd:31`, `factors.jp.qmd:43`, `flexdashboard.jp.qmd:48`,
`ggplot_basics.jp.qmd:42`, `ggplot_tips.jp.qmd:37`, `interactive_plots.jp.qmd:67`,
`iteration.jp.qmd:43`, `joining_matching.jp.qmd:45`, `missing_data.jp.qmd:43`,
`moving_average.jp.qmd:36`, `pivoting.jp.qmd:71`, `plot_continuous.jp.qmd:89`,
`plot_discrete.jp.qmd:61`, `regression.jp.qmd:48`, `relational_databases.jp.qmd:24`,
`stat_tests.jp.qmd:52`, `survival_analysis.jp.qmd:75`, `tables_descriptive.jp.qmd:53`,
`tables_presentation.jp.qmd:134` → dataset `linelist_cleaned_rds`.
`pivoting.jp.qmd:50` → `malaria_facility_count_data`.
`time_series.jp.qmd:57` → `campylobacter_germany`.

#### pt (28)
`age_pyramid.pt.qmd:52`, `characters_strings.pt.qmd:54`, `combination_analysis.pt.qmd:98`,
`descriptive_statistics.pt.qmd:31`, `diagrams.pt.qmd:43`, `factors.pt.qmd:43`,
`flexdashboard.pt.qmd:48`, `ggplot_basics.pt.qmd:48`, `ggplot_tips.pt.qmd:37`,
`grouping.pt.qmd:53`, `heatmaps.pt.qmd:59`, `interactive_plots.pt.qmd:68`,
`iteration.pt.qmd:42`, `joining_matching.pt.qmd:48`, `missing_data.pt.qmd:43`,
`moving_average.pt.qmd:36`, `pivoting.pt.qmd:79`, `plot_continuous.pt.qmd:89`,
`plot_discrete.pt.qmd:61`, `regression.pt.qmd:50`, `relational_databases.pt.qmd:24`,
`stat_tests.pt.qmd:54`, `survival_analysis.pt.qmd:72`, `tables_descriptive.pt.qmd:51`,
`tables_presentation.pt.qmd:136` → dataset `linelist_cleaned_rds`.
`cleaning.pt.qmd:136` → `case_linelists_linelist_raw`.
`pivoting.pt.qmd:57` → `malaria_facility_count_data`.
`time_series.pt.qmd:65` → `campylobacter_germany`.

#### ru (24 — ru's translation set omits several chapters entirely, e.g. `descriptive_statistics.ru.qmd`, `plot_continuous.ru.qmd`, `plot_discrete.ru.qmd` don't exist)
`age_pyramid.ru.qmd:52`, `characters_strings.ru.qmd:54`, `combination_analysis.ru.qmd:88`,
`diagrams.ru.qmd:43`, `factors.ru.qmd:46`, `flexdashboard.ru.qmd:48`,
`ggplot_basics.ru.qmd:44`, `ggplot_tips.ru.qmd:37`, `grouping.ru.qmd:56`,
`heatmaps.ru.qmd:59`, `interactive_plots.ru.qmd:67`, `iteration.ru.qmd:46`,
`joining_matching.ru.qmd:48`, `missing_data.ru.qmd:43`, `moving_average.ru.qmd:40`,
`pivoting.ru.qmd:78`, `regression.ru.qmd:50`, `stat_tests.ru.qmd:54`,
`survival_analysis.ru.qmd:75`, `tables_descriptive.ru.qmd:54`,
`tables_presentation.ru.qmd:133` → dataset `linelist_cleaned_rds`.
`cleaning.ru.qmd:117` → `case_linelists_linelist_raw`.
`pivoting.ru.qmd:56` → `malaria_facility_count_data`.
`time_series.ru.qmd:64` → `campylobacter_germany`.

#### tr (28)
`age_pyramid.tr.qmd:44`, `characters_strings.tr.qmd:53`, `combination_analysis.tr.qmd:77`,
`descriptive_statistics.tr.qmd:31`, `diagrams.tr.qmd:42`, `factors.tr.qmd:46`,
`flexdashboard.tr.qmd:46`, `ggplot_basics.tr.qmd:42`, `ggplot_tips.tr.qmd:34`,
`grouping.tr.qmd:51`, `heatmaps.tr.qmd:59`, `interactive_plots.tr.qmd:66`,
`iteration.tr.qmd:46`, `joining_matching.tr.qmd:48`, `missing_data.tr.qmd:43`,
`moving_average.tr.qmd:40`, `pivoting.tr.qmd:77`, `plot_continuous.tr.qmd:89`,
`plot_discrete.tr.qmd:61`, `regression.tr.qmd:49`, `relational_databases.tr.qmd:24`,
`stat_tests.tr.qmd:53`, `survival_analysis.tr.qmd:74`, `tables_descriptive.tr.qmd:58`,
`tables_presentation.tr.qmd:132` → dataset `linelist_cleaned_rds`.
`cleaning.tr.qmd:123` → `case_linelists_linelist_raw`.
`pivoting.tr.qmd:55` → `malaria_facility_count_data`.
`time_series.tr.qmd:59` → `campylobacter_germany`.

#### vn (28)
`age_pyramid.vn.qmd:52`, `characters_strings.vn.qmd:54`, `combination_analysis.vn.qmd:98`,
`descriptive_statistics.vn.qmd:31`, `diagrams.vn.qmd:43`, `factors.vn.qmd:44`,
`flexdashboard.vn.qmd:48`, `ggplot_basics.vn.qmd:42`, `ggplot_tips.vn.qmd:37`,
`grouping.vn.qmd:47`, `heatmaps.vn.qmd:57`, `interactive_plots.vn.qmd:67`,
`iteration.vn.qmd:46`, `joining_matching.vn.qmd:45`, `missing_data.vn.qmd:41`,
`moving_average.vn.qmd:36`, `pivoting.vn.qmd:71`, `plot_continuous.vn.qmd:89`,
`plot_discrete.vn.qmd:61`, `regression.vn.qmd:47`, `relational_databases.vn.qmd:24`,
`stat_tests.vn.qmd:54`, `survival_analysis.vn.qmd:75`, `tables_descriptive.vn.qmd:51`,
`tables_presentation.vn.qmd:134` → dataset `linelist_cleaned_rds`.
`cleaning.vn.qmd:134` → `case_linelists_linelist_raw`.
`pivoting.vn.qmd:50` → `malaria_facility_count_data`.
`time_series.vn.qmd:57` → `campylobacter_germany`.

Five more sentences were hand-written (not scripted) because the surrounding HTML was
already malformed pre-existing (broken anchor tags with stray `<`/missing `>`/missing
`<` on the closing tag), so the automated converter couldn't match them:
`interactive_plots.jp.qmd:67`, `interactive_plots.pt.qmd:68`, `heatmaps.ru.qmd:59`,
`pivoting.jp.qmd:71`, `diagrams.pt.qmd:43`. Same templates, same review need.

### `data_used.<lang>.qmd` — COMPLETE, do not redo

The seven translated "Download handbook and data" pages were fully aligned with English and
signed off by independent adversarial review on 2026-07-25. They now match English in structure
and in what they claim.

This entry is kept only to stop anyone reopening it. Details are in
[STAKEHOLDERS.md](STAKEHOLDERS.md) under "2.7 → 2.8", and the method in
`PLAN-translated-data-used.md`. Nothing in these seven files is outstanding.

### Still open elsewhere, outside `data_used`

- **`ggplot_basics_old.{es,fr,pt,tr,vn}.qmd` and `data_table.jp.qmd`** had only their stale URLs
  corrected, not their download links converted to `get_data()`. `ggplot_basics_old` is an
  undeclared legacy chapter not in `_quarto.yml`; `data_table` is one English deliberately left
  reading `data/` directly. Converting either would assert a code/data correspondence nobody has
  verified for those chapters. Leave them unless you verify it.
- **`data/malaria_app/data/facility_count_data.rds`** has no **appliedepidata** counterpart — a
  genuine, pre-existing gap recorded in `utils/data-map.tsv`. Its download link is intentionally
  kept.
