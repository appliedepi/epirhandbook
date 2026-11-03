# 2  Download handbook and data

## 2.1 Download offline handbook

You can download this handbook and read it without an internet connection. Each language is a zip file holding the whole site: every chapter, every image and the navigation sidebar.

- Download the zip for your language, then unzip it.
- Open `index.html` in the unzipped folder to start reading.
- See the [Suggested packages](packages_suggested.llms.md) page to install the R packages you need before you lose your connection.

**To download the handbook:**

[Download the handbook (zip)](https://github.com/appliedepi/epirhandbook/releases/download/offline/epirhandbook-en.zip)

The zip is rebuilt automatically, so it always follows the latest version of the handbook.

## 2.2 Download data to follow along

To “follow along” with the handbook pages, you can load the example data straight into R with our companion R package, **appliedepidata**. It contains every example dataset used in this handbook.

### Install the package

**appliedepidata** is not on CRAN, so install it from its [Github repository](https://github.com/appliedepi/appliedepidata) with **pak**:

``` r
# install the latest version of the appliedepidata package
pak::pak("appliedepi/appliedepidata")
```

### Load a dataset directly

Use `get_data()` with the dataset’s `name =` to load it straight into R - no download, no file path, no `import()` step. The function returns the dataset as an R object (a data frame, an `sf` object, a `phylo` tree, etc., depending on the dataset).

``` r
# load the cleaned case linelist directly into R
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

Each page of this handbook that uses example data shows the `get_data(name = "...")` call needed for that page, right where the data are first used.

### Save a dataset to a real file

Some pages teach you how to import a *file* (e.g. an Excel workbook, or a folder of files) rather than an R object. For these, use `save_data()` to write the real file(s) to a folder of your choice with `name =` and `path =`:

``` r
# write the raw linelist Excel file to your working directory
appliedepidata::save_data(name = "case_linelists_linelist_raw", path = getwd())
```

You can then `import()` it as you would any file on your computer - see the [Import and export](importing.llms.md) page for details. Note that `save_data()` does not automatically unzip datasets that are distributed as a .zip bundle (e.g. multi-file shapefiles, or folders of files); use `utils::unzip()` on the saved .zip afterwards.

### Browse what’s available

- `appliedepidata::search_data()` launches an interactive Shiny app so you can filter and search all the datasets in the package by language and keyword.
- `appliedepidata::list_data()` returns a data frame listing every dataset name programmatically, for use in scripts.

``` r
# browse datasets interactively
appliedepidata::search_data()

# list all dataset names programmatically
appliedepidata::list_data()
```

If you wish, you can also review the raw data files in the **[“data” folder](https://github.com/appliedepi/appliedepidata/tree/main/inst/extdata)** of the **appliedepidata** Github repository.

### Dataset reference, by page

Below is the `get_data()`/`save_data()` name to use for the example data referenced on each page of this handbook.

#### Case linelist

This is a fictional Ebola outbreak, expanded by the handbook team from the `ebola_sim` practice dataset in the **outbreaks** package.

``` r
# the "raw" linelist - an Excel spreadsheet with messy data
# use this to follow along with the Cleaning data and core functions page
raw_linelist <- appliedepidata::get_data(name = "case_linelists_linelist_raw")

# the "clean" linelist - an R-specific .rds file that preserves column classes
# use this for all other pages of this handbook that use the linelist
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")

# the "clean" linelist, as an Excel file instead
linelist_excel <- appliedepidata::get_data(name = "linelist_cleaned_excel")
```

Part of the cleaning page uses a “cleaning dictionary” (.csv file). You can load it directly into R by running the following command:

``` r
cleaning_dict <- appliedepidata::get_data(name = "case_linelists_cleaning_dict")
```

#### Working with dates

The [Working with dates](dates.llms.md) page uses counts of cases by district and date:

``` r
counts <- appliedepidata::get_data(name = "example_district_weekly_count_data")
```

#### Writing functions

The [Writing functions](writing_functions.llms.md) page uses a linelist of the 2013 H7N9 influenza outbreak in China:

``` r
flu_china <- appliedepidata::get_data(name = "fluH7N9_China_2013")
```

#### Iteration, loops, and lists

The [Iteration, loops, and lists](iteration.llms.md) page imports an Excel workbook with one sheet per hospital. Save it as a file first:

``` r
appliedepidata::save_data(name = "example_hospital_linelists", path = getwd())
```

#### Import and export

The [Import and export](importing.llms.md) page imports the linelist from Excel files. Save them as files first:

``` r
# the raw linelist
appliedepidata::save_data(name = "linelist_raw", path = getwd())

# the clean linelist
appliedepidata::save_data(name = "linelist_cleaned", path = getwd())
```

#### Malaria count data

These data are fictional counts of malaria cases by age group, facility, and day. A .rds file is an R-specific file type that preserves column classes. This ensures you will have only minimal cleaning to do after importing the data into R.

``` r
malaria_data <- appliedepidata::get_data(name = "malaria_facility_count_data")
```

#### Likert-scale data

These are fictional data from a Likert-style survey, used in the page on [Demographic pyramids and Likert-scales](age_pyramid.llms.md).

``` r
likert_data <- appliedepidata::get_data(name = "likert_data")
```

#### Flexdashboard

Below are links to the files associated with the page on [Dashboards with R Markdown](flexdashboard.llms.md). These are R Markdown/HTML source files, not example datasets, so they are not part of the **appliedepidata** package - download them directly from Github:

- To download the R Markdown for the outbreak dashboard, right-click this [link](https://github.com/appliedepi/epirhandbook/raw/main/data/flexdashboard/outbreak_dashboard.Rmd) (Cmd+click for Mac) and select “Save link as”.
- To download the HTML dashboard, right-click this [link](https://github.com/appliedepi/epirhandbook/raw/main/data/flexdashboard/outbreak_dashboard_test.html) (Cmd+click for Mac) and select “Save link as”.

#### Contact Tracing

The [Contact Tracing](contact_tracing.llms.md) page analyses example contact tracing data from [Go.Data](https://github.com/WorldHealthOrganization/godata/tree/master/analytics/r-reporting). These data are part of **appliedepidata**:

``` r
# case investigation data
cases <- appliedepidata::get_data(name = "cases_clean")

# contact registration data
contacts <- appliedepidata::get_data(name = "contacts_clean")

# contact follow-up data
followups <- appliedepidata::get_data(name = "followups_clean")

# links between cases and contacts
relationships <- appliedepidata::get_data(name = "relationships_clean")
```

***NOTE:*** Structured contact tracing data from other software (e.g. KoBo, DHIS2 Tracker, CommCare) may look different. If you would like to contribute alternative sample data or content for this page, please [contact us](index.llms.md).

***TIP:*** If you are deploying Go.Data and want to connect to your instance’s API, see the Import and export page [(API section)](importing.llms.md#import_api) and the [Go.Data Community of Practice](https://community-godata.who.int/).

#### GIS

Shapefiles have many sub-component files, each with a different file extension. One file will have the “.shp” extension, but others may have “.dbf”, “.prj”, etc. **appliedepidata** bundles each shapefile’s component files together as a single .zip, so `save_data()` and then unzip:

``` r
# load the Sierra Leone admin-3 shapefile directly as an sf object
sle_adm3 <- appliedepidata::get_data(name = "sle_adm3")

# load the health facility points as an sf object
sle_hf <- appliedepidata::get_data(name = "sle_hf")

# load the ADM3 population table
sle_adm3_pop <- appliedepidata::get_data(name = "sle_admpop_adm3_2020")

# OR save the raw shapefile component files to a folder
shp_dir <- "sle_adm3_files"
dir.create(shp_dir)
appliedepidata::save_data(name = "sle_adm3", path = shp_dir)
utils::unzip(file.path(shp_dir, "sle_adm3.zip"), exdir = shp_dir)
```

The [GIS basics](gis.llms.md) page loads all three data sets: the admin-3 boundaries `sle_adm3`, the health facility points `sle_hf`, and the population table `sle_admpop_adm3_2020`. To read a shapefile from your own file path, use `read_sf()` from the **sf** package. The [GIS basics](gis.llms.md) page also links to the *Humanitarian Data Exchange* website, where you can download further shapefiles as zipped files. The health facility points, for example, are [here](https://data.humdata.org/dataset/hotosm_sle_health_facilities).

#### Phylogenetic trees

See the page on [Phylogenetic trees](phylogenetic_trees.llms.md). Newick file of phylogenetic tree constructed from whole genome sequencing of 299 Shigella sonnei samples and corresponding sample data (converted to a text file). The Belgian samples and resulting data are kindly provided by the Belgian NRC for Salmonella and Shigella in the scope of a project conducted by an ECDC EUPHEM Fellow, and will also be published in a manuscript. The international data are openly available on public databases (ncbi) and have been previously published.

``` r
# the phylogenetic tree, as a "phylo" object (ape package)
tree <- appliedepidata::get_data(name = "Shigella_tree")

# additional information on each sample
sample_data <- appliedepidata::get_data(name = "sample_data_Shigella_tree")

# the subset-tree created later in the page
subtree <- appliedepidata::get_data(name = "Shigella_subtree_2")
```

#### Standardization

See the page on [Standardised rates](standardization.llms.md). You can load the data directly with the following commands:

``` r
##############
# Country A
##############
# demographics for country A
A_demo <- appliedepidata::get_data(name = "country_demographics")

# deaths for country A
A_deaths <- appliedepidata::get_data(name = "deaths_countryA")

##############
# Country B
##############
# demographics for country B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")

# deaths for country B
B_deaths <- appliedepidata::get_data(name = "deaths_countryB")


###############
# Reference Pop
###############
# world standard population, by sex
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

#### Time series and outbreak detection

See the page on [Time series and outbreak detection](time_series.llms.md). We use campylobacter cases reported in Germany 2002-2011, as available from the **surveillance** R package. (*nb.* this dataset has been adapted from the original, in that 3 months of data have been deleted from the end of 2011 for demonstration purposes)

``` r
counts <- appliedepidata::get_data(name = "campylobacter_germany")
```

We also use climate data from Germany 2002-2011 (temperature in degrees celsius and rain fall in millimetres). These were downloaded from the EU Copernicus satellite reanalysis dataset using the **ecmwfr** package, and are bundled by **appliedepidata** as one .zip of ten yearly .nc files. `get_data()` reads the whole bundle in as one combined **stars** object directly; `save_data()` gives you the raw .nc files if you want to inspect or process them yourself.

``` r
# read the combined weather data directly as a stars object
weather_data <- appliedepidata::get_data(name = "germany_weather")

# OR save the raw yearly .nc files to a folder
weather_dir <- "germany_weather_files"
dir.create(weather_dir)
appliedepidata::save_data(name = "germany_weather", path = weather_dir)
utils::unzip(file.path(weather_dir, "germany_weather.zip"), exdir = weather_dir)
```

#### Survey analysis

For the [survey analysis](survey_analysis.llms.md) page we use fictional mortality survey data based off MSF OCA survey templates. This fictional data was generated as part of the [“R4Epis” project](https://r4epis.netlify.app/).

``` r
# fictional survey data
survey_data <- appliedepidata::get_data(name = "survey_data")

# fictional survey data dictionary
survey_dict <- appliedepidata::get_data(name = "survey_dict")

# fictional survey population data
population <- appliedepidata::get_data(name = "population")
```

#### Shiny

The page on [Dashboards with Shiny](shiny_basics.llms.md) demonstrates the construction of a simple app to display malaria data. The app’s data are part of **appliedepidata**:

``` r
malaria_data <- appliedepidata::get_data(name = "malaria_facility_count_data")
```

The app’s R scripts are not example data, so they are not part of **appliedepidata** - download them directly from Github:

You can [click here to download the app.R file that contains both the UI and Server code for the Shiny app.](https://github.com/appliedepi/epirhandbook/raw/main/data/malaria_app/app.R)

You can [click here to download the global.R file](https://github.com/appliedepi/epirhandbook/raw/main/data/malaria_app/global.R) that should run prior to the app opening, as explained in the page.

You can [click here to download the plot_epicurve.R file](https://github.com/appliedepi/epirhandbook/raw/main/data/malaria_app/funcs/plot_epicurve.R) that is sourced by global.R. Note that you may need to store it within a “funcs” folder for the here() file paths to work correctly.
