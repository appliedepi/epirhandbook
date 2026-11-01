# 45  Directory interactions

In this page we cover common scenarios where you create, interact with, save, and import with directories (folders).

## 45.1 Preparation

### **fs** package

The **fs** package is a **tidyverse** package that facilitate directory interactions, improving on some of the **base** R functions. In the sections below we will often use functions from **fs**.

``` r
pacman::p_load(
  fs,             # file/directory interactions
  rio,            # import/export
  here,           # relative file pathways
  tidyverse)      # data management and visualization
```

### Print directory as a dendrogram tree

Use the function `dir_tree()` from **fs**.

Provide the folder filepath to `path =`. Set `recurse = FALSE` to show one level, or `recurse = TRUE` to show all files in all sub-levels. Below we use `here()` as shorthand for the R project and specify its sub-folder “data”, which holds the example data of this handbook. We set it to display all files within “data” and its sub-folders.

``` r
fs::dir_tree(path = here("data"), recurse = TRUE)
```

    data
    ├── case_linelists
    │   └── linelist_cleaned.rds
    ├── example
    │   ├── central_hospital.csv
    │   ├── district_weekly_count_data.xlsx
    │   ├── fluh7n9_china_2013.csv
    │   ├── hospital_linelists.xlsx
    │   ├── linelists
    │   │   ├── 20201007linelist.csv
    │   │   ├── case_linelist20201006.csv
    │   │   ├── case_linelist_2020-10-02.csv
    │   │   ├── case_linelist_2020-10-03.csv
    │   │   ├── case_linelist_2020-10-04.csv
    │   │   ├── case_linelist_2020-10-05.csv
    │   │   └── case_linelist_2020-10-08.xlsx
    │   ├── military_hospital.csv
    │   ├── missing.csv
    │   ├── other.csv
    │   ├── port_hospital.csv
    │   └── st_marks_maternity_hospital.csv
    ├── flexdashboard
    │   ├── outbreak_dashboard.Rmd
    │   ├── outbreak_dashboard.html
    │   └── outbreak_dashboard_test.html
    └── malaria_app
        ├── app.R
        ├── data
        │   └── facility_count_data.rds
        ├── funcs
        │   └── plot_epicurve.R
        ├── global.R
        ├── malaria_app.Rproj
        ├── server.R
        └── ui.R

## 45.2 List files in a directory

To list just the file names in a directory you can use `dir()` from **base** R. For example, this command lists the file names of the files in the “linelists” subfolder of the “example” folder in an R project. The relative filepath is provided using `here()` (which you can read about more in the [Import and export](importing.llms.md) page).

``` r
# file names
dir(here("data", "example", "linelists"))
```

    [1] "20201007linelist.csv"          "case_linelist_2020-10-02.csv" 
    [3] "case_linelist_2020-10-03.csv"  "case_linelist_2020-10-04.csv" 
    [5] "case_linelist_2020-10-05.csv"  "case_linelist_2020-10-08.xlsx"
    [7] "case_linelist20201006.csv"    

To list the full file paths of the directory’s files, you can use you can use `dir_ls()` from **fs**. A **base** R alternative is `list.files()`.

``` r
# file paths
dir_ls(here("data", "example", "linelists"))
```

    data/example/linelists/20201007linelist.csv
    data/example/linelists/case_linelist20201006.csv
    data/example/linelists/case_linelist_2020-10-02.csv
    data/example/linelists/case_linelist_2020-10-03.csv
    data/example/linelists/case_linelist_2020-10-04.csv
    data/example/linelists/case_linelist_2020-10-05.csv
    data/example/linelists/case_linelist_2020-10-08.xlsx

To get all the metadata information about each file in a directory, (e.g. path, modification date, etc.) you can use `dir_info()` from **fs**.

This can be particularly useful if you want to extract the last modification time of the file, for example if you want to import the most recent version of a file. For an example of this, see the [Import and export](importing.llms.md) page.

``` r
# file info
dir_info(here("data", "example", "linelists"))
```

Here is the data frame returned. Scroll to the right to see all the columns.

## 45.3 File information

To extract metadata information about a specific file, you can use `file_info()` from **fs** (or `file.info()` from **base** R).

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))
```

Here we use the `$` to index the result and return only the `modification_time` value.

``` r
file_info(here("data", "case_linelists", "linelist_cleaned.rds"))$modification_time
```

    [1] "2026-11-01 15:52:15 UTC"

## 45.4 Check if exists

### R objects

You can use `exists()` from **base** R to check whether an R object exists *within* R (supply the object name in quotes).

``` r
exists("linelist")
```

    [1] FALSE

Note that some **base** R packages use generic object names like “data” behind the scenes, that will appear as TRUE unless `inherit = FALSE` is specified. This is one reason to not name your dataset “data”.

``` r
exists("data")
```

    [1] TRUE

``` r
exists("data", inherit = FALSE)
```

    [1] FALSE

If you are writing a function, you should use `missing()` from **base** R to check if an argument is present or not, instead of `exists()`.

### Directories

To check whether a directory exists, provide the file path (and file name) to `is_dir()` from **fs**. Scroll to the right to see that `TRUE` is printed.

``` r
is_dir(here("data"))
```

    data 
    TRUE 

An alternative is `file.exists()` from **base** R.

### Files

To check if a specific file exists, use `is_file()` from **fs**. Scroll to the right to see that `TRUE` is printed.

``` r
is_file(here("data", "case_linelists", "linelist_cleaned.rds"))
```

    data/case_linelists/linelist_cleaned.rds 
                                        TRUE 

A **base** R alternative is `file.exists()`.

## 45.5 Create

### Directories

To create a new directory (folder) you can use `dir_create()` from **fs**. If the directory already exists, it will not be overwritten and no error will be returned.

``` r
dir_create(here("data", "test"))
```

An alternative is `dir.create()` from **base** R, which will show an error if the directory already exists. In contrast, `dir_create()` in this scenario will be silent.

### Files

You can create an (empty) file with `file_create()` from **fs**. If the file already exists, it will not be over-written or changed.

``` r
file_create(here("data", "test.rds"))
```

A **base** R alternative is `file.create()`. But if the file already exists, this option will truncate it. If you use `file_create()` the file will be left unchanged.

### Create if does not exists

UNDER CONSTRUCTION

## 45.6 Delete

### R objects

Use `rm()` from **base** R to remove an R object.

### Directories

Use `dir_delete()` from **fs**.

### Files

You can delete files with `file_delete()` from **fs**.

## 45.7 Running other files

### `source()`

To run one R script from another R script, you can use the `source()` command (from **base** R).

``` r
source(here("scripts", "cleaning_scripts", "clean_testing_data.R"))
```

This is equivalent to viewing the above R script and clicking the “Source” button in the upper-right of the script. This will execute the script but will do it silently (no output to the R console) unless specifically intended.

[![](../../images/source_button.png)](../../images/source_button.png)

### `render()`

`render()` is a variation on `source()` most often used for R markdown scripts. You provide the `input =` which is the R markdown file, and also the `output_format =` (typically either “html_document”, “pdf_document”, “word_document”, ““)

See the page on [Reports with R Markdown](rmarkdown.llms.md) for more details. Also see the documentation for `render()` [here](https://rmarkdown.rstudio.com/docs/reference/render.html) or by entering `?render`.

### Run files in a directory

You can create a *for loop* and use it to `source()` every file in a directory, as identified with `dir()`.

``` r
for(script in dir(here("scripts"), pattern = ".R$")) {   # for each script name in the R Project's "scripts" folder (with .R extension)
  source(here("scripts", script))                        # source the file with the matching name that exists in the scripts folder
}
```

If you only want to run certain scripts, you can identify them by name like this:

``` r
scripts_to_run <- c(
     "epicurves.R",
     "demographic_tables.R",
     "survival_curves.R"
)

for(script in scripts_to_run) {
  source(here("scripts", script))
}
```

Here is a [comparison](https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html) of the **fs** and **base** R functions.

### Import files in a directory

See the page on \[Import and export\] for importing and exporting individual files.

Also see the [Import and export](importing.llms.md) page for methods to automatically import the most recent file, based on a date in the file name *or* by looking at the file meta-data.

See the page on \[Iteration, loops, and lists\] for an example with the package **purrr** demonstrating:

- Splitting a data frame and saving it out as multiple CSV files  
- Splitting a data frame and saving each part as a separate sheet within one Excel workbook  
- Importing multiple CSV files and combining them into one dataframe  
- Importing an Excel workbook with multiple sheets and combining them into one dataframe

## 45.8 **base** R

See below the functions `list.files()` and `dir()`, which perform the same operation of listing files within a specified directory. You can specify `ignore.case =` or a pattern to look for. `pattern =` takes a regular expression, not a file glob, so `"\\.csv$"` means “ends in .csv”.

``` r
list.files(path = here("data"))

list.files(path = here("data", "example"), pattern = "\\.csv$")
# dir(path = here("data", "example"), pattern = "\\.csv$")

list.files(path = here("data", "example"), pattern = "hospital", ignore.case = TRUE)
```

If a file is currently “open”, it will display in your folder with a tilde in front, like “~\$hospital_linelists.xlsx”.

## 45.9 Resources

https://cran.r-project.org/web/packages/fs/vignettes/function-comparisons.html
