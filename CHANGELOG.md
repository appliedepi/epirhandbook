# CHANGELOG — epiRhandbook

The record of how this handbook got to its current shape: what changed, and why. Newest first.

Each entry describes the project AS IT WAS when it was written. Later work has superseded parts
of it, and that is expected of a changelog. Read it as a record, never as current documentation.
`README.md` is the current state.

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
