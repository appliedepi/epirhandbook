# The repository's checks: what they cover, and how to run them

Run `checks/check-sync.sh` from the repository root. It changes nothing, takes about a
minute, and ends with `IN SYNC` or `DRIFT`. Add `--render` for the render gate, about 20
minutes. Repeat after any English chapter changes, and every few months regardless.

Every check below was used in the 2026-09 fix pass. `archive/modernization` holds the record
of that pass. Each check has a script, an expected output, and a remedy. The remedies are the
same scripts and agent workflows that did the work the first time. A drift of the same kind
then costs minutes, not days.

## What "in sync" means

English is the reference. For every chapter listed in `_quarto.yml` and every language in
`babelquarto.languages` (49 chapters x 7 languages since the GIS chapter returned on 2026-09-02):

| Property | Expected | Check | Remedy |
|---|---|---|---|
| the translated file exists | 343 of 343 | check 1 | translate the chapter |
| code chunk count equals the English | 343 of 343 | check 1 | the align-chunks agent workflow, one agent per chapter, then `sync-chunks.py` |
| heading sequence equals the English, count and level, fenced blocks stripped | 343 of 343 | check 1 | the align-headings agent workflow, one agent per chapter |
| every heading with an English `{#id}` carries that id | 0 headings differ, 0 dead links | check 2 | `sync-anchors.py`, no agent |
| every aligned chunk's code equals the English, comments free | 0 chunks differ | check 3 | `sync-chunks.py`, no agent |
| inline code spans in prose name things the English names | informational | check 4 | the inline-pass agent workflow over the new suspects |
| every changed chapter renders without execution, fences balanced | 0 fail | check 6, with `--render` | read the log under `/tmp/render-gate/` |
| no R chunk parses worse than the English chunk | 0 files worse | `chunk-parse-gate.py <base>` | the sync, or a source defect |
| every internal link resolves, stays on its page and stays in its language | 0 dead, 0 same-page and 0 cross-language links in the 400 declared files | check 5 | `rewrite-links.py`, no agent |
| no chunk that executes names the `data/` folder, outside the two chapters that teach file paths | 0 lines in the 400 declared files | check 7 | load the data with `appliedepidata::get_data()`, or set `eval=F` |

Each agent workflow named in the Remedy column is a `.js` file in the workflows folder of
`archive/modernization`.

Check 4 is informational because a suspect span is often right: a placeholder the reader
replaces, or a word the author put in code font. The baseline after the 2026-09-02 inline pass
is 356 suspects, all judged placeholders or noise; the GIS chapter, restored the same day,
added one, a French verb in code font. A rise above that is what to look at, not
the number itself. A translated file without an English chapter is skipped and listed.
`chapters/` holds none today.

## Check 5: internal links

Run `python3 checks/check-links.py`. `check-sync.sh` runs it as check 5. It reads the
400 declared files, which are `index.qmd` and the 49 chapters, in English and in the 7
translation languages. It prints one line for each link it rejects, and exits 1 when it finds
one. It rejects three link forms.

```
DEAD chapters/basics.qmd:372 #objectstructure (no id objectstructure on this page)
SAME-PAGE chapters/basics.qmd:372 basics.qmd#objects
LANGUAGE-MISMATCH chapters/packages_suggested.es.qmd:158 data_used.qmd
```

A link is dead when its `.qmd` target does not exist, or when the target page does not define
the `#fragment`. The line number is the first source line that holds the target. Pandoc's
markdown reader gives no source position, so `?` after the number means the target occurs on
more than one line.

Two rules cover the other two forms.

- Write a link to a section of the same page as `#id`. The long form `file.qmd#id` is
  `same-page`. It resolves, and it breaks as soon as the file is renamed.
- A link never crosses languages. A link from a page of one language to a `.qmd` file of
  another is `language-mismatch`. Point it at the target in its own language.

Pandoc renders each file to one standalone HTML page, `pandoc -s -f markdown -t html`. Python's
`html.parser` reads that page once. The ids are the ones a browser sees: `id` on any element,
and `name` on an `<a>` element. The links are the `href` of every `<a>` element.

Pandoc resolves a heading, a div, a span, a metadata title, raw HTML, an HTML comment and a
character reference into that one page. So the checker does not re-implement pandoc's identifier
rule, and it does not read markdown itself. A link in a YAML `title` renders on the page, so it
counts. None of the 400 declared files carries such a link today.

The checker takes three options.

- `--summary` prints the counts and no link lines. It gives files scanned, the pandoc binary
  and its version, one line for each language, `same-page N`, `language-mismatch N` and
  `dead N`.
- `--fixture <dir>` uses every `*.qmd` in that directory as the file set. It reads the language
  of each file from the name, so a fixture can carry a cross-language link.
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
DATA-READ chapters/standardization.fr.qmd:147
DATA-WRITE chapters/importing.es.qmd:412
```

`DATA-READ` names a line outside the two chapters that teach file paths. `DATA-WRITE` names a
line inside those two that also calls a function that writes. Those functions are `export`,
`write*`, `save`, `saveRDS`, `st_write`, `file.copy`, `file.create`, `dir.create`,
`dir_create`, `file_create`, `download.file` and `unzip`. Either line makes `check-sync.sh`
end with `DRIFT`.

The checker takes two options.

- `--summary` prints the counts and no detail lines. It gives files scanned, one line for each
  language, and `data-reads N`. That count holds both kinds of line.
- `--fixture <dir>` uses every `*.qmd` in that directory as the file set. It reads the language of
  each file from the name.

The check is lexical. It reads the source line, and it does not follow a path through a variable.
A chunk that builds a path on one line and reads it on another passes.

### Remedy

1. Load the data with `appliedepidata::get_data()`.
2. Set `eval=F` on a chunk whose subject is the path itself, not the data.
3. Delete a chunk that writes into `data/`.

The root `CLAUDE.md` carries the same rule, for an agent that edits a chapter.

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
4. `chunk-parse-gate.py <base>` and `render-gate.sh <base>` on the changed files.
5. Commit each step on its own, signed, and run `check-sync.sh` again.
