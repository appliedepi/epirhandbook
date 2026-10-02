# Rules for this repository

Every rule below covers a chapter file under `content/<lang>/`. `checks/check-sync.sh` enforces
them all. Run it from the repository root before you finish.

- A chapter MUST load its data with `appliedepidata::get_data()`.
- The directories chapter and the importing chapter teach file paths. Only those two MAY run
  `here("data", ...)`, because a reader needs this repository's `data/` folder to follow them.
- Every other chapter MAY show a `data/` path in an `eval=F` chunk, and MUST NOT run one.
- A chunk MUST NOT write into `data/`, in any chapter.
- A link to a section of the same page is `#id`, never `file.qmd#id`.
- A link MUST NOT cross languages. Point it at `<stem>.qmd` in the same folder.
- Every chapter file except `index.qmd` MUST carry an `aliases:` entry that keeps its old URL
  alive: `/new_pages/<stem>.html` in English, `/new_pages/<stem>.<lang>.html` elsewhere. The
  spelling MUST match the old page. `transition_to_r` is the one stem that page spelled
  differently, as `transition_to_R`, and English keeps both spellings. `editorial_style` also
  carries the aliases of `about` and `acknowledgements`, the two pages merged into it: their
  `/new_pages/` URLs and their current `/<stem>.html` URLs.
- `languages.yml` is the language list, and `content/<lang>/_quarto.yaml` is the chapter list.
  The eight project files MUST declare the same stems in the same order. Every declared stem
  MUST exist as a file in every language folder.

# Visual design

Visual design follows the Applied Epi design system: https://claude.ai/artifact/2xfUuazFtAp5oqzya4NH7X. Read its `project/README.md` before you change `theme-*.scss`, `ael-extras.html`, `banner.html` or any landing-page markup.
