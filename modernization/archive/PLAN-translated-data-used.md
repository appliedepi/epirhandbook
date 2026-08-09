# Plan: finish aligning the translated "Download handbook and data" pages

**Status: COMPLETE.** Closed 2026-07-25 on a clean verdict from an independent adversarial
review, after eight review rounds. All seven translated pages now match the English reference in
structure and in what they claim. The record below is kept because the *method* is the reusable
part, not the fix.

**What it took, and the lesson.** Eight review passes found 11, 8, 6, 2, 4, 2, 1 and 0 defects.
The first three rounds were largely damage from my own scripted edits — deleted content, mangled
comments, prose I had reported fixed and had not. The last four were pre-existing translation
defects the review surfaced while checking the work: a translated Quarto class, corrupted words,
untranslated fragments older than this migration.

**Not one of them was visible to a structural check.** Fence balance, indentation, parse success
and a clean render all passed throughout. Every real defect was found by reading the translated
prose against its English counterpart and asking whether it was true.

`chapters/data_used.qmd` (English) was rewritten for the 2.8 **appliedepidata** migration.
`chapters/data_used.{es,fr,jp,pt,ru,tr,vn}.qmd` were migrated by script over three passes. They now
render cleanly and contain no functional errors, but their **prose still describes the old
download-a-file-and-import-it workflow** while the code beside it loads objects from a package.

English is the reference. Read it first; it is the target shape.

---

## Why the previous passes did not finish the job

Three scripted passes each fixed what could be measured and left what could not. The gates used
were: code-fence balance, zero indented fences, zero literal `{r, eval=F}` in rendered HTML, and a
successful render.

**Those gates are structural. They cannot see a sentence that is untrue.** Every defect below
passes all four. That is the whole reason this file exists rather than a fourth script.

Two independent adversarial reviews found this class of defect after each pass. What they caught
that automated checks did not: empty bullets, a retired package's API, instructions that promise a
download the code no longer performs, and section text contradicting the code beneath it.

Do not write a fourth pattern-matching pass. The remaining work is translation.

---

## What is already correct — do not redo

* Code fences balanced, at column 0, never indented inside a list item. Quarto only treats a
  4-space-indented fence as inline code, which is what produced literal `{r, eval=F}` on the live
  site. Keep fences unindented.
* No literal chunk headers leak into rendered HTML.
* All seven render in the 2.8 container with zero warnings.
* No calls to the retired `epirhandbook` package remain — `download_book()`, `get_data("all")` and
  `get_data(file = )` are all gone. `appliedepidata::get_data()` takes **`name =`**.
* The `epirhandbook` strings that remain are repository URLs for the renamed repo. They are correct.
* Bullet descriptions for the Excel linelist were restored from each translator's own pre-migration
  wording in `fr`, `jp`, `ru`, `tr`, `vn`.

---

## The work, section by section

For each language, compare against the same section of `chapters/data_used.qmd` and make the prose
say what the code does. Verified defects, all present in `fr` and expected in the others:

### 1. The install / "get the data" section

The prose still says the data must be transferred "onto your computer" and that one call fetches
*all* the example data. Neither is true. `get_data()` returns an R object; `save_data()` writes one
named dataset to a path. English states this plainly: no download, no file path, no `import()` step.

### 2. "Option 2" is dangling

The text tells the reader to "try option 2" if something fails. There is no second method any more —
the subsection it referred to was the retired package's `download_book()`, correctly removed.
Either remove the reference or point it at the direct download link above it.

### 3. GIS

Still carries manual GitHub-download prose and screenshot instructions, then shows only
`get_data(name = "sle_adm3")`. It also claims "option 1" includes all the shapefiles; option 1 saves
a single linelist. English gives both routes explicitly: `get_data()` for the object, and
`save_data()` plus `unzip()` for the raw shapefile set.

### 4. Phylogenetic trees

Tells the reader to import with `ape::read.tree("Shigella_tree.txt")`, but nothing saved a `.txt`.
English says `get_data()` returns a **`phylo`** object directly.

### 5. Climate / weather

Says to download all the climate data and import it with `stars::read_stars()`. English says
`get_data()` reads the whole bundle as one combined **`stars`** object, and `save_data()` is only
needed if you want the raw `.nc` files.

### 6. Shiny

Omits the package data load entirely and links an old `facility_count_data.rds`. English loads
`malaria_facility_count_data` from the package and downloads only the app's `.R` scripts, which are
code and genuinely still downloads.

### 7. Cross-references — mostly a FRENCH problem, not a uniform one

Bare anchors of the form `](#gis)`, `](#time_series)`, `](#contact_tracing)`,
`](#phylogenetic_trees)`, `](#standardisation)`, `](#survey_analysis)`, `](#shiny)`. They render
without error while pointing nowhere useful.

Measured counts, so you know what to aim at rather than guessing:

| en | es | fr | jp | pt | ru | tr | vn |
|---|---|---|---|---|---|---|---|
| 2 | 2 | **10** | 2 | 0 | 2 | 2 | 2 |

**English itself has 2, so 2 is the legitimate baseline** — those two resolve. Only French deviates,
with 8 extra. The adversarial review that found this examined French only; do not assume the other
six need work here. Fix French, and leave the rest unless a specific anchor is shown not to resolve.

**When adding a link, the target must carry the language suffix** — `importing.fr.qmd` from a
`.fr.qmd` file, never bare `importing.qmd`. A bare target sends the reader to the English page *and*
makes Quarto copy the English source into that language's site as a raw download. Four such bugs
were fixed in commit `a5a6760`; do not reintroduce them.

### 8. Pre-existing translation defects, French (not caused by the migration)

`dossiet` for `dossier`; `differement`; `cliquez à droite` for `cliquez droit`; the lowercase heading
`#### recherche des contacts`; `locations des établissements`; an untranslated "Standardization";
English comments inside French code chunks. Worth fixing while the file is open.

---

## Machine-written prose to review

`TRANSLATION-BACKLOG.md` lists, by file and line, the 188 sentences written by machine during the
migration. They are grammatical but were not written by a translator. A native-speaker pass over
those lines belongs with this work.

---

## Verification

Structural checks are necessary but **not sufficient** — they are what let all of the above through.

Run these, and expect the values shown:

```bash
# fences balanced, none indented, no empty chunks
python3 - <<'PY'
import pathlib
for L in ('','.es','.fr','.jp','.pt','.ru','.tr','.vn'):
    s = pathlib.Path(f'chapters/data_used{L}.qmd').read_text().splitlines()
    n   = sum(1 for l in s if l.strip().startswith('```'))
    ind = sum(1 for l in s if l.startswith('    ') and l.strip().startswith('```'))
    print(f"data_used{L or ' (en)'}: fences={n} {'even' if n%2==0 else 'ODD'} indented={ind}")
PY

# no retired API anywhere. Match a CALL, not the substring: the heading anchor
# {#download_book_data} contains "download_book" and is not an API call -- a
# looser grep false-positives on French and wastes a round.
grep -nE 'download_book\(|get_data\("all"\)|get_data\(file' chapters/data_used*.qmd

# any cross-reference to another page MUST carry the language suffix. A bare
# ](importing.qmd) from a .fr.qmd sends the reader to the English page AND makes
# Quarto copy the English source into /fr/ as a raw download.
grep -nE '\]\([a-z_]+\.qmd\)' chapters/data_used.{es,fr,jp,pt,ru,tr,vn}.qmd

# bare anchors: expect 2 per language (English's baseline), 0 for pt, and
# French to come DOWN from 10 as section 7 is worked
for L in es fr jp pt ru tr vn; do
  printf '%s: %s\n' "$L" "$(grep -oE '\]\(#[a-z_]+\)' chapters/data_used.$L.qmd | wc -l)"
done
```

Then render. There is no Docker on `bench`; use `compute`:

```bash
ssh compute 'cd ~/render-check/epirhandbook && docker run --rm -v "$PWD":/w -w /w ghcr.io/appliedepi/aedockerpublic/epirhandbook-basics:2.8 quarto render chapters/data_used.fr.qmd --to html'
```

**The check that actually matters, and it is a human one:** read each section beside its English
counterpart and ask whether a reader following the translated text would end up where the code
takes them. Nothing automated caught any of the eight defects above.

---

## Separate open findings, not part of this file's work

Recorded here so they are not lost. All CONFIRMED by adversarial review against the shipped code.

| Where | Finding |
|---|---|
| `aedockerpublic` `.github/scripts/plan.py` | A group image can declare `renders:` for a chapter belonging to another group and validate. The name/dir check ties the image *name* to the group, never the *chapters* to the group. Reproduced: `epirhandbook-analysis` rendering `chapters/importing.qmd` passes. |
| same | Duplicate-render detection compares raw strings, so `chapters/x.qmd` and `./chapters/x.qmd` count as different files and both validate. `--chapter-images` then emits the same chapter twice with two different images. |
| same | Nothing validates the catalog against the book's real chapter list. A catalog can omit a real chapter, or name one that does not exist, and pass. |
| `epirhandbook` `.github/workflows/build-deploy.yml` | Only the *registry prefix* of `docker-images.yml` is pinned. A pull request can name any public image in that namespace and have it executed on the runner. |
| same | The comment claiming a private image "will fail the pull" is now false: the workflow authenticates with `GITHUB_TOKEN` and holds `packages: read`, so a private image the repo has access to may pull successfully. |
| `aedockerpublic` `.github/workflows/build.yml` | The accepted-risk comment is imprecise in both directions. "Any of 473 packages can push to the registry" is too broad — package write access is grant-dependent. And the token is exposed as **step environment** to the retry action, not only as a BuildKit secret inside `docker build`, so the exposure is wider than stated while the consequence is narrower. |
