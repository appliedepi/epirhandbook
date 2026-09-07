
# Use these commands to actually render the handbook
# See format and content choices below  
# Load necessary libraries
library(rlang)
library(readr)
library(yaml)
library(fs)
library(quarto)
library(withr)
library(purrr)
library(xml2)
library(brio)
library(cli)

# Define the functions

render_book <- function(project_path = ".", site_url = NULL) {
  render(path = project_path, site_url = site_url, type = "book")
}

render_website <- function(project_path = ".", site_url = NULL) {
  render(path = project_path, site_url = site_url, type = "website")
}

read_yaml_custom <- function(file) {
  string <- paste(readr::read_lines(file), collapse = "\n")
  yaml::yaml.load(string)
}

# Replace logical TRUE and FALSE with character "true" and "false" 
# in a nested list
replace_true_false <- function(list) {
  if (is.list(list)) {
    list <- lapply(list, replace_true_false)
  } else if (is.logical(list)) {
    list <- as.character(list)
    list <- gsub("TRUE", "true", list)
    list <- gsub("FALSE", "false", list)
    # Set class of this character vector to 'verbatim'
    # so that yaml::write_yaml() will not add quotation marks
    class(list) <- "verbatim"
  }
  return(list)
}

render <- function(path = ".", site_url = NULL, type = c("book", "website")) {
  # configuration ----
  config <- file.path(path, "_quarto.yml")
  config_contents <- read_yaml_custom(config)
  
  if (is.null(site_url)) {
    if (nzchar(Sys.getenv("BABELQUARTO_TESTS_URL")) || !on_ci()) {
      site_url <- site_url %||% config_contents[[type]][["site-url"]] %||% ""
    } else {
      # no end slash
      # for deploy previews
      # either root website (Netlify deploys)
      # or something else
      site_url <- Sys.getenv("BABELQUARTO_CI_URL", "")
    }
  }
  site_url <- sub("/$", "", site_url)
  
  output_dir <- config_contents[["project"]][["output-dir"]] %||%
    switch(
      type,
      book = "_book",
      website = "_site"
    )
  
  language_codes <- config_contents[["babelquarto"]][["languages"]]
  if (is.null(language_codes)) {
    cli::cli_abort("Can't find {.field babelquarto/languages} in {.field _quarto.yml}")
  }
  main_language <- config_contents[["babelquarto"]][["mainlanguage"]]
  if (is.null(main_language)) {
    cli::cli_abort("Can't find {.field babelquarto/mainlanguage} in {.field _quarto.yml}")
  }
  
  output_folder <- file.path(path, output_dir)
  if (fs::dir_exists(output_folder)) fs::dir_delete(output_folder)
  
  # render project ----
  temporary_directory <- withr::local_tempdir()
  fs::dir_copy(path, temporary_directory)
  withr::with_dir(file.path(temporary_directory, fs::path_file(path)), {
    fs::file_delete(fs::dir_ls(regexp = "\\...\\.qmd"))
    # metadata <- list("true")
    # names(metadata) <- sprintf("lang-%s", main_language)
    quarto::quarto_render(as_job = FALSE)
  })
  fs::dir_copy(
    file.path(temporary_directory, fs::path_file(path), output_dir),
    path
  )
  
  purrr::walk(
    language_codes,
    render_quarto_lang,
    path = path,
    output_dir = output_dir,
    type = type
  )
  
  # Add the language switching link to the sidebar ----
  ## For the main language ----
  
  # we need to recurse but not inside the language folders!
  all_docs <- fs::dir_ls(output_folder, glob = "*.html", recurse = TRUE)
  other_language_docs <- unlist(
    purrr::map(
      language_codes,
      ~fs::dir_ls(file.path(output_folder, .x), glob = "*.html", recurse = TRUE)
    )
  )
  main_language_docs <- setdiff(all_docs, other_language_docs)
  
  purrr::walk(
    language_codes,
    ~ purrr::walk(
      main_language_docs,
      add_link,
      main_language = main_language,
      language_code = .x,
      site_url = site_url,
      type = type,
      config = config_contents,
      output_folder = output_folder
    )
  )
  
  ## For other languages ----
  for (other_lang in language_codes) {
    
    languages_to_add <- c(main_language, setdiff(language_codes, other_lang))
    purrr::walk(
      languages_to_add,
      ~ purrr::walk(
        fs::dir_ls(file.path(output_folder, other_lang),
                   glob = "*.html", recurse = TRUE
        ),
        add_link,
        main_language = main_language,
        language_code = .x,
        site_url = site_url,
        type = type,
        config = config_contents,
        output_folder = output_folder
      )
    )
  }
  
}

render_quarto_lang <- function(language_code, path, output_dir, type) {
  
  temporary_directory <- withr::local_tempdir()
  fs::dir_copy(path, temporary_directory)
  project_name <- fs::path_file(path)
  
  config <- read_yaml_custom(file.path(temporary_directory, project_name, "_quarto.yml"))
  config$lang <- language_code
  config[[type]][["title"]] <- config[[sprintf("title-%s", language_code)]] %||% config[[type]][["title"]]
  config[[type]][["description"]] <- config[[sprintf("description-%s", language_code)]] %||% config[[type]][["description"]]
  
  if (type == "book") {
    config[[type]][["author"]] <- config[[sprintf("author-%s", language_code)]] %||% config[[type]][["author"]]
    config[["book"]][["chapters"]] <- purrr::map(
      config[["book"]][["chapters"]],
      use_lang_chapter,
      language_code = language_code,
      book_name = project_name,
      directory = temporary_directory
    )
    # Replace TRUE and FALSE with 'true' and 'false'
    # to avoid converting to "yes" and "no"
    config <- replace_true_false(config)
    yaml::write_yaml(config, file.path(temporary_directory, project_name, "_quarto.yml"))
  }
  
  if (type == "website") {
    
    # only keep what's needed
    qmds <- fs::dir_ls(
      file.path(temporary_directory, fs::path_file(path)),
      glob = "*.qmd"
    )
    language_qmds <- qmds[grepl(sprintf("%s.qmd", language_code), qmds)]
    fs::file_delete(qmds[!(qmds %in% language_qmds)])
    for (qmd_path in language_qmds) {
      fs::file_move(
        qmd_path,
        sub(sprintf("%s.qmd", language_code), "qmd", qmd_path)
      )
    }
    # Replace TRUE and FALSE with 'true' and 'false'
    # to avoid converting to "yes" and "no"
    config <- replace_true_false(config)
    
    yaml::write_yaml(config, file.path(temporary_directory, project_name, "_quarto.yml"))
  }
  
  config_lines <- brio::read_lines(file.path(temporary_directory, project_name, "_quarto.yml"))
  brio::write_lines(config_lines, file.path(temporary_directory, project_name, "_quarto.yml"))
  
  # Render language book
  # metadata <- list("yes")
  # names(metadata) <- sprintf("lang-%s", language_code)
  withr::with_dir(file.path(temporary_directory, project_name), {
    quarto::quarto_render(
      as_job = FALSE
    )
  })
  
  # Copy it to local not temporary _book/<language-code>
  fs::dir_copy(
    file.path(temporary_directory, project_name, output_dir),
    file.path(path, output_dir, language_code)
  )
  
}

use_lang_chapter <- function(chapters_list, language_code, book_name, directory) {
  withr::local_dir(file.path(directory, book_name))
  
  original_chapters_list <- chapters_list
  
  if (is.list(chapters_list)) {
    # part translation
    chapters_list[["part"]] <- chapters_list[[sprintf("part-%s", language_code)]] %||%
      chapters_list[["part"]]
    
    # chapters translation
    
    chapters_list$chapters <- gsub("\\.Rmd", sprintf(".%s.Rmd", language_code), chapters_list$chapters)
    chapters_list$chapters <- gsub("\\.qmd", sprintf(".%s.qmd", language_code), chapters_list$chapters)
    if (any(!fs::file_exists(chapters_list$chapters))) {
      chapters_not_translated <- !fs::file_exists(chapters_list$chapters)
      fs::file_move(
        original_chapters_list$chapters[chapters_not_translated],
        gsub("\\.Rmd", sprintf(".%s.Rmd", language_code) ,
             gsub(
               "\\.qmd", sprintf(".%s.qmd", language_code),
               original_chapters_list$chapters[chapters_not_translated])
        )
      )
    }
    
    if (length(chapters_list$chapters) == 1) {
      chapters_list$chapters <- as.list(chapters_list$chapters) # https://github.com/ropensci-review-tools/babelquarto/issues/32
    }
  } else {
    chapters_list <- gsub("\\.Rmd", sprintf(".%s.Rmd", language_code), chapters_list)
    chapters_list <- gsub("\\.qmd", sprintf(".%s.qmd", language_code), chapters_list)
    if (!fs::file_exists(file.path(directory, book_name, chapters_list))) {
      fs::file_move(
        original_chapters_list,
        chapters_list
      )
    }
  }
  
  chapters_list
}

add_link <- function(path, main_language = main_language,
                     language_code, site_url, type, config, output_folder) {
  html <- xml2::read_html(path)
  
  document_path <- path
  
  codes <- config[["babelquarto"]][["languagecodes"]]
  current_lang <- purrr::keep(codes, ~.x[["name"]] == language_code)
  
  version_text <- if (length(current_lang) > 0) {
    current_lang[[1]][["text"]] %||%
      sprintf("Version in %s", toupper(language_code))
  } else {
    sprintf("Version in %s", toupper(language_code))
  }
  
  code_in_filename <- unlist(regmatches(path, gregexpr("\\...\\.html", path)))
  code_in_path <- unlist(regmatches(path, gregexpr(
    file.path(output_folder, "..", basename(path)),
    path
  )))
  
  if (length(code_in_filename) > 0) {
    file_lang <- sub("\\.", "", sub("\\.html", "", code_in_filename))
    path <- sub(sprintf("\\.%s\\.html$", file_lang), ".html", path)
  } else {
    if (length(code_in_path) > 0) {
      messy_code <- sub(
        output_folder,
        "",
        sub(basename(path), "", path)
      )
      file_lang <- unlist(
        regmatches(messy_code, gregexpr("[a-zA-Z]+", messy_code))
      )
    } else {
      file_lang <- main_language
    }
  }
  
  if (language_code == main_language) {
    new_path <-  if (type == "book") {
      sub(
        "\\...\\.html", ".html",
        path_rel(path, output_folder, file_lang, main_language)
      )
    } else {
      path_rel(path, output_folder, file_lang, main_language)
    }
    href <- sprintf("%s/%s", site_url, new_path)
  } else {
    base_path <- sub(
      "\\..\\.html", ".html",
      path_rel(path, output_folder, file_lang, main_language)
    )
    new_path <- if (type == "book") {
      fs::path_ext_set(base_path, sprintf(".%s.html", language_code))
    } else {
      base_path
    }
    href <- sprintf("%s/%s/%s", site_url, language_code, new_path)
  }
  
  if (type == "book") {
    
    logo <- xml2::xml_find_first(html, "//div[contains(@class,'sidebar-header')]")
    
    languages_links <- xml2::xml_find_first(html, "//ul[@id='languages-links']")
    languages_links_div_exists <- (length(languages_links) > 0)
    
    if (!languages_links_div_exists) {
      xml2::xml_add_sibling(
        logo,
        "div",
        class = "dropdown",
        id = "languages-links-parent",
        .where = "after"
      )
      
      parent <- xml2::xml_find_first(html, "//div[@id='languages-links-parent']")
      xml2::xml_add_child(
        parent,
        "button",
        "",
        class = "btn btn-primary dropdown-toggle",
        type="button",
        `data-bs-toggle` = "dropdown",
        `aria-expanded` = "false",
        id = "languages-button"
      )
      
      xml2::xml_add_child(
        xml2::xml_find_first(html, "//button[@id='languages-button']"),
        "i",
        class = "bi bi-globe2"
      )
      
      xml2::xml_add_child(
        parent,
        "ul",
        class = "dropdown-menu",
        id = "languages-links"
      )
      
      languages_links <- xml2::xml_find_first(html, "//ul[@id='languages-links']")
    }
    
    xml2::xml_add_child(
      languages_links,
      "a",
      version_text,
      class = "dropdown-item",
      href = href,
      id = sprintf("language-link-%s", language_code)
    )
    xml2::xml_add_parent(
      xml2::xml_find_first(html, sprintf("a[id='%s']", sprintf("language-link-%s", language_code))),
      "li"
    )
    
  } else {
    
    languages_links <- xml2::xml_find_first(html, "//ul[@id='languages-links']")
    languages_links_div_exists <- (length(languages_links) > 0)
    
    if (!languages_links_div_exists) {
      navbar <- xml2::xml_find_first(html, "//div[@id='navbarCollapse']")
      
      xml2::xml_add_child(
        navbar,
        "div",
        class = "dropdown",
        id = "languages-links-parent",
        .where = 0
      )
      
      parent <- xml2::xml_find_first(html, "//div[@id='languages-links-parent']")
      xml2::xml_add_child(
        parent,
        "button",
        "",
        class = "btn btn-primary dropdown-toggle",
        type="button",
        `data-bs-toggle` = "dropdown",
        `aria-expanded` = "false",
        id = "languages-button"
      )
      
      xml2::xml_add_child(
        xml2::xml_find_first(html, "//button[@id='languages-button']"),
        "i",
        class = "bi bi-globe2"
      )
      
      xml2::xml_add_child(
        parent,
        "ul",
        class = "dropdown-menu",
        id = "languages-links"
      )
      
      languages_links <- xml2::xml_find_first(html, "//ul[@id='languages-links']")
    }
    xml2::xml_add_child(
      languages_links,
      "a",
      version_text,
      class = "dropdown-item",
      href = href,
      id = sprintf("language-link-%s", language_code),
      .where = 0
    )
    xml2::xml_add_parent(
      xml2::xml_find_first(html, sprintf("//a[@id='language-link-%s']", language_code)),
      "li"
    )
  }
  
  xml2::write_html(html, document_path)
}

# as in testthat
on_ci <- function() {
  isTRUE(as.logical(Sys.getenv("CI", "false")))
}

path_rel <- function(path, output_folder, lang, main_language) {
  if (lang == main_language) {
    fs::path_rel(path, start = output_folder)
  } else {
    fs::path_rel(path, start = file.path(output_folder, lang))
  }
}



# Call the render_book function
render_book()


# WHOLE HANDBOOK
# babelquarto::render_book()

# PREVIEW ONLY ONE OR SOME PAGES
# changes the metadata-files tag in _quarto.yml
