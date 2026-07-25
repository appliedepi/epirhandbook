# Staging area for data that appears to be dead

Nothing here is deleted. This directory holds files that look unused, kept in git so the
judgement can be reviewed — and reversed — before anything is actually removed.

## covid_example_data/ (9 files, 12 MB)

A COVID-19 example spreadsheet and the Fulton County ZIP-code shapefile. **Nothing
references them.** A full-text search across every `.qmd`, `.R`, `.yml` and `.md` in the
repository — including the retired chapters under `_excluded/` — returns no mention of
`covid_example_data`, `FultonCounty`, or `fulton`. They are also the only files under the
old `data/` folder with no counterpart in the **appliedepidata** package.

## Why the rest of data/ is still where it was

After the appliedepidata migration, 89 of the 124 files under `data/` no longer have their
filename written literally anywhere. That does **not** make them dead, and they were not
moved on that basis:

* **Filenames get constructed.** `chapters/time_series.qmd` builds its climate filenames
  with `paste0("germany_weather", i, ".nc")`, so those ten files never appear literally
  while being very much in use. A basename search cannot see that.
* **The retired chapters still need their data.** `_excluded/gis.qmd` and
  `_excluded/epidemic_models.qmd` reference `data/gis/` and `data/cache/epidemic_models/`
  624 times between them. Both chapters are cut for package reasons that may be fixed;
  removing their data would make reinstating them harder than it needs to be.
* **Some files were already dead before this work.** `data/rmarkdown/` is not referenced by
  `chapters/rmarkdown.qmd` and was not referenced before the migration either. That is a
  pre-existing question, not one this migration answers.

A file being redundant with **appliedepidata** is a good reason to stop *reading* it from
here — which the chapters now do. It is a separate decision whether the copy should also
stop *existing* here, and that decision is deliberately left open.
