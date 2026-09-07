# Keeping the translations in sync: the checks, and how to repeat them

Run `modernization/check-sync.sh` from the repository root. It changes nothing, takes about a
minute, and ends with `IN SYNC` or `DRIFT`. Add `--render` for the render gate, about 20
minutes. Repeat after any English chapter changes, and every few months regardless.

Every check below was used in the 2026-09 fix pass, recorded in `FIX-PASS.md`. Each has a
script, an expected output, and a remedy. The remedies are the same scripts and workflows
that did the work the first time, so a drift of the same kind costs minutes, not days.

## What "in sync" means

English is the reference. For every chapter listed in `_quarto.yml` and every language in
`babelquarto.languages` (49 chapters x 7 languages since the GIS chapter returned on 2026-09-02):

| Property | Expected | Check | Remedy |
|---|---|---|---|
| the translated file exists | 343 of 343 | check 1 | translate the chapter |
| code chunk count equals the English | 343 of 343 | check 1 | `workflows/epirhandbook-align-chunks.js`, one agent per chapter, then `sync-chunks.py` |
| heading sequence equals the English, count and level, fenced blocks stripped | 343 of 343 | check 1 | `workflows/epirhandbook-align-headings.js`, one agent per chapter |
| every heading with an English `{#id}` carries that id | 0 headings differ, 0 dead links | check 2 | `sync-anchors.py`, no agent |
| every aligned chunk's code equals the English, comments free | 0 chunks differ | check 3 | `sync-chunks.py`, no agent |
| inline code spans in prose name things the English names | informational | check 4 | `workflows/epirhandbook-inline-pass.js` over the new suspects |
| every changed chapter renders without execution, fences balanced | 0 fail | check 6, with `--render` | read the log under `/tmp/render-gate/` |
| no R chunk parses worse than the English chunk | 0 files worse | `chunk-parse-gate.py <base>` | the sync, or a source defect |
| every internal link resolves | 0 dead links in the 400 declared files | check 5 | `rewrite-links.py`, no agent |

Check 4 is informational because a suspect span is often right: a placeholder the reader
replaces, or a word the author put in code font. The baseline after the 2026-09-02 inline pass
is 356 suspects, all judged placeholders or noise; the GIS chapter, restored the same day,
added one, a French verb in code font. A rise above that is what to look at, not
the number itself. Files without an English chapter, such as `across.*` and `first_page.*`,
are skipped and listed; that is expected.

## Check 5: internal links

Run `python3 modernization/check-links.py`. `check-sync.sh` runs it as check 5. It reads the
400 declared files, which are `index.qmd` and the 49 chapters, in English and in the 7
translation languages. It prints one line for each dead link and exits 1 when it finds one.

```
DEAD chapters/basics.qmd:372 #objectstructure (no id objectstructure on this page)
```

A link is dead when its `.qmd` target does not exist, or when the target page does not define
the `#fragment`. The line number is the first source line that holds the target. Pandoc's
markdown reader gives no source position, so `?` after the number means the target occurs on
more than one line.

Pandoc renders each file to one standalone HTML page, `pandoc -s -f markdown -t html`. Python's
`html.parser` reads that page once. The ids are the ones a browser sees: `id` on any element,
and `name` on an `<a>` element. The links are the `href` of every `<a>` element.

Pandoc resolves a heading, a div, a span, a metadata title, raw HTML, an HTML comment and a
character reference into that one page. So the checker does not re-implement pandoc's identifier
rule, and it does not read markdown itself. A link in a YAML `title` renders on the page, so it
counts. None of the 400 declared files carries such a link today.

The checker takes three options.

- `--summary` prints the counts and no link lines. It gives files scanned, the pandoc binary
  and its version, one line for each language, `language-mismatch N` and `dead N`.
- `--fixture <dir>` uses every `*.qmd` in that directory as the file set.
- `--pandoc <cmd>` names the binary. The default is `quarto pandoc`, and plain `pandoc` when
  quarto is not on PATH.

Check 5 prints the counts, from `--summary`. When a link is dead it prints the DEAD lines too,
and `check-sync.sh` ends with `DRIFT`.

The sweep of 2026-09-07 cleared the backlog. It rewrote 1,854 links in 240 of the 400 declared
files, and the checker now reports `dead 0`. All but six were cross-chapter links written as a
bare `#anchor`. The counts before the sweep were 450 Spanish, 445 Japanese, 444 Portuguese,
427 French, 28 Turkish, 22 English, 20 Vietnamese and 18 Russian.

`language-mismatch` counts a live link from a page of one language to a `.qmd` file of another.
It is informational. The file exists, so the link works.

One step comes before the parse. Pandoc reads the knitr chunk header ```` ```{r} ```` as a
paragraph, not as a fence. The checker rewrites each chunk header to ```` ```{.r} ````, line
for line, as knitr does. Without that step every `#` comment in an R chunk becomes a heading
with an id. It rewrites a fence line indented by fewer than four spaces, which is the CommonMark
rule. An indented literal fence inside a paragraph changes nothing.

### Remedy: rewrite-links.py

`modernization/rewrite-links.py` rewrites every dead link the checker reports.

1. Run `python3 modernization/check-links.py` and read the DEAD lines.
2. Add a row to `modernization/link-map.tsv` for each target the table does not hold.
3. Run `python3 modernization/rewrite-links.py --dry-run` for the count.
4. Run `python3 modernization/rewrite-links.py` to write the files.

The table columns are `old_id`, `stem`, `anchor` and `note`. `old_id` is the link target exactly
as the checker reports it. `stem` is the chapter that holds the content today. `anchor` is an
in-page id, and it stays empty unless every language version of that chapter defines that id. An
anchor that only English defines is a dead link in the other seven languages.

The script writes nothing until every file rewrites cleanly. It stops when the table holds no
row for a reported target. It also stops when the number of links it finds in prose differs from
the number of findings. It skips a fenced code block and an HTML comment, because pandoc reads
no link there.

## Do not render an English chapter with the gate

`render-gate.sh` renders translated chapters only, on purpose. Rendering a main-language
chapter in this book project makes quarto rewrite `.gitignore` and delete three tracked files
under `site_libs/quarto-search/`; observed on 2026-09-02 and restored from HEAD. Check an
English chapter with the fence-parity count and the R parse gate instead.

## What the checks do not cover

- Meaning. A translation that says something the English does not, in prose, is invisible to
  every check here. That was the prose sweep, `RESUME.md`, at about 100,000 tokens per
  chapter-language pair; repeat it only for chapters whose English prose changed.
- Comments inside chunks. The sync keeps a translated comment where its code line survives
  and falls back to the English comment otherwise; nothing checks that comments are translated.
- Plot labels and other display strings, which the sync sets to the English.
- The 17 English source defects in `findings/fix-pass/source-defects.tsv`, which the
  translations now mirror on purpose.

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
