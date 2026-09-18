# CHANGELOG — epiRhandbook

The record of how this handbook got to its current shape: what changed, and why. Newest first.

Each entry describes the project AS IT WAS when it was written. Later work has superseded parts
of it, and that is expected of a changelog. Read it as a record, never as current documentation.
`README.md` is the current state.

---

## 2026-09-18: the landing page becomes a hero, and the Welcome page splits in three

Phase 2 of the Applied Epi redesign. Phase 1 added the theme. This phase replaces the landing
page, and moves the prose that used to sit under it.

### The problem

`content/<lang>/index.qmd` was one long page in eight copies. It carried:

- a banner image
- a usage claim
- an offer of tutorials
- a hardcoded list of seven `epirhandbook.com` URLs
- the Applied Epi logo lockup and the contact bullets
- the acknowledgements, and the terms of use

Nothing tied the eight copies together, so each was free to drift.

### What changed

Every landing page now renders one hero from one markup source. `utils/landing-hero.R` builds the
HTML. `landing.yml` holds the strings, keyed by language code. A key a language does not declare
falls back to English, so a new language reads in English rather than showing an empty box.

`index.qmd` keeps four things: its `aliases:`, its `<meta name="description">`, its unnumbered
`# Welcome` heading and one R chunk. The chunk is byte-identical in all eight languages, and it
reads its own language from the working directory. The heading stays because a Quarto book
numbers a chapter that has no unnumbered heading, which would renumber all 49 chapters. The hero
hides it and carries the visible title.

The prose moved to two new chapters in every language:

- `about.qmd` takes the "R for applied epidemiology and public health" heading, the Objective
  paragraph and the "How to use this handbook" section. Portuguese also carries its call for
  help with the translation, which no hero element replaces.
- `acknowledgements.qmd` takes Acknowledgements and Terms of Use and Contribution, with their six
  sub-sections, verbatim.

These blocks are superseded, each by a hero element:

- the banner image
- the usage line
- the tutorials offer
- the hardcoded language list
- the "written by epidemiologists" line
- the logo lockup with its nonprofit prose
- the contact bullets with the live-training pitch
- the live PayPal donation form

The real language switcher supersedes the hardcoded list. It sits in the app bar, and
`inject_language_links.R` builds it from `languages.yml`.

The donation form is gone, and no hero element replaces it. It was the one part of the old page
that took money. Richard read that and decided to remove it, so the landing page now collects no
donations. The form posted to `paypal.com/donate` with a hidden button id, a donate button image
and a tracking pixel. Read the pre-plan file at `a5b7317d` to recover any of it.

No hero string is translated yet. All eight landing pages read in English, through the fallback.
`landing.yml` carries an empty block for each of the seven other codes, which is where a
translated string goes.

### The counts that moved together

52 stems, 51 non-index stems, 357 translated pairs and 416 aliases. `docker-images.yml` gained a
row for each new stem, on the basics image, which already covers the "About this book" part.
Without those rows `check_manifest_covers_book()` stops the build before it renders anything.

The hero's chapter count is computed, never written down. It is the 52 stems less `index`,
`about` and `acknowledgements`, which is 49. The language count comes from `languages.yml`.

### Corrections to the draft markup

The search box in the draft was an `<input>` wired to nothing. It now drives the one
`#quarto-search` that the app bar hosts. Quarto builds two different widgets there. Below 992px
it builds a button, `.aa-DetachedSearchButton`, and a click on that button is the only thing that
opens the overlay. Above 991px it builds an inline input with `openOnFocus`. The hero box takes
the button first and the input second.

`theme-ael.scss` gained the landing component layer. Three rules differ from the draft:

- the duplicated `.ael-hsearch` declaration is gone
- `.nplockup` collapses with `grid-template-columns`, not an inert `flex-direction`
- the four uppercase rules read `--ael-caps` and `--ael-track`, like the rest of the file

The usage stat reads "3 million+ times". An earlier draft added the base, "by 850,000 people",
so that the number described itself. Richard cut it: the hero is a finished design, and the page
it replaces was cluttered. The full claim stays in the pre-plan file and in this record.

All three stat labels are lower case, so each one reads as a phrase with its own number:
"3 million+ times", "49 chapters", "8 languages". The uppercase rule in `theme-ael.scss` reads
`--ael-caps`, which `:lang(jp)`, `:lang(vn)` and `:lang(ru)` set to `none`. Mixed case would have
shown on those three pages alone.

---

## 2026-09-17: the directories chapter teaches a regular expression, not a glob

Triage of issue #457, the follow-ups flagged while closing #450 and #451.

### The problem

`content/<lang>/directories.qmd` showed `list.files(pattern = ".csv")` in all 8 languages. The
surrounding prose called it "a specific pattern to look for". `pattern =` takes a regular
expression. The dot matches any character, and the expression is not anchored, so the call also
matches names like `notes.csv.bak` and `xcsvy.txt`.

The example folder held only real `.csv` files, so both forms returned the same 7 names. No check
could go red on it.

Separately, `modernization/STAKEHOLDERS.md` cited six backing files that this repository has never
held. Two of them carried the verification table's strongest claims.

### What changed

The chunk now reads `pattern = "\\.csv$"`, and the prose says that `pattern =` takes a regular
expression. `checks/sync-chunks.py` propagated the code to the 7 translations and kept their
comments. The commented-out `dir()` line was edited by hand. `sync-chunks.py` compares the
code before any `#`. That is empty on a fully commented line, so the gate never syncs one.

`STAKEHOLDERS.md` no longer names `BREAKAGE.tsv`, `DIFFERENCES.tsv`, `forward-port.patch`,
`FORWARD-PORT.tsv`, `verify_render_26.04.tsv` or `verify_render_multiling.tsv`. None is tracked
today. None was tracked at `621c4b05`. None appears anywhere in history. The render claims now
state that the run record was not retained.

The file also lost its 22 over-limit sentences, bringing it under the 25-word house limit.

`utils/data-callsites.tsv` row 24 and `utils/data-map.tsv` rows 83 and 84 said
`content/en/data_table.qmd:53` must remain a file-based read. That chapter now calls
`appliedepidata::get_data(name = "linelist_cleaned_excel")`.

### What a reader should know

The `data_table` chapter resolved its gap by substitution, not by closing it. It used to read
`data/linelist_cleaned.xlsx`, sha `800b7786`, which has no `appliedepidata` equivalent. It now
reads the byte-distinct `case_linelists/linelist_cleaned.xlsx`. The chapter therefore loads
different bytes than before. The gap in the package is still open.

---

## 2026-09-17: the seven translated home pages keep their old URL

Found while checking alias coverage before the first production promotion (issue #456).

### The problem

The live site serves each translated home page at `/<lang>/index.<lang>.html`, for example
`/fr/index.fr.html`. The `/<lang>/index.html` path is a redirect stub that points at it. Search
engines index the `.<lang>.html` form, because that is the page with the content.

The new `content/<lang>/` layout publishes the home page at `/<lang>/index.html` only. Nothing
produced the old path. The first promotion would have returned 404 for seven live URLs, one per
translated language. English was never affected: it had no `.en.html` form.

The cause was a stated rule, not an oversight in a file. `CLAUDE.md` required an `aliases:` entry
on every chapter file "except `index.qmd`", and check 9 in `checks/check-sync.sh` skips
`index.qmd` for the same reason. Eight home pages sat outside the one mechanism that keeps an old
URL alive.

### What changed

- Each of `content/{es,fr,jp,pt,ru,tr,vn}/index.qmd` now carries front matter declaring one alias,
  `/index.<lang>.html`. Quarto writes a redirect stub at that path.
- `checks/README.md`: the documented check-9 alias count moved from 393 to 400.

### How the gap was found

The live URL set came from `search.json` on each of the eight languages: 408 distinct page URLs.
The same set was derived a second way, from the links on each language home page, and the two
agreed. The staging set came from the built tree on `origin/staging`.

The `aliases:` keys were not trusted on their own. Every one of the 393 alias stubs in the built
tree was parsed, its `var redirects` target resolved against the tree, and every target exists.

Two gaps remained. The seven home pages above are fixed here. The eight `epidemic_models` URLs are
not: that chapter stays excluded, and Richard accepted the 404 on 2026-09-17.

### What a reader should know

A Quarto alias stub is a JavaScript redirect, not an HTTP 301. It carries the hash and the query
string. A crawler that does not run JavaScript sees an empty page, so no link equity passes
through it.

---

## 2026-09-02: the GIS chapter returns

Restored to the build after being cut in the 2.7 upgrade. Written up the same day, converted
from a set of teaching notes on 2026-09-17.

**Since superseded:** the image line named below was 2.8 and is now 2.9; `brio` and
`rewrite_lang_config.R` were both removed from the 2.9 image; the chapter's package list moved
from `epirhandbook/2.8/chapters/gis/` to the 2.9 tree.

### The problem


- **Why the chapter was cut.** `chapters/gis.qmd` calls `OpenStreetMap::openmap()` while it
      renders. That fetches map tiles from tile.openstreetmap.org. CI renders every chapter inside a
      Docker container that reaches only the registry, so the render failed there. The 2.7 upgrade
      commented the chapter out of `_quarto.yml` and moved it to `_excluded/`.
- **Why nothing else in the chapter was a blocker.** tmap 4.3, spdep 1.4.2 and sf 1.1 still run
      the 2021 code. tmap 4 keeps a v3 compatibility layer and prints deprecation messages, which the
      chunks suppress with `message=F`. Verified by an executing render, not by reading.
- **A second, invisible defect.** Three sentences report a computed number (cases outside every
      clinic buffer, Moran's I, Lee's L) with inline R. Commit `d3fdc233` (a January 2025 revert of
      "Handbook v2.5 en") removed the `r` from `` `r round(...)` ``, so the page printed the code
      instead of the number. Every translation except Japanese carried the same loss, in four
      different spellings. `git log -S` on the span found it.
- **How the translations had drifted.** Spanish had five extra chunks (hidden duplicates that
      ran the code, plus `eval=FALSE` copies that showed it, plus two `library("janitor")` chunks).
      French had an untranslated duplicate heading and two headings at the wrong level. The sync
      tools pair chunks and headings by position, so counts must match before they can run.

### The solution

- **The offline design.** The visible `openmap()` chunk keeps its code and gets `eval=FALSE`.
      Every chunk that plots the basemap gets `eval=FALSE` too. Separate `echo=F` chunks call
      `knitr::include_graphics()` on five committed PNGs, `images/gis_basemap_0*.png`. No chunk
      reads `data/gis/osm_basemap.rds`; `data/gis/osm_basemap.R` re-creates that file. The reader
      sees the same code and the same plots. The build never opens a socket.
- **Why the bounds come from the whole linelist.** The chapter draws a random sample of 1000
      cases with no seed. A basemap fetched from the sample's bounds would differ per render. The
      full linelist's bounds contain every sample's bounds.
- **How the proof was made hermetic.** Each of the eight files was rendered with execution
      inside `unshare -rn`, a network namespace with no interfaces. A render that reached the
      network would have failed. All eight passed in about 41 s each.
- **Order of the sync.** Structure first (chunk counts, heading sequence), then
      `sync-chunks.py` (code identical, translated comments kept), then `sync-anchors.py`, then
      `check-sync.sh` until it prints IN SYNC. The hidden chunk had to be inserted into every
      translation before the chunk sync, because the sync pairs chunks by position.
- **The image side.** The analysis group image lacked tmap, spdep, OpenStreetMap, rJava and 22
      dependencies. The chapter's package list is `loadedNamespaces()` at the end of one executing
      render, minus base R. It lives under `epirhandbook/2.8/chapters/gis/`, not under 2.7, and
      `generate_groups.py` learned to read that directory for a stem with no 2.7 image.
- **What "in sync" does not cover.** Meaning. A translated sentence can still say something the
      English does not. Comments inside chunks are kept where the code line survives and fall back
      to English otherwise.

### The broader context

- **Two repositories, two owners.** The handbook owns content and the choice of image
      (`docker-images.yml`). aedockerpublic owns packages and images. Neither fetches from the other
      at build time. A chapter with no manifest row fails the handbook build on purpose.
- **Why the image change ships first.** The handbook's CI pulls `epirhandbook-analysis:2.8`.
      Pushing the handbook before the rebuilt image publishes gives a red staging build with a
      missing-package error.
- **Visibility.** The nine 2.8 images are public; the README said they were private. A new
      image NAME starts private and needs an org admin. Adding a chapter to an existing group
      creates no new image.
- **Flagged in round one, fixed in round two** (section 4): `st_buffer()` attributed to tmap,
      `..level..`, the rio `trust` warning, the retired data package name, the unseeded sample.
      Still open: tmap v3 syntax throughout (works through tmap 4's compatibility layer), and the
      translated headings that carry ids the English lacks (corpus convention, no link targets one).


### Second round (same day): the flagged items, and what the reviews caught

- **Why common could not rebuild.** babeldown's DESCRIPTION declares `Remotes: babelquarto`;
      pak resolves that to the repository HEAD, which moved past the pinned babelquarto SHA. A pin
      on a package with a `Remotes:` field is only as stable as the other repository's HEAD.
- **Why the fix was removal, not a bump.** Neither package is used at render time (the render
      scripts vendor babelquarto's logic; babeldown serves only `_translation.R`). A bump realigns
      the two refs once; the `Remotes:` edge stays and conflicts again on the next HEAD move.
- **What the plan review caught that reading did not.** `brio` came into the common image only
      through those pins, and `rewrite_lang_config.R` calls `library(brio)`. Every load check would
      have passed and the first real CI render would have died. The lesson: before you remove a pin,
      grep the scripts that run in that image for `library()` and `::`.
- **Why the CI gate was a NO GO.** A "previous run failed" check forgets the failure after any
      intervening run, cannot see re-run attempts, ignores cancelled jobs, and parses display names.
      The persistent alternative (rebuild every transitive base whenever a dependent builds) costs
      about 40 CI minutes per push. Decide on the invariant before you decide on the mechanism.
- **Why the GIS chapter, alone, showed the rio warning.** It was excluded during the migration to
      `appliedepidata::get_data()`, so it still calls `rio::import()` on an .rds. `echo=F` hides code,
      not warnings.
- **What `/en/` means at promotion.** Production still serves the old layout under `/en/` and
      Cloudflare redirects root paths into it. Staging puts English at the root. Every existing
      English URL 404s at the first promotion unless something redirects the other way.
