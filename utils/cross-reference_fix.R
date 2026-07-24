pacman::p_load(tidyverse,
               here,
               stringr)

# Define the base folder containing the Quarto files
folder_path <- here("chapters")

# Provided list of chapter base names
chapter_list <- c("editorial_style", "data_used", "basics", "transition_to_r", "packages_suggested", "r_projects", "importing", "cleaning", 
                 "dates", "characters_strings", 
                 "factors", "pivoting", "grouping", "joining_matching", "deduplication", "iteration", "tables_descriptive", "stat_tests", "regression", "missing_data", 
                 "standardization", "moving_average", "time_series", "epidemic_models", "contact_tracing", "survey_analysis", "survival_analysis", "gis", "tables_presentation", "ggplot_basics", "ggplot_tips", "epicurves", "age_pyramid", "heatmaps", "diagrams", "combination_analysis", "transmission_chains", "phylogenetic_trees", "interactive_plots", "rmarkdown", "reportfactory", "flexdashboard", "shiny_basics", "writing_functions", "directories", "collaboration", "errors", "help", "network_drives", "data_table")

# List of language codes including 'en' for English (original version)
language_codes <- c("en", "fr", "es", "vn", "jp", "tr", "pt", "ru", "de")

# Function to extract chapter name from the first non-empty line starting with '#'
extract_chapter_name <- function(file_path) {
  lines <- readLines(file_path)
  for (line in lines) {
    if (nchar(trimws(line)) > 0 && grepl("^#", line)) {
      return(sub("^# ", "", line))
    }
  }
  return(NA)  # Return NA if no chapter title is found
}

# Initialize a list to hold chapter names for each language version of the chapters
chapter_names <- list()

# Loop through each chapter base name
for (chapter_base in chapter_list) {
  # Loop through each language code
  for (lang_code in language_codes) {
    # Construct the file name for the current language version
    # English version files don't have a language code extension
    file_name <- ifelse(lang_code == "en", 
                        paste0(chapter_base, ".qmd"), 
                        paste0(chapter_base, ".", lang_code, ".qmd"))
    
    file_path <- file.path(folder_path, file_name)
    
    # Check if the file exists
    if (file.exists(file_path)) {
      # Extract the chapter name
      chapter_name <- extract_chapter_name(file_path)
      # Store the chapter name, using the file name as the key
      chapter_names[[file_name]] <- chapter_name
    }
  }
}


# Update chapter labels in the list based on file names
# Loop through the chapter_names list
for (file_name in names(chapter_names)) {
     chapter_name <- chapter_names[[file_name]]
     
     # Determine the label from the file name by removing the '.qmd' extension
     label <- sub("\\.qmd$", "", file_name)
     
     # Check conditions and update the chapter name accordingly
     if (grepl("\\{\\s*\\}", chapter_name)) {
          # If the title has blank {}, add the label inside
          labeled_chapter_name <- sub("\\{\\s*\\}", sprintf("{#%s}", label), chapter_name)
     } else if (!grepl("\\{.*\\}", chapter_name)) {
          # If the title doesn't have {}, add {#label} directly after the title
          labeled_chapter_name <- sprintf("%s{#%s}", chapter_name, label)
     } else {
          # If the title already contains {} with a label, do nothing
          labeled_chapter_name <- chapter_name
     }
     
     # Update the chapter name in the list
     chapter_names[[file_name]] <- labeled_chapter_name
}


# Loop through the chapter_names list
for (file_name in names(chapter_names)) {
     # Construct the full path to the file
     file_path <- file.path(folder_path, file_name)
     
     # Read the content of the file
     file_content <- readLines(file_path)
     
     # Initialize a variable to track the line number of the first title
     title_line_number <- NA
     
     # Iterate over the file content to find the first title line
     for (i in 1:length(file_content)) {
          line <- file_content[i]
          # Check if the line is a non-empty line starting with '#'
          if (is.na(title_line_number) && nchar(trimws(line)) > 0 && grepl("^#", line)) {
               title_line_number <- i
               break # Stop the loop once the first title line is found
          }
     }
     
     # Check if a title line was found
     if (!is.na(title_line_number)) {
          # Format the updated title with a leading hash and a space
          updated_title <- paste0("# ", chapter_names[[file_name]])
          
          # Replace the title line with the updated title
          file_content[title_line_number] <- updated_title
          
          # Write the modified content back to the file
          writeLines(file_content, file_path)
     }
}



saveRDS(chapter_no_reference, "D:/Book Writing/chapter_no_reference.rds")









