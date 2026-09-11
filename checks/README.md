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

Every check below was used in the 2026-09 fix pass. `archive/modernization` holds the record
of that pass. Each check has a script, an expected output, and a remedy. The remedies are the
same scripts and agent workflows that did the work the first time. A drift of the same kind
then costs minutes, not days.

## What "in sync" means

The repository declares its layout in two files. `languages.yml` names the eight languages, and
`content/en/_quarto.yaml` names the 50 stems. Every chapter file is `content/<lang>/<stem>.qmd`,
so a file's language is the folder that holds it.

English is the reference. Checks 1 to 3 pair each translated chapter with
`content/en/<stem>.qmd`. That set is 49 chapters and 7 translation languages: the landing page
`index.qmd` and English itself stay out of it. 49 x 7 has held since the GIS chapter returned
on 2026-09-02.

| Property | Expected | Check | Remedy |
|---|---|---|---|
| the translated file exists | 343 of 343 | check 1 | translate the chapter |
| code chunk count equals the English | 343 of 343 | check 1 | the align-chunks agent workflow, one agent per chapter, then `sync-chunks.py` |
| heading sequence equals the English, count and level, fenced blocks stripped | 343 of 343 | check 1 | the align-headings agent workflow, one agent per chapter |
| every heading with an English `{#id}` carries that id | 0 headings differ, 0 dead links | check 2 | `sync-anchors.py`, no agent |
| every aligned chunk's code equals the English, comments free | 0 chunks differ | check 3 | `sync-chunks.py`, no agent |
| inline code spans in prose name things the English names | informational | check 4 | the inline-pass agent workflow over the new suspects |
| every changed chapter renders without execution, fences balanced | 0 FAIL | check 6, with `--base` or `--render` | read the log under `/tmp/render-gate/` |
| no R chunk parses worse than the English chunk | 0 files worse | check 8, with `--base` or `--render` | the sync, or a source defect |
| every internal link resolves, stays on its page and stays in its language | 0 dead, 0 same-page, 0 cross-language and 0 unterminated links in the 400 declared files | check 5 | `rewrite-links.py`, no agent |
| no chunk that executes names the `data/` folder, outside the two chapters that teach file paths | 0 lines in the 400 declared files | check 7 | load the data with `appliedepidata::get_data()`, or set `eval=F` |
| the eight language folders, project files, chapter files, manifest rows and alias lines agree | `8 languages, 50 stems, 393 aliases, drifted: 0` | check 9 | edit the file the DRIFT line names |

Each agent workflow named in the Remedy column is a `.js` file in the workflows folder of
`archive/modernization`.

Check 4 is informational because a suspect span is often right: a placeholder the reader
replaces, or a word the author put in code font. The baseline after the 2026-09-02 inline pass
is 356 suspects, all judged placeholders or noise; the GIS chapter, restored the same day,
added one, a French verb in code font. A rise above that is what to look at, not
the number itself. Check 4 measures the declared set: the 49 chapters in the 7 translation
languages. A file that `content/en/_quarto.yaml` does not declare is not measured here, and
check 9 reports it. A declared file that is missing gets a one-line note, and check 9 reports
that too.

## Check 5: internal links

Run `python3 checks/check-links.py`. `check-sync.sh` runs it as check 5. It reads the
400 declared files, which are `index.qmd` and the 49 chapters, in English and in the 7
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
counts. None of the 400 declared files carries such a link today.

The checker takes three options.

- `--summary` prints the counts and no link lines. It gives files scanned, the pandoc binary
  and its version, one line for each language, `same-page N`, `language-mismatch N`,
  `unterminated-links N` and `dead N`.
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
400 declared files as check 5. Three rules govern the `data/` folder.

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
`<base>`. It needs quarto and git. It runs no R, because `--no-execute` skips the knitr engine.

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
close inside its paragraph now stops the gate with `FAIL-placeholder`. The 400 declared files
hold 81 inline R expressions, and none of them crosses a line break.

The gate stops with exit 2, before it renders anything, in four cases.

- A base or a head that is not a commit.
- A `git diff` that fails.
- A temporary copy path that the repository tracks.
- A temporary copy path that already exists.

The gate skipped a file with inline R until 2026-09-09, and 17 of the 99 files then in the
changed set carried one. A broken YAML header in `content/es/gis.qmd` passed that gate,
because the gate never read the file.

A file with an odd number of fence lines FAILS before the render. Pandoc renders an unclosed
fence with exit 0, so the render alone cannot see that class.

Per-file output goes to `/tmp/render-gate/<stem>.log`, and the result of each file to
`/tmp/render-gate/SUMMARY.tsv`.

## Check 8: the chunk parse gate

Run `python3 checks/chunk-parse-gate.py <base> [head]`. `check-sync.sh` runs it as check 8, with
the base it was given. It parses every R chunk of every changed translated chapter with R, in
the version at `<base>` and in the version in the working tree.

It compares the two versions chunk index by chunk index. A chunk index that fails after and did
not fail before is a regression, unless the English chunk at that index fails too. A count
comparison reads `same` when one chunk breaks and another is repaired in the same file, so the
gate compares indices instead.

The gate stops with exit 2 in four cases.

- A base or a head that is not a commit.
- A `git` command that fails.
- `Rscript` that is not on PATH.
- `Rscript` that returns non-zero. The gate prints `Rscript`'s own stderr.

## Check 9: the layout

`check-sync.sh` runs check 9 itself, and it needs no base commit. It reads `languages.yml`, the
eight `content/<lang>/_quarto.yaml` project files, `docker-images.yml` and the front matter of
the 400 declared files. Regular expressions read every one of them, because the
translation-sync runner carries no yaml module.

It prints one summary line, and one `DRIFT` line for each finding:

```
   layout: 8 languages, 50 stems, 393 aliases, drifted: 0
```

A finding sets the DRIFT exit. Check 9 reports nine kinds.

- A language `languages.yml` declares with no `content/<code>/_quarto.yaml`.
- A `content/<x>/` folder that holds `.qmd` files for a code `languages.yml` does not declare.
- A project file whose flattened chapter list differs from `content/en/_quarto.yaml` in set or
  in order, or whose part count differs.
- A project file whose `lang` is not its own folder, or whose `book.title` differs from the
  title `languages.yml` gives that code.
- A declared stem with no file in one of the eight language folders. `index` is a declared
  stem, so every folder needs its own landing page.
- A `docker-images.yml` that does not hold exactly one row per declared stem, or that holds a
  row for something else.
- A `docker-images.yml` row under `chapters:` with no `stem:` key, or with no `image:` key.
  The `stem:` key names the chapter, and the `image:` key names the image CI renders it in.
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

Check 9 reads the aliases from the block list under the front matter's top-level `aliases:`
key. A list under another key counts for nothing, and neither does a list below the front
matter.

A missing file never stops check 9. It reports the file, skips the comparisons that need it,
and still reports what it can see. A missing `content/en/_quarto.yaml`, a missing
`docker-images.yml` and a missing `languages.yml` each give check 9 one `DRIFT` line and no
traceback.

Checks 1, 4, 5 and 7 read `languages.yml` without a guard. Delete that file and each of the
four raises a traceback, above check 9's own `DRIFT languages.yml` line.

Checks 1, 5 and 7 read the stem list from `content/en/_quarto.yaml`. Without that file each one
stops with a one-line message, and check 9 names the file to restore.

### Remedy

Edit the file the `DRIFT` line names. A drifted chapter list is the common finding. You add a
chapter to seven of the eight project files and miss one. Nothing else in the repository
notices.

## Do not render an English chapter with the gate

`render-gate.sh` renders translated chapters only, on purpose. Rendering a main-language
chapter in this book project makes quarto rewrite `.gitignore`. On 2026-09-02 it also deleted
the three `site_libs/quarto-search/` files the repository tracked then, and `archive` holds
those files now. Check an English chapter with the fence-parity count and the R parse gate
instead.

## What the checks do not cover

- Meaning. A translation that says something the English does not, in prose, is invisible to
  every check here. That was the prose sweep, at about 100,000 tokens per chapter-language
  pair, and `archive/modernization` records it. Repeat it only for chapters whose English
  prose changed.
- Comments inside chunks. The sync keeps a translated comment where its code line survives
  and falls back to the English comment otherwise; nothing checks that comments are translated.
- Plot labels and other display strings, which the sync sets to the English.
- The 17 English source defects that the translations now mirror on purpose. The
  source-defects table of the fix-pass record lists them, under `archive/modernization`.

## The reasoning behind the design, so it is not re-derived

- Code chunks are copied, not reviewed, because 94% of aligned chunks were identical or
  differed only in comments, and the 459 that differed in code held defects far more often
  than deliberate choices. Renamed objects were rare, Portuguese-only, and half inconsistent.
- Comments are merged by line, not translated, because a translation pass over 4,500 comments
  would cost more than the whole prose sweep and add risk; a comment on a code line the
  translator got wrong falls back to English.
- Anchors take the English id because cross-links are written English-style throughout the
  corpus and a divergent id is a dead link; only one link in the corpus ever targeted a
  translation's own id.
- Heading and chunk alignment use one agent per chapter because the edit is structural and
  small, and the mechanical count afterwards is the proof, not the agent's report.
- Every check was proved red before it was trusted: a corrupted span, an extra parenthesis, a
  broken YAML front matter, an unclosed fence, a demoted heading. Check 3 was proved both ways
  on 2026-09-02: one changed code token inside a Turkish chunk reports DRIFT; a changed or added
  comment inside a chunk stays IN SYNC. That is the rule: code exact, comments free. A check
  that has not been seen to fail is not a check.

## Order, when several things drift at once

1. `check-sync.sh` to see what.
2. Chunk count or heading sequence first, with the alignment workflows. The syncs pair by
   position and need the counts to match.
3. `sync-chunks.py`, then `sync-anchors.py`.
4. `check-sync.sh --base <base>`, which adds check 8 and check 6 on the changed files.
5. Commit each step on its own, signed, and run `check-sync.sh` again.
