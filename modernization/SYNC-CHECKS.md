# Keeping the translations in sync: the checks, and how to repeat them

Run `modernization/check-sync.sh` from the repository root. It changes nothing, takes about a
minute, and ends with `IN SYNC` or `DRIFT`. Add `--render` for the render gate, about 20
minutes. Repeat after any English chapter changes, and every few months regardless.

Every check below was used in the 2026-09 fix pass, recorded in `FIX-PASS.md`. Each has a
script, an expected output, and a remedy. The remedies are the same scripts and workflows
that did the work the first time, so a drift of the same kind costs minutes, not days.

## What "in sync" means

English is the reference. For every chapter listed in `_quarto.yml` and every language in
`babelquarto.languages`:

| Property | Expected | Check | Remedy |
|---|---|---|---|
| the translated file exists | 336 of 336 | check 1 | translate the chapter |
| code chunk count equals the English | 336 of 336 | check 1 | `workflows/epirhandbook-align-chunks.js`, one agent per chapter, then `sync-chunks.py` |
| heading sequence equals the English, count and level, fenced blocks stripped | 336 of 336 | check 1 | `workflows/epirhandbook-align-headings.js`, one agent per chapter |
| every heading with an English `{#id}` carries that id | 0 headings differ, 0 dead links | check 2 | `sync-anchors.py`, no agent |
| every aligned chunk's code equals the English, comments free | 0 chunks differ | check 3 | `sync-chunks.py`, no agent |
| inline code spans in prose name things the English names | informational | check 4 | `workflows/epirhandbook-inline-pass.js` over the new suspects |
| every changed chapter renders without execution, fences balanced | 0 fail | `render-gate.sh` | read the log under `/tmp/render-gate/` |
| no R chunk parses worse than the English chunk | 0 files worse | `chunk-parse-gate.py <base>` | the sync, or a source defect |

Check 4 is informational because a suspect span is often right: a placeholder the reader
replaces, or a word the author put in code font. The baseline after the 2026-09-02 inline pass
is 360 suspects, all judged placeholders or noise. A rise above that is what to look at, not
the number itself. Files without an English chapter, such as `across.*` and `first_page.*`,
are skipped and listed; that is expected.

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
  broken YAML front matter, an unclosed fence, a demoted heading. A check that has not been
  seen to fail is not a check.

## Order, when several things drift at once

1. `check-sync.sh` to see what.
2. Chunk count or heading sequence first, with the alignment workflows. The syncs pair by
   position and need the counts to match.
3. `sync-chunks.py`, then `sync-anchors.py`.
4. `chunk-parse-gate.py <base>` and `render-gate.sh <base>` on the changed files.
5. Commit each step on its own, signed, and run `check-sync.sh` again.
