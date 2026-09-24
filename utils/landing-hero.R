# The landing hero and the nonprofit band, in one place for all eight languages.
#
# content/<lang>/index.qmd carries one chunk, byte-identical in every language:
#
#     source(here::here("utils", "landing-hero.R"))
#     cat(landing_hero(basename(getwd())))
#
# Quarto renders a chapter with content/<lang> as the working directory, so
# basename(getwd()) is the language code. here::here() anchors on
# epiRhandbook.Rproj at the repository root. The per-language project file is
# named _quarto.yaml, not _quarto.yml, so here() does not stop at it.
#
# The strings come from landing.yml, keyed by language code. A key the language
# does not declare falls back to English. A key no language declares stops the
# render, because an empty string in a rendered page looks deliberate.
#
# Three values are counted here and written down nowhere else:
#   the hero title      languages.yml, the title of this language
#   the chapter count   content/<main>/_quarto.yaml, book.chapters less index,
#                       about and acknowledgements, which are not chapters
#   the language count  languages.yml
#
# yaml::read_yaml reads an unquoted yes, no, true, false, on, off, y or n as a
# logical. The handlers keep each one as its text, as
# utils/check-language-consistency.R does.
# The Norwegian code no then stays a code, and a no: block key stays a key.
# landing.yml is stricter. An unquoted true or false, in any case, stops the
# render, because check 15 reads those two words as booleans and rejects them.
# Without this, eyebrow: true renders the text "true" and check 15 fails.
#
# The old Welcome page carried a live PayPal donation form. It is not here, and
# it MUST NOT come back. Richard removed it on 2026-09-18. Its button id is in no
# file of this repository, and the landing page gate fails on that string
# anywhere in the hero source. The nonprofit band ends with the Applied Epi link
# and the contact line, and that is the whole of it.

landing_hero <- function(lang, root = here::here()) {
  as_text <- list("bool#yes" = function(x) x, "bool#no" = function(x) x)
  read <- function(..., handlers = as_text) {
    yaml::read_yaml(file.path(root, ...), handlers = handlers)
  }
  # yaml catches an error inside a handler, warns, and keeps the logical. So the
  # handler only records the value, and the stop comes after the read.
  bools <- character(0)
  refuse_bool <- function(x) {
    if (tolower(x) %in% c("true", "false")) {
      bools <<- c(bools, x)
    }
    x
  }
  strings <- read(
    "landing.yml",
    handlers = list("bool#yes" = refuse_bool, "bool#no" = refuse_bool)
  )
  if (length(bools)) {
    stop(
      "landing.yml has the unquoted value or key ",
      paste(unique(bools), collapse = ", "),
      ". Put it in quotes, because check 15 reads it as a boolean."
    )
  }
  langs <- read("languages.yml")

  pick <- function(block, key) {
    if (!is.list(block) || is.null(names(block)) || !key %in% names(block)) {
      return(NULL)
    }
    block[[key]]
  }
  empty <- function(v) {
    is.null(v) || (is.character(v) && (length(v) != 1L || !nzchar(v)))
  }
  s <- function(key) {
    v <- pick(strings[[lang]], key)
    if (empty(v)) {
      v <- pick(strings[["en"]], key)
    }
    if (empty(v)) {
      stop(
        "landing.yml gives no value for '",
        key,
        "' on the ",
        lang,
        " landing page"
      )
    }
    v
  }
  svcs <- function() {
    v <- pick(strings[[lang]], "svc")
    if (!is.list(v) || !length(v)) {
      v <- pick(strings[["en"]], "svc")
    }
    if (!is.list(v) || !length(v)) {
      stop("landing.yml declares no service cards")
    }
    v
  }

  codes <- vapply(langs$languages, function(x) x$code, character(1))
  titles <- vapply(langs$languages, function(x) x$title, character(1))
  i <- match(lang, codes)
  if (is.na(i)) {
    i <- match(langs$main, codes)
  }
  title <- titles[i]
  languages_n <- length(codes)

  book <- read("content", langs$main, "_quarto.yaml")
  # The .qmd entries of book.chapters: the walk of project() in checks/langs.py.
  # A part that names a .qmd file is a page too, and it comes before its chapters.
  entries <- function(items) {
    out <- character(0)
    for (x in items) {
      if (is.character(x) && length(x) == 1 && endsWith(x, ".qmd")) {
        out <- c(out, x)
      } else if (is.list(x)) {
        part <- x[["part"]]
        if (is.character(part) && length(part) == 1 && endsWith(part, ".qmd")) {
          out <- c(out, part)
        }
        out <- c(out, entries(x[["chapters"]]))
      }
    }
    out
  }
  stems <- sub("\\.qmd$", "", entries(book$book$chapters))
  # index, about and acknowledgements are pages of the book, not chapters of it.
  chapters_n <- length(setdiff(stems, c("index", "about", "acknowledgements")))

  lead <- sub(
    "{brand}",
    paste0('<span class="brandname">', s("np_brand"), "</span>"),
    s("np_lead"),
    fixed = TRUE
  )

  card <- function(x) {
    paste0(
      '<div class="svc"><div class="svch">',
      x$h,
      "</div>",
      '<p class="svcp">',
      x$p,
      "</p>",
      '<a class="svclink" href="',
      x$href,
      '">',
      x$link,
      "</a></div>"
    )
  }

  stat <- function(num, label) {
    paste0(
      '<div class="ael-hstat"><div class="statnum">',
      num,
      "</div>",
      '<div class="statlbl">',
      label,
      "</div></div>"
    )
  }

  # Landing-only page chrome. It cannot live in theme-ael.scss, which every
  # chapter loads: hiding the title block there would hide every chapter title.
  # index.qmd keeps its "# Welcome {.unnumbered}" heading, because a Quarto book
  # numbers a chapter that has no unnumbered heading, and that would renumber all
  # 49 chapters. The heading is hidden here, and the hero carries the real title.
  style <- paste(
    "<style>",
    "#title-block-header { display: none; }",
    "#quarto-document-content > section > h1 { display: none; }",
    "main#quarto-document-content { padding-top: 0; }",
    "main.content { margin-top: 0 !important; }",
    "#quarto-content.page-columns { padding-top: 0 !important; margin-top: 0 !important; }",
    ".ael-hero, .npband { margin-left: calc(-1 * var(--ael-gutter, 2.4rem)); }",
    ".npband { border-bottom: none !important; }",
    ".page-navigation { display: none !important; }",
    "#quarto-document-content > section { padding-left: 0 !important; }",
    "</style>",
    sep = "\n"
  )

  # The hero search box is a handle on the real search, never a second one.
  # Quarto builds one #quarto-search per page and ael-extras.html moves it into
  # the app bar. What that container holds depends on the viewport, because
  # quarto-search.js sets detachedMediaQuery to "(max-width: 991px)" for a
  # textbox search:
  #   below 992px  a button, .aa-DetachedSearchButton. Clicking it opens the
  #                full-screen search overlay. Nothing else opens it.
  #   above 991px  an inline input, .aa-Input, configured with openOnFocus.
  #                Focusing it opens the panel.
  # The box takes the button first and the input second. Both branches read the
  # DOM when the reader acts, never at load, so a resize needs no rebinding.
  search_js <- paste(
    "<script>",
    "(function () {",
    '  var box = document.getElementById("ael-hsearch-input");',
    "  if (!box) { return; }",
    "  function openSearch() {",
    '    var button = document.querySelector("#quarto-search .aa-DetachedSearchButton");',
    "    if (button) { button.click(); return true; }",
    '    var input = document.querySelector("#quarto-search input");',
    "    if (!input) { return false; }",
    "    input.focus();",
    "    var text = box.value;",
    "    if (text) {",
    '      var d = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");',
    "      if (d) { d.set.call(input, text); } else { input.value = text; }",
    '      input.dispatchEvent(new Event("input", { bubbles: true }));',
    "    }",
    "    return true;",
    "  }",
    "  function handover(e) {",
    "    if (!openSearch()) { return; }",
    '    box.value = "";',
    "    box.blur();",
    "    if (e) { e.preventDefault(); }",
    "  }",
    '  box.addEventListener("focus", handover);',
    '  box.addEventListener("click", handover);',
    '  box.addEventListener("input", handover);',
    '  box.addEventListener("keydown", function (e) {',
    '    if (e.key === "Enter") { handover(e); }',
    "  });",
    "})();",
    "</script>",
    sep = "\n"
  )

  hero <- paste0(
    '<div class="ael-hero">\n',
    '<div class="ael-eyebrow">',
    s("eyebrow"),
    "</div>\n",
    '<h1 class="ael-htitle">',
    title,
    "</h1>\n",
    '<p class="ael-hsub">',
    s("subtitle"),
    "</p>\n",
    '<div class="ael-hsearch">\n',
    # No viewBox. Pandoc's HTML writer lowercases an attribute name, and SVG is
    # case-sensitive, so viewBox arrives as viewbox. A browser repairs that when it
    # parses foreign content in HTML, and libxml2 does not. The coordinates below are
    # already in the 16 by 16 user space, so no viewBox is needed at all.
    '<svg width="16" height="16" fill="none" stroke="currentColor" ',
    'stroke-width="1.5" stroke-linecap="round" aria-hidden="true">',
    '<circle cx="7" cy="7" r="4.6"></circle>',
    '<line x1="14" y1="14" x2="10.8" y2="10.8"></line></svg>\n',
    '<input id="ael-hsearch-input" type="search" placeholder="',
    s("search_placeholder"),
    '" aria-label="',
    s("search_label"),
    '">\n',
    "</div>\n",
    '<div class="ael-hbtns">\n',
    '<a class="btn light" href="',
    s("btn_start_href"),
    '">',
    s("btn_start"),
    "</a>\n",
    '<a class="btn out" href="',
    s("btn_offline_href"),
    '">',
    s("btn_offline"),
    "</a>\n",
    "</div>\n",
    '<div class="ael-hstats">\n',
    stat(s("stat_used_num"), s("stat_used_label")),
    "\n",
    stat(chapters_n, s("stat_chapters_label")),
    "\n",
    stat(languages_n, s("stat_languages_label")),
    "\n",
    "</div>\n</div>"
  )

  band <- paste0(
    '<div class="npband">\n',
    '<div class="nplockup">\n',
    '<img src="../../images/Applied_Epi_logo.png" alt="',
    s("np_brand"),
    '">\n',
    '<p class="nplead">',
    lead,
    "</p>\n</div>\n",
    '<div class="nptrust">',
    s("np_trust"),
    "</div>\n",
    '<div class="svcs">\n',
    paste(vapply(svcs(), card, character(1)), collapse = "\n"),
    "\n</div>\n",
    '<div class="npfoot">\n',
    '<a class="btn" href="',
    s("np_btn_href"),
    '">',
    s("np_btn"),
    "</a>\n",
    '<div class="nplinks">',
    s("np_links"),
    "</div>\n",
    "</div>\n</div>"
  )

  paste(
    "::: {.column-screen-right}",
    "```{=html}",
    style,
    hero,
    search_js,
    "```",
    ":::",
    "",
    "::: {.column-screen-right}",
    "```{=html}",
    band,
    "```",
    ":::",
    "",
    sep = "\n"
  )
}
