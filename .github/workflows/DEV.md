# Translation branches and the automatic per-language PRs

This file covers one thing: the GitHub Action that fans an English change out into a pull request
per language.

**For everything else — branching, previewing, publishing — read
["How this all works"](../../README.md#how-this-all-works) in the repository README.** That is the
current process and the only one kept up to date.

## What the Action does

Workflow file: [`create_pr_on_pr.yml`](create_pr_on_pr.yml)

It triggers on a push to any branch matching `handbook_v*_en`. For each of the seven translated
languages (`fr`, `es`, `vn`, `jp`, `tr`, `pt`, `ru`) it:

1. creates or updates the matching `handbook_v*_<lang>` branch, merging in the English branch's new
   commits;
2. opens or updates a pull request from that branch **into `main`**;
3. adds a checkbox per new English commit to the pull request description, with a link to each.

The language lead is notified by email for every new change on the English branch. The checkboxes
exist so the lead and the coordinator can track which English commits have been reflected in their
language before merging.

## What it does not do

**It does not translate anything.** It propagates the English text into the language branches and
tells a human. The actual translation is a separate, manual step — see `_translation.R` at the
repository root, which drives [babeldown](https://docs.ropensci.org/babeldown/) against the DeepL
API and needs a key in a local, gitignored `.env`.

Note that babeldown decides what to update by comparing commit timestamps, not content. If a
translated file was edited more recently than its English source, it does nothing at all — silently,
without an error. Divergence between a language and English is caught by a human reviewing the pull
request, not by tooling.

## If you are reading an older copy of this file

Earlier versions described a flow built around a `deploy-preview` branch, a `master` default branch,
and a `render_book_on_pr.yml` workflow. None of those apply any more:

| Was | Now |
|---|---|
| branch off `deploy-preview` | branch off `main` |
| default branch `master` | default branch `main` |
| translation PRs merge into `deploy-preview` | they merge into `main` |
| `render_book_on_pr.yml` renders on merge | `preview.yml` / `staging.yml` / `production.yml` |
| built HTML committed into `deploy-preview` | built HTML force-pushed to `preview`, `staging`, `production`, which hold no source |
