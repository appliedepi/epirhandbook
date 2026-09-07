# archive

This folder holds files the handbook no longer uses. No build-deciding file and no live check
names a file here.

The move happened on 2026-09-07. GitHub issue 448 lists most of what moved:
https://github.com/appliedepi/epirhandbook/issues/448

Every file keeps its original path under `archive/`. `MANIFEST.tsv` records all 808 moves in
three columns: `source`, `destination` and `blob`. The `blob` column holds the git object hash
the file had at commit 44da099b, before the move. A reader can compare it against the file
here and prove the content did not change.

## What moved here

- 145 chapter files: 17 chapters that `_quarto.yml` does not declare, their 113 translations,
  and 15 translations whose English chapter no longer exists.
- 597 files from `modernization/`, which are the whole record of the 2026-09 fix pass.
  `modernization/` now holds `STAKEHOLDERS.md` alone, and the nine live tooling files moved
  to `checks/`.
- 36 images that no file in the scan scope names. The section "How the image list was
  built" gives that scope.
- 16 files under `renv/`, `site_libs/` and `datatoremove/`.
- 14 single files that issue 448 names, among them `quarto_runfile.R`, `_translation.R`,
  `theme-light.scss` and `contribution_guide_05-02-2021.qmd`.

## How the image list was built

The scan compared each image basename against the text of 652 files, as tracked at commit
44da099b:

- `chapters/*.qmd`
- the root `*.qmd`, `*.yml`, `*.scss`, `*.html` and `*.md` files
- `_excluded/**/*.qmd`
- every file under `.github/`
- the root-level `*.sh`, `*.py` and `*.md` files of `modernization/`
- every file under `utils/`

An image moved here when its basename appeared in none of those 652 files. 36 of the 222
tracked images moved, and 186 stayed.

## The translation backlog

The translation backlog moved to `archive/modernization/TRANSLATION-BACKLOG.md`. The work it
still listed is now GitHub issue 449:
https://github.com/appliedepi/epirhandbook/issues/449

## Running the fix-pass scripts

Run the fix-pass scripts from `archive/modernization/`. Their relative paths, such as
`findings/fix-pass/` and `workflows/`, again point at the record that sits beside them.
