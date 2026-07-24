# Equivalence harness for Unit C1 (rewrite EXECUTED data loads to appliedepidata).
#
# For every `access == "get_data"` row in utils/data-callsites.tsv, load the
# dataset TWO ways and compare with all.equal(..., check.attributes = FALSE):
#   (a) "original": the file-based reader appropriate to the referenced file
#       (rio::import(), sf::read_sf(), or ape::read.tree()), reconstructed from
#       the path literally quoted inside the call site's current_expr and
#       cross-checked against utils/data-map.tsv;
#   (b) "package":  appliedepidata::get_data(name = <aed_name>)
#
# Two datasets need bespoke reconstruction because they are not single files:
#   - germany_weather: 10 .nc files merged with stars::read_stars(fp, along = "time")
#     (the literal `stars::read_stars(file_paths)` call in time_series.qmd, with
#     no `along =`, errors under the installed stars 0.7-2 -- see run report)
#   - sle_adm3:         a multi-file shapefile bundle; only the "sle_adm3.shp"
#     entry point is read (sf::read_sf() follows the sidecar .dbf/.shx/.prj)
#
# Run from the repo root: Rscript utils/check-data-equivalence.R
# Requires: appliedepidata, rio, sf, ape, stars (installed via pak if missing).

d <- read.delim(
  "utils/data-callsites.tsv",
  sep = "\t",
  quote = "\"",
  stringsAsFactors = FALSE
)
gd <- d[d$access == "get_data", ]
gd$chapter[gd$chapter == "chapters/gis.qmd"] <- "_excluded/gis.qmd"
gd$chapter[
  gd$chapter == "chapters/epidemic_models.qmd"
] <- "_excluded/epidemic_models.qmd"

extract_path <- function(expr) {
  # pull every double-quoted literal that looks like a path component or filename
  m <- gregexpr('"([^"]*)"', expr)
  parts <- regmatches(expr, m)[[1]]
  parts <- gsub('"', "", parts)
  # drop obvious non-path literals (e.g. sep="," , na.strings, sheet names, comments)
  parts <- parts[parts != "," & parts != "NA" & nchar(parts) > 0]
  parts
}

reader_for_ext <- function(path) {
  ext <- tolower(tools::file_ext(path))
  if (ext %in% c("rds", "csv", "xlsx")) {
    return("rio")
  }
  if (ext == "shp") {
    return("sf")
  }
  if (ext == "txt") {
    return("ape")
  }
  if (ext == "json") {
    return("sf")
  }
  NA_character_
}

load_original <- function(row) {
  nm <- row$aed_name
  if (nm == "germany_weather") {
    fp <- list.files(
      here::here("data", "time_series", "weather"),
      full.names = TRUE
    )
    fp <- fp[grepl("germany", fp)]
    return(stars::read_stars(fp, along = "time"))
  }
  if (nm == "sle_adm3") {
    return(sf::read_sf(here::here("data", "gis", "shp", "sle_adm3.shp")))
  }
  parts <- extract_path(row$current_expr)
  # keep only the parts that form a data/... path (drop trailing args like which=.x names)
  if (length(parts) == 0 || parts[1] != "data") {
    stop("could not parse a data/ path from: ", row$current_expr)
  }
  # find the longest data/... prefix that is an existing file
  for (k in length(parts):2) {
    candidate <- here::here(do.call(file.path, as.list(parts[1:k])))
    if (file.exists(candidate)) {
      reader <- reader_for_ext(candidate)
      if (is.na(reader)) {
        stop("no reader for extension: ", candidate)
      }
      obj <- switch(
        reader,
        rio = rio::import(candidate),
        sf = sf::read_sf(candidate),
        ape = ape::read.tree(candidate)
      )
      return(obj)
    }
  }
  stop("no existing file found for: ", row$current_expr)
}

results <- data.frame(
  chapter = character(0),
  line = integer(0),
  aed_name = character(0),
  status = character(0),
  detail = character(0),
  stringsAsFactors = FALSE
)

for (i in seq_len(nrow(gd))) {
  row <- gd[i, ]
  status <- NA_character_
  detail <- ""
  orig <- tryCatch(load_original(row), error = function(e) e)
  pkg <- tryCatch(
    appliedepidata::get_data(name = row$aed_name),
    error = function(e) e
  )
  if (inherits(orig, "error") || inherits(pkg, "error")) {
    status <- "errored"
    detail <- paste0(
      if (inherits(orig, "error")) {
        paste0("original: ", conditionMessage(orig), "; ")
      } else {
        ""
      },
      if (inherits(pkg, "error")) {
        paste0("package: ", conditionMessage(pkg))
      } else {
        ""
      }
    )
  } else {
    eq <- tryCatch(
      all.equal(orig, pkg, check.attributes = FALSE),
      error = function(e) e
    )
    if (inherits(eq, "error")) {
      status <- "errored"
      detail <- paste0("all.equal: ", conditionMessage(eq))
    } else if (isTRUE(eq)) {
      status <- "identical"
    } else {
      status <- "different"
      detail <- paste(eq, collapse = " | ")
    }
  }
  results <- rbind(
    results,
    data.frame(
      chapter = row$chapter,
      line = row$line,
      aed_name = row$aed_name,
      status = status,
      detail = detail,
      stringsAsFactors = FALSE
    )
  )
}

cat("=== Equivalence harness results ===\n")
print(table(results$status))
cat("\n--- NOT identical (FAIL) ---\n")
notok <- results[results$status != "identical", ]
if (nrow(notok) == 0) {
  cat("(none)\n")
} else {
  for (i in seq_len(nrow(notok))) {
    r <- notok[i, ]
    cat(sprintf(
      "[%s] %s:%d  aed_name=%s\n  %s\n",
      r$status,
      r$chapter,
      r$line,
      r$aed_name,
      r$detail
    ))
  }
}

cat("\n--- full per-row results ---\n")
print(results, row.names = FALSE)
