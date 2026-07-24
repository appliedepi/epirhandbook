# The Epidemiologist R Handbook 

# About this handbook
**The Epi R Handbook is a R reference manual for applied epidemiology and public health.**  

***Go to www.epiRhandbook.com to see the latest version of the online handbook.***

![Project logo](https://github.com/appliedepi/epirhandbook/blob/master/images/Epi%20R%20Handbook%20Banner%20Beige%201500x500.png)

**This book strives to:**  

* Serve as a quick epi R code reference manual  
* Provide task-centered examples addressing common epidemiological problems  
* Assist epidemiologists transitioning to R  
* Be accessible in settings with low internet-connectivity via an **offline version**
  

<img src="https://github.com/appliedepi/epirhandbook/blob/master/images/epiRhandbook_HexSticker_500x500.png" width="200" height="200">

<span style="color: black;">**Written by epis, for epis**</span>
We are applied epis from around the world, writing in our spare time to offer this resource to the community. Your encouragement and feedback is most welcome:  

* Structured **[feedback form](https://forms.gle/A5SnRVws7tPD15Js9)**  
* Email **epiRhandbook@gmail.com** or tweet **[\@epiRhandbook](https://twitter.com/epirhandbook)**  
* Submit issues to our **[Github repository](https://github.com/epirhandbook/Epi_R_handbook)**  


## How to use this handbook  


* Browse the pages in the Table of Contents, or use the search box
* Click the "copy" icons to copy code  
* You can follow-along with [the example data][Download handbook and data]  
* See the "Resources" section of each page for further material  

**Offline version**  

See instructions in the [Download handbook and data] page.  

**Languages**  

We want to translate this into languages other than English. If you can help, please contact us.  



## How this all works

This section explains how the handbook is built, translated, and published. It is for
anyone changing a chapter, adding a language, or debugging a broken build.

### The two-repo split

Two repositories build this handbook, and each owns a different part:

* **[appliedepi/aedockerpublic](https://github.com/appliedepi/aedockerpublic)** owns the R
  packages, the Docker images, and the render scripts.
* **This repository** owns the `.qmd` content, in every language, and the choice of
  which image renders each chapter.

Neither repository fetches from the other at build time.

They are split because a chapter's prose and a chapter's package set change on
different schedules, and by different people. An author can fix a sentence today
without waiting on a package upgrade. A package upgrade can happen without touching
a single word of text.

### The manifest

`docker-images.yml`, in this repository, maps each chapter to a Docker image.

Each chapter gets **one entry**, called a "stem" (e.g. `time_series`). One entry
covers all of that chapter's languages, because a translation runs the same R code
as the English original, so it needs the same packages.

To move one chapter to a different image version, change that one line.

The language list is **not** in this manifest. It lives in `_quarto.yml`'s
`babelquarto:` block, which is the single source of truth for which languages ship.

### How languages are handled

English is the main language. It renders at the site root.

Every other language renders from its own `.<lang>.qmd` files (e.g.
`time_series.fr.qmd`) and lands under `<lang>/` (e.g. `/fr/`).

Old `/new_pages/...` URLs still work. Every chapter file carries an `aliases:` entry
in its front matter, and Quarto turns that into a redirect stub at the old path:

```
---
aliases:
  - /new_pages/time_series.html
---
```

The alias value must be root-relative — it must start with a leading `/`. Without
the leading slash, Quarto writes the redirect stub in the wrong place, and the old
link stays broken.

### The three environments

Three environments publish from this repository:

* **`preview`** — one build per pull request.
* **`staging`** — builds on every push to `main`.
* **`production`** — updated only when a release is published, by promoting
  staging. Nothing is rendered at release time.

**Production is a promotion of staging, not a rebuild.** Cutting a release force-pushes
the already-built `staging` artifact to `production`. Nothing is rebuilt at release
time. What goes live is exactly what was already reviewed on staging — not a fresh
render that might behave differently.

**Previews only work for pull requests opened from a branch in this repository.**
GitHub deliberately withholds repository secrets from a pull request opened from a
fork, and the build needs one to pull its Docker images. A fork's preview therefore
stops at the login step with an explicit error rather than rendering. That is the
safe behaviour: the alternative — handing a token to a workflow that runs code the
pull request controls — is how CI credentials get stolen. Once the images are public
the login step goes away and fork previews work too.

### Publishing an update, end to end

This is the same flow as
[appliedepi/websitetimecourse](https://github.com/appliedepi/websitetimecourse). Content
changes, translations included, all go through it.

1. Create a branch off `main` and make your edits.
2. Check they render locally.
3. Open a pull request into `main`.
4. That triggers a build to the **`preview`** branch. View it at the preview website
   URL. **Check it before merging.**
5. Merge the pull request into `main`. That triggers a build to the **`staging`**
   branch. Check the build succeeded.
6. If staging is good, create a GitHub release, following the versioning conventions.
   That pulls `staging` into `production`, and a webhook updates the live site.

Only rendered HTML reaches `preview`, `staging` and `production`. They are orphan
branches: CI force-pushes them, nothing is ever merged into them, and they contain no
`.qmd` source. The source lives on `main` and nowhere else.

Nothing is re-rendered at release time. Step 6 copies the artifact you already checked
in step 5, so what goes live is exactly what was reviewed.

### Where things live

| To change... | Edit... |
|---|---|
| A chapter's prose | this repository, in `chapters/` |
| A chapter's R packages | [appliedepi/aedockerpublic](https://github.com/appliedepi/aedockerpublic) |
| Which image a chapter uses | `docker-images.yml`, in this repository |

### Routine maintenance

**Bump one chapter's image.** Edit that chapter's row in `docker-images.yml` to
point at the new image tag. Every other chapter keeps its own tag and is
unaffected.

**Add a new chapter.** Four things, across both repositories:

1. A `.qmd` file here, in `chapters/` (plus translated `.qmd` files, if any).
2. An image in aedockerpublic — a new one, or an existing one that already has the
   right packages.
3. A new row in `docker-images.yml`, in this repository.
4. A new entry in `_quarto.yml`, in this repository, under `book.chapters`.
5. If the chapter replaces an old URL, an `aliases:` entry in the chapter's own
   front matter — not in `_quarto.yml`. The value needs a leading `/`.

### Debugging a failed render

Start by identifying three things: which job failed, which language, and which
chapter.

**A render that exits 0 is not proof the chapter is correct.** A chapter can render
successfully and still be wrong — stale output, a broken cross-reference, a
computed value that silently changed. The build validates its own output as a
separate step; check what that validation reports, not just whether the render
job's exit code was 0.

### Excluded chapters

Two chapters are currently excluded from the build. Both are commented out of
`_quarto.yml`, under `book.chapters`.

* **`gis`** — it depends on an external OpenStreetMap service. That makes its
  render network-dependent, which is not suitable for a hermetic CI build.
* **`epidemic_models`** — it fails on a recorded EpiNow2 API break (an
  `xy.coords()` error; see aedockerpublic's `epirhandbook/2.7/BREAKAGE.tsv`).

**Their old URLs will stop working.** `/new_pages/gis.html` and
`/new_pages/epidemic_models.html` still return HTTP 200 today, from the version
built before this exclusion. They will stop resolving once this deploys. A chapter
absent from `book.chapters` is never rendered, so it never emits the alias redirect
stub that would otherwise keep the old URL alive.

**Other chapters link to them, in two different ways, with two different fates.**

*Links to the chapter page* — 31 of them, in 21 files, across English, Japanese,
Portuguese, Russian, Turkish and Vietnamese. They are written as `(gis.qmd)`,
`(gis.ru.qmd)` and so on, from `basics`, `data_used`, `flexdashboard`, `importing`,
`rmarkdown` and `survey_analysis`. These work today and stop working while the
chapter is excluded. Leave them: they start working again the moment the target
renders. One further link, to `epidemic_models`, behaves the same way.

*Links to an anchor inside the chapter* — 26 of them, written as `(#gis)` or
`(#gis-basics)`. **These are already broken today**, in the currently published
site, and excluding the chapter does not change that. A same-page anchor never
reaches another page, so restoring `gis` will not fix them either. They are
ordinary content bugs and belong with the other prose fixes in
[TRANSLATION-BACKLOG.md](TRANSLATION-BACKLOG.md) — the production render carries
106 dead fragments in total, of which these are the largest single group.

**What it would take to bring each back:**

* `gis` needs a way to render without reaching an external network service during
  CI — for example, a vendored or mocked tile source instead of a live OpenStreetMap
  call.
* `epidemic_models` needs its EpiNow2 code rewritten against the current API (the
  chapter uses result accessors that EpiNow2 has since removed), then a verified
  end-to-end render.



<!-- ======================================================= -->
## Acknowledgements   

This handbook is produced by a collaboration of epidemiologists from around the world drawing upon experience with organizations including local, state, provincial, and national health agencies, the World Health Organization (WHO), Médecins Sans Frontières / Doctors without Borders (MSF), hospital systems, and academic institutions.

This handbook is **not** an approved product of any specific organization. Although we strive for accuracy, we provide no guarantee of the content in this book.  



### Contributors  

**Editor:** [Neale Batra](https://www.linkedin.com/in/neale-batra/) 

**Project core team:** [Neale Batra](https://www.linkedin.com/in/neale-batra/), [Alex Spina](https://github.com/aspina7), [Amrish Baidjoe](https://twitter.com/Ammer_B), Pat Keating, [Henry Laurenson-Schafer](https://github.com/henryls1), [Finlay Campbell](https://github.com/finlaycampbell)  

**Authors**: [Neale Batra](https://www.linkedin.com/in/neale-batra/), [Alex Spina](https://github.com/aspina7), [Paula Blomquist](https://www.linkedin.com/in/paula-bianca-blomquist-53188186/), [Finlay Campbell](https://github.com/finlaycampbell), [Henry Laurenson-Schafer](https://github.com/henryls1), [Isaac Florence](www.Twitter.com/isaacatflorence), [Natalie Fischer](www.linkedin.com/in/nataliefischer211), [Aminata Ndiaye](https://twitter.com/aminata_fadl), [Liza Coyer]( https://www.linkedin.com/in/liza-coyer-86022040/), [Jonathan Polonsky](https://twitter.com/jonny_polonsky), [Yurie Izawa](https://ch.linkedin.com/in/yurie-izawa-a1590319), [Chris Bailey](https://twitter.com/cbailey_58?lang=en), [Daniel Molling](https://www.linkedin.com/in/daniel-molling-4005716a/), [Isha Berry](https://twitter.com/ishaberry2), [Emma Buajitti](https://twitter.com/buajitti), [Mathilde Mousset](https://mathildemousset.wordpress.com/research/), [Sara Hollis](https://www.linkedin.com/in/saramhollis/), Wen Lin  

**Reviewers**: Pat Keating, Annick Lenglet, Margot Charette, Daniely Xavier, Esther Kukielka, Michelle Sloan, Aybüke Koyuncu, Rachel Burke, Kate Kelsey, [Berhe Etsay](https://www.linkedin.com/in/berhe-etsay-5752b1154/), John Rossow, Mackenzie Zendt, James Wright, Laura Haskins, [Flavio Finger](ffinger.github.io), Tim Taylor, [Jae Hyoung Tim Lee](https://www.linkedin.com/in/jaehyoungtlee/), [Brianna Bradley](https://www.linkedin.com/in/brianna-bradley-bb8658155), [Wayne Enanoria](https://www.linkedin.com/in/wenanoria), Manual Albela Miranda, [Molly Mantus](https://www.linkedin.com/in/molly-mantus-174550150/), Pattama Ulrich, Joseph Timothy, Adam Vaughan, Olivia Varsaneux, Lionel Monteiro, Joao Muianga  

**Illustrations**: Calder Fong  


<!-- **Editor-in-Chief:** Neale Batra  -->

<!-- **Project core team:** Neale Batra, Alex Spina, Amrish Baidjoe, Pat Keating, Henry Laurenson-Schafer, Finlay Campbell   -->

<!-- **Authors**: Neale Batra, Alex Spina, Paula Blomquist, Finlay Campbell, Henry Laurenson-Schafer, [Isaac Florence](www.Twitter.com/isaacatflorence), Natalie Fischer, Aminata Ndiaye, Liza Coyer, Jonathan Polonsky, Yurie Izawa, Chris Bailey, Daniel Molling, Isha Berry, Emma Buajitti, Mathilde Mousset, Sara Hollis, Wen Lin   -->

<!-- **Reviewers**: Pat Keating, Mathilde Mousset, Annick Lenglet, Margot Charette, Isha Berry, Paula Blomquist, Natalie Fischer, Daniely Xavier, Esther Kukielka, Michelle Sloan, Aybüke Koyuncu, Rachel Burke, Daniel Molling, Kate Kelsey, Berhe Etsay, John Rossow, Mackenzie Zendt, James Wright, Wayne Enanoria, Laura Haskins, Flavio Finger, Tim Taylor, Jae Hyoung Tim Lee, Brianna Bradley, Manual Albela Miranda, Molly Mantus, Priscilla Spencer, Pattama Ulrich, Joseph Timothy, Adam Vaughan, Olivia Varsaneux, Lionel Monteiro, Joao Muianga   -->


### Funding and support   


The handbook received supportive funding via a COVID-19 emergency capacity-building grant from [TEPHINET](https://www.tephinet.org/), the global network of Field Epidemiology Training Programs (FETPs).  

Administrative support was provided by the EPIET Alumni Network ([EAN](https://epietalumni.net/)), with special thanks to Annika Wendland. EPIET is the European Programme for Intervention Epidemiology Training.  

Special thanks to Médecins Sans Frontières (MSF) Operational Centre Amsterdam (OCA) for their support during the development of this handbook.  


*This publication was supported by Cooperative Agreement number NU2GGH001873, funded by the Centers for Disease Control and Prevention through TEPHINET, a program of The Task Force for Global Health. Its contents are solely the responsibility of the authors and do not necessarily represent the official views of the Centers for Disease Control and Prevention, the Department of Health and Human Services, The Task Force for Global Health, Inc. or TEPHINET.*

### Inspiration   

The multitude of tutorials and vignettes that provided knowledge for development of handbook content are credited within their respective pages.  

More generally, the following sources provided inspiration for this handbook:  
[The "R4Epis" project](https://r4epis.netlify.app/) (a collaboration between MSF and RECON)  
[R Epidemics Consortium (RECON)](https://www.repidemicsconsortium.org/)  
[R for Data Science book (R4DS)](https://r4ds.had.co.nz/)  
[bookdown: Authoring Books and Technical Documents with R Markdown](https://bookdown.org/yihui/bookdown/)  
[Netlify](https://www.netlify.com) hosts this website  


<!-- ### Image credits {-}   -->

<!-- Images in logo from US CDC Public Health Image Library) include [2013 Yemen looking for mosquito breeding sites](https://phil.cdc.gov/Details.aspx?pid=19623), [Ebola virus](https://phil.cdc.gov/Details.aspx?pid=23186), and [Survey in Rajasthan](https://phil.cdc.gov/Details.aspx?pid=19838).   -->


## Terms of Use and License   

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.


Academic courses and epidemiologist training programs are welcome to use this handbook with their students. If you have questions about your intended use, email **epirhandbook@gmail.com**.  


## Citation  

Batra, Neale et al. (2021), The Epidemiologist R Handbook. <a rel="license" href="https://zenodo.org/badge/231610102.svg"><img alt="DOI" style="border-width:0" src="https://zenodo.org/badge/231610102.svg" /></a><br />



## Contribution

If you would like to make a content contribution, please contact with us first via Github issues or by email. We are implementing a schedule for updates and are creating a contributor guide.  

Please note that the epiRhandbook project is released with a [Contributor Code of Conduct](https://contributor-covenant.org/version/2/0/CODE_OF_CONDUCT.html). By contributing to this project, you agree to abide by its terms.

