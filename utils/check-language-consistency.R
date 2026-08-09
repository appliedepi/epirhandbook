# Cross-language consistency check for the chapters that _quarto.yml declares.
#
# The check compares each English chapter against each translation on three axes.
#
# Chunk extraction.
#   A chunk opens on a fence line whose engine is r. The engine name ends at
#   }, at a comma, or at whitespace. An engine such as ruby, rust or rmd
#   starts with r and is not R. The check MUST NOT open a chunk there.
#   A chunk opened with N backticks closes on the first fence line of N or
#   more backticks. A shorter run of backticks is chunk content.
#
# Axis 1: chunk bodies.
#   The check extracts every ```{r ...} chunk and normalises each chunk body.
#   Normalisation runs four steps on each body line:
#     1. Remove the comment tail. A # inside a string literal is not a comment.
#     2. Replace each string literal with a fixed placeholder.
#     3. Remove all whitespace.
#     4. Drop the line when nothing is left.
#   A chunk that normalises to zero lines still counts as a chunk.
#   Each pair is chunk-count, code-diff or clean.
#
# Axis 2: chunk headers.
#   The check compares the ordered list of fence opening lines, after trimws().
#   Each pair is identical, count-differs or text-differs.
#   A text-differs pair is cosmetic when the two lists agree after the check
#   removes all whitespace and rewrites ' as ". Every other one is semantic.
#   A dropped echo=F is semantic. It changes what the reader sees, and a
#   body-only check cannot find it.
#
# Axis 3a: get_data() call-site counts, per language pair.
#   The check counts get_data(name = ) call sites inside R chunks only, and it
#   counts them in the normalised chunk code of axis 1. A commented-out call
#   and a call inside a string literal are text, not call sites.
#   Prose names get_data() too, so a whole-file count reports false divergences.
#   This axis needs executable code only. It never needs the dataset name, so
#   the axis 1 normaliser may mask every string literal.
#
# Axis 3b: dataset names, validated at two scopes.
#   The check validates every get_data(name = "X") literal against
#   appliedepidata::list_data()$name. It reports two scopes separately.
#     whole-file  Every literal in the file, prose included. A chapter that
#                 prints a wrong name in a sentence is a defect. A reader
#                 copies that sentence and runs it.
#     in-chunk    Every literal inside an {r} chunk, after the check removes
#                 the R comment tails. The string literal contents stay whole,
#                 so the dataset name survives.
#   An R comment stripper MUST NOT run over a whole .qmd file. Every markdown
#   heading starts with #, so the stripper would delete the prose.
#   The in-chunk scope drops a commented-out name. It keeps a name that sits
#   inside a string literal, because it cannot mask the literal and still read
#   the name. Axis 3a masks the literals, and it needs no name.
#   For each name outside the catalogue the report prints the scopes that hold
#   it. A name in a chunk is live code. A name only in prose is not.
#   The literal "..." is a placeholder that English carries too. The report
#   names it as a placeholder, not as a defect.
#
# Three input rules decide the counts.
#   1. Read book.chapters from _quarto.yml. Keep the .qmd entries only. The same
#      structure also holds the part titles in 9 languages.
#   2. Keep the .qmd entries under chapters/ only. index.qmd sits at the repo
#      root. It is the book landing page and it has no translations in
#      chapters/. The report prints the entry it skips.
#   3. Read babelquarto.languages, which holds 7 languages. The check MUST NOT
#      read babelquarto.languagecodes, which holds 9 entries and adds de and en.
#      The German chapters live under _excluded/de/.
#
# Nothing runs this script automatically. A human types the command.
#
# Run from the repo root: Rscript utils/check-language-consistency.R
# Pass a chapters directory as the first argument to check a copy:
#   Rscript utils/check-language-consistency.R /tmp/scratch/chapters
# Requires: yaml, appliedepidata.

args <- commandArgs(trailingOnly = TRUE)
chapters_dir <- if (length(args) >= 1) args[[1]] else "chapters"

FENCE_OPEN <- "^[ \t]*`{3,}\\{r[},[:space:]]"
FENCE_RUN <- "`{3,}"
FENCE_CLOSE_FMT <- "^[ \t]*`{%d,}[ \t]*$"
STRING_PLACEHOLDER <- "<string>"
GET_DATA_CALL <- "get_data\\s*\\(\\s*name\\s*="
GET_DATA_NAME <- "get_data\\s*\\(\\s*name\\s*=\\s*[\"']([^\"']*)[\"']"
NAME_PLACEHOLDER <- "..."

read_lines_utf8 <- function(path) {
  readLines(path, warn = FALSE, encoding = "UTF-8")
}

# Count the backticks in the fence run that opens a line.
fence_length <- function(ln) {
  nchar(regmatches(ln, regexpr(FENCE_RUN, ln)))
}

# The closing fence of a chunk opened with n backticks needs n or more.
fence_close <- function(n) {
  sprintf(FENCE_CLOSE_FMT, n)
}

# Split a chapter into R chunk headers (with their line numbers) and chunk bodies.
read_chunks <- function(path) {
  lines <- read_lines_utf8(path)
  headers <- character(0)
  header_lines <- integer(0)
  bodies <- list()
  open <- FALSE
  close_pattern <- ""
  buf <- character(0)
  for (i in seq_along(lines)) {
    ln <- lines[[i]]
    if (!open) {
      if (grepl(FENCE_OPEN, ln)) {
        open <- TRUE
        close_pattern <- fence_close(fence_length(ln))
        buf <- character(0)
        headers <- c(headers, trimws(ln))
        header_lines <- c(header_lines, i)
      }
    } else if (grepl(close_pattern, ln)) {
      open <- FALSE
      bodies[[length(bodies) + 1L]] <- buf
    } else {
      buf <- c(buf, ln)
    }
  }
  if (open) {
    bodies[[length(bodies) + 1L]] <- buf
  }
  list(headers = headers, header_lines = header_lines, bodies = bodies)
}

# Remove the comment tail from one R source line.
# The scan is per line and tracks the quote character, so a # inside a string
# stays and a quote inside a comment is ignored.
# keep_strings decides what the scan does with each string literal.
#   TRUE  keeps the literal and its contents, so a dataset name survives.
#   FALSE replaces the literal with STRING_PLACEHOLDER.
scan_code_line <- function(s, keep_strings) {
  chars <- strsplit(s, "", fixed = TRUE)[[1]]
  n <- length(chars)
  out <- character(0)
  quote <- ""
  i <- 1L
  while (i <= n) {
    ch <- chars[[i]]
    if (quote == "") {
      if (ch == "#") {
        break
      }
      if (ch == "\"" || ch == "'") {
        quote <- ch
        out <- c(out, if (keep_strings) ch else STRING_PLACEHOLDER)
        i <- i + 1L
        next
      }
      out <- c(out, ch)
      i <- i + 1L
    } else {
      if (ch == "\\") {
        if (keep_strings) {
          out <- c(out, chars[seq.int(i, min(i + 1L, n))])
        }
        i <- i + 2L
        next
      }
      if (ch == quote) {
        quote <- ""
      }
      if (keep_strings) {
        out <- c(out, ch)
      }
      i <- i + 1L
    }
  }
  paste(out, collapse = "")
}

# Axis 1 form: no comment tail, and every string literal masked.
strip_code_line <- function(s) {
  scan_code_line(s, keep_strings = FALSE)
}

# Name-scope form: no comment tail, and every string literal kept whole.
strip_comment_tail <- function(s) {
  scan_code_line(s, keep_strings = TRUE)
}

normalise_body <- function(body) {
  x <- vapply(body, strip_code_line, character(1), USE.NAMES = FALSE)
  x <- gsub("[[:space:]]", "", x)
  x[nzchar(x)]
}

canonical_header <- function(h) {
  gsub("'", "\"", gsub("[[:space:]]", "", h))
}

count_matches <- function(txt, pattern) {
  if (length(txt) == 0 || !nzchar(txt)) {
    return(0L)
  }
  m <- gregexpr(pattern, txt)[[1]]
  if (length(m) == 1L && m[[1]] == -1L) 0L else length(m)
}

# Count call sites in normalised chunk code, not in raw chunk text.
# Normalisation drops the R comments and masks the string literals.
# A commented-out call is not a call site. Nor is a call inside a string.
count_get_data_calls <- function(bodies) {
  code <- unlist(lapply(bodies, normalise_body), use.names = FALSE)
  count_matches(paste(code, collapse = "\n"), GET_DATA_CALL)
}

names_in_text <- function(txt) {
  m <- regmatches(txt, gregexpr(GET_DATA_NAME, txt))[[1]]
  if (length(m) == 0) character(0) else sub(GET_DATA_NAME, "\\1", m)
}

# Whole-file scope. Every literal in the file, prose included.
# An R comment stripper MUST NOT run here. Every markdown heading starts with #.
get_data_names_in_file <- function(path) {
  names_in_text(paste(read_lines_utf8(path), collapse = "\n"))
}

# In-chunk scope. Every literal inside an {r} chunk, comment tails removed.
# The string literal contents stay whole, so the dataset name survives.
get_data_names_in_chunks <- function(path) {
  bodies <- read_chunks(path)$bodies
  code <- unlist(
    lapply(
      bodies,
      function(b) vapply(b, strip_comment_tail, character(1), USE.NAMES = FALSE)
    ),
    use.names = FALSE
  )
  names_in_text(paste(code, collapse = "\n"))
}

# --- inputs -------------------------------------------------------------

cfg <- yaml::read_yaml("_quarto.yml")
declared <- unlist(cfg$book$chapters, use.names = FALSE)
declared_qmd <- declared[grepl("\\.qmd$", declared)]
declared_here <- declared_qmd[grepl("^chapters/", declared_qmd)]
declared_elsewhere <- setdiff(declared_qmd, declared_here)
stems <- sub("\\.qmd$", "", basename(declared_here))
langs <- unlist(cfg$babelquarto$languages, use.names = FALSE)
catalogue <- appliedepidata::list_data()$name

english_path <- function(stem) file.path(chapters_dir, paste0(stem, ".qmd"))
translated_path <- function(stem, lang) {
  file.path(chapters_dir, paste0(stem, ".", lang, ".qmd"))
}

# --- comparison ---------------------------------------------------------

results <- data.frame(
  chapter = character(0),
  lang = character(0),
  chunks_en = integer(0),
  chunks_tr = integer(0),
  body = character(0),
  chunks_differing = integer(0),
  header = character(0),
  header_kind = character(0),
  headers_differing = integer(0),
  get_data_en = integer(0),
  get_data_tr = integer(0),
  get_data = character(0),
  stringsAsFactors = FALSE
)
body_detail <- list()
header_detail <- list()
missing_files <- character(0)

for (stem in stems) {
  en_file <- english_path(stem)
  if (!file.exists(en_file)) {
    missing_files <- c(missing_files, en_file)
    next
  }
  en <- read_chunks(en_file)
  en_norm <- lapply(en$bodies, normalise_body)
  en_calls <- count_get_data_calls(en$bodies)
  for (lang in langs) {
    tr_file <- translated_path(stem, lang)
    if (!file.exists(tr_file)) {
      missing_files <- c(missing_files, tr_file)
      next
    }
    pair <- paste0(stem, ".", lang)
    tr <- read_chunks(tr_file)
    tr_norm <- lapply(tr$bodies, normalise_body)
    tr_calls <- count_get_data_calls(tr$bodies)

    n_body_diff <- 0L
    if (length(en_norm) != length(tr_norm)) {
      body_status <- "chunk-count"
    } else {
      differing <- which(!mapply(identical, en_norm, tr_norm))
      n_body_diff <- length(differing)
      body_status <- if (n_body_diff > 0L) "code-diff" else "clean"
      for (k in differing) {
        body_detail[[length(body_detail) + 1L]] <- list(
          pair = pair,
          chunk = k,
          en_line = en$header_lines[[k]],
          tr_line = tr$header_lines[[k]],
          en_only = setdiff(en_norm[[k]], tr_norm[[k]]),
          tr_only = setdiff(tr_norm[[k]], en_norm[[k]])
        )
      }
    }

    n_header_diff <- 0L
    header_kind <- ""
    if (length(en$headers) != length(tr$headers)) {
      header_status <- "count-differs"
    } else if (identical(en$headers, tr$headers)) {
      header_status <- "identical"
    } else {
      header_status <- "text-differs"
      differing <- which(en$headers != tr$headers)
      n_header_diff <- length(differing)
      header_kind <- if (
        identical(canonical_header(en$headers), canonical_header(tr$headers))
      ) {
        "cosmetic"
      } else {
        "semantic"
      }
      for (k in differing) {
        header_detail[[length(header_detail) + 1L]] <- list(
          pair = pair,
          kind = header_kind,
          chunk = k,
          en_line = en$header_lines[[k]],
          tr_line = tr$header_lines[[k]],
          en = en$headers[[k]],
          tr = tr$headers[[k]]
        )
      }
    }

    results <- rbind(
      results,
      data.frame(
        chapter = stem,
        lang = lang,
        chunks_en = length(en$bodies),
        chunks_tr = length(tr$bodies),
        body = body_status,
        chunks_differing = n_body_diff,
        header = header_status,
        header_kind = header_kind,
        headers_differing = n_header_diff,
        get_data_en = en_calls,
        get_data_tr = tr_calls,
        get_data = if (en_calls == tr_calls) "match" else "differs",
        stringsAsFactors = FALSE
      )
    )
  }
}

# --- dataset names ------------------------------------------------------

name_rows <- data.frame(
  file = character(0),
  name = character(0),
  status = character(0),
  scope = character(0),
  in_whole_file = logical(0),
  in_chunk = logical(0),
  stringsAsFactors = FALSE
)
n_literals_whole <- 0L
n_literals_chunk <- 0L
n_files_scanned <- 0L
for (stem in stems) {
  files <- c(
    english_path(stem),
    vapply(
      langs,
      function(l) translated_path(stem, l),
      character(1)
    )
  )
  for (f in files) {
    if (!file.exists(f)) {
      next
    }
    n_files_scanned <- n_files_scanned + 1L
    found_whole <- get_data_names_in_file(f)
    found_chunk <- get_data_names_in_chunks(f)
    n_literals_whole <- n_literals_whole + length(found_whole)
    n_literals_chunk <- n_literals_chunk + length(found_chunk)
    outside <- unique(c(found_whole, found_chunk))
    outside <- outside[!outside %in% catalogue]
    for (nm in outside) {
      seen_whole <- nm %in% found_whole
      seen_chunk <- nm %in% found_chunk
      name_rows <- rbind(
        name_rows,
        data.frame(
          file = f,
          name = nm,
          status = if (nm == NAME_PLACEHOLDER) {
            "placeholder"
          } else {
            "unknown-name"
          },
          scope = if (seen_whole && seen_chunk) {
            "whole-file+in-chunk"
          } else if (seen_chunk) {
            "in-chunk only"
          } else {
            "whole-file only"
          },
          in_whole_file = seen_whole,
          in_chunk = seen_chunk,
          stringsAsFactors = FALSE
        )
      )
    }
  }
}
outside_whole <- name_rows[name_rows$in_whole_file, , drop = FALSE]
outside_chunk <- name_rows[name_rows$in_chunk, , drop = FALSE]

# --- report -------------------------------------------------------------

cat("=== Cross-language code and chunk-header consistency ===\n")
cat("chapters directory:", chapters_dir, "\n")
cat(
  "declared .qmd entries in _quarto.yml book.chapters:",
  length(declared_qmd),
  "\n"
)
cat(
  "  under chapters/ and checked:",
  length(stems),
  "\n"
)
cat(
  "  outside chapters/ and skipped:",
  length(declared_elsewhere),
  if (length(declared_elsewhere) > 0) {
    paste0("(", paste(declared_elsewhere, collapse = ", "), ")")
  } else {
    ""
  },
  "\n"
)
cat(
  "languages from babelquarto.languages:",
  length(langs),
  paste0("(", paste(langs, collapse = ", "), ")"),
  "\n"
)
cat("pairs:", nrow(results), "\n")
cat("missing files:", length(missing_files), "\n")
if (length(missing_files) > 0) {
  cat(paste0("  ", missing_files, collapse = "\n"), "\n")
}

cat("\n--- chunk bodies ---\n")
print(table(results$body))
cat(
  "differing chunks inside code-diff pairs:",
  sum(results$chunks_differing),
  "\n"
)

cat("\n--- chunk headers ---\n")
print(table(results$header))
cat(
  "text-differs split: cosmetic",
  sum(results$header_kind == "cosmetic"),
  "/ semantic",
  sum(results$header_kind == "semantic"),
  "\n"
)

cat("\n--- get_data(name = ) call sites inside R chunks ---\n")
print(table(results$get_data))

cat("\n--- dataset names against appliedepidata::list_data() ---\n")
cat("files scanned:", n_files_scanned, "\n")
cat("catalogue entries:", length(catalogue), "\n")

cat("\n[whole-file scope] every literal in the file, prose included\n")
cat("  name literals found:", n_literals_whole, "\n")
cat("  dataset names outside catalogue:", nrow(outside_whole), "\n")
cat(
  "    benign placeholder \"...\":",
  sum(outside_whole$status == "placeholder"),
  "\n"
)
cat("    unknown names:", sum(outside_whole$status == "unknown-name"), "\n")

cat("\n[in-chunk scope] literals inside {r} chunks, R comment tails removed\n")
cat("  name literals found:", n_literals_chunk, "\n")
cat("  dataset names outside catalogue:", nrow(outside_chunk), "\n")
cat(
  "    benign placeholder \"...\":",
  sum(outside_chunk$status == "placeholder"),
  "\n"
)
cat("    unknown names:", sum(outside_chunk$status == "unknown-name"), "\n")

cat(
  "\nprose-only name literals (whole-file minus in-chunk):",
  n_literals_whole - n_literals_chunk,
  "\n"
)

cat("\nnames outside the catalogue, and the scopes that hold each one:\n")
cat("  whole-file+in-chunk: the name sits in R chunk code. Treat it as live.\n")
cat("  whole-file only: the name sits in prose, or in an R comment.\n")
cat(
  "  in-chunk only: the chunk scope reads it and the whole-file scope does not.\n"
)
if (nrow(name_rows) == 0) {
  cat("(none)\n")
} else {
  print(
    name_rows[, c("file", "name", "status", "scope")],
    row.names = FALSE
  )
}

cat("\n--- FAIL: chunk body divergences ---\n")
bad_body <- results[results$body != "clean", ]
if (nrow(bad_body) == 0) {
  cat("(none)\n")
} else {
  for (i in seq_len(nrow(bad_body))) {
    r <- bad_body[i, ]
    cat(sprintf(
      "[%s] %s.%s  chunks en=%d tr=%d  differing=%d\n",
      r$body,
      r$chapter,
      r$lang,
      r$chunks_en,
      r$chunks_tr,
      r$chunks_differing
    ))
  }
  cat("\n  per differing chunk (normalised lines):\n")
  for (d in body_detail) {
    cat(sprintf(
      "  %s  chunk %d  (en line %d, tr line %d)\n",
      d$pair,
      d$chunk,
      d$en_line,
      d$tr_line
    ))
    if (length(d$en_only) == 0 && length(d$tr_only) == 0) {
      cat("    same lines, different order\n")
    }
    for (x in d$en_only) {
      cat("    en only: ", x, "\n", sep = "")
    }
    for (x in d$tr_only) {
      cat("    tr only: ", x, "\n", sep = "")
    }
  }
}

cat("\n--- FAIL: chunk header divergences ---\n")
bad_header <- results[results$header != "identical", ]
if (nrow(bad_header) == 0) {
  cat("(none)\n")
} else {
  for (i in seq_len(nrow(bad_header))) {
    r <- bad_header[i, ]
    cat(sprintf(
      "[%s%s] %s.%s  headers en=%d tr=%d  differing=%d\n",
      r$header,
      if (nzchar(r$header_kind)) paste0("/", r$header_kind) else "",
      r$chapter,
      r$lang,
      r$chunks_en,
      r$chunks_tr,
      r$headers_differing
    ))
  }
  cat("\n  semantic header differences:\n")
  semantic <- Filter(function(d) d$kind == "semantic", header_detail)
  if (length(semantic) == 0) {
    cat("  (none)\n")
  }
  for (d in semantic) {
    cat(sprintf("  %s  chunk %d\n", d$pair, d$chunk))
    cat("    en line ", d$en_line, ": ", d$en, "\n", sep = "")
    cat("    tr line ", d$tr_line, ": ", d$tr, "\n", sep = "")
  }
  cat("\n  cosmetic header differences:\n")
  cosmetic <- Filter(function(d) d$kind == "cosmetic", header_detail)
  if (length(cosmetic) == 0) {
    cat("  (none)\n")
  }
  for (d in cosmetic) {
    cat(sprintf("  %s  chunk %d\n", d$pair, d$chunk))
    cat("    en line ", d$en_line, ": ", d$en, "\n", sep = "")
    cat("    tr line ", d$tr_line, ": ", d$tr, "\n", sep = "")
  }
}

cat("\n--- FAIL: get_data(name = ) call-site counts ---\n")
bad_calls <- results[results$get_data != "match", ]
if (nrow(bad_calls) == 0) {
  cat("(none)\n")
} else {
  for (i in seq_len(nrow(bad_calls))) {
    r <- bad_calls[i, ]
    cat(sprintf(
      "[differs] %s.%s  en=%d tr=%d\n",
      r$chapter,
      r$lang,
      r$get_data_en,
      r$get_data_tr
    ))
  }
}

cat("\n--- full per-row results ---\n")
print(results, row.names = FALSE)
