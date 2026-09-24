# The repository's checks: what they cover, and how to run them

Run `checks/check-sync.sh` from the repository root. It changes nothing, takes about half a
minute, and ends with `IN SYNC` or `DRIFT`. Repeat after any English chapter changes, and every
few months regardless.

Checks 6 and 8 need a base commit, and they do not run without one. Add `--base <sha>` to run
them over the files changed since `<sha>`. Add `--render` to run them over the whole tree, which
takes about 20 minutes. Every other check, check 9 included, runs without a base commit.

The result line names what ran. It reads `IN SYNC` when checks 6 and 8 ran, and
`IN SYNC (checks 6 and 8 not run)` when they did not. The script exits 0 on `IN SYNC`, 1 on
`DRIFT`, and 2 when `--base` names something that is not a commit.
`.github/workflows/translation-sync.yml` passes `--base` on every push and every pull request.

Every check writes its full output under `/tmp/check-sync/`. The lines the script prints come
from those files.

Every check below was used in the 2026-09 fix pass. The record of that pass is the
[`archive/modernization` tree](https://github.com/appliedepi/epirhandbook/tree/621c4b053a1b8cba0d969dad13fb5c2a6e9155a8/archive/modernization), pinned at the last commit that carried it. Each check has a script, an expected output, and a remedy. The remedies are the
same scripts and agent workflows that did the work the first time. A drift of the same kind
then costs minutes, not days.

## What "in sync" means

The repository declares its layout in two files. `languages.yml` names the eight languages, and
`content/en/_quarto.yaml` names the 52 stems. Every chapter file is `content/<lang>/<stem>.qmd`,
so a file's language is the folder that holds it.

`checks/langs.py` reads both files for the checks. `read_languages()` returns the main code and
the declared codes, and checks 1 to 8 call it. `read_stems()` returns the stems in file order,
and checks 1, 2, 4, 5 and 7 call it. Checks 9 and 15 use the module's loader.

The loader is `yaml.BaseLoader`, and it refuses a duplicate key. BaseLoader keeps every scalar a
string, so the Norwegian code `no` stays a code. When a function cannot read a file, the check
stops with one line that names the file. The causes are a missing file, a file that does not
parse, and a `languages.yml` with no `main:` or no code.

The landing page hero says 49 chapters. That is a narrower count, and both are right. It is the
52 stems less `index`, `about` and `acknowledgements`. Those three are pages of the book, not
chapters of it.

English is the reference. Checks 1 to 3 pair each translated chapter with
`content/en/<stem>.qmd`. That set is 51 non-index stems and 7 translation languages. The landing
page `index.qmd` and English itself stay out of it. The set was 49 x 7 from 2026-09-02, when
the GIS chapter returned. It became 51 x 7 on 2026-09-18, when `about.qmd` and
`acknowledgements.qmd` split off the landing page.

| Property | Expected | Check | Remedy |
|---|---|---|---|
| the translated file exists | 357 of 357 | check 1 | translate the chapter |
| code chunk count equals the English | 357 of 357 | check 1 | the align-chunks agent workflow, one agent per chapter, then `sync-chunks.py` |
| heading sequence equals the English, count and level, fenced blocks stripped | 357 of 357 | check 1 | the align-headings agent workflow, one agent per chapter |
| every heading with an English `{#id}` carries that id | 0 headings differ, 0 dead links | check 2 | `sync-anchors.py`, no agent |
| every aligned chunk's code equals the English, comments free | 0 chunks differ | check 3 | `sync-chunks.py`, no agent |
| inline code spans in prose name things the English names | informational | check 4 | the inline-pass agent workflow over the new suspects |
| every changed chapter renders without execution, fences balanced | 0 FAIL | check 6, with `--base` or `--render` | read the log under `/tmp/render-gate/` |
| no R chunk parses worse than the English chunk | 0 files worse | check 8, with `--base` or `--render` | the sync, or a source defect |
| every internal link resolves, stays on its page and stays in its language | 0 dead, 0 same-page, 0 cross-language and 0 unterminated links in the 416 declared files | check 5 | `rewrite-links.py`, no agent |
| no chunk that executes names the `data/` folder, outside the two chapters that teach file paths | 0 lines in the 416 declared files | check 7 | load the data with `appliedepidata::get_data()`, or set `eval=F` |
| the eight language folders, project files, chapter files, manifest rows and alias lines agree | `8 languages, 52 stems, 416 aliases, drifted: 0` | check 9 | edit the file the DRIFT line names |

Each agent workflow named in the Remedy column is a `.js` file in `checks/workflows/`. A
remedy is a current procedure, so it lives in the tree beside the check it repairs. The other
ten workflows of the 2026-09 fix pass ran once and are history: they are in the
[fix-pass record](https://github.com/appliedepi/epirhandbook/tree/621c4b053a1b8cba0d969dad13fb5c2a6e9155a8/archive/modernization/workflows).

Check 4 is informational because a suspect span is often right: a placeholder the reader
replaces, or a word the author put in code font. The baseline is 357 suspects as of 2026-09-17. All were judged placeholders or noise. The GIS chapter, restored the same
day, added one more: a French verb in code font. A rise above that is what to look at, not
the number itself. Check 4 measures the declared set: the 51 non-index stems in the 7 translation
languages. A file that `content/en/_quarto.yaml` does not declare is not measured here, and
check 9 reports it. A declared file that is missing gets a one-line note, and check 9 reports
that too.

## Check 5: internal links

Run `python3 checks/check-links.py`. `check-sync.sh` runs it as check 5. It reads the
416 declared files, which are `index.qmd` and the 51 other stems, in English and in the 7
translation languages. It prints one line for each link it rejects, and exits 1 when it finds
one. It rejects four link forms.

```
DEAD content/en/basics.qmd:372 #objectstructure (no id objectstructure on this page)
SAME-PAGE content/en/basics.qmd:372 basics.qmd#objects
LANGUAGE-MISMATCH content/es/packages_suggested.qmd:158 ../en/data_used.qmd
UNTERMINATED-LINK content/pt/basics.qmd:925 ... na seção [Importar e exportar](#importing.
```

A link is dead when its `.qmd` target does not exist, or when the target page does not define
the `#fragment`. The line number is the first source line that holds the target. Pandoc's
markdown reader gives no source position, so `?` after the number means the target occurs on
more than one line.

Three rules cover the other three forms.

- Write a link to a section of the same page as `#id`. The long form `file.qmd#id` is
  `same-page`. It resolves, and it breaks as soon as the file is renamed.
- A link never crosses languages. A file's language is the folder that holds it, and a link
  target's language is the language of its resolved path. So `../en/basics.qmd` written in a
  French chapter is `language-mismatch`. Point it at `<stem>.qmd` in the same folder.
- Close every link. A `](` whose destination never closes is `unterminated-link`.

The unterminated form is the one pandoc cannot report. Pandoc reads no link in
`[text](#target`, so the page carries no `<a>` element and nothing checks the target. That
form sat in `content/pt/basics.qmd` for years and every run said `dead 0`. So the checker
reads the raw source for this form alone.

The search for the closing parenthesis stops at the next blank line, because an inline link
cannot cross one. A destination written on the next line therefore passes, which CommonMark
allows, and three links in the corpus use that shape. The search counts nested parentheses, so
a URL that holds a balanced pair passes. It skips a fenced code block, an HTML comment and a
code span.

Pandoc renders each file to one standalone HTML page, `pandoc -s -f markdown -t html`. Python's
`html.parser` reads that page once. The ids are the ones a browser sees: `id` on any element,
and `name` on an `<a>` element. The links are the `href` of every `<a>` element.

Pandoc resolves a heading, a div, a span, a metadata title, raw HTML, an HTML comment and a
character reference into that one page. So the checker does not re-implement pandoc's identifier
rule, and it does not read markdown itself. A link in a YAML `title` renders on the page, so it
counts. None of the 416 declared files carries such a link today.

A file that pandoc cannot read is a failure, not a crash. The usual cause is a front matter that
does not parse as YAML. The checker prints `PANDOC-FAILED <file>` with the first line of the
pandoc message, and counts it under `pandoc-failed`. That file has no ids, so a link into it can
also appear as dead.

The checker takes three options.

- `--summary` prints the counts and no link lines. It gives files scanned, the pandoc binary
  and its version, one line for each language, `same-page N`, `language-mismatch N`,
  `unterminated-links N`, `dead N` and `pandoc-failed N`.
- `--fixture <dir>` uses every `<lang>/*.qmd` under that directory as the file set. The folder
  gives each file its language, so a fixture can carry a cross-language link.
- `--pandoc <cmd>` names the binary. The default is `quarto pandoc`, and plain `pandoc` when
  quarto is not on PATH.

Check 5 prints the counts, from `--summary`. When it rejects a link it prints the detail lines
too, and `check-sync.sh` ends with `DRIFT`.

The sweep of 2026-09-07 cleared the backlog. It rewrote 1,854 links in 240 of the 400 declared
files, and the checker now reports `dead 0`. All but six were cross-chapter links written as a
bare `#anchor`. The counts before the sweep were 450 Spanish, 445 Japanese, 444 Portuguese,
427 French, 28 Turkish, 22 English, 20 Vietnamese and 18 Russian.

The pass of 2026-09-08 cleared 21 same-page links and 7 cross-language links, in the 400
declared files. It also made the checker fail on either form. Both counts were informational
before that date.

One step comes before the parse. Pandoc reads the knitr chunk header ```` ```{r} ```` as a
paragraph, not as a fence. The checker rewrites each chunk header to ```` ```{.r} ````, line
for line, as knitr does. Without that step every `#` comment in an R chunk becomes a heading
with an id. It rewrites a fence line indented by fewer than four spaces, which is the CommonMark
rule. An indented literal fence inside a paragraph changes nothing.

### Remedy: rewrite-links.py

`checks/rewrite-links.py` rewrites every dead link the checker reports.

1. Run `python3 checks/check-links.py` and read the DEAD lines.
2. Add a row to `checks/link-map.tsv` for each target the table does not hold.
3. Run `python3 checks/rewrite-links.py --dry-run` for the count.
4. Run `python3 checks/rewrite-links.py` to write the files.

The table columns are `old_id`, `stem`, `anchor` and `note`. `old_id` is the link target exactly
as the checker reports it. `stem` is the chapter that holds the content today. `anchor` is an
in-page id, and it stays empty unless every language version of that chapter defines that id. An
anchor that only English defines is a dead link in the other seven languages.

The script writes nothing until every file rewrites cleanly. It stops when the table holds no
row for a reported target. It also stops when the number of links it finds in prose differs from
the number of findings. It skips a fenced code block and an HTML comment, because pandoc reads
no link there.

## Check 7: the data folder

Run `python3 checks/check-data-reads.py`. `check-sync.sh` runs it as check 7. It reads the same
416 declared files as check 5. Three rules govern the `data/` folder.

- A chunk that executes may not name `data/`. The handbook loads its data with
  `appliedepidata::get_data()`.
- The directories chapter and the importing chapter are the exception. They teach file paths, so
  a reader runs them against the repository's own `data/` folder.
- No chunk writes into `data/`, in any chapter.

A chunk executes when its fence options do not set `eval=F` or `eval=FALSE`. Any chapter may show
a `data/` path in a chunk that does not execute.

The checker strips the `#` comment from each line of an executing chunk. It then matches three
lexical forms.

- `here("data"`, `here::here("data"`, `file.path("data"`, `fs::path("data"` or `path("data"`
- a string that starts `data/`
- a string that starts `../data/`

It prints one line for each line it rejects, and exits 1 when it finds one.

```
DATA-READ content/fr/standardization.qmd:147
DATA-WRITE content/es/importing.qmd:412
```

`DATA-READ` names a line outside the two chapters that teach file paths. `DATA-WRITE` names a
line inside those two that also calls a function that writes. Those functions are `export`,
`write*`, `save`, `saveRDS`, `st_write`, `file.copy`, `file.create`, `dir.create`,
`dir_create`, `file_create`, `download.file` and `unzip`. Either line makes `check-sync.sh`
end with `DRIFT`.

The checker takes two options.

- `--summary` prints the counts and no detail lines. It gives files scanned, one line for each
  language, and `data-reads N`. That count holds both kinds of line.
- `--fixture <dir>` uses every `<lang>/*.qmd` under that directory as the file set. The folder
  gives each file its language.

The check is lexical. It reads the source line, and it does not follow a path through a variable.
A chunk that builds a path on one line and reads it on another passes.

### Remedy

1. Load the data with `appliedepidata::get_data()`.
2. Set `eval=F` on a chunk whose subject is the path itself, not the data.
3. Delete a chunk that writes into `data/`.

The root `CLAUDE.md` carries the same rule, for an agent that edits a chapter.

## Check 6: the render gate

Run `checks/render-gate.sh <base> [head]`. `check-sync.sh` runs it as check 6, with the base it
was given. It runs `quarto render --no-execute` on every translated chapter that changed since
`<base>`. It needs quarto, git and PyYAML. It runs no R, because `--no-execute` skips the knitr
engine.

A translated chapter is a file under `content/<lang>/` whose language is not the main language
in `languages.yml`. Each one renders as a temporary copy beside the original,
`content/<lang>/<stem>.render-gate-tmp.qmd`. In that copy every inline R expression
`` `r ... ` `` outside a fenced block becomes the placeholder `INLINE_R`. `quarto render
--no-execute` stops at an inline R expression, so the placeholder is what lets the gate read a
file that holds one. The copy sits in the language folder, so `content/<lang>/_quarto.yaml` and
every relative path resolve as they do for the original.

A trap deletes every copy and every artifact beside it, on success and on failure. It also
deletes the `content/<lang>/html_outputs/` and `content/<lang>/.quarto/` folders the render
creates. It deletes only those: the gate records at start which of them are already there. In a
fresh clone the gate leaves no file at all.

The search for the end of an inline R expression stops at the next blank line, because an inline
expression cannot cross one. Without that bound the match runs to the next backtick anywhere in
the file, and one unterminated expression swallows whole paragraphs into the placeholder. The
gate then reads a copy that is missing prose the original carries. An expression that does not
close inside its paragraph now stops the gate with `FAIL-placeholder`. The 416 declared files
hold 81 inline R expressions, in 33 of those files, and none of them crosses a line break. That
count uses the gate's own `INLINE` pattern, on prose only, with fenced blocks skipped. A plain
count of `` `r `` over the same files gives 105, because it also counts text inside fenced
blocks.

The gate stops with exit 2, before it renders anything, in five cases.

- A `languages.yml` that `checks/langs.py` cannot read.
- A base or a head that is not a commit.
- A `git diff` that fails.
- A temporary copy path that the repository tracks.
- A temporary copy path that already exists.

The gate skipped a file with inline R until 2026-09-09, and 17 of the 99 files then in the
changed set carried one. A broken YAML header in `content/es/gis.qmd` passed that gate,
because the gate never read the file.

A file with an odd number of fence lines FAILS before the render. Pandoc renders an unclosed
fence with exit 0, so the render alone cannot see that class.

Per-file output goes to `/tmp/render-gate/<lang>.<stem>.log`, and the result of each file to
`/tmp/render-gate/SUMMARY.tsv`.

## Check 8: the chunk parse gate

Run `python3 checks/chunk-parse-gate.py <base> [head]`. `check-sync.sh` runs it as check 8, with
the base it was given. It parses every R chunk of every changed translated chapter with R, in
the version at `<base>` and in the version in the working tree.

It compares the two versions chunk index by chunk index. A chunk index that fails after and did
not fail before is a regression, unless the English chunk at that index fails too. A count
comparison reads `same` when one chunk breaks and another is repaired in the same file, so the
gate compares indices instead.

The gate stops with exit 2 in five cases.

- A base or a head that is not a commit.
- A `git` command that fails.
- `Rscript` that is not on PATH.
- A `languages.yml` that `checks/langs.py` cannot read.
- `Rscript` that returns non-zero. The gate prints `Rscript`'s own stderr.

## Check 9: the layout

`check-sync.sh` runs check 9 itself, and it needs no base commit. It reads `languages.yml`, the
eight `content/<lang>/_quarto.yaml` project files, `docker-images.yml` and the front matter of
the 416 declared files. PyYAML parses every one of them with `yaml.BaseLoader`, which makes every
scalar a string. `yaml.safe_load` reads an unquoted `no` as False, so the Norwegian code `no`
would not survive it. `.github/workflows/translation-sync.yml` installs `python3-yaml` before it
runs `check-sync.sh`.

It prints one summary line, and one `DRIFT` line for each finding:

```
   layout: 8 languages, 52 stems, 416 aliases, drifted: 0
```

A finding sets the DRIFT exit. Check 9 reports ten kinds.

- A file check 9 reads that does not parse as YAML. The `DRIFT` line names the file and the
  line that PyYAML reports. For a chapter file, it names the front matter.
- A language `languages.yml` declares with no `content/<code>/_quarto.yaml`.
- A `content/<x>/` folder that holds `.qmd` files for a code `languages.yml` does not declare.
- A project file whose flattened chapter list differs from `content/en/_quarto.yaml` in set or
  in order, or whose part count differs.
- A project file whose `lang` differs from the tag `languages.yml` gives that code, or whose
  `book.title` differs from the title `languages.yml` gives that code.
- A declared stem with no file in one of the eight language folders. `index` is a declared
  stem, so every folder needs its own landing page.
- A `docker-images.yml` that does not hold exactly one row per declared stem, or that holds a
  row for something else.
- A `docker-images.yml` row under `chapters:` with no `stem:` key, or with no `image:` key.
  The `stem:` key names the chapter, and the `image:` key names the image CI renders it in. A
  key with an empty value, a list or a mapping names nothing, so it counts as absent.
- A `.qmd` file in a language folder that `content/en/_quarto.yaml` does not declare,
  `index.qmd` aside.
- A chapter file, `index.qmd` aside, whose aliases are not the ones the layout wants. English
  wants `/new_pages/<stem>.html`, and every other language wants
  `/new_pages/<stem>.<lang>.html`.

The alias keeps the chapter's old `/new_pages/` URL alive, so it spells the stem the way that
page spelled it. `transition_to_r` is the one stem the old page spelled differently, as
`transition_to_R`, so its alias keeps the capital R in all eight languages. The English chapter
shipped under both spellings, so it wants two aliases: `/new_pages/transition_to_R.html` and
`/new_pages/transition_to_r.html`. Check 9 compares the aliases case-sensitively, because a URL
path is case-sensitive. Two identical lines are not two aliases.

Check 9 reads the aliases from the list under the front matter's top-level `aliases:` key, in
block or flow style. A list under another key counts for nothing, and neither does a list below
the front matter.

A missing file, or a file that does not parse, gives check 9 one `DRIFT` line and no traceback.
Check 9 then skips the comparisons that need that file, and still reports what it can see.
`languages.yml` is the exception, because without it there is nothing to compare. When it is
missing, does not parse or names no `main:` language, check 9 stops after that one line.

Checks 1 and 4 read `languages.yml` and the stem list through `checks/langs.py`. When either file
is missing or does not parse, each prints one line that ends `Check 9 below reports it.` Checks 5
and 7 stop with one line that names the file. Check 9 then prints its own `DRIFT` line.

### Remedy

Edit the file the `DRIFT` line names. A drifted chapter list is the common finding. You add a
chapter to seven of the eight project files and miss one. Nothing else in the repository
notices.

## Do not render an English chapter with the gate

`render-gate.sh` renders translated chapters only, on purpose. Rendering a main-language
chapter in this book project makes quarto rewrite `.gitignore`. On 2026-09-02 it also deleted
the three `site_libs/quarto-search/` files the repository tracked then. Those files are in
the [archived tree](https://github.com/appliedepi/epirhandbook/tree/621c4b053a1b8cba0d969dad13fb5c2a6e9155a8/archive/site_libs/quarto-search). Check an English chapter with the fence-parity count and the R parse gate
instead.

## What the checks do not cover

- Meaning. A translation that says something the English does not, in prose, is invisible to
  every check here. That was the prose sweep, at about 100,000 tokens per chapter-language
  pair, and the [fix-pass record](https://github.com/appliedepi/epirhandbook/tree/621c4b053a1b8cba0d969dad13fb5c2a6e9155a8/archive/modernization) records it. Repeat it only for chapters whose
  English prose changed.
- Comments inside chunks. The sync keeps a translated comment where its code line survives
  and falls back to the English comment otherwise; nothing checks that comments are translated.
- Plot labels and other display strings, which the sync sets to the English.
- The 17 English source defects that the translations now mirror on purpose. The
  source-defects table of the [fix-pass record](https://github.com/appliedepi/epirhandbook/tree/621c4b053a1b8cba0d969dad13fb5c2a6e9155a8/archive/modernization) lists them.

## The reasoning behind the design, so it is not re-derived

- Code chunks are copied, not reviewed. 94% of aligned chunks were identical, or differed
  only in comments. Of the 459 that differed in code, most held defects rather than
  deliberate choices. Renamed objects were rare, Portuguese-only, and half inconsistent.
- Comments are merged by line, not translated. A translation pass over 4,500 comments would
  cost more than the whole prose sweep, and add risk. A comment on a code line the translator
  got wrong falls back to English.
- Anchors take the English id. Cross-links are written English-style throughout the corpus,
  so a divergent id is a dead link. Only one link in the corpus ever targeted a translation's
  own id.
- Heading and chunk alignment use one agent per chapter, because the edit is structural and
  small. The mechanical count afterwards is the proof, not the agent's report.
- Every check was proved red before it was trusted. The inputs were a corrupted span, an
  extra parenthesis, a broken YAML front matter, an unclosed fence and a demoted heading. Check 3 was proved both ways
  on 2026-09-02. One changed code token inside a Turkish chunk reports DRIFT. A changed or
  added comment inside a chunk stays IN SYNC. That is the rule: code exact, comments free. A check
  that has not been seen to fail is not a check.

## Order, when several things drift at once

1. `check-sync.sh` to see what.
2. Chunk count or heading sequence first, with the alignment workflows. The syncs pair by
   position and need the counts to match.
3. `sync-chunks.py`, then `sync-anchors.py`.
4. `check-sync.sh --base <base>`, which adds check 8 and check 6 on the changed files.
5. Commit each step on its own, signed, and run `check-sync.sh` again.

## 10. Unparsed links

`checks/check-unparsed-links.py`. Reports markdown that looks like a link but that pandoc never
parsed into one.

Check 5 asks pandoc which links it found, then checks their targets. Anything that never parses
is invisible to it. Four defect forms came out of that blind spot, all found by reading:

| form | example |
|---|---|
| reference link with no definition | `[R project][r_projects]` |
| bracket and paren transposed | `[R project(r_projects.qmd)]` |
| opening bracket missing | `R project](r_projects.qmd)` |
| two bare `$` pairing as TeX math | `table(d$col)` ... `[link](x.qmd)` ... `table(d$other)` |

The rule is one line: a link that parsed leaves no brackets behind. Render the chapter, then look
for a residual `](`, `][`, or a bracketed span whose content looks like a link target. Fenced code,
HTML comments, inline R and rendered `<code>` are removed first, because each produces that
signature without being a defect.

Expected output: `unparsed links: 0`.

Remedy: fix the link. A reference link needs either a `[label]: target` definition or conversion to
an inline link. A `$` swallowing a link means bare R code needs backticks.

## 11. Image names

`checks/check-image-names.py`. Every `images/` file a chapter names must exist.

Reads `knitr::include_graphics(here::here("images", ...))` and plain markdown image links.
**Commented lines count.** The defect this was written for lived inside an R comment in all eight
languages: `images/survanalysis.png`, absent, named by `survival_analysis.qmd`. Nothing rendered
it, so nothing caught it.

Expected output: `missing from images/: 0`.

Remedy: add the image, correct the name, or delete the line.

## 12. Clean failure

`checks/check-clean-failure.py`. Every check must report a missing input, not crash on it.

A check that dies with a `FileNotFoundError` traceback still blocks, so the repository is not
unsafe. It is unusable: the reader gets a stack trace instead of the one sentence naming the
missing file. Two boxes of issue 455 were this, and one crashed four checks at once.

It also covers the worse case. A check whose input is EMPTY rather than absent reports a clean
tree and exits 0. Nothing is measured and the result says success.

For each check and each required input, it builds a fixture without that input. For
`languages.yml` it also builds a fixture where that file does not parse. It then asserts that the
run exits non-zero, prints no traceback, and names the missing thing.

The two sync scripts run with `--dry-run`, so they write nothing. Checks 6 and 8 compare two
commits, so they run with `HEAD HEAD` in a fixture that is a git repository. The other six
checks run with `--summary`.

It does NOT pass `--fixture`. That flag makes a check derive its file set by globbing. Globbing
bypasses `languages.yml`, and would exercise a path the repository never runs.

Expected output: `checks that do not fail cleanly: 0`.

Remedy: guard the read. Say which file is missing and why the check needs it.

**What it does not cover.** Checks 1, 4 and 9 are inline python inside `check-sync.sh`, not
separate scripts, so check 12 never runs them. Check 9 was verified by hand on 2026-09-16 to
degrade to a DRIFT line for a missing `languages.yml` and for a missing `docker-images.yml`.
Checks 1 and 4 were verified by hand on 2026-09-24 to print one line for a missing
`languages.yml` and for one that does not parse. Any new check written inline rather than as
`checks/<name>.py` is outside this gate for the same reason.

## 13. Language copies (removed)

`checks/check-language-copies.py` was deleted on 2026-09-24. It compared the language list in
`languages.yml` with the `const translations = {...}` object in `banner.html`. That object held
the "Need help learning R?" course banner, which was removed on the same day. `banner.html` now
holds only the webfont links, so no second copy of the language list is left for this check to
compare. The number 13 is not reused.

## 14. Image versions in prose

`checks/check-image-version-refs.py`. Every image version the documentation names must be one
the repository actually uses.

`docker-images.yml` and `.devcontainer.json` decide which image line is live. Prose does not, so
prose rots silently. After the 2.9 migration, `README.md` still said 2.8 in three places. One was
a code block claiming to show the contents of `.devcontainer.json`, which by then said 2.9.
A contributor copying that block opened the repository in the wrong image.

Live versions come from image DECLARATIONS in those two files, not from any `2.<n>` in them.
Both carry narrative comments naming past lines, and counting those as live made every
superseded version acceptable forever. The first version of this check did exactly that and
could not have caught the defect it was written for.

A version named in a `docker-images.yml` comment counts as live. The manifest documents pinning
a chapter back to an older image, and that is a real option.

Expected output: `stale: 0`.

Remedy: update the prose. If a version is genuinely live, declare it in one of the two files.

## 15. The landing page gate

`checks/check-landing-strings.py`. Every language must resolve a complete landing page: its
strings, the theme that renders them, and the slot each string lands in.

`landing.yml` is a second copy of the language list. This check is what keeps it in step with
`languages.yml`.

The check needs PyYAML. `.github/workflows/translation-sync.yml` installs `python3-yaml`, and
the render job of `.github/workflows/build-deploy.yml` already installed it. It reads four
inputs:

- `languages.yml`, for the code list
- `landing.yml`, for the strings
- `utils/landing-hero.R`, for the keys the hero reads
- each `content/<code>/_quarto.yaml`, for the theme wiring. Rule 9 reads `content/en/_quarto.yaml`
  a second time, for the chapter count the hero shows.

Reading the key set from the consumer is what makes "complete" checkable. Rename a key in the
hero, and English no longer declares it.

Rules 1 to 8 run by default:

1. Every code `languages.yml` declares has a block in `landing.yml`.
2. Every block in `landing.yml` names a code `languages.yml` declares.
3. The `en` block declares every key `utils/landing-hero.R` reads, and gives none of them an
   empty string. English is the fallback of last resort. The hero reads every key the `en`
   block declares, so a key nothing reads is a failure.
4. Every key a translated block declares also exists under `en`. Every value is a string. A
   declared `svc` list holds 3 cards, and every card carries `h`, `p`, `link` and `href`.
5. No value is an empty string. Omit the key, and the value falls back to English.
6. No translated value is byte-identical to the English value for that key.
7. No two languages give one key the same value.
8. Every `content/<code>/_quarto.yaml` names `../../ael-extras.html` under
   `format.html.include-after-body`, and names both token layers and `../../theme-ael.scss`
   under `format.html.theme.light` and `format.html.theme.dark`.

Rule 10 runs by default as well, and it has its own section below. Rule 9 is the one rule
that needs a rendered page. A number names a rule, never the order it runs in: rule 10 came
last, so its number sits after the render rule.

**Rule 3 runs in both directions, and one direction alone is blind.** Rule 3 names a key the
hero reads and `en` omits. Its mirror names a key `en` declares and no `s("key")` call reads.
`donate_label` sat under `en` from 2026-09-18, when the donation form went, and the gate passed
it on every run.

The mirror takes its legal set from `utils/landing-hero.R`, so a rename in the hero moves it.
`svc` is legal because `svcs()` reads it. The 6 `INVARIANT` keys are legal because the hero
reads all 6. The mirror asks about the `en` block alone, and rule 4 closes the other seven. A
key a translated block declares must also exist under `en`.

Rule 7 is the pairwise rule, and rule 6 cannot replace it. Rule 6 compares each language against
English alone, so a French block set to the Spanish values passes it byte for byte. That is a
French page serving Spanish text, shipped clean.

The `svc` clause of rule 4 is the one that reaches furthest. A translated `svc: []`, a
shortened card list or a malformed field used to pass every rule here. Rule 9 then took the
short translated list as the EXPECTED list, so the slot total fell and nothing failed. That is
a check that cannot fail, inside the gate written to stop exactly that.

Three blind spots of the same shape are closed with it. A value that is not a string is NAMED,
so `btn_start: 3` is a failure rather than an omission. The card count is pinned at 3, never
read from the English list. So a matched reduction of English and a translation cannot lower
what rule 9 expects. Rule 3 checks the English values for emptiness, because rule 5 reads
translated blocks alone.

`yaml.safe_load` is what makes the type rule possible. The check carried a hand-written reader
until 2026-09-18, and that reader returned the string `'3'` for both `btn_start: 3` and
`btn_start: "3"`. On that path the type rule could not fire at all, so the reader went and
`.github/workflows/translation-sync.yml` installs `python3-yaml` instead.

Rule 8 is the theme wiring. `theme-ael.scss` hides the sidebar search box and the colour-scheme
toggle from CSS, with no condition on it. `ael-extras.html` is what puts both back, in the top
app bar. A language that does not include it ships with no search box and no dark-mode toggle,
and the render reports nothing. Rule 8 names each required VALUE, never the key alone. On
2026-09-18 every project file named `theme-dark.scss` on its own. So a `--brand` or `Spectral`
probe stayed green while the language was un-wired from `theme-ael.scss`.

Rule 8 reads the PATH, not the file. Quarto reads these three keys under `format.html` and
nowhere else, so a value parked under `book:` satisfies a grep and changes nothing about the
render. The check parses the project file with `yaml.safe_load` and asks what path each key sits
at.

Rule 7 takes two exclusions, both measured on 2026-09-18 over 86 cross-language collisions. 84
are service-card hrefs, one string in every language by design. 2 are Spanish and Portuguese
cognates, `capítulos` and `idiomas`, which the two languages spell identically. Each allowlist
entry pins the key, the ordered pair `("es", "pt")` AND the exact value. Edit the Spanish string
and the entry stops matching, so the check fires rather than exempting in silence. Rule 6 takes
the href exclusion and no other.

The href exclusion names the FIELD as well as the shape, and `svc[i].href` is the whole of that
field. It matched any URL-shaped value until 2026-09-18. Give `fr` and `es` one identical
`btn_start` of `https://example.org/x` on that version, and both rules exempt it. A French page
carrying Spanish text then ships clean, whenever the shared string looks like a URL.

Remedy for rules 1 to 7: edit `landing.yml`. Remedy for rule 8: restore the missing line in
`content/<code>/_quarto.yaml`, copying it from a language the check reports as wired.

Expected output:

```
languages declared: 8 (en fr es vn jp pt tr ru)
project files wired to the theme and the app bar: 8 of 8
keys the hero reads: 18, plus the svc cards (from utils/landing-hero.R)
keys declared: 166 across the 7 translated blocks; 'en' declares 30
translated blocks complete: 7 of 7; a complete block declares 13 keys, and 2 pinned omissions are allowed
against 'en': 21 values match it and are service-card hrefs, which the href rule allows
pairwise: 28 ordered language pairs; 84 service-card hrefs and 2 allowed cognates skipped
problems: 0
```

With `--slots`, after a render, three more lines sit before `problems: 0`:

```
slots read: 231 across the 7 rendered page(s); 44 of them fall back to 'en'
slots expected: 231, which is 7 page(s) x (21 scalar slots + 4 fields x 3 cards)
slot mismatches: 0
```

### Rule 10, the completeness rule

Rule 10 asks every translated block for every translatable key. Rules 1 to 8 never ask. Replace
the `fr:` block with `fr: {}` on the 2026-09-18 version and all eight hold. The block declares
nothing, so every key it declares exists under `en`, no value is empty, and no value matches
another language. `keys declared:` falls from 166 to 142 and `problems:` stays 0. A
language that lost every translation looks clean, and that is how all eight heroes shipped in
English after the tagline was removed.

**A translatable key is one the hero reads and `INVARIANT` does not name.** That one line is
what separates a block nobody translated from a key that falls back on purpose. It comes from
`utils/landing-hero.R`, so no edit to `landing.yml` can lower it. Today it is 13: the 18 keys
the hero reads, less the 6 `INVARIANT` names, plus the `svc` list.

Three omissions stay legal, and a rule that rejected every omission would break all three:

- **A language-invariant key.** `INVARIANT` names 6: `btn_start_href`, `btn_offline_href`,
  `np_brand`, `np_btn`, `np_btn_href` and `np_links`. Each is a path, a URL or a brand name, so
  a translation of it would be the same string. No block declares one, and rule 10 never asks.
- **A pinned omission.** `OMISSIONS` names 2, both `stat_used_num`. The Spanish and Portuguese
  source pages read "3 millón de veces" and "3 milhão de vezes", singular after three. A block
  that copied one would carry the error into the hero, so the count falls back to English.
- **The fallback itself.** The hero reads `en` for any key the language omits, so the page still
  renders. Rule 10 changes nothing about that. It reports the gap and leaves the choice to a
  reader.

Every other omission is a fault, whether the block lost one key or all 13.

An `OMISSIONS` entry pins the key and the ONE language, so it weakens the gate for one value of
one block. Declare the key again and the entry stops matching. Rule 10 then reports the entry
as stale. A stale entry would otherwise permit the same loss a second time.

Remedy for rule 10: translate the key and add it to that language's block. Where the source
carries an error the translation would import, add an `OMISSIONS` entry and write the reason in
it.

### Rule 9, the transport rule

Rule 9 reads a rendered page, so `check-sync.sh` does not run it. Run it locally with:

```
checks/render-gate.sh --landing
```

That mode renders every translated `index.qmd` with execution, runs rule 9 over the pages, and
deletes every folder and file the render created. It takes about 20 seconds and it is the only
mode of `render-gate.sh` that executes R. It needs the R packages `yaml` and `here`, which
`utils/landing-hero.R` loads.

Rule 9 reads 33 slots on each of the 7 translated pages, 231 in all, and compares each one
against its source. 166 of those values come from the language's own block, which is every key
`keys declared:` counts. 44 fall back to English. 42 are the 6 `INVARIANT` keys on all 7
pages, and 2 are `stat_used_num` on the Spanish and the Portuguese page. The last 21 are the 3
slots `landing.yml` does not key, one set per page:

| Slot | Source |
|---|---|
| `hero_title` | `languages.yml`, the `title` of this language |
| `stat_chapters_num` | `content/en/_quarto.yaml`, `book.chapters` less `index`, `about` and `acknowledgements` |
| `stat_languages_num` | `languages.yml`, the count of declared codes |

Without this rule a value that never reaches its slot ships clean.

**Rule 9 read 24 slots per page until 2026-09-18.** It skipped both button targets, both
computed counts, the hero title and 4 of the 6 nonprofit-band fields. Every one of those is a
rendered slot, `slots read:` counted none of them, and the printed count was honest about its
own narrower coverage.

**The total is an assertion, not a line of output.** Rule 9 computes it as pages x (21 scalar
slots + 4 fields x 3 cards) and fails on any deviation, in either direction. The 3 is pinned in
the check, never read from `landing.yml`, so the data cannot move the expectation. A printed
number nobody compares is decoration, and a slot that goes unread lowers the total in silence.

**A pinned total stops the data moving it and cannot stop the slot list moving it.** Delete one
name from `SCALAR_SLOTS` and `slots read:` and `slots expected:` both fall to 32, in step, and
the run stays green. So the check asks `utils/landing-hero.R` for its key list and names any
key `SCALAR_SLOTS` omits. That assertion needs no rendered page, and it runs in every mode.

Rule 9 reads every slot with `findall`, never `search`, and requires exactly one occurrence.
`search` stops at the first hit, so a second copy of a slot carrying the wrong value would pass
while the total still matched. Upward drift has to fail the count as surely as downward drift.

**Rule 9 verifies the strings the server sends. It cannot verify anything the browser builds.**
`ael-extras.html` builds the top app bar in JavaScript at load. Rule 8 checks that every project
file includes that script, and nothing here verifies what the script then builds. The
measurement below is on the deployed site, `origin/staging` at `f18ff0e4`, the deploy of
`2bdfad56`.

| Measured on `origin/staging` at `f18ff0e4` | Result |
|---|---|
| `<div class="dropdown" id="languages-links-parent">` as a real element | 416 of the 833 HTML files, which is every rendered page |
| language links inside that element, on `en/index.html` | 7 |
| `class="ael-appbar"` as a real element, on `en/index.html` | 0 |
| `ael-appbar` anywhere in `en/index.html` | 5, and all 5 are script text |
| `ael-appbar`, `--brand`, `Spectral`, `ael-hero` and `ael-navhelp` in the compiled CSS | present in the light bundle and in the dark bundle |

The injector ran in production. The compiled CSS carries every theme token, and the switcher
parent is on every rendered page. The app bar is absent from the served HTML because the script
builds it in the browser. The other 417 HTML files of that deploy are redirect stubs, and a stub
carries no chrome.

A headless browser would close this limit. It would load an assembled page, run the script, and
assert two things. `.ael-appbar` MUST exist, and `#languages-links-parent` MUST have
`.ael-appbar-tools` as its parent. `ael-extras.html` makes that move at line 86. This machine
carries no chromium, no playwright, no puppeteer and no chromote, so the gate does not run it.

Two flags aim it elsewhere:

- `--pages <template>` says where a rendered page is. `{code}` is the language code, and the
  default is `content/{code}/html_outputs/index.html`.
- `--only <code>` checks one language. It accepts the main language too, and the expected slot
  total follows the selection.

`--slots` refuses to run when a rendered page is absent, and it never skips. Check 12 covers
that refusal with a second fixture, because the first one renders nothing.

Remedy for rule 9: edit `landing.yml`. A slot mismatch with no `landing.yml` fault is a defect
in `utils/landing-hero.R`, or in this check's own slot patterns.

**CI runs rule 9 in the render leg of `.github/workflows/build-deploy.yml`,** one language per
leg, after the render and before the artifact upload. The leg writes that language's site to
the root of its output directory, so the step passes
`--only "$LANG_CODE" --pages html_outputs/index.html`. The leg also renders with `--no-inject`,
so nothing has re-serialised the page and the slot patterns read what Quarto wrote. A leg whose
hero is broken fails before it uploads anything.
`.github/workflows/translation-sync.yml` runs every rule but rule 9. It renders no landing
page, and its runner carries neither the `here` R package nor a language image.
