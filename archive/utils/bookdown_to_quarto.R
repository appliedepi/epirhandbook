# Load packages
pacman::p_load(fs, 
               readr,
               stringr)

# Change file names ended with .Rmd to .qmd in ROOT FOLDER
rmd_names_root <- dir_ls(path = ".", glob = "*.Rmd")       
qmd_names_root <- str_replace(string = rmd_names_root,
                                 pattern = "Rmd",
                                 replacement = "qmd")
file_move(path = rmd_names_root,
          new_path = qmd_names_root)



# Change file names ended with .Rmd to .qmd in CHAPTER FOLDER
rmd_names_chapter <- dir_ls(path = "chapters", glob = "*.Rmd")    
qmd_names_chapter <- str_replace(string = rmd_names_chapter,
                         pattern = "Rmd",
                         replacement = "qmd")
file_move(path = rmd_names_chapter,
          new_path = qmd_names_chapter)


# Converto _bookdown.yml to _quarto.yml
file_move(path = "_bookdown.yml",
          new_path = "_quarto.yml")


# Replace the chapter names in _bookdown.yml from .Rmd to .quarto in _quarto.yml 

quarto_yaml_rmd <- read_lines("_quarto.yml")

quarto_yaml_qmd <- str_replace_all(string = quarto_yaml_rmd,
                                   pattern = "Rmd",
                                   replacement = "qmd")
write_lines(
  x = quarto_yaml_qmd,
  file = "_quarto.yml"
)


# In string containing chapters/, remove quotation marks

quarto_chapter <- read_lines("_quarto.yml")

quarto_chapter_remove <- str_replace_all(string = quarto_chapter,
                                         pattern = c('qmd",' = "qmd", '"chapters/' = '- chapters/'))
write_lines(
  x = quarto_chapter_remove,
  file = "_quarto.yml"
)
