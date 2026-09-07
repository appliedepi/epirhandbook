# Consolidate all modernization work into modernization/ and fix every reference

Repo: /home/raw996/ae/epiRhandbook_eng   (also touches /home/raw996/ae/aedockerpublic)

## Why

The session is ending for quota. 8.4M tokens of work is scattered across the repo, `~/.claude`
and `/tmp`. `/tmp` will be cleared. Everything needed to resume on Wednesday MUST end up in the
repo, and every reference to a moved file MUST still resolve.

**Do NOT commit. Do NOT push.** The orchestrator commits.

## Invariant

`modernization/` contains everything needed to resume, and no link anywhere in either repo points
at a path that no longer exists.

## Target layout

```
modernization/
  README.md                     index, written by you (see below)
  PLAN.md                       copy of ~/.claude/plans/noble-mixing-matsumoto.md
  RESUME.md                     moved from utils/PROSE-SWEEP-RESUME.md
  STAKEHOLDERS.md               moved from repo root
  TRANSLATION-BACKLOG.md        moved from repo root
  PLAN-translated-data-used.md  moved from repo root
  findings/
    language-prose-drift.tsv        moved from utils/
    language-prose-coverage.tsv     moved from utils/
    prose-sweep/                    moved from utils/prose-sweep/  (98 JSON)
    sonnet-ab/                      copy of /tmp/gate/prose-sonnet/*.json  (4 JSON, the A/B)
  workflows/                    copy the 3 workflow scripts, see below
  reviews/                      the 4 Codex verdicts and their finding sections
  briefs/                       copy /tmp/gate/*brief*.md and /tmp/gate/phase1a-transcript*.md
```

`utils/check-language-consistency.R` STAYS in `utils/`. It is a working tool beside
`utils/check-data-equivalence.R`, not bookkeeping. Do not move it.

## Sources outside the repo

- Plan: `~/.claude/plans/noble-mixing-matsumoto.md`
- Workflow scripts: `~/.claude/projects/-home-raw996-ae/5d0394ed-b037-40d5-b069-f1722bddc6a4/workflows/scripts/*.js`
  (three: the 336-pair finder, the 5-pair finish, the Sonnet A/B)
- Codex verdicts: `/tmp/gate/phase1a*.verdict`
- Codex logs: `/tmp/codex-review/phase1a-language-checker-attempt{1,2,3,4}.log`.
  **These are ~200KB each. Do NOT copy them whole.** Extract only the final `codex` answer block
  of each — the findings list and the `BLOCK:`/`ALLOW:` line — into
  `reviews/codex-round<N>.md`, and say in each file which log it came from.
- Briefs and transcripts: `/tmp/gate/*brief*.md`, `/tmp/gate/phase1a-transcript.md`,
  `/tmp/gate/phase1a-transcript-archive.md`, `/tmp/gate/phase1b-record-transcript.md`

## Reference fixes — this is the part that breaks silently

**In this repo, 13 references.** Verified by the orchestrator with `command grep`:

```
README.md:29, 32, 270                    -> STAKEHOLDERS.md, TRANSLATION-BACKLOG.md
STAKEHOLDERS.md:8, 114, 115, 342, 348    -> TRANSLATION-BACKLOG.md, PLAN-translated-data-used.md
TRANSLATION-BACKLOG.md:4, 12, 13, 312, 313 -> STAKEHOLDERS.md, PLAN-translated-data-used.md
PLAN-translated-data-used.md:131         -> TRANSLATION-BACKLOG.md
```

`README.md` stays at the root, so its links become `modernization/STAKEHOLDERS.md`. Links
BETWEEN the three moved documents stay relative and unchanged, because they move together — but
CHECK each one rather than assuming, and report which you changed and which you did not.

**In `/home/raw996/ae/aedockerpublic`, 5 absolute URLs** that GitHub will NOT redirect:

```
epirhandbook/2.7/CHANGES-2.6-to-2.7.md:5, 16
epirhandbook/2.7/README.md:97, 100
```
They are of the form `https://github.com/appliedepi/epirhandbook/blob/main/STAKEHOLDERS.md`.
Repoint each to `.../blob/main/modernization/<file>`. That repo is a separate git repository:
edit the files, do NOT commit there either.

## modernization/README.md

Follow `rw-technical-prose`. It is the index someone opens cold on Wednesday. It MUST carry:

1. What this folder is, in two sentences.
2. **State right now**: Phase 1a complete and Codex-reviewed; prose sweep 98 of 336 pairs, 493
   findings, 5561 coverage rows, 14 chapters done and 34 never started; NO verification has run
   on any finding.
3. **What to do first on Wednesday**: read `PLAN.md`, re-approve it, start at Phase A (the
   deterministic segmenter).
4. **The measured facts that drive the plan**: Opus 54,820 tokens per pair versus Sonnet medium
   118,244 (2.2x MORE) at 44% of the findings; the decision is Opus. ~13M tokens to finish the
   remaining 238 pairs.
5. **The two defects the resumed run MUST avoid**: no budget guard (336 agents launched at once,
   253 killed by the session limit), and return-based accounting (the workflow reported 83 pairs
   when 94 files existed on disk).
6. **A map of the folder**, one line per entry.
7. **What is NOT here**: the gate state and phase ledger, which were session-scoped in `/tmp` and
   are deliberately not preserved.

State the base with every number. "493 findings over 98 pairs in 14 chapters", never "493 findings".

## Discriminator

```
command grep -rIn -E '\]\((\.\/)?(STAKEHOLDERS|TRANSLATION-BACKLOG|PLAN-translated-data-used)\.md' --include='*.md' . | command grep -v 'modernization/' | command grep -v '_excluded/' | command grep -v 'html_outputs/'
```

MUST return nothing: no markdown link outside `modernization/` may point at a bare root path.

Also run, and report raw:
```
ls modernization/findings/prose-sweep/*.json | wc -l          # MUST be 98
ls modernization/findings/sonnet-ab/*.json | wc -l            # MUST be 4
Rscript -e 'd <- read.delim("modernization/findings/language-prose-drift.tsv", sep="\t", quote=""); c2 <- read.delim("modernization/findings/language-prose-coverage.tsv", sep="\t", quote=""); stopifnot(nrow(d)==493, nrow(c2)==5561); cat("drift",nrow(d),"coverage",nrow(c2),"\n")'
git -C /home/raw996/ae/epiRhandbook_eng status --porcelain | head -40
```

## Pass/fail

PASS when: the discriminator grep is empty; 98 and 4 JSON present; the two TSVs still parse at
493 and 5561 rows; the three root documents are gone from the root and present in
`modernization/`; `utils/check-language-consistency.R` is untouched; the 5 aedockerpublic links
are repointed; `README.md` at the root resolves to the new locations; and nothing is committed in
either repo.

FAIL if any moved file lost content, if a reference still points at a root path, or if you
committed anything.

## Forbidden

- `git commit`, `git push`, `git tag` in EITHER repo.
- Touching any `.qmd`, `_quarto.yml`, `.github/`, `renv.lock`, `utils/check-language-consistency.R`.
- Copying the four 200KB Codex logs whole.
- Bare `grep`. It is a ugrep-backed shell function whose output has no `./` prefix, so `^\./`
  filters are silently inert. Use `command grep`.
- Deleting anything from `/tmp` — the orchestrator may still need it this session.

Use `git mv` for files already tracked, so history follows. Plain `cp`/`mv` for untracked ones.
