library(fs)
library(withr)
# Add list of chapters to index files --------------------------------------------------------

# Define the list of chapters
chapter_list <- c("editorial_style.qmd", "data_used.qmd", "basics.qmd", "transition_to_r.qmd", "packages_suggested.qmd", "r_projects.qmd", "importing.qmd", "cleaning.qmd",
                 "dates.qmd", "characters_strings.qmd", "factors.qmd", "pivoting.qmd", "grouping.qmd", "joining_matching.qmd", "deduplication.qmd", "iteration.qmd", "tables_descriptive.qmd", "stat_tests.qmd", "regression.qmd", "missing_data.qmd",
                 "standardization.qmd", "moving_average.qmd", "time_series.qmd", "epidemic_models.qmd", "contact_tracing.qmd", "survey_analysis.qmd", "survival_analysis.qmd", "gis.qmd", "tables_presentation.qmd", "ggplot_basics.qmd", "ggplot_tips.qmd", "epicurves.qmd", "age_pyramid.qmd", "heatmaps.qmd", "diagrams.qmd", "combination_analysis.qmd", "transmission_chains.qmd", "phylogenetic_trees.qmd", "interactive_plots.qmd", "rmarkdown.qmd", "reportfactory.qmd", "flexdashboard.qmd", "shiny_basics.qmd", "writing_functions.qmd", "directories.qmd", "collaboration.qmd", "errors.qmd", "help.qmd", "network_drives.qmd", "data_table.qmd")

# Define the list of languages
languages <- c('fr', 'es', 'vn', 'jp', 'pt', 'tr', 'ru')
titles <- c(
  "fr" = "Le Epi R Handbook",
  "es" = "EpiRhandbook en español",
  "vn" = "Cẩm nang dịch tễ học với R",
  "jp" = "疫学のための R ハンドブック",
  "pt" = "Manual de R para Epidemiologistas",
  "tr" = "Epidemiyologun R Rehberi",
  "ru" = "Справочник эпидемиолога R"
)

# Define the folder path
subfolder <- "offline_long"
chapters_folder <- "chapters"

#! Adding content to file is dangerous, check carefully. 
# Loop through each language
for (lang in languages) {
  
  # Create the index file name for the current language
  index_file <- file.path(subfolder, paste0("index.", lang, ".qmd"))
  
  # Read the content of the index file
  if (fs::file_exists(index_file)) {
    existing_content <- readLines(index_file)
  } else {
    existing_content <- character()
  }
  
  # Open a connection to the index file in write mode to add YAML header and existing content
  con <- file(index_file, open = "w")
  
  # Write the YAML header
  writeLines(c(
    "---",
    paste0("title: ", titles[lang]),
    "format:",
    "  html:",
    "    toc: true",
    "    embed-resources: true",
    "---",
    ""
  ), con)
  
  # Write the existing content back to the file
  writeLines(existing_content, con)
  
  # Loop through each chapter and append the include statement to the index file if it doesn't already exist
  for (chapter in chapter_list) {
    chapter_include <- paste0("{{< include ", sub(".qmd", paste0(".", lang, ".qmd"), chapter), " >}}")
    if (!chapter_include %in% existing_content) {
      writeLines(chapter_include, con)
    }
  }
  
  # Close the connection to the index file
  close(con)
}



# Copy chapters and index files to a temporary folder ----------------------------------------

# Define the content to add to the beginning of specific files
content_to_add <- list(
  "standardization.qmd" = c(
    "```{r, echo=F}",
    "# Country A",
    "library(conflicted)",
    'conflict_prefer("select", "dplyr")',
    'conflict_prefer("filter", "dplyr")',
    "```",
    ""
  ),
  "time_series.qmd" = c(
    "```{r, echo=F}",
    "# Country A",
    "library(conflicted)",
    'conflict_prefer("lag", "dplyr")',
    'conflict_prefer("year", "lubridate")',
    "```",
    ""
  ),
  "survey_analysis.qmd" = c(
    "```{r, echo=F}",
    "library(conflicted)",
    "library(srvyr)",
    "library(patchwork)",
    'conflict_prefer("filter", "dplyr")',
    "```",
    ""
  ),
  "survival_analysis.qmd" = c(
    "```{r, echo=F}",
    "library(conflicted)",
    'conflict_prefer("legend", "graphics")',
    'conflict_prefer("clean_names", "janitor")',
    "```",
    ""
  ),
  "diagrams.qmd" = c(
    "```{r, echo=F}",
    "library(vistime)",
    "```",
    ""
  ),
  "transmission_chains.qmd" = c(
    "```{r, echo=F}",
    "# Country A",
    "library(conflicted)",
    "library(epicontacts)",
    'conflict_prefer("fisher.test", "janitor")',
    "```",
    ""
  ),
  "phylogenetic_trees.qmd" = c(
    "```{r, echo=F}",
    "library(conflicted)",
    "library(ggtree)",
    'conflict_prefer("rotate", "ggpubr")',
    'conflict_prefer("expand", "tidyr")',
    'conflict_prefer("extract", "tidyr")',
    'conflict_prefer("geom_point2", "ggtree")',
    "```",
    ""
  ),
  "writing_functions.qmd" = c(
    "```{r, echo=F}",
    "# Country A",
    "library(highcharter)",
    "```",
    ""
  ),
  "data_table.qmd" = c(
    "```{r, echo=F}",
    "library(data.table)",
    "library(conflicted)",
    'conflict_prefer("month", "data.table")',
    "```",
    ""
  )
)

# Function to replace specific lines in a file
replace_specific_lines <- function(file_path) {
  if (file_exists(file_path)) {
    file_content <- readLines(file_path)
    file_content <- stringr::str_replace_all(file_content, "(?<!dplyr::)select\\(Country, everything\\(\\)\\)", "dplyr::select(Country, everything())")
    file_content <- gsub("f = table", "f = function(a, b) table(a, b)", file_content)
    writeLines(file_content, file_path)
  }
}

# Function to handle both English and other languages
handle_language <- function(lang) {
  # Create a temporary directory for this language
  temporary_directory <- withr::local_tempdir()

  # Copy the images and data folders to the temporary directory
  if (dir_exists("images")) {
    dir_copy("images", file.path(temporary_directory, "images"))
  }
  if (dir_exists("data")) {
    dir_copy("data", file.path(temporary_directory, "data"))
  }

  # Set the file suffix
  suffix <- if (lang == "en") "" else paste0(".", lang)

  # Copy the index file to the temporary directory
  index_file <- file.path("offline_long", paste0("index", suffix, ".qmd"))
  if (file_exists(index_file)) {
    file_copy(index_file, temporary_directory)
  }

  # Loop through each chapter and copy the chapter file to the temporary directory
  for (chapter in chapter_list) {
    chapter_file <- file.path("chapters", sub(".qmd", paste0(suffix, ".qmd"), chapter))
    if (file_exists(chapter_file)) {
      file_copy(chapter_file, temporary_directory)
    }
  }

  # Edit specific files as per the instructions
  for (file_name in names(content_to_add)) {
    file_path <- file.path(temporary_directory, sub(".qmd", paste0(suffix, ".qmd"), file_name))

    if (file_exists(file_path)) {
      file_content <- readLines(file_path)

      # Add content only if it's not already there
      if (!all(content_to_add[[file_name]] %in% file_content)) {
        new_content <- c(content_to_add[[file_name]], file_content)
        writeLines(new_content, file_path)
      }
    }
  }

  # Replace specific lines in transmission_chains.qmd and others
  for (file_name in c("transmission_chains.qmd", chapter_list)) {
    file_path <- file.path(temporary_directory, sub(".qmd", paste0(suffix, ".qmd"), file_name))
    replace_specific_lines(file_path)
  }

  # Save the path of the temporary directory for rendering
  assign(paste0("temp_dir_", lang), temporary_directory, envir = .GlobalEnv)
  
  # Print the path to the temporary directory for verification
  print(paste("Temporary directory for", lang, "with copied files is located at:", temporary_directory))
}

# Loop through each language and handle it
for (lang in languages) {
  handle_language(lang)
}

# Rendering and copying commands for each language
render_and_copy <- function(lang) {
  suffix <- if (lang == "en") "" else paste0(".", lang)
  temp_dir <- get(paste0("temp_dir_", lang))
  with_dir(temp_dir, {
    render_command <- paste("quarto render", paste0("index", suffix, ".qmd"))
    system(render_command)
  })
  output_file <- file.path(temp_dir, paste0("index", suffix, ".html"))
  if (file_exists(output_file)) {
    file_copy(output_file, "offline_long") #? file.path("offline_long", paste0("index", suffix, ".html"))
  }
}

# Rendering and copying for each language
render_and_copy("en")
render_and_copy("fr")
render_and_copy("es")
render_and_copy("vn")
render_and_copy("jp")
render_and_copy("pt")
render_and_copy("tr")
render_and_copy("ru")


# #! Old script --------------------------------------------------------------------------------

# # Function to replace specific lines in a file
# replace_specific_lines <- function(file_path) {
#   if (file_exists(file_path)) {
#     file_content <- readLines(file_path)
#     file_content <- gsub("f = table", "f = function(a, b) table(a, b)", file_content)
#     file_content <- gsub("select\\(Country, everything\\(\\)\\)", "dplyr::select(Country, everything())", file_content) # Specifically replace select(Country, everything())
#     writeLines(file_content, file_path)
#   }
# }

# # Loop through each language
# for (lang in languages) {
#   # Create a temporary directory for this language
#   temporary_directory <- withr::local_tempdir()

#   # Copy the images and data folders to the temporary directory
#   if (dir_exists("images")) {
#     dir_copy("images", file.path(temporary_directory, "images"))
#   }
#   if (dir_exists("data")) {
#     dir_copy("data", file.path(temporary_directory, "data"))
#   }

#   # Copy the index file to the temporary directory
#   index_file <- file.path("offline_long", paste0("index.", lang, ".qmd"))
#   if (file_exists(index_file)) {
#     file_copy(index_file, temporary_directory)
#   }

#   # Loop through each chapter and copy the chapter file to the temporary directory
#   for (chapter in chapter_list) {
#     chapter_file <- file.path("chapters", sub(".qmd", paste0(".", lang, ".qmd"), chapter))
#     if (file_exists(chapter_file)) {
#       file_copy(chapter_file, temporary_directory)
#     }
#   }

#   # Edit specific files as per the instructions
#   for (file_name in names(content_to_add)) {
#     file_path <- file.path(temporary_directory, sub(".qmd", paste0(".", lang, ".qmd"), file_name))

#     if (file_exists(file_path)) {
#       file_content <- readLines(file_path)

#       # Add content only if it's not already there
#       if (!all(content_to_add[[file_name]] %in% file_content)) {
#         new_content <- c(content_to_add[[file_name]], file_content)
#         writeLines(new_content, file_path)
#       }
#     }
#   }

#   # Replace specific lines in transmission_chains.qmd and others
#   for (file_name in c("transmission_chains.qmd", chapter_list)) {
#     file_path <- file.path(temporary_directory, sub(".qmd", paste0(".", lang, ".qmd"), file_name))
#     replace_specific_lines(file_path)
#   }

#   # Save the path of the temporary directory for rendering
#   assign(paste0("temp_dir_", lang), temporary_directory)
  
#   # Print the path to the temporary directory for verification
#   print(paste("Temporary directory for", lang, "with copied files is located at:", temporary_directory))
# }

# # Render the book for French
# with_dir(get("temp_dir_fr"), {
#   render_command <- "quarto render index.fr.qmd"
#   system(render_command)
# })

# # Copy the output file back to the original offline_long folder
# output_file <- file.path(get("temp_dir_fr"), "index.fr.html")
# if (file_exists(output_file)) {
#   file_copy(output_file, "offline_long")
# }

# # Render the book for Spanish
# with_dir(get("temp_dir_es"), {
#   render_command <- "quarto render index.es.qmd"
#   system(render_command)
# })

# # Copy the output file back to the original offline_long folder
# output_file <- file.path(get("temp_dir_es"), "index.es.html")
# if (file_exists(output_file)) {
#   file_copy(output_file, "offline_long")
# }

# # Render the book for Vietnamese
# with_dir(get("temp_dir_vn"), {
#   render_command <- "quarto render index.vn.qmd"
#   system(render_command)
# })

# # Copy the output file back to the original offline_long folder
# output_file <- file.path(get("temp_dir_vn"), "index.vn.html")
# if (file_exists(output_file)) {
#   file_copy(output_file, "offline_long")
# }

# # Render the book for Japanese
# with_dir(get("temp_dir_jp"), {
#   render_command <- "quarto render index.jp.qmd"
#   system(render_command)
# })

# # Copy the output file back to the original offline_long folder
# output_file <- file.path(get("temp_dir_jp"), "index.jp.html")
# if (file_exists(output_file)) {
#   file_copy(output_file, "offline_long")
# }

# # Render the book for Portuguese
# with_dir(get("temp_dir_pt"), {
#   render_command <- "quarto render index.pt.qmd"
#   system(render_command)
# })

# # Copy the output file back to the original offline_long folder
# output_file <- file.path(get("temp_dir_pt"), "index.pt.html")
# if (file_exists(output_file)) {
#   file_copy(output_file, "offline_long")
# }

# # Render the book for Turkish
# with_dir(get("temp_dir_tr"), {
#   render_command <- "quarto render index.tr.qmd"
#   system(render_command)
# })

# # Copy the output file back to the original offline_long folder
# output_file <- file.path(get("temp_dir_tr"), "index.tr.html")
# if (file_exists(output_file)) {
#   file_copy(output_file, "offline_long")
# }

# # Render the book for Russian
# with_dir(get("temp_dir_ru"), {
#   render_command <- "quarto render index.ru.qmd"
#   system(render_command)
# })

# # Copy the output file back to the original offline_long folder
# output_file <- file.path(get("temp_dir_ru"), "index.ru.html")
# if (file_exists(output_file)) {
#   file_copy(output_file, "offline_long")
# }

# #! For English file only ----------------------------------------------------------------------

# # Create a temporary directory for English files
# temporary_directory <- withr::local_tempdir()

# # Copy the images and data folders to the temporary directory
# if (dir_exists("images")) {
#   dir_copy("images", file.path(temporary_directory, "images"))
# }
# if (dir_exists("data")) {
#   dir_copy("data", file.path(temporary_directory, "data"))
# }

# # Copy the index file to the temporary directory
# index_file <- file.path("offline_long", "index.qmd")
# if (file_exists(index_file)) {
#   file_copy(index_file, temporary_directory)
# }

# # Loop through each chapter and copy the chapter file to the temporary directory
# for (chapter in chapter_list) {
#   chapter_file <- file.path("chapters", chapter)
#   if (file_exists(chapter_file)) {
#     file_copy(chapter_file, temporary_directory)
#   }
# }

# # Edit specific files as per the instructions
# for (file_name in names(content_to_add)) {
#   file_path <- file.path(temporary_directory, file_name)

#   if (file_exists(file_path)) {
#     file_content <- readLines(file_path)

#     # Add content only if it's not already there
#     if (!all(content_to_add[[file_name]] %in% file_content)) {
#       new_content <- c(content_to_add[[file_name]], file_content)
#       writeLines(new_content, file_path)
#     }
#   }
# }

# # Replace specific lines in transmission_chains.qmd
# transmission_file_path <- file.path(temporary_directory, "transmission_chains.qmd")
# replace_specific_lines(transmission_file_path)

# # Change the directory to the temporary directory and render the book for English
# with_dir(temporary_directory, {
#   render_command <- "quarto render index.qmd"
#   system(render_command)
# })

# # Copy the output file back to the original offline_long folder
# output_file <- file.path(temporary_directory, "index.html")
# if (file_exists(output_file)) {
#   file_copy(output_file, "offline_long")
# }

# # Print the path to the temporary directory
# print(paste("Temporary directory with copied files is located at:", temporary_directory))