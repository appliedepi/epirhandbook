# 17  Descriptive tables

[![](../../images/descriptive_tables.png)](../../images/descriptive_tables.png)

This page demonstrates the use of **janitor**, **dplyr**, **gtsummary**, **rstatix**, and **base** R to summarise data and create tables with descriptive statistics.

*This page covers how to* create\* the underlying tables, whereas the [Tables for presentation](tables_presentation.llms.md) page covers how to nicely format and print them.\*

Each of these packages has advantages and disadvantages in the areas of code simplicity, accessibility of outputs, quality of printed outputs. Use this page to decide which approach works for your scenario.

You have several choices when producing tabulation and cross-tabulation summary tables. Some of the factors to consider include code simplicity, customizeability, the desired output (printed to R console, as data frame, or as “pretty” .png/.jpeg/.html image), and ease of post-processing. Consider the points below as you choose the tool for your situation.

- Use `tabyl()` from **janitor** to produce and “adorn” tabulations and cross-tabulations  
- Use `get_summary_stats()` from **rstatix** to easily generate data frames of numeric summary statistics for multiple columns and/or groups  
- Use `summarise()` and `count()` from **dplyr** for more complex statistics, tidy data frame outputs, or preparing data for `ggplot()`  
- Use `tbl_summary()` from **gtsummary** to produce detailed publication-ready tables  
- Use `table()` from **base** R if you do not have access to the above packages

## 17.1 Preparation

### Load packages

This code chunk shows the loading of packages required for the analyses. In this handbook we emphasize `p_load()` from **pacman**, which installs the package if necessary *and* loads it for use. You can also load installed packages with `library()` from **base** R. See the page on [R basics](basics.llms.md) for more information on R packages.

``` r
pacman::p_load(
  rio,          # File import
  here,         # File locator
  skimr,        # get overview of data
  tidyverse,    # data management + ggplot2 graphics 
  gtsummary,    # summary statistics and tests
  rstatix,      # summary statistics and statistical tests
  janitor,      # adding totals and percents to tables
  scales,       # easily convert proportions to percents  
  flextable,    # converting tables to pretty images
  appliedepidata # example datasets used in this handbook
  )
```

### Import data

We import the dataset of cases from a simulated Ebola epidemic. Load it directly with `appliedepidata::get_data(name = "linelist_cleaned_rds")` (see the [Download handbook and data](download.llms.md) page for details).

``` r
# import the linelist
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

The first 50 rows of the linelist are displayed below.

## 17.2 Browse data

### **skimr** package

By using the **skimr** package, you can get a detailed and aesthetically pleasing overview of each of the variables in your dataset. Read more about **skimr** at its [github page](https://github.com/ropensci/skimr).

Below, the function `skim()` is applied to the entire `linelist` data frame. An overview of the data frame and a summary of every column (by class) is produced.

``` r
## get information about each variable in a dataset 
skim(linelist)
```

|                                                  |          |
|:-------------------------------------------------|:---------|
| Name                                             | linelist |
| Number of rows                                   | 5888     |
| Number of columns                                | 30       |
| \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |          |
| Column type frequency:                           |          |
| character                                        | 13       |
| Date                                             | 4        |
| factor                                           | 2        |
| numeric                                          | 11       |
| \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |          |
| Group variables                                  | None     |

Data summary {.caption-top .table .table-sm .table-striped .small}

**Variable type: character**

| skim_variable  | n_missing | complete_rate | min | max | empty | n_unique | whitespace |
|:---------------|----------:|--------------:|----:|----:|------:|---------:|-----------:|
| case_id        |         0 |          1.00 |   6 |   6 |     0 |     5888 |          0 |
| outcome        |      1323 |          0.78 |   5 |   7 |     0 |        2 |          0 |
| gender         |       278 |          0.95 |   1 |   1 |     0 |        2 |          0 |
| age_unit       |         0 |          1.00 |   5 |   6 |     0 |        2 |          0 |
| hospital       |         0 |          1.00 |   5 |  36 |     0 |        6 |          0 |
| infector       |      2088 |          0.65 |   6 |   6 |     0 |     2697 |          0 |
| source         |      2088 |          0.65 |   5 |   7 |     0 |        2 |          0 |
| fever          |       249 |          0.96 |   2 |   3 |     0 |        2 |          0 |
| chills         |       249 |          0.96 |   2 |   3 |     0 |        2 |          0 |
| cough          |       249 |          0.96 |   2 |   3 |     0 |        2 |          0 |
| aches          |       249 |          0.96 |   2 |   3 |     0 |        2 |          0 |
| vomit          |       249 |          0.96 |   2 |   3 |     0 |        2 |          0 |
| time_admission |       765 |          0.87 |   5 |   5 |     0 |     1072 |          0 |

**Variable type: Date**

| skim_variable | n_missing | complete_rate | min | max | median | n_unique |
|:---|---:|---:|:---|:---|:---|---:|
| date_infection | 2087 | 0.65 | 2014-03-19 | 2015-04-27 | 2014-10-11 | 359 |
| date_onset | 256 | 0.96 | 2014-04-07 | 2015-04-30 | 2014-10-23 | 367 |
| date_hospitalisation | 0 | 1.00 | 2014-04-17 | 2015-04-30 | 2014-10-23 | 363 |
| date_outcome | 936 | 0.84 | 2014-04-19 | 2015-06-04 | 2014-11-01 | 371 |

**Variable type: factor**

| skim_variable | n_missing | complete_rate | ordered | n_unique | top_counts |
|:---|---:|---:|:---|---:|:---|
| age_cat | 86 | 0.99 | FALSE | 8 | 0-4: 1095, 5-9: 1095, 20-: 1073, 10-: 941 |
| age_cat5 | 86 | 0.99 | FALSE | 17 | 0-4: 1095, 5-9: 1095, 10-: 941, 15-: 743 |

**Variable type: numeric**

| skim_variable | n_missing | complete_rate | mean | sd | p0 | p25 | p50 | p75 | p100 |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| generation | 0 | 1.00 | 16.56 | 5.79 | 0.00 | 13.00 | 16.00 | 20.00 | 37.00 |
| age | 86 | 0.99 | 16.07 | 12.62 | 0.00 | 6.00 | 13.00 | 23.00 | 84.00 |
| age_years | 86 | 0.99 | 16.02 | 12.64 | 0.00 | 6.00 | 13.00 | 23.00 | 84.00 |
| lon | 0 | 1.00 | -13.23 | 0.02 | -13.27 | -13.25 | -13.23 | -13.22 | -13.21 |
| lat | 0 | 1.00 | 8.47 | 0.01 | 8.45 | 8.46 | 8.47 | 8.48 | 8.49 |
| wt_kg | 0 | 1.00 | 52.64 | 18.58 | -11.00 | 41.00 | 54.00 | 66.00 | 111.00 |
| ht_cm | 0 | 1.00 | 124.96 | 49.52 | 4.00 | 91.00 | 129.00 | 159.00 | 295.00 |
| ct_blood | 0 | 1.00 | 21.21 | 1.69 | 16.00 | 20.00 | 22.00 | 22.00 | 26.00 |
| temp | 149 | 0.97 | 38.56 | 0.98 | 35.20 | 38.20 | 38.80 | 39.20 | 40.80 |
| bmi | 0 | 1.00 | 46.89 | 55.39 | -1200.00 | 24.56 | 32.12 | 50.01 | 1250.00 |
| days_onset_hosp | 256 | 0.96 | 2.06 | 2.26 | 0.00 | 1.00 | 1.00 | 3.00 | 22.00 |

You can also use the `summary()` function, from **base** R, to get information about an entire dataset, but this output can be more difficult to read than using **skimr**. Therefore the output is not shown below, to conserve page space.

``` r
## get information about each column in a dataset 
summary(linelist)
```

### Summary statistics

You can use **base** R functions to return summary statistics on a numeric column. You can return most of the useful summary statistics for a numeric column using `summary()`, as below. Note that the data frame name must also be specified as shown below.

``` r
summary(linelist$age_years)
```

       Min. 1st Qu.  Median    Mean 3rd Qu.    Max.     NAs 
       0.00    6.00   13.00   16.02   23.00   84.00      86 

You can access and save one specific part of it with index brackets \[ \]:

``` r
summary(linelist$age_years)[[2]]            # return only the 2nd element
```

    [1] 6

``` r
# equivalent, alternative to above by element name
# summary(linelist$age_years)[["1st Qu."]]  
```

You can return individual statistics with **base** R functions like `max()`, `min()`, `median()`, `mean()`, `quantile()`, `sd()`, and `range()`. See the [R basics](basics.llms.md) page for a complete list.

***CAUTION:*** If your data contain missing values, R wants you to know this and so will return `NA` unless you specify to the above mathematical functions that you want R to ignore missing values, via the argument `na.rm = TRUE`.

You can use the `get_summary_stats()` function from **rstatix** to return summary statistics *in a data frame format*. This can be helpful for performing subsequent operations or plotting on the numbers. See the [Simple statistical tests](stat_tests.llms.md) page for more details on the **rstatix** package and its functions.

``` r
linelist %>% 
  get_summary_stats(
    age, wt_kg, ht_cm, ct_blood, temp,  # columns to calculate for
    type = "common")                    # summary stats to return
```

    # A tibble: 5 × 10
      variable     n   min   max median   iqr  mean     sd    se    ci
      <fct>    <dbl> <dbl> <dbl>  <dbl> <dbl> <dbl>  <dbl> <dbl> <dbl>
    1 age       5802   0    84     13      17  16.1 12.6   0.166 0.325
    2 wt_kg     5888 -11   111     54      25  52.6 18.6   0.242 0.475
    3 ht_cm     5888   4   295    129      68 125.  49.5   0.645 1.26 
    4 ct_blood  5888  16    26     22       2  21.2  1.69  0.022 0.043
    5 temp      5739  35.2  40.8   38.8     1  38.6  0.977 0.013 0.025

## 17.3 **janitor** package

The **janitor** packages offers the `tabyl()` function to produce tabulations and cross-tabulations, which can be “adorned” or modified with helper functions to display percents, proportions, counts, etc.

Below, we pipe the `linelist` data frame to **janitor** functions and print the result. If desired, you can also save the resulting tables with the assignment operator `<-`.

### Simple tabyl

The default use of `tabyl()` on a specific column produces the unique values, counts, and column-wise “percents” (actually proportions). The proportions may have many digits. You can adjust the number of decimals with `adorn_rounding()` as described below.

``` r
linelist %>% tabyl(age_cat)
```

     age_cat    n     percent valid_percent
         0-4 1095 0.185971467   0.188728025
         5-9 1095 0.185971467   0.188728025
       10-14  941 0.159816576   0.162185453
       15-19  743 0.126188859   0.128059290
       20-29 1073 0.182235054   0.184936229
       30-49  754 0.128057065   0.129955188
       50-69   95 0.016134511   0.016373664
         70+    6 0.001019022   0.001034126
        <NA>   86 0.014605978            NA

As you can see above, if there are missing values they display in a row labeled `<NA>`. You can suppress them with `show_na = FALSE`. If there are no missing values, this row will not appear. If there are missing values, all proportions are given as both raw (denominator inclusive of `NA` counts) and “valid” (denominator excludes `NA` counts).

If the column is class Factor and only certain levels are present in your data, all levels will still appear in the table. You can suppress this feature by specifying `show_missing_levels = FALSE`. Read more on the [Factors](factors.llms.md) page.

### Cross-tabulation

Cross-tabulation counts are achieved by adding one or more additional columns within `tabyl()`. Note that now only counts are returned - proportions and percents can be added with additional steps shown below.

``` r
linelist %>% tabyl(age_cat, gender)
```

     age_cat   f   m NA_
         0-4 640 416  39
         5-9 641 412  42
       10-14 518 383  40
       15-19 359 364  20
       20-29 468 575  30
       30-49 179 557  18
       50-69   2  91   2
         70+   0   5   1
        <NA>   0   0  86

### “Adorning” the tabyl

Use **janitor**’s “adorn” functions to add totals or convert to proportions, percents, or otherwise adjust the display. Often, you will pipe the tabyl through several of these functions.

| Function | Outcome |
|----|----|
| `adorn_totals()` | Adds totals (`where =` “row”, “col”, or “both”). Set `name =` for “Total”. |
| `adorn_percentages()` | Convert counts to proportions, with `denominator =` “row”, “col”, or “all” |
| `adorn_pct_formatting()` | Converts proportions to percents. Specify `digits =`. Remove the “%” symbol with `affix_sign = FALSE`. |
| `adorn_rounding()` | To round proportions to `digits =` places. To round percents use `adorn_pct_formatting()` with `digits =`. |
| `adorn_ns()` | Add counts to a table of proportions or percents. Indicate `position =` “rear” to show counts in parentheses, or “front” to put the percents in parentheses. |
| `adorn_title()` | Add string via arguments `row_name =` and/or `col_name =` |

Be conscious of the order you apply the above functions. Below are some examples.

A simple one-way table with percents instead of the default proportions.

``` r
linelist %>%               # case linelist
  tabyl(age_cat) %>%       # tabulate counts and proportions by age category
  adorn_pct_formatting()   # convert proportions to percents
```

     age_cat    n percent valid_percent
         0-4 1095   18.6%         18.9%
         5-9 1095   18.6%         18.9%
       10-14  941   16.0%         16.2%
       15-19  743   12.6%         12.8%
       20-29 1073   18.2%         18.5%
       30-49  754   12.8%         13.0%
       50-69   95    1.6%          1.6%
         70+    6    0.1%          0.1%
        <NA>   86    1.5%             -

A cross-tabulation with a total row and row percents.

``` r
linelist %>%                                  
  tabyl(age_cat, gender) %>%                  # counts by age and gender
  adorn_totals(where = "row") %>%             # add total row
  adorn_percentages(denominator = "row") %>%  # convert counts to proportions
  adorn_pct_formatting(digits = 1)            # convert proportions to percents
```

     age_cat     f     m    NA_
         0-4 58.4% 38.0%   3.6%
         5-9 58.5% 37.6%   3.8%
       10-14 55.0% 40.7%   4.3%
       15-19 48.3% 49.0%   2.7%
       20-29 43.6% 53.6%   2.8%
       30-49 23.7% 73.9%   2.4%
       50-69  2.1% 95.8%   2.1%
         70+  0.0% 83.3%  16.7%
        <NA>  0.0%  0.0% 100.0%
       Total 47.7% 47.6%   4.7%

A cross-tabulation adjusted so that both counts and percents are displayed.

``` r
linelist %>%                                  # case linelist
  tabyl(age_cat, gender) %>%                  # cross-tabulate counts
  adorn_totals(where = "row") %>%             # add a total row
  adorn_percentages(denominator = "col") %>%  # convert to proportions
  adorn_pct_formatting() %>%                  # convert to percents
  adorn_ns(position = "front") %>%            # display as: "count (percent)"
  adorn_title(                                # adjust titles
    row_name = "Age Category",
    col_name = "Gender")
```

                          Gender                            
     Age Category              f              m          NA_
              0-4   640  (22.8%)   416  (14.8%)  39  (14.0%)
              5-9   641  (22.8%)   412  (14.7%)  42  (15.1%)
            10-14   518  (18.5%)   383  (13.7%)  40  (14.4%)
            15-19   359  (12.8%)   364  (13.0%)  20   (7.2%)
            20-29   468  (16.7%)   575  (20.5%)  30  (10.8%)
            30-49   179   (6.4%)   557  (19.9%)  18   (6.5%)
            50-69     2   (0.1%)    91   (3.2%)   2   (0.7%)
              70+     0   (0.0%)     5   (0.2%)   1   (0.4%)
             <NA>     0   (0.0%)     0   (0.0%)  86  (30.9%)
            Total 2,807 (100.0%) 2,803 (100.0%) 278 (100.0%)

### Printing the tabyl

By default, the tabyl will print raw to your R console.

Alternatively, you can pass the tabyl to **flextable** or similar package to print as a “pretty” image in the RStudio Viewer, which could be exported as .png, .jpeg, .html, etc. This is discussed in the page [Tables for presentation](tables_presentation.llms.md). Note that if printing in this manner and using `adorn_titles()`, you must specify `placement = "combined"`.

``` r
linelist %>%
  tabyl(age_cat, gender) %>% 
  adorn_totals(where = "col") %>% 
  adorn_percentages(denominator = "col") %>% 
  adorn_pct_formatting() %>% 
  adorn_ns(position = "front") %>% 
  adorn_title(
    row_name = "Age Category",
    col_name = "Gender",
    placement = "combined") %>% # this is necessary to print as image
  flextable::flextable() %>%    # convert to pretty image
  flextable::autofit()          # format to one line per row 
```

| Age Category/Gender | f           | m           | NA\_       | Total         |
|---------------------|-------------|-------------|------------|---------------|
| 0-4                 | 640 (22.8%) | 416 (14.8%) | 39 (14.0%) | 1,095 (18.6%) |
| 5-9                 | 641 (22.8%) | 412 (14.7%) | 42 (15.1%) | 1,095 (18.6%) |
| 10-14               | 518 (18.5%) | 383 (13.7%) | 40 (14.4%) | 941 (16.0%)   |
| 15-19               | 359 (12.8%) | 364 (13.0%) | 20 (7.2%)  | 743 (12.6%)   |
| 20-29               | 468 (16.7%) | 575 (20.5%) | 30 (10.8%) | 1,073 (18.2%) |
| 30-49               | 179 (6.4%)  | 557 (19.9%) | 18 (6.5%)  | 754 (12.8%)   |
| 50-69               | 2 (0.1%)    | 91 (3.2%)   | 2 (0.7%)   | 95 (1.6%)     |
| 70+                 | 0 (0.0%)    | 5 (0.2%)    | 1 (0.4%)   | 6 (0.1%)      |
|                     | 0 (0.0%)    | 0 (0.0%)    | 86 (30.9%) | 86 (1.5%)     |

### Use on other tables

You can use **janitor**’s `adorn_*()` functions on other tables, such as those created by `summarise()` and `count()` from **dplyr**, or `table()` from **base** R. Simply pipe the table to the desired **janitor** function. For example:

``` r
linelist %>% 
  count(hospital) %>%   # dplyr function
  adorn_totals()        # janitor function
```

                                 hospital    n
                         Central Hospital  454
                        Military Hospital  896
                                  Missing 1469
                                    Other  885
                            Port Hospital 1762
     St. Mark's Maternity Hospital (SMMH)  422
                                    Total 5888

### Saving the tabyl

If you convert the table to a “pretty” image with a package like **flextable**, you can save it with functions from that package - like `save_as_html()`, `save_as_word()`, `save_as_ppt()`, and `save_as_image()` from **flextable** (as discussed more extensively in the [Tables for presentation](tables_presentation.llms.md) page). Below, the table is saved as a Word document, in which it can be further hand-edited.

``` r
linelist %>%
  tabyl(age_cat, gender) %>% 
  adorn_totals(where = "col") %>% 
  adorn_percentages(denominator = "col") %>% 
  adorn_pct_formatting() %>% 
  adorn_ns(position = "front") %>% 
  adorn_title(
    row_name = "Age Category",
    col_name = "Gender",
    placement = "combined") %>% 
  flextable::flextable() %>%                     # convert to image
  flextable::autofit() %>%                       # ensure only one line per row
  flextable::save_as_docx(path = "tabyl.docx")   # save as Word document to filepath
```

[![](../../images/tabyl_word.png)](../../images/tabyl_word.png)

### Statistics

You can apply statistical tests on tabyls, like `chisq.test()` or `fisher.test()` from the **stats** package, as shown below. Note missing values are not allowed so they are excluded from the tabyl with `show_na = FALSE`.

We use `fisher.test()` because the 70+ row has expected counts below 5, which makes the chi-squared approximation unreliable. On this 8 x 2 table, the exact test stops with an error:

``` r
age_by_outcome <- linelist %>% 
  tabyl(age_cat, outcome, show_na = FALSE) 

fisher.test(age_by_outcome)
```

    Error in `stats::fisher.test()`:
    ! FEXACT error 7(location). LDSTP=17820 is too small for this problem,
      (pastp=817.256, ipn_0:=ipoin[itp=178]=174, stp[ipn_0]=815.749).
    Increase workspace or consider using 'simulate.p.value=TRUE'

`fisher.test()` computes the exact p-value with a network algorithm. The algorithm stores partial results in a table, and the `workspace` argument sets the size of that table. “FEXACT error 7” means that this table is too small for the partial results of this problem. A larger `workspace` does not solve it here, because `workspace = 2e8` also fails. Instead, `simulate.p.value = TRUE` estimates the same exact p-value from random tables with the same row and column totals. `set.seed()` makes this estimate reproducible.

``` r
set.seed(1)
fisher.test(age_by_outcome, simulate.p.value = TRUE)
```


        Fisher's Exact Test for Count Data with simulated p-value (based on
        2000 replicates)

    data:  age_by_outcome
    p-value = 0.4863
    alternative hypothesis: two.sided

See the page on [Simple statistical tests](stat_tests.llms.md) for more code and tips about statistics.

### Other tips

- Include the argument `na.rm = TRUE` to exclude missing values from any of the above calculations.  
- If applying any `adorn_*()` helper functions to tables not created by `tabyl()`, you can specify particular column(s) to apply them to like `adorn_percentage(,,,c(cases,deaths))` (specify them to the 4th unnamed argument). The syntax is not simple. Consider using `summarise()` instead.  
- You can read more detail in the [janitor page](https://cran.r-project.org/web/packages/janitor/vignettes/janitor.html) and this [tabyl vignette](https://cran.r-project.org/web/packages/janitor/vignettes/tabyls.html).

## 17.4 **dplyr** package

**dplyr** is part of the **tidyverse** packages and is an very common data management tool. Creating tables with **dplyr** functions `summarise()` and `count()` is a useful approach to calculating summary statistics, summarize *by group*, or pass tables to `ggplot()`.

`summarise()` creates a *new, summary data frame*. If the data are *ungrouped*, it will return a one-row dataframe with the specified summary statistics of the entire data frame. If the data are *grouped*, the new data frame will have one row per *group* (see [Grouping data](grouping.llms.md) page).

Within the `summarise()` parentheses, you provide the names of each new summary column followed by an equals sign and a statistical function to apply.

***TIP:*** The summarise function works with both UK and US spelling (`summarise()` and `summarize()`).

### Get counts

The most simple function to apply within `summarise()` is `n()`. Leave the parentheses empty to count the number of rows.

``` r
linelist %>%                 # begin with linelist
  summarise(n_rows = n())    # return new summary dataframe with column n_rows
```

      n_rows
    1   5888

This gets more interesting if we have grouped the data beforehand.

``` r
linelist %>% 
  group_by(age_cat) %>%     # group data by unique values in column age_cat
  summarise(n_rows = n())   # return number of rows *per group*
```

    # A tibble: 9 × 2
      age_cat n_rows
      <fct>    <int>
    1 0-4       1095
    2 5-9       1095
    3 10-14      941
    4 15-19      743
    5 20-29     1073
    6 30-49      754
    7 50-69       95
    8 70+          6
    9 <NA>        86

The above command can be shortened by using the `count()` function instead. `count()` does the following:

1.  Groups the data by the columns provided to it  
2.  Summarises them with `n()` (creating column `n`)  
3.  Un-groups the data

``` r
linelist %>% 
  count(age_cat)
```

      age_cat    n
    1     0-4 1095
    2     5-9 1095
    3   10-14  941
    4   15-19  743
    5   20-29 1073
    6   30-49  754
    7   50-69   95
    8     70+    6
    9    <NA>   86

You can change the name of the counts column from the default `n` to something else by specifying it to `name =`.

Tabulating counts of two or more grouping columns are still returned in “long” format, with the counts in the `n` column. See the page on [Pivoting data](pivoting.llms.md) to learn about “long” and “wide” data formats.

``` r
linelist %>% 
  count(age_cat, outcome)
```

       age_cat outcome   n
    1      0-4   Death 471
    2      0-4 Recover 364
    3      0-4    <NA> 260
    4      5-9   Death 476
    5      5-9 Recover 391
    6      5-9    <NA> 228
    7    10-14   Death 438
    8    10-14 Recover 303
    9    10-14    <NA> 200
    10   15-19   Death 323
    11   15-19 Recover 251
    12   15-19    <NA> 169
    13   20-29   Death 477
    14   20-29 Recover 367
    15   20-29    <NA> 229
    16   30-49   Death 329
    17   30-49 Recover 238
    18   30-49    <NA> 187
    19   50-69   Death  33
    20   50-69 Recover  38
    21   50-69    <NA>  24
    22     70+   Death   3
    23     70+ Recover   3
    24    <NA>   Death  32
    25    <NA> Recover  28
    26    <NA>    <NA>  26

### Show all levels

If you are tabling a column of class *factor* you can ensure that *all* levels are shown (not just the levels with values in the data) by adding `.drop = FALSE` into the `summarise()` or `count()` command.

This technique is useful to standardise your tables/plots. For example if you are creating figures for multiple sub-groups, or repeatedly creating the figure for routine reports. In each of these circumstances, the presence of values in the data may fluctuate, but you can define levels that remain constant.

See the page on [Factors](factors.llms.md) for more information.

### Proportions

Proportions can be added by piping the table to `mutate()` to create a new column. Define the new column as the counts column (`n` by default) divided by the `sum()` of the counts column (this will return a proportion).

Note that in this case, `sum()` in the `mutate()` command will return the sum of the whole column `n` for use as the proportion denominator. As explained [in the Grouping data page](grouping.llms.md#group_summarise), *if* `sum()` is used in *grouped* data (e.g. if the `mutate()` immediately followed a `group_by()` command), it will return sums *by group*. As stated just above, `count()` finishes its actions by *ungrouping*. Thus, in this scenario we get full column proportions.

To easily display percents, you can wrap the proportion in the function `percent()` from the package **scales** (note this convert to class character).

``` r
age_summary <- linelist %>% 
  count(age_cat) %>%                     # group and count by gender (produces "n" column)
  mutate(                                # create percent of column - note the denominator
    percent = scales::percent(n / sum(n))) 

# print
age_summary
```

      age_cat    n percent
    1     0-4 1095  18.60%
    2     5-9 1095  18.60%
    3   10-14  941  15.98%
    4   15-19  743  12.62%
    5   20-29 1073  18.22%
    6   30-49  754  12.81%
    7   50-69   95   1.61%
    8     70+    6   0.10%
    9    <NA>   86   1.46%

Below is a method to calculate proportions *within groups*. It relies on different levels of data grouping being selectively applied and removed. First, the data are grouped on `outcome` via `group_by()`. Then, `count()` is applied. This function further groups the data by `age_cat` and returns counts for each `outcome`-`age-cat` combination. Importantly - as it finishes its process, `count()` also *ungroups* the `age_cat` grouping, so the only remaining data grouping is the original grouping by `outcome`. Thus, the final step of calculating proportions (denominator `sum(n)`) is still grouped by `outcome`.

``` r
age_by_outcome <- linelist %>%                  # begin with linelist
  group_by(outcome) %>%                         # group by outcome 
  count(age_cat) %>%                            # group and count by age_cat, and then remove age_cat grouping
  mutate(percent = scales::percent(n / sum(n))) # calculate percent - note the denominator is by outcome group
```

### Plotting

To display a “long” table output like the above with `ggplot()` is relatively straight-forward. The data are naturally in “long” format, which is naturally accepted by `ggplot()`. See further examples in the pages [ggplot basics](ggplot_basics.llms.md) and [ggplot tips](ggplot_tips.llms.md).

``` r
linelist %>%                      # begin with linelist
  count(age_cat, outcome) %>%     # group and tabulate counts by two columns
  ggplot()+                       # pass new data frame to ggplot
    geom_col(                     # create bar plot
      mapping = aes(   
        x = outcome,              # map outcome to x-axis
        fill = age_cat,           # map age_cat to the fill
        y = n))                   # map the counts column `n` to the height
```

[![](tables_descriptive_files/figure-html/unnamed-chunk-29-1.png)](tables_descriptive_files/figure-html/unnamed-chunk-29-1.png)

### Summary statistics

One major advantage of **dplyr** and `summarise()` is the ability to return more advanced statistical summaries like `median()`, `mean()`, `max()`, `min()`, `sd()` (standard deviation), and percentiles. You can also use `sum()` to return the number of rows that meet certain logical criteria. As above, these outputs can be produced for the whole data frame set, or by group.

The syntax is the same - within the `summarise()` parentheses you provide the names of each new summary column followed by an equals sign and a statistical function to apply. Within the statistical function, give the column(s) to be operated on and any relevant arguments (e.g. `na.rm = TRUE` for most mathematical functions).

You can also use `sum()` to return the number of rows that meet a logical criteria. The expression within is counted if it evaluates to `TRUE`. For example:

- `sum(age_years < 18, na.rm=T)`  
- `sum(gender == "male", na.rm=T)`  
- `sum(response %in% c("Likely", "Very Likely"))`

Below, `linelist` data are summarised to describe the days delay from symptom onset to hospital admission (column `days_onset_hosp`), by hospital.

``` r
summary_table <- linelist %>%                                        # begin with linelist, save out as new object
  group_by(hospital) %>%                                             # group all calculations by hospital
  summarise(                                                         # only the below summary columns will be returned
    cases       = n(),                                                # number of rows per group
    delay_max   = max(days_onset_hosp, na.rm = T),                    # max delay
    delay_mean  = round(mean(days_onset_hosp, na.rm=T), digits = 1),  # mean delay, rounded
    delay_sd    = round(sd(days_onset_hosp, na.rm = T), digits = 1),  # standard deviation of delays, rounded
    delay_3     = sum(days_onset_hosp >= 3, na.rm = T),               # number of rows with delay of 3 or more days
    pct_delay_3 = scales::percent(delay_3 / cases)                    # convert previously-defined delay column to percent 
  )

summary_table  # print
```

    # A tibble: 6 × 7
      hospital               cases delay_max delay_mean delay_sd delay_3 pct_delay_3
      <chr>                  <int>     <dbl>      <dbl>    <dbl>   <int> <chr>      
    1 Central Hospital         454        12        1.9      1.9     108 24%        
    2 Military Hospital        896        15        2.1      2.4     253 28%        
    3 Missing                 1469        22        2.1      2.3     399 27%        
    4 Other                    885        18        2        2.2     234 26%        
    5 Port Hospital           1762        16        2.1      2.2     470 27%        
    6 St. Mark's Maternity …   422        18        2.1      2.3     116 27%        

Some tips:

- Use `sum()` with a logic statement to “count” rows that meet certain criteria (`==`)  
- Note the use of `na.rm = TRUE` within mathematical functions like `sum()`, otherwise `NA` will be returned if there are any missing values  
- Use the function `percent()` from the **scales** package to easily convert to percents
  - Set `accuracy =` to 0.1 or 0.01 to ensure 1 or 2 decimal places respectively  
- Use `round()` from **base** R to specify decimals  
- To calculate these statistics on the entire dataset, use `summarise()` without `group_by()`  
- You may create columns for the purposes of later calculations (e.g. denominators) that you eventually drop from your data frame with `select()`.

### Conditional statistics

You may want to return *conditional statistics* - e.g. the maximum of rows that meet certain criteria. This can be done by subsetting the column with brackets `[ ]`. The example below returns the maximum temperature for patients classified having or not having fever. Be aware however - it may be more appropriate to add another column to the `group_by()` command and `pivot_wider()` (as demonstrated [below](#tbls_pivot_wider)).

``` r
linelist %>% 
  group_by(hospital) %>% 
  summarise(
    max_temp_fvr = max(temp[fever == "yes"], na.rm = T),
    max_temp_no = max(temp[fever == "no"], na.rm = T)
  )
```

    # A tibble: 6 × 3
      hospital                             max_temp_fvr max_temp_no
      <chr>                                       <dbl>       <dbl>
    1 Central Hospital                             40.4        38  
    2 Military Hospital                            40.5        38  
    3 Missing                                      40.6        38  
    4 Other                                        40.8        37.9
    5 Port Hospital                                40.6        38  
    6 St. Mark's Maternity Hospital (SMMH)         40.6        37.9

### Glueing together

The function `str_glue()` from **stringr** is useful to combine values from several columns into one new column. In this context this is typically used *after* the `summarise()` command.

In the [Characters and strings](characters_strings.llms.md) page, various options for combining columns are discussed, including `unite()`, and `paste0()`. In this use case, we advocate for `str_glue()` because it is more flexible than `unite()` and has more simple syntax than `paste0()`.

Below, the `summary_table` data frame (created above) is mutated such that columns `delay_mean` and `delay_sd` are combined, parentheses formating is added to the new column, and their respective old columns are removed.

Then, to make the table more presentable, a total row is added with `adorn_totals()` from **janitor** (which ignores non-numeric columns). Lastly, we use `select()` from **dplyr** to both re-order and rename to nicer column names.

Now you could pass to **flextable** and print the table to Word, .png, .jpeg, .html, Powerpoint, RMarkdown, etc.! (see the [Tables for presentation](tables_presentation.llms.md) page).

``` r
summary_table %>% 
  mutate(delay = str_glue("{delay_mean} ({delay_sd})")) %>%  # combine and format other values
  select(-c(delay_mean, delay_sd)) %>%                       # remove two old columns   
  adorn_totals(where = "row") %>%                            # add total row
  select(                                                    # order and rename cols
    "Hospital Name"   = hospital,
    "Cases"           = cases,
    "Max delay"       = delay_max,
    "Mean (sd)"       = delay,
    "Delay 3+ days"   = delay_3,
    "% delay 3+ days" = pct_delay_3
    )
```

                            Hospital Name Cases Max delay Mean (sd) Delay 3+ days
                         Central Hospital   454        12 1.9 (1.9)           108
                        Military Hospital   896        15 2.1 (2.4)           253
                                  Missing  1469        22 2.1 (2.3)           399
                                    Other   885        18   2 (2.2)           234
                            Port Hospital  1762        16 2.1 (2.2)           470
     St. Mark's Maternity Hospital (SMMH)   422        18 2.1 (2.3)           116
                                    Total  5888       101         -          1580
     % delay 3+ days
                 24%
                 28%
                 27%
                 26%
                 27%
                 27%
                   -

#### Percentiles

*Percentiles* and quantiles in **dplyr** deserve a special mention. To return quantiles, use `quantile()` with the defaults or specify the value(s) you would like with `probs =`.

``` r
# get default percentile values of age (0%, 25%, 50%, 75%, 100%)
linelist %>% 
  reframe(age_percentiles = quantile(age_years, na.rm = TRUE))
```

      age_percentiles
    1               0
    2               6
    3              13
    4              23
    5              84

``` r
# get manually-specified percentile values of age (5%, 50%, 75%, 98%)
linelist %>% 
  reframe(
    age_percentiles = quantile(
      age_years,
      probs = c(.05, 0.5, 0.75, 0.98), 
      na.rm=TRUE)
    )
```

      age_percentiles
    1               1
    2              13
    3              23
    4              48

If you want to return quantiles *by group*, you may encounter long and less useful outputs if you simply add another column to `group_by()`. So, try this approach instead - create a column for each quantile level desired.

``` r
# get manually-specified percentile values of age (5%, 50%, 75%, 98%)
linelist %>% 
  group_by(hospital) %>% 
  summarise(
    p05 = quantile(age_years, probs = 0.05, na.rm=T),
    p50 = quantile(age_years, probs = 0.5, na.rm=T),
    p75 = quantile(age_years, probs = 0.75, na.rm=T),
    p98 = quantile(age_years, probs = 0.98, na.rm=T)
    )
```

    # A tibble: 6 × 5
      hospital                               p05   p50   p75   p98
      <chr>                                <dbl> <dbl> <dbl> <dbl>
    1 Central Hospital                         1    12    21  48  
    2 Military Hospital                        1    13    24  45  
    3 Missing                                  1    13    23  48.2
    4 Other                                    1    13    23  50  
    5 Port Hospital                            1    14    24  49  
    6 St. Mark's Maternity Hospital (SMMH)     2    12    22  50.2

While **dplyr** `summarise()` certainly offers more fine control, you may find that all the summary statistics you need can be produced with `get_summary_stat()` from the **rstatix** package. If operating on grouped data, if will return 0%, 25%, 50%, 75%, and 100%. If applied to ungrouped data, you can specify the percentiles with `probs = c(.05, .5, .75, .98)`.

``` r
linelist %>% 
  group_by(hospital) %>% 
  rstatix::get_summary_stats(age, type = "quantile")
```

    # A tibble: 6 × 8
      hospital                         variable     n  `0%` `25%` `50%` `75%` `100%`
      <chr>                            <fct>    <dbl> <dbl> <dbl> <dbl> <dbl>  <dbl>
    1 Central Hospital                 age        445     0     6    12    21     58
    2 Military Hospital                age        884     0     6    14    24     72
    3 Missing                          age       1441     0     6    13    23     76
    4 Other                            age        873     0     6    13    23     69
    5 Port Hospital                    age       1739     0     6    14    24     68
    6 St. Mark's Maternity Hospital (… age        420     0     7    12    22     84

``` r
linelist %>% 
  rstatix::get_summary_stats(age, type = "quantile")
```

    # A tibble: 1 × 7
      variable     n  `0%` `25%` `50%` `75%` `100%`
      <fct>    <dbl> <dbl> <dbl> <dbl> <dbl>  <dbl>
    1 age       5802     0     6    13    23     84

### Summarise aggregated data

*If you begin with aggregated data*, using `n()` return the number of *rows*, not the sum of the aggregated counts. To get sums, use `sum()` on the data’s counts column.

For example, let’s say you are beginning with the data frame of counts below, called `linelist_agg` - it shows in “long” format the case counts by outcome and gender.

Below we create this example data frame of `linelist` case counts by outcome and gender (missing values removed for clarity).

``` r
linelist_agg <- linelist %>% 
  drop_na(gender, outcome) %>% 
  count(outcome, gender)

linelist_agg
```

      outcome gender    n
    1   Death      f 1227
    2   Death      m 1228
    3 Recover      f  953
    4 Recover      m  950

To sum the counts (in column `n`) by group you can use `summarise()` but set the new column equal to `sum(n, na.rm=T)`. To add a conditional element to the sum operation, you can use the subset bracket \[ \] syntax on the counts column.

``` r
linelist_agg %>% 
  group_by(outcome) %>% 
  summarise(
    total_cases  = sum(n, na.rm=T),
    male_cases   = sum(n[gender == "m"], na.rm=T),
    female_cases = sum(n[gender == "f"], na.rm=T))
```

    # A tibble: 2 × 4
      outcome total_cases male_cases female_cases
      <chr>         <int>      <int>        <int>
    1 Death          2455       1228         1227
    2 Recover        1903        950          953

### `across()` multiple columns

You can use `summarise()` across multiple columns using `across()`. This makes life easier when you want to calculate the same statistics for many columns. Place `across()` within `summarise()` and specify the following:

- `.cols =` as either a vector of column names `c()` or “tidyselect” helper functions (explained below)  
- `.fns =` the function to perform (no parentheses) - you can provide multiple within a `list()`

Below, `mean()` is applied to several numeric columns. A vector of columns are named explicitly to `.cols =` and a single function `mean` is specified (no parentheses) to `.fns =`. Any additional arguments for the function (e.g. `na.rm=TRUE`) are provided after `.fns =`, separated by a comma.

It can be difficult to get the order of parentheses and commas correct when using `across()`. Remember that within `across()` you must include the columns, the functions, and any extra arguments needed for the functions.

``` r
linelist %>% 
  group_by(outcome) %>% 
  summarise(across(.cols = c(age_years, temp, wt_kg, ht_cm),  # columns
                   .fns = ~ mean(.x, na.rm=T)))                                  # extra arguments
```

    # A tibble: 3 × 5
      outcome age_years  temp wt_kg ht_cm
      <chr>       <dbl> <dbl> <dbl> <dbl>
    1 Death        15.9  38.6  52.6  125.
    2 Recover      16.1  38.6  52.5  125.
    3 <NA>         16.2  38.6  53.0  125.

Multiple functions can be run at once. Below the functions `mean` and `sd` are provided to `.fns =` within a `list()`. You have the opportunity to provide character names (e.g. “mean” and “sd”) which are appended in the new column names.

``` r
linelist %>% 
  group_by(outcome) %>% 
  summarise(across(.cols = c(age_years, temp, wt_kg, ht_cm), # columns
                   .fns = list("mean" = ~mean(.x, na.rm=T), "sd" = ~sd(.x, na.rm=T))))                                 # extra arguments
```

    # A tibble: 3 × 9
      outcome age_years_mean age_years_sd temp_mean temp_sd wt_kg_mean wt_kg_sd
      <chr>            <dbl>        <dbl>     <dbl>   <dbl>      <dbl>    <dbl>
    1 Death             15.9         12.3      38.6   0.962       52.6     18.4
    2 Recover           16.1         13.0      38.6   0.997       52.5     18.6
    3 <NA>              16.2         12.8      38.6   0.976       53.0     18.9
    # ℹ 2 more variables: ht_cm_mean <dbl>, ht_cm_sd <dbl>

Here are those “tidyselect” helper functions you can provide to `.cols =` to select columns:

- `everything()` - all other columns not mentioned  
- `last_col()` - the last column  
- `where()` - applies a function to all columns and selects those which are TRUE  
- `starts_with()` - matches to a specified prefix. Example: `starts_with("date")`
- `ends_with()` - matches to a specified suffix. Example: `ends_with("_end")`  
- `contains()` - columns containing a character string. Example: `contains("time")`
- `matches()` - to apply a regular expression (regex). Example: `contains("[pt]al")`  
- `num_range()` -
- `any_of()` - matches if column is named. Useful if the name might not exist. Example: `any_of(date_onset, date_death, cardiac_arrest)`

For example, to return the mean of every numeric column use `where()` and provide the function `as.numeric()` (without parentheses). All this remains within the `across()` command.

``` r
linelist %>% 
  group_by(outcome) %>% 
  summarise(across(
    .cols = where(is.numeric),  # all numeric columns in the data frame
    .fns = ~ mean(.x, na.rm=T)))
```

    # A tibble: 3 × 12
      outcome generation   age age_years   lon   lat wt_kg ht_cm ct_blood  temp
      <chr>        <dbl> <dbl>     <dbl> <dbl> <dbl> <dbl> <dbl>    <dbl> <dbl>
    1 Death         16.7  15.9      15.9 -13.2  8.47  52.6  125.     21.3  38.6
    2 Recover       16.4  16.2      16.1 -13.2  8.47  52.5  125.     21.1  38.6
    3 <NA>          16.5  16.3      16.2 -13.2  8.47  53.0  125.     21.2  38.6
    # ℹ 2 more variables: bmi <dbl>, days_onset_hosp <dbl>

### Pivot wider

If you prefer your table in “wide” format you can transform it using the **tidyr** `pivot_wider()` function. You will likely need to re-name the columns with `rename()`. For more information see the page on [Pivoting data](pivoting.llms.md).

The example below begins with the “long” table `age_by_outcome` from the [proportions section](#tbl_dplyr_prop). We create it again and print, for clarity:

``` r
age_by_outcome <- linelist %>%                  # begin with linelist
  group_by(outcome) %>%                         # group by outcome 
  count(age_cat) %>%                            # group and count by age_cat, and then remove age_cat grouping
  mutate(percent = scales::percent(n / sum(n))) # calculate percent - note the denominator is by outcome group
```

To pivot wider, we create the new columns from the *values* in the existing column `age_cat` (by setting `names_from = age_cat`). We also specify that the new table values will come from the existing column `n`, with `values_from = n`. The columns not mentioned in our pivoting command (`outcome`) will remain unchanged on the far left side.

``` r
age_by_outcome %>% 
  select(-percent) %>%   # keep only counts for simplicity
  pivot_wider(names_from = age_cat, values_from = n)  
```

    # A tibble: 3 × 10
    # Groups:   outcome [3]
      outcome `0-4` `5-9` `10-14` `15-19` `20-29` `30-49` `50-69` `70+`  `NA`
      <chr>   <int> <int>   <int>   <int>   <int>   <int>   <int> <int> <int>
    1 Death     471   476     438     323     477     329      33     3    32
    2 Recover   364   391     303     251     367     238      38     3    28
    3 <NA>      260   228     200     169     229     187      24    NA    26

### Total rows

When `summarise()` operates on grouped data it does not automatically produce “total” statistics. Below, two approaches to adding a total row are presented:

#### **janitor**’s `adorn_totals()`

If your table consists only of counts or proportions/percents that can be summed into a total, then you can add *sum* totals using **janitor**’s `adorn_totals()` as described in the section above. Note that this function can only sum the numeric columns - if you want to calculate other total summary statistics see the next approach with **dplyr**.

Below, `linelist` is grouped by gender and summarised into a table that described the number of cases with known outcome, deaths, and recovered. Piping the table to `adorn_totals()` adds a total row at the bottom reflecting the sum of each column. The further `adorn_*()` functions adjust the display as noted in the code.

``` r
linelist %>% 
  group_by(gender) %>%
  summarise(
    known_outcome = sum(!is.na(outcome)),           # Number of rows in group where outcome is not missing
    n_death  = sum(outcome == "Death", na.rm=T),    # Number of rows in group where outcome is Death
    n_recover = sum(outcome == "Recover", na.rm=T), # Number of rows in group where outcome is Recovered
  ) %>% 
  adorn_totals() %>%                                # Adorn total row (sums of each numeric column)
  adorn_percentages("col") %>%                      # Get column proportions
  adorn_pct_formatting() %>%                        # Convert proportions to percents
  adorn_ns(position = "front")                      # display % and counts (with counts in front)
```

     gender  known_outcome        n_death      n_recover
          f 2,180  (47.8%) 1,227  (47.5%)   953  (48.1%)
          m 2,178  (47.7%) 1,228  (47.6%)   950  (47.9%)
       <NA>   207   (4.5%)   127   (4.9%)    80   (4.0%)
      Total 4,565 (100.0%) 2,582 (100.0%) 1,983 (100.0%)

#### `summarise()` on “total” data and then `bind_rows()`

If your table consists of summary statistics such as `median()`, `mean()`, etc, the `adorn_totals()` approach shown above will *not* be sufficient. Instead, to get summary statistics for the entire dataset you must calculate them with a separate `summarise()` command and then bind the results to the original grouped summary table. To do the binding you can use `bind_rows()` from **dplyr** s described in the [Joining data](joining_matching.llms.md) page. Below is an example:

You can make a summary table of outcome *by hospital* with `group_by()` and `summarise()` like this:

``` r
by_hospital <- linelist %>% 
  filter(!is.na(outcome) & hospital != "Missing") %>%  # Remove cases with missing outcome or hospital
  group_by(hospital, outcome) %>%                      # Group data
  summarise(                                           # Create new summary columns of indicators of interest
    N = n(),                                            # Number of rows per hospital-outcome group     
    ct_value = median(ct_blood, na.rm=T))               # median CT value per group
  
by_hospital # print table
```

    # A tibble: 10 × 4
    # Groups:   hospital [5]
       hospital                             outcome     N ct_value
       <chr>                                <chr>   <int>    <dbl>
     1 Central Hospital                     Death     193       22
     2 Central Hospital                     Recover   165       22
     3 Military Hospital                    Death     399       21
     4 Military Hospital                    Recover   309       22
     5 Other                                Death     395       22
     6 Other                                Recover   290       21
     7 Port Hospital                        Death     785       22
     8 Port Hospital                        Recover   579       21
     9 St. Mark's Maternity Hospital (SMMH) Death     199       22
    10 St. Mark's Maternity Hospital (SMMH) Recover   126       22

To get the totals, run the same `summarise()` command but only group the data by outcome (not by hospital), like this:

``` r
totals <- linelist %>% 
      filter(!is.na(outcome) & hospital != "Missing") %>%
      group_by(outcome) %>%                            # Grouped only by outcome, not by hospital    
      summarise(
        N = n(),                                       # These statistics are now by outcome only     
        ct_value = median(ct_blood, na.rm=T))

totals # print table
```

    # A tibble: 2 × 3
      outcome     N ct_value
      <chr>   <int>    <dbl>
    1 Death    1971       22
    2 Recover  1469       22

We can bind these two data frames together. Note that `by_hospital` has 4 columns whereas `totals` has 3 columns. By using `bind_rows()`, the columns are combined by name, and any extra space is filled in with `NA` (e.g the column `hospital` values for the two new `totals` rows). After binding the rows, we convert these empty spaces to “Total” using `replace_na()` (see [Cleaning data and core functions](cleaning.llms.md) page).

``` r
table_long <- bind_rows(by_hospital, totals) %>% 
  mutate(hospital = replace_na(hospital, "Total"))
```

Here is the new table with “Total” rows at the bottom.

This table is in a “long” format, which may be what you want. *Optionally*, you can *pivot* this table *wider* to make it more readable. See the section on pivoting wider above, and the [Pivoting data](pivoting.llms.md) page. You can also add more columns, and arrange it nicely. This code is below.

``` r
table_long %>% 
  
  # Pivot wider and format
  ########################
  mutate(hospital = replace_na(hospital, "Total")) %>% 
  pivot_wider(                                         # Pivot from long to wide
    values_from = c(ct_value, N),                       # new values are from ct and count columns
    names_from = outcome) %>%                           # new column names are from outcomes
  mutate(                                              # Add new columns
    N_Known = N_Death + N_Recover,                               # number with known outcome
    Pct_Death = scales::percent(N_Death / N_Known, 0.1),         # percent cases who died (to 1 decimal)
    Pct_Recover = scales::percent(N_Recover / N_Known, 0.1)) %>% # percent who recovered (to 1 decimal)
  select(                                              # Re-order columns
    hospital, N_Known,                                   # Intro columns
    N_Recover, Pct_Recover, ct_value_Recover,            # Recovered columns
    N_Death, Pct_Death, ct_value_Death)  %>%             # Death columns
  arrange(N_Known)                                  # Arrange rows from lowest to highest (Total row at bottom)
```

    # A tibble: 6 × 8
    # Groups:   hospital [6]
      hospital      N_Known N_Recover Pct_Recover ct_value_Recover N_Death Pct_Death
      <chr>           <int>     <int> <chr>                  <dbl>   <int> <chr>    
    1 St. Mark's M…     325       126 38.8%                     22     199 61.2%    
    2 Central Hosp…     358       165 46.1%                     22     193 53.9%    
    3 Other             685       290 42.3%                     21     395 57.7%    
    4 Military Hos…     708       309 43.6%                     22     399 56.4%    
    5 Port Hospital    1364       579 42.4%                     21     785 57.6%    
    6 Total            3440      1469 42.7%                     22    1971 57.3%    
    # ℹ 1 more variable: ct_value_Death <dbl>

And then you can print this nicely as an image - below is the output printed with **flextable**. You can read more in depth about this example and how to achieve this “pretty” table in the [Tables for presentation](tables_presentation.llms.md) page.

| Hospital | Total cases with known outcome | Recovered |  |  | Died |  |  |
|----|----|----|----|----|----|----|----|
|  |  | Total | % of cases | Median CT values | Total | % of cases | Median CT values |
| St. Mark's Maternity Hospital (SMMH) | 325 | 126 | 38.8% | 22 | 199 | 61.2% | 22 |
| Central Hospital | 358 | 165 | 46.1% | 22 | 193 | 53.9% | 22 |
| Other | 685 | 290 | 42.3% | 21 | 395 | 57.7% | 22 |
| Military Hospital | 708 | 309 | 43.6% | 22 | 399 | 56.4% | 21 |
| Missing | 1,125 | 514 | 45.7% | 21 | 611 | 54.3% | 21 |
| Port Hospital | 1,364 | 579 | 42.4% | 21 | 785 | 57.6% | 22 |
| Total | 3,440 | 1,469 | 42.7% | 22 | 1,971 | 57.3% | 22 |

## 17.5 **gtsummary** package

If you want to print your summary statistics in a pretty, publication-ready graphic, you can use the **gtsummary** package and its function `tbl_summary()`. The code can seem complex at first, but the outputs look very nice and print to your RStudio Viewer panel as an HTML image. Read a [vignette here](http://www.danieldsjoberg.com/gtsummary/articles/tbl_summary.html).

You can also add the results of statistical tests to **gtsummary** tables. This process is described in the **gtsummary** section of the [Simple statistical tests](stat_tests.llms.md#stats_gt) page.

To introduce `tbl_summary()` we will show the most basic behavior first, which actually produces a large and beautiful table. Then, we will examine in detail how to make adjustments and more tailored tables.

### Summary table

The default behavior of `tbl_summary()` is quite incredible - it takes the columns you provide and creates a summary table in one command. The function prints statistics appropriate to the column class: median and inter-quartile range (IQR) for numeric columns, and counts (%) for categorical columns. Missing values are converted to “Unknown”. Footnotes are added to the bottom to explain the statistics, while the total N is shown at the top.

``` r
linelist %>% 
  select(age_years, gender, outcome, fever, temp, hospital) %>%  # keep only the columns of interest
  tbl_summary()                                                  # default
```

[TABLE]

### Adjustments

Now we will explain how the function works and how to make adjustments. The key arguments are detailed below:

**`by =`**  
You can stratify your table by a column (e.g. by `outcome`), creating a 2-way table.

**`statistic =`**  
Use an equations to specify which statistics to show and how to display them. There are two sides to the equation, separated by a tilde `~`. On the right side, in quotes, is the statistical display desired, and on the left are the columns to which that display will apply.

- The right side of the equation uses the syntax of `str_glue()` from **stringr** (see \[Characters and Strings\])(characters_strings.qmd), with the desired display string in quotes and the statistics themselves within curly brackets. You can include statistics like “n” (for counts), “N” (for denominator), “mean”, “median”, “sd”, “max”, “min”, percentiles as “p##” like “p25”, or percent of total as “p”. See `?tbl_summary` for details.  
- For the left side of the equation, you can specify columns by name (e.g. `age` or `c(age, gender)`) or using helpers such as `all_continuous()`, `all_categorical()`, `contains()`, `starts_with()`, etc.

A simple example of a `statistic =` equation might look like below, to only print the mean of column `age_years`:

``` r
linelist %>% 
  select(age_years) %>%         # keep only columns of interest 
  tbl_summary(                  # create summary table
    statistic = age_years ~ "{mean}") # print mean of age
```

| **Characteristic** | **N = 5,888**¹ |
|--------------------|----------------|
| age_years          | 16             |
|     Unknown        | 86             |
| ¹ Mean             |                |

A slightly more complex equation might look like `"({min}, {max})"`, incorporating the max and min values within parentheses and separated by a comma:

``` r
linelist %>% 
  select(age_years) %>%                       # keep only columns of interest 
  tbl_summary(                                # create summary table
    statistic = age_years ~ "({min}, {max})") # print min and max of age
```

| **Characteristic** | **N = 5,888**¹ |
|--------------------|----------------|
| age_years          | (0, 84)        |
|     Unknown        | 86             |
| ¹ (Min, Max)       |                |

You can also differentiate syntax for separate columns or types of columns. In the more complex example below, the value provided to `statistc =` is a **list** indicating that for all continuous columns the table should print mean with standard deviation in parentheses, while for all categorical columns it should print the n, denominator, and percent.

**`digits =`**  
Adjust the digits and rounding. Optionally, this can be specified to be for continuous columns only (as below).

**`label =`**  
Adjust how the column name should be displayed. Provide the column name and its desired label separated by a tilde. The default is the column name.

**`missing_text =`**  
Adjust how missing values are displayed. The default is “Unknown”.

**`type =`**  
This is used to adjust how many levels of the statistics are shown. The syntax is similar to `statistic =` in that you provide an equation with columns on the left and a value on the right. Two common scenarios include:

- `type = all_categorical() ~ "categorical"` Forces dichotomous columns (e.g. `fever` yes/no) to show all levels instead of only the “yes” row  
- `type = all_continuous() ~ "continuous2"` Allows multi-line statistics per variable, as shown in a later section

In the example below, each of these arguments is used to modify the original summary table:

``` r
linelist %>% 
  select(age_years, gender, outcome, fever, temp, hospital) %>% # keep only columns of interest
  drop_na(outcome) %>%
  tbl_summary(     
    by = outcome,                                               # stratify entire table by outcome
    statistic = list(all_continuous() ~ "{mean} ({sd})",        # stats and format for continuous columns
                     all_categorical() ~ "{n} / {N} ({p}%)"),   # stats and format for categorical columns
    digits = all_continuous() ~ 1,                              # rounding for continuous columns
    type   = all_categorical() ~ "categorical",                 # force all categorical levels to display
    label  = list(                                              # display labels for column names
      age_years ~ "Age (years)",
      gender    ~ "Gender",
      temp      ~ "Temperature",
      hospital  ~ "Hospital"),
    missing_text = "Missing"                                    # how missing values should display
  )
```

[TABLE]

### Multi-line stats for continuous variables

If you want to print multiple lines of statistics for continuous variables, you can indicate this by setting the `type =` to “continuous2”. You can combine all of the previously shown elements in one table by choosing which statistics you want to show. To do this you need to tell the function that you want to get a table back by entering the type as “continuous2”. The number of missing values is shown as “Unknown”.

``` r
linelist %>% 
  select(age_years, temp) %>%                      # keep only columns of interest
  tbl_summary(                                     # create summary table
    type = all_continuous() ~ "continuous2",       # indicate that you want to print multiple statistics 
    statistic = all_continuous() ~ c(
      "{mean} ({sd})",                             # line 1: mean and SD
      "{median} ({p25}, {p75})",                   # line 2: median and IQR
      "{min}, {max}")                              # line 3: min and max
    )
```

[TABLE]

There are many other ways to modify these tables, including adding p-values, adjusting color and headings, etc. Many of these are described in the documentation (enter `?tbl_summary` in Console), and some are given in the section on [statistical tests](https://epirhandbook.com/simple-statistical-tests.html).

## 17.6 **base** R

You can use the function `table()` to tabulate and cross-tabulate columns. Unlike the options above, you must specify the dataframe each time you reference a column name, as shown below.

***CAUTION:*** `NA` (missing) values will **not** be tabulated unless you include the argument `useNA = "always"` (which could also be set to “no” or “ifany”).

***TIP:*** You can use the `%$%` from **magrittr** to remove the need for repeating data frame calls within **base** functions. For example the below could be written `linelist %$% table(outcome, useNA = "always")`

``` r
table(linelist$outcome, useNA = "always")
```


      Death Recover    <NA> 
       2582    1983    1323 

Multiple columns can be cross-tabulated by listing them one after the other, separated by commas. Optionally, you can assign each column a “name” like `Outcome = linelist$outcome`.

``` r
age_by_outcome <- table(linelist$age_cat, linelist$outcome, useNA = "always") # save table as object
age_by_outcome   # print table
```

           
            Death Recover <NA>
      0-4     471     364  260
      5-9     476     391  228
      10-14   438     303  200
      15-19   323     251  169
      20-29   477     367  229
      30-49   329     238  187
      50-69    33      38   24
      70+       3       3    0
      <NA>     32      28   26

### Proportions

To return proportions, passing the above table to the function `prop.table()`. Use the `margins =` argument to specify whether you want the proportions to be of rows (1), of columns (2), or of the whole table (3). For clarity, we pipe the table to the `round()` function from **base** R, specifying 2 digits.

``` r
# get proportions of table defined above, by rows, rounded
prop.table(age_by_outcome, 1) %>% round(2)
```

           
            Death Recover <NA>
      0-4    0.43    0.33 0.24
      5-9    0.43    0.36 0.21
      10-14  0.47    0.32 0.21
      15-19  0.43    0.34 0.23
      20-29  0.44    0.34 0.21
      30-49  0.44    0.32 0.25
      50-69  0.35    0.40 0.25
      70+    0.50    0.50 0.00
      <NA>   0.37    0.33 0.30

### Totals

To add row and column totals, pass the table to `addmargins()`. This works for both counts and proportions.

``` r
addmargins(age_by_outcome)
```

           
            Death Recover <NA>  Sum
      0-4     471     364  260 1095
      5-9     476     391  228 1095
      10-14   438     303  200  941
      15-19   323     251  169  743
      20-29   477     367  229 1073
      30-49   329     238  187  754
      50-69    33      38   24   95
      70+       3       3    0    6
      <NA>     32      28   26   86
      Sum    2582    1983 1323 5888

### Convert to data frame

Converting a `table()` object directly to a data frame is not straight-forward. One approach is demonstrated below:

1.  Create the table, *without using* `useNA = "always"`. Instead convert `NA` values to “(Missing)” with `fct_explicit_na()` from **forcats**.  
2.  Add totals (optional) by piping to `addmargins()`  
3.  Pipe to the **base** R function `as.data.frame.matrix()`  
4.  Pipe the table to the **tibble** function `rownames_to_column()`, specifying the name for the first column  
5.  Print, View, or export as desired. In this example we use `flextable()` from package **flextable** as described in the [Tables for presentation](tables_presentation.llms.md) page. This will print to the RStudio viewer pane as a pretty HTML image.

``` r
table(fct_na_value_to_level(linelist$age_cat, level = "(Missing)"), fct_na_value_to_level(linelist$outcome, level = "(Missing)")) %>% 
  addmargins() %>% 
  as.data.frame.matrix() %>% 
  tibble::rownames_to_column(var = "Age Category") %>% 
  flextable::flextable()
```

| Age Category | Death | Recover | (Missing) | Sum   |
|--------------|-------|---------|-----------|-------|
| 0-4          | 471   | 364     | 260       | 1,095 |
| 5-9          | 476   | 391     | 228       | 1,095 |
| 10-14        | 438   | 303     | 200       | 941   |
| 15-19        | 323   | 251     | 169       | 743   |
| 20-29        | 477   | 367     | 229       | 1,073 |
| 30-49        | 329   | 238     | 187       | 754   |
| 50-69        | 33    | 38      | 24        | 95    |
| 70+          | 3     | 3       | 0         | 6     |
| (Missing)    | 32    | 28      | 26        | 86    |
| Sum          | 2,582 | 1,983   | 1,323     | 5,888 |

## 17.7 Resources

Much of the information in this page is adapted from these resources and vignettes online:

[gtsummary](http://www.danieldsjoberg.com/gtsummary/articles/tbl_summary.html)

[dplyr](https://dplyr.tidyverse.org/articles/grouping.html)
