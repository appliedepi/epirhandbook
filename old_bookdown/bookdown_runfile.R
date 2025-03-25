
# Use these commands to actually render the handbook
# See format and content choices below  
# test
################################################################################
# BS4 BOOKDOWN STYLE (WEBSITE VERSION) ##
#########################################
# WHOLE HANDBOOK
# for online viewing only - not available as a self-contained file  
bookdown::render_book(
     output_format = 'bookdown::bs4_book',
     config_file = "_bookdown.yml")


# PREVIEW ONLY ONE OR SOME PAGES
# !!! NOTE - sometimes running this command renders the entire book!
# !!! In this case, just stop the rendering and re-run the command. It should work the second time.
# Edit which pages to include in "_small_bookdown.yml"
# To view, navigate to the "preview" folder and open "index.html"
bookdown::render_book(
     output_format = 'bookdown::bs4_book',
     config_file = "_small_bookdown.yml")


# To print only text with no code or figures, adjust this in the common.R script, also look at top of index.rmd
# print only text (not code)
#library(knitr)
#opts_chunk$set(list(echo = FALSE, eval = FALSE))

################################################################################

# WHOLE HANDBOOK WITHOUT TABS (long html)
# Available as a self-contained html file
# Ctrl+f Search functionality spans whole book


# !!! NOTE: this will output as "main.html" in the root folder. !!!
# Then you have to copy and re-name the file into the offline_long folder
bookdown::render_book(
        output_format = 'bookdown::html_document2',
        config_file = "_offline_long.yml")


################################################################################

# WHOLE HANDBOOK AS TABBED HTML
# for offline viewing - can be saved as a self-contained file
rmarkdown::render_site(
     output_format = 'bookdown::html_document2')

# PREVIEW ONLY ONE OR SOME PAGES (tabbed html)
# For offline viewing - can be saved as a self-contained file
# Edit which pages are included in "_small_bookdown.yml"
# To view: navigate to the root project folder and open "_main.html"
bookdown::render_book(
     output_format = 'bookdown::html_document2',
     config_file = "_small_bookdown.yml")


################################################################################

# Render Long static pdf without tabs

bookdown::render_book(
        output_format = 'bookdown::html_document2',
        config_file = "_pdf_long.yml")




# render the contribution guide:  

rmarkdown::render("contribution_guide_05-02-2021.Rmd", "html_document")

