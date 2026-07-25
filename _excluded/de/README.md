# German (`de`) — retired, not shipped

These 49 files are the German translation: 48 chapters plus `index.de.qmd`.

German is **not built**. `_quarto.yml`'s `babelquarto.languages` lists
`['fr', 'es', 'vn', 'jp', 'pt', 'tr', 'ru']` — `de` is commented out of it, and has been
for some time. The files sat in `chapters/` looking live: they were never rendered, never
verified, and drifted (two of their cross-references pointed at the wrong language).

They are here rather than deleted because the translation is real work that may be
resumed. Nothing is lost — `git log --follow` still reaches their full history.

## If German comes back

1. Move these files back to `chapters/` (and `index.de.qmd` to the repository root).
2. Add `'de'` to `babelquarto.languages` in `_quarto.yml`.
3. Re-run the data migration on them. The rest of the book now loads its example data
   from the **appliedepidata** package; these files still read from the repository's own
   `data/` folder, which the other languages no longer use.

`_quarto.yml` keeps its `title-de:` and `part-de:` labels and the `de` entry in
`babelquarto.languagecodes`. They are inert while German is not in `languages`, and
keeping them makes step 2 a one-line change.

## Why a subdirectory

`_excluded/` itself holds the two chapters cut for package reasons — `gis` and
`epidemic_models` — in every language, including German. Those are excluded because of
what they *are*. The files here are excluded because of what *language* they are in.
Different reasons, so they are kept apart.

Quarto skips any path whose name or parent directory begins with `_`, which is what stops
all of this being copied into the rendered site as downloadable source.
