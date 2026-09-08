# Rules for this repository

Every rule below covers a chapter file under `chapters/`. `checks/check-sync.sh` enforces them
all. Run it from the repository root before you finish.

- A chapter MUST load its data with `appliedepidata::get_data()`.
- The directories chapter and the importing chapter teach file paths. Only those two MAY run
  `here("data", ...)`, because a reader needs this repository's `data/` folder to follow them.
- Every other chapter MAY show a `data/` path in an `eval=F` chunk, and MUST NOT run one.
- A chunk MUST NOT write into `data/`, in any chapter.
- A link to a section of the same page is `#id`, never `file.qmd#id`.
- A link MUST NOT cross languages. Point it at the target in its own language.
