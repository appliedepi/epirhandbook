# Fix pass: verify and fix the 1617 prose-sweep findings in one read

Run on 2026-09-01 and 2026-09-02 from commit `52442a79`. This replaces Phase D, E and F of
`SWEEP-PLAN.md` under the owner's amendment: verification and fixing are one pass, and each
agent reads only the extracted spans, never a whole chapter.

## Result

| Verdict | Findings | Meaning |
|---|---|---|
| fixed | 1511 | The finding was correct. The translated file is edited. |
| deferred | 76 | The finding was correct, but the fix is outside the pass's permissions. `findings/fix-pass/deferred.tsv`. |
| rejected | 30 | The finding was wrong or not a defect. Nothing edited. `findings/fix-pass/rejected.tsv`. |

1511 + 76 + 30 = 1617. Every finding has exactly one of the three outcomes. The 26 findings whose
spans did not parse ran last, as nine `odd-*` batches, after the owner said to do the whole set:
23 fixed, 3 deferred. `findings/fix-pass/unextractable-spans.tsv` records how each span was read.

By language, over the 1591 extractable findings:

| Language | fixed | deferred | rejected |
|---|---|---|---|
| tr | 323 | 5 | 6 |
| jp | 253 | 11 | 6 |
| pt | 208 | 22 | 7 |
| fr | 204 | 19 | 3 |
| ru | 171 | 2 | 3 |
| es | 166 | 10 | 1 |
| vn | 163 | 4 | 4 |

The diff from `52442a79` touches 317 translated chapter files: 1637 insertions, 1519 deletions.
No English chapter, no `*.de.qmd` and no file outside `chapters/` changed. No existing `{r` chunk was edited; `basics.fr.qmd` gained two chunks copied verbatim from the English, and `errors.tr.qmd` had two error-output fences corrected to R's literal English error text.
Nothing is pushed.

## Two named sets that need the owner, and a third for the English

**Deferred, 76 findings plus 5 review rows.** 65 name a defect inside a code chunk, which this pass may not edit:
a wrong package name in `p_load()`, a misspelled argument, a French translation of an R keyword.
7 name a defect in the English source. 6 need a structural change. Each row carries the agent's
one-sentence reason. These are the highest-value residue: a code-chunk defect makes a reader
type code that cannot run.

**Rejected, 30 findings.** Read them before you trust the drift file's counts. Several are
places where the translation is right and the English is wrong, such as `%M` for minutes in
the Portuguese and Vietnamese date chapters.

**Source defects, 11 English places.** `findings/fix-pass/source-defects.tsv`. Every one was
found because a translation was made to match the English and a reviewer then showed the
English contradicts its own code chunk, its own figure, or has a dead link. Nothing in this pass
edits an English file.

## Method

1. `extract-spans.py` reads every finding's spans from the files at `52442a79` with `git show`,
   never from the working tree, with 8 lines of context each side. Deterministic. Proved red:
   a span corrupted to line 9999 lands in `unextractable.tsv` and drops out of the evidence.
2. `make-batches.py` groups by language and kind, at most 20 findings per batch, and schedules
   waves in which no two batches share a file. 97 batches.
3. `workflows/epirhandbook-fix-pass-wave.js` runs one wave. One opus agent at xhigh per batch.
   The agent reads only its evidence file, edits with exact string replacement, and writes
   `findings/fix-pass/<batch>.json` with a verdict and the exact old and new text per finding.
4. `reconcile-fix-pass.py` checks every result file against the working tree: ids by name,
   new text present, old text absent, no change outside the batch's files. Proved red three ways.
5. `commit-batch.sh` commits one batch, signed, after the checker passes. 97 batches, 97 commits.

**Count artifacts, not returns.** Every wave was reconciled from the result files on disk.
No agent died after writing in this run, but the wave-2 quota kill left two partial edits with
no result file; they were stashed and the wave re-run from a clean tree.

## Cost

| Item | Value |
|---|---|
| Subagent tokens, 97 completed agents | 9,617,128 |
| Subagent tokens lost to the quota kill on wave 2 | 976,612 |
| Per completed agent, mean | 99,145 |
| Wall clock per wave of 14 | 8 to 11 minutes |
| Subagent tokens, 9 odd-span batches | 506,954 |
| Subagent tokens, 18 review agents | 2,913,765 |
| Subagent tokens, 8 deferred-pass agents | 723,262 |
| Subagent tokens, 22 inline-pass agents | 1,976,923 |
| Subagent tokens, 18 chunk-alignment agents | 1,184,297 |
| Subagent tokens, 14 heading-alignment agents | 767,127 |
| Subagent tokens, 14 English source-fix agents | 747,328 |
| Subagent tokens, 6 mirror-pass agents | 384,273 |
| Subagent tokens, all passes | 20,198,999 |
| Codex, Turkish, two calls | 375,699 and 199,301 tokens |

The owner's estimate of 2.5M tokens assumed about 30,000 per agent. The fixed overhead of an
agent that reads a 40 to 60 KB evidence file and makes 15 to 20 edits is about three times that.
On this session's first two batches, in the harness's token unit,
`tokens ~= 64,000 + 600 * evidence_KB`, fitted on 39 and 63 KB. It predicted wave 1 8% low.

## Independent check: codex, one language per call

The diff is where a wrong edit is visible. Codex read each language's diff with the verdicts
and the current chapter files, read-only, at reasoning effort high. Verdicts are in `reviews/`.

| Call | Hunks | Verdict | Verified repairs | Rejected claims |
|---|---|---|---|---|
| tr part 1 | 165 | BLOCK, 22 | 24, see commit `4a05d937` | 2 |
| tr part 2 | 131 | BLOCK, 26 | 1, see commit `ada77630` | 5, and 20 were the part-1 repairs |
| jp | 228 | none: cut off by the codex usage limit after 320,388 tokens | n/a | n/a |
| pt | 179 | none: cut off by the codex usage limit | n/a | n/a |
| es, fr, ru, vn | 150, 174, 154, 147 | not started: the owner chose not to wait for codex | n/a | n/a |

Four defect classes came out of the Turkish review, and each was then swept mechanically across
all seven languages: an inserted link that points at the English chapter, a translated R literal,
a lost trailing hard break, and a literal folder name translated. The sweep found one more
Portuguese literal and 13 lost hard breaks in three languages. The wave brief gained one rule
per class before the last three waves ran.

Two codex runs died with "Selected model is at capacity" when four ran at once. Two at a time
was stable until the owner's codex usage limit tripped at about 02:15 on 2026-09-02; it resets
at 06:14. `codex-bundle.sh <lang> 52442a79 HEAD <lang>` rebuilds any language's workspace, and
`codex-prompt.txt` is the prompt. The owner decides whether to fund the six remaining calls.

**Claude review of the six other languages.** With codex blocked, the owner said to do it
without codex. Eighteen opus agents at xhigh, one per diff part of about 90 KB, read all 1032
hunks of es, fr, jp, pt, ru and vn with the codex brief, flag-only. `reviews/claude-fixpass/`
holds the 18 result files. They flagged 62 hunks: 21 broken markup, 20 not fluent, 16 wrong
meaning, 3 wrong insertions, 2 wrong removals. Every flag was verified against the current file
and the English. 52 were applied in commits `b01db9d6` and `f6e8ced4`. 10 were rejected: 6
match the English source word for word and are in `source-defects.tsv`; 4 name a defect
inside a code chunk and are appended to `deferred.tsv`. This is one model family reviewing its
own family's work, which the owner's standing rule says not to trust alone; it stands in for
the codex calls the usage limit blocked, and the owner chose it.

## Deferred pass: the code-chunk defects

The owner then asked for the deferred set to be fixed with subagents. Eight opus agents at
xhigh, one per language and at most 20 findings each, with a brief that MAY edit inside a
code chunk of a translated file to make it do what the English chunk does, and MAY add a chunk
the translation lacks, copied verbatim. Still forbidden: renaming a translator's own valid and
consistent object or column name, and any edit to an English file.

| Outcome | Rows |
|---|---|
| fixed | 67 |
| rejected: the translation already matched the English, or the English is the defective side | 10 |
| still deferred | 4 |

The four still open: two French sentences in `grouping` where the French states dplyr's
behaviour correctly and the English inverts it; a Vietnamese date-format list where the
Vietnamese is right; and one Russian legend label whose rename would touch 14 note labels in
nine other chapters. The first three are English source defects and are in
`source-defects.tsv`, now 14 rows. `workflows/epirhandbook-fix-pass-deferred.js` is the brief,
`findings/fix-pass/def-*.json` the verdicts, commits `a0a9ed67` to `d7f22cd4` the edits:
42 files, 199 insertions, 89 deletions. Two batches were committed by hand because the checker
saw the replaced line still present elsewhere in the file, where it was correct.

**Gates on the code-chunk edits.** `chunk-parse-gate.py` runs `Rscript parse()` on every R
chunk of every changed translated file, before and after, and fails when a file has more
parse failures after. Proved red on an extra closing parenthesis. After the chunk sync below the gate reports 5 files with more parse failures than at `52442a79`, each because the English `eval=F` chunk itself does not parse; see `source-defects.tsv`.
`render-gate.sh` on the 42 files the deferred pass touched: 40 pass, 0 fail, 2 skipped for inline R or a tracked artifact. Verified by `modernization/render-gate.sh fc2079cf HEAD`.

## Chunk sync: every aligned chunk identical to the English

The owner then asked whether the code chunks should not simply be copies of the English.
Measured first, over all 65 chapter files per language: 94% of aligned chunk pairs were
identical or differed only in comments; 459 differed in code, 160 in string literals only, and
18 pairs had different chunk counts. Renamed objects were rare, Portuguese-only in practice,
and half of them inconsistent within their chapter, so a copy loses nothing a reader relies on
except translated comments.

`sync-chunks.py` makes every aligned chunk the English chunk, line by line, keeping the
translated line where its code part matches, so its comment survives, and keeping a
comment-only line at the same aligned place. No model. Proved red and green on a copy of
`basics.tr.qmd`. First run over-reached and replaced translated comment-only lines; corrected
and re-run from the pre-sync files in commit `a1b59b3f`. Net result against the pre-sync files:
187 files, 2519 insertions, 2855 deletions, 13,224 standalone comment lines before and 13,214
after. Portuguese prose that named a renamed object was pointed back at the English name.

Skipped, chunk count differs from the English: `data_used` in 5 languages, `epicurves` in 3,
`ggplot_tips` in 3, `phylogenetic_trees.es`, `survey_analysis.es`. These are aligned by an
agent each, then synced.

**Alignment of the 18 chapters with a different chunk count.** One opus agent per chapter
deleted chunks the English lacks, inserted English chunks verbatim where the translation
lacked them, and moved misplaced ones. `data_used` in all seven languages carried six extra
download chunks from an older English version. Every one of the 18 then matched the English
count and was synced: 160 chunks. 1,184,297 tokens. `findings/fix-pass/aln-*.json`, commits
`9b851d5e` and `b76c5b56`. `sync-chunks.py --dry-run` now changes nothing: every translated
chapter with an English source carries the English chunks.

**Gates after the sync.** `chunk-parse-gate.py`, all 33,520 chunks of the 328 changed files,
before and after, ignoring a failure the English chunk at the same index shares: 0 files worse,
55 better. `render-gate.sh`: 166 pass, 0 fail, 21 skipped for inline R over the 187 first-sync
files; 18 pass, 0 fail over the 18 aligned ones. Verified by both scripts on 2026-09-02.

**One incident.** The render gate's per-file `git ls-files` check failed while a concurrent
commit held the index lock, so it rendered `contact_tracing.ru.qmd` and dropped an untracked
`.html` beside it, which `git add chapters/` in commit `78bfaa3e` then swept into the
repository. Removed in `712f8497`. The gate now reads `git ls-tree -r HEAD` once at start.

**Structure check, all 336 declared pairs.** Every translated file exists. Chunk count equals
the English in 336 of 336. Heading sequence, counted with every fenced block stripped, equals
the English in 336 of 336 after one agent per chapter aligned 11 chapters, commit `360f5ec1`,
767,127 tokens. Three further apparent mismatches were `#` lines inside bare output fences,
which the first count did not strip. `render-gate.sh` on the 11 edited files: 7 pass, 0 fail, 4 skipped for inline R.

**Anchor sync.** Of 8,414 heading attribute blocks, 48 carried a different anchor id from
the English or none where the English has one, and 12 links written English-style into those
chapters were dead. `sync-anchors.py` set the English id on those 48 headings, kept each
translation's own classes, and rewrote the one link that targeted an old id: dead links 12
before, 0 after, counted over every translated file. Commit `9ac73410`. `render-gate.sh` on the 41 files: 41 pass, 0 fail, 0 skipped for inline R or a tracked artifact.

**Inline-code pass.** Every \`span\` in translated prose that occurs nowhere in the English
chapter is a suspect: 686 of about 34,000, 1.9%. One agent per batch of at most 40 sorts them
into fix, keep and noise, and edits the fixes. Result, 22 agents, 1,976,923 tokens: 349 fixed, 320 rejected as a placeholder or a deliberate code-font word, 17 deferred to a sentence rewrite. `findings/fix-pass/inl-*.json`, commits `2debe888` to `88e063c6`: 113 files, 465 insertions, 455 deletions.

**Structural sweep, all languages, no codex.** For every one of the 317 changed files, the
counts of fence lines, `{r` chunk openers, headings and `{#anchor}` attributes before and after.
Fifteen files changed a count. Fourteen are alignment fixes that add or remove a section the
English has or lacks, one anchor restored from the English, and two English code chunks the
French `basics` chapter had dropped. One was a defect: a repaired link in `help.es.qmd`
targeted an in-page anchor where the English targets `collaboration.qmd`. Fixed in commit
`afc3b69e`. Fence counts stay even in every file.

## English source fixes and the mirror pass

The owner then asked for the open sets to be closed. Fourteen opus agents, one per English
chapter, fixed 17 of the 18 recorded source defects in `chapters/*.qmd`, the first edits to
an English file in this work: wrong column, function, side or statistic in prose; three inline
row counts written as plain code; a dead and an empty link; the strptime minute code; four
`eval=F` chunks that did not parse. The 18th, the `add_count()` sentences in `grouping.qmd`,
was already correct; the French pair was the inverted one. Commit `7f183974`, 747,328 tokens.
`sync-chunks.py` then carried the four corrected chunks into 21 translated files, `fb65c948`.

One opus agent per language then made the translated prose follow the corrected English at
the 21 listed places and closed the inline-code deferrals: 16 fixed, 4 already matching, 1
fixed by hand. Commit `62fff305`, 384,273 tokens. `check-sync.sh`: IN SYNC, 355 informational
inline suspects. RENDER_GATE_8_LINE

Still open: `editorial_style.ru#1`, a Russian legend label whose rename would touch 14 note
labels in nine other chapters; and the German translation, excluded from
`babelquarto.languages`.

## What this pass did not do

- Phase G ran as `render-gate.sh`: `quarto render --no-execute` per changed translated file,
  plus a fence-parity check, because pandoc renders an unclosed fence with exit 0. First run,
  before the review repairs: 287 pass, 0 fail, 32 skipped for inline R, of 319 files.
  Second run, on the 45 files the review repairs touched: 40 pass, 0 fail, 5 skipped. Verified by `modernization/render-gate.sh`.
- No push. A push to `main` deploys to staging.
- The translated `DOĞRU`/`YANLIŞ` for `TRUE`/`FALSE` occurs on about 12 more Turkish lines that
  no finding named. They are untouched.
