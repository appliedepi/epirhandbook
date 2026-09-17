# utils/

Scripts and records from the 2026-09 migration that moved the handbook's data loads to
`appliedepidata::get_data()`.

## `data-map.tsv` and `data-callsites.tsv` are a snapshot, not a current inventory

Both files record the state of `data/` at the time of that migration. Neither is maintained, and
neither gates anything. No check reads them.

Do not treat either as authority over what `data/` holds today. Both are already wrong:

- `data-map.tsv` names 12 files that are not at the paths it gives, among them the whole
  `data/covid_example_data/` tree and two `data/flexdashboard/` sources. All 12 were moved into
  `archive/` during the migration: 9 to `archive/datatoremove/`, 3 to `archive/data/`. The
  `archive/` folder was itself deleted on 2026-09-17, so those 12 now survive only in git
  history.
- Two of the 12, `data/flexdashboard/outbreak_dashboard_shiny.Rmd` and
  `outbreak_dashboard_test.Rmd`, carry `disposition = keep` and were moved out of `data/`
  anyway. A `keep` row has been overridden before.
- `data-callsites.tsv` row 24 says `content/en/data_table.qmd:53` "must remain a file-based
  read". That chapter now calls `appliedepidata::get_data(name = "linelist_cleaned_excel")`.

Read the `disposition` column as the migration's answer to one question: does this file have an
`appliedepidata` equivalent. `in_package` means yes. `keep` means the question did not apply,
which is why the `evidence` column on most `keep` rows says `notdata`. It does not mean the file
must stay in the repository.

## What decides `data/` today

Three things, and nothing else:

1. `checks/check-data-reads.py`. It permits only the `directories` and `importing` chapters to
   name `data/` in an executing chunk. Every other chapter MUST load data through
   `appliedepidata::get_data()`.
2. The download buttons on `content/en/data_used.qmd`, which link files by raw GitHub URL.
3. The Shiny app bundle under `data/malaria_app/`. It carries its own `.here` anchor, so
   `here::here()` inside `global.R` resolves to that folder and not to the repository root.

On 2026-09-17 the folder went from 115 tracked files to 28 on those three rules. See issue 451.

## `check-data-equivalence.R`

A one-off harness from the migration. It compared each dataset loaded from a file against the
same dataset from `appliedepidata`. It reads `data-callsites.tsv`, and it reconstructs the file
side from paths under `data/`. Most of those files are now deleted, so it can no longer run for
those datasets. The migration it verified is complete and no check depends on it.
