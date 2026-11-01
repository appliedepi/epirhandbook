# 13  Grouping data

[![](../../images/grouping_1500x500.png)](../../images/grouping_1500x500.png)

This page covers how to group and aggregate data for descriptive analysis. It makes use of the **tidyverse** family of packages for common and easy-to-use functions.

Grouping data is a core component of data management and analysis. Grouped data statistically summarised by group, and can be plotted by group. Functions from the **dplyr** package (part of the **tidyverse**) make grouping and subsequent operations quite easy.

This page will address the following topics:

- Group data with the `group_by()` function  
- Un-group data  
- `summarise()` grouped data with statistics  
- The difference between `count()` and `tally()`  
- `arrange()` applied to grouped data  
- `filter()` applied to grouped data  
- `mutate()` applied to grouped data  
- `select()` applied to grouped data  
- The **base** R `aggregate()` command as an alternative

## 13.1 Preparation

### Load packages

This code chunk shows the loading of packages required for the analyses. In this handbook we emphasize `p_load()` from **pacman**, which installs the package if necessary *and* loads it for use. You can also load installed packages with `library()` from **base** R. See the page on [R basics](basics.llms.md) for more information on R packages.

``` r
pacman::p_load(
  rio,       # to import data
  here,      # to locate files
  tidyverse, # to clean, handle, and plot the data (includes dplyr)
  janitor,   # adding total rows and columns
  appliedepidata) # example datasets used in this handbook
```

### Import data

We import the dataset of cases from a simulated Ebola epidemic. Load it directly with `appliedepidata::get_data(name = "linelist_cleaned_rds")` (see the [Download handbook and data](download.llms.md) page for details).

``` r
linelist <- appliedepidata::get_data(name = "linelist_cleaned_rds")
```

The first 50 rows of `linelist`:

## 13.2 Grouping

The function `group_by()` from **dplyr** groups the rows by the unique values in the column specified to it. If multiple columns are specified, rows are grouped by the unique combinations of values across the columns. Each unique value (or combination of values) constitutes a group. Subsequent changes to the dataset or calculations can then be performed within the context of each group.

For example, the command below takes the `linelist` and groups the rows by unique values in the column `outcome`, saving the output as a new data frame `ll_by_outcome`. The grouping column(s) are placed inside the parentheses of the function `group_by()`.

``` r
ll_by_outcome <- linelist %>% 
  group_by(outcome)
```

**Note that there is no perceptible change to the dataset** after running `group_by()`, *until* another **dplyr** verb such as `mutate()`, `summarise()`, or `arrange()` is applied on the “grouped” data frame.

You can however “see” the groupings by printing the data frame. When you print a grouped data frame, you will see it has been transformed into a [`tibble` class object](https://tibble.tidyverse.org/) which, when printed, displays which groupings have been applied and how many groups there are - written just above the header row.

``` r
# print to see which groups are active
ll_by_outcome
```

    # A tibble: 5,888 × 30
    # Groups:   outcome [3]
       case_id generation date_infection date_onset date_hospitalisation
       <chr>        <dbl> <date>         <date>     <date>              
     1 5fe599           4 2014-05-08     2014-05-13 2014-05-15          
     2 8689b7           4 NA             2014-05-13 2014-05-14          
     3 11f8ea           2 NA             2014-05-16 2014-05-18          
     4 b8812a           3 2014-05-04     2014-05-18 2014-05-20          
     5 893f25           3 2014-05-18     2014-05-21 2014-05-22          
     6 be99c8           3 2014-05-03     2014-05-22 2014-05-23          
     7 07e3e8           4 2014-05-22     2014-05-27 2014-05-29          
     8 369449           4 2014-05-28     2014-06-02 2014-06-03          
     9 f393b4           4 NA             2014-06-05 2014-06-06          
    10 1389ca           4 NA             2014-06-05 2014-06-07          
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_outcome <date>, outcome <chr>, gender <chr>,
    #   age <dbl>, age_unit <chr>, age_years <dbl>, age_cat <fct>, age_cat5 <fct>,
    #   hospital <chr>, lon <dbl>, lat <dbl>, infector <chr>, source <chr>,
    #   wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>, chills <chr>,
    #   cough <chr>, aches <chr>, vomit <chr>, temp <dbl>, time_admission <chr>,
    #   bmi <dbl>, days_onset_hosp <dbl>

### Unique groups

**The groups created reflect each unique combination of values across the grouping columns.**

To see the groups *and the number of rows in each group*, pass the grouped data to `tally()`. To see just the unique groups without counts you can pass to `group_keys()`.

See below that there are **three** unique values in the grouping column `outcome`: “Death”, “Recover”, and `NA`. See that there were `nrow(linelist %>% filter(outcome == "Death"))` deaths, `nrow(linelist %>% filter(outcome == "Recover"))` recoveries, and `nrow(linelist %>% filter(is.na(outcome)))` with no outcome recorded.

``` r
linelist %>% 
  group_by(outcome) %>% 
  tally()
```

    # A tibble: 3 × 2
      outcome     n
      <chr>   <int>
    1 Death    2582
    2 Recover  1983
    3 <NA>     1323

You can group by more than one column. Below, the data frame is grouped by `outcome` and `gender`, and then tallied. Note how each unique combination of `outcome` and `gender` is registered as its own group - including missing values for either column.

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally()
```

    # A tibble: 9 × 3
    # Groups:   outcome [3]
      outcome gender     n
      <chr>   <chr>  <int>
    1 Death   f       1227
    2 Death   m       1228
    3 Death   <NA>     127
    4 Recover f        953
    5 Recover m        950
    6 Recover <NA>      80
    7 <NA>    f        627
    8 <NA>    m        625
    9 <NA>    <NA>      71

### New columns

You can also create a new grouping column *within* the `group_by()` statement. This is equivalent to calling `mutate()` before the `group_by()`. For a quick tabulation this style can be handy, but for more clarity in your code consider creating this column in its own `mutate()` step and then piping to `group_by()`.

``` r
# group dat based on a binary column created *within* the group_by() command
linelist %>% 
  group_by(
    age_class = ifelse(age >= 18, "adult", "child")) %>% 
  tally(sort = T)
```

    # A tibble: 3 × 2
      age_class     n
      <chr>     <int>
    1 child      3618
    2 adult      2184
    3 <NA>         86

### Add/drop grouping columns

By default, if you run `group_by()` on data that are already grouped, the old groups will be removed and the new one(s) will apply. If you want to add new groups to the existing ones, include the argument `.add = TRUE`.

``` r
# Grouped by outcome
by_outcome <- linelist %>% 
  group_by(outcome)

# Add grouping by gender in addition
by_outcome_gender <- by_outcome %>% 
  group_by(gender, .add = TRUE)
```

\*\* Keep all groups\*\*

If you group on a column of class factor there may be levels of the factor that are not currently present in the data. If you group on this column, by default those non-present levels are dropped and not included as groups. To change this so that all levels appear as groups (even if not present in the data), set `.drop = FALSE` in your `group_by()` command.

## 13.3 Un-group

Data that have been grouped will remain grouped until specifically ungrouped via `ungroup()`. If you forget to ungroup, it can lead to incorrect calculations! Below is an example of removing all groupings:

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally() %>% 
  ungroup()
```

You can also remove grouping for only specific columns, by placing the column name inside `ungroup()`.

``` r
linelist %>% 
  group_by(outcome, gender) %>% 
  tally() %>% 
  ungroup(gender) # remove the grouping by gender, leave grouping by outcome
```

***NOTE:*** The verb `count()` automatically ungroups the data after counting.

## 13.4 Summarise

See the **dplyr** section of the [Descriptive tables](tables_descriptive.llms.md) page for a detailed description of how to produce summary tables with `summarise()`. Here we briefly address how its behavior changes when applied to grouped data.

The **dplyr** function `summarise()` (or `summarize()`) takes a data frame and converts it into a *new* summary data frame, with columns containing summary statistics that you define. On an ungrouped data frame, the summary statistics will be calculated from all rows. Applying `summarise()` to grouped data produces those summary statistics *for each group*.

The syntax of `summarise()` is such that you provide the name(s) of the **new** summary column(s), an equals sign, and then a statistical function to apply to the data, as shown below. For example, `min()`, `max()`, `median()`, or `sd()`. Within the statistical function, list the column to be operated on and any relevant argument (e.g. `na.rm = TRUE`). You can use `sum()` to count the number of rows that meet a logical criteria (with double equals `==`).

Below is an example of `summarise()` applied *without grouped data*. The statistics returned are produced from the entire dataset.

``` r
# summary statistics on ungrouped linelist
linelist %>% 
  summarise(
    n_cases  = n(),
    mean_age = mean(age_years, na.rm=T),
    max_age  = max(age_years, na.rm=T),
    min_age  = min(age_years, na.rm=T),
    n_males  = sum(gender == "m", na.rm=T))
```

      n_cases mean_age max_age min_age n_males
    1    5888 16.01831      84       0    2803

In contrast, below is the same `summarise()` statement applied to grouped data. The statistics are calculated for each `outcome` group. Note how grouping columns will carry over into the new data frame.

``` r
# summary statistics on grouped linelist
linelist %>% 
  group_by(outcome) %>% 
  summarise(
    n_cases  = n(),
    mean_age = mean(age_years, na.rm=T),
    max_age  = max(age_years, na.rm=T),
    min_age  = min(age_years, na.rm=T),
    n_males    = sum(gender == "m", na.rm=T))
```

    # A tibble: 3 × 6
      outcome n_cases mean_age max_age min_age n_males
      <chr>     <int>    <dbl>   <dbl>   <dbl>   <int>
    1 Death      2582     15.9      76       0    1228
    2 Recover    1983     16.1      84       0     950
    3 <NA>       1323     16.2      69       0     625

***TIP:*** The summarise function works with both UK and US spelling - `summarise()` and `summarize()` call the same function.

## 13.5 Counts and tallies

`count()` and `tally()` provide similar functionality but are different. Read more about the distinction between `tally()` and `count()` [here](https://dplyr.tidyverse.org/reference/tally.html)

### `tally()`

`tally()` is shorthand for `summarise(n = n())`, and *does not* group data. Thus, to achieve grouped tallys it must follow a `group_by()` command. You can add `sort = TRUE` to see the largest groups first.

``` r
linelist %>% 
  tally()
```

         n
    1 5888

``` r
linelist %>% 
  group_by(outcome) %>% 
  tally(sort = TRUE)
```

    # A tibble: 3 × 2
      outcome     n
      <chr>   <int>
    1 Death    2582
    2 Recover  1983
    3 <NA>     1323

### `count()`

In contrast, `count()` does the following:

1.  applies `group_by()` on the specified column(s)  
2.  applies `summarise()` and returns column `n` with the number of rows per group  
3.  applies `ungroup()`

``` r
linelist %>% 
  count(outcome)
```

      outcome    n
    1   Death 2582
    2 Recover 1983
    3    <NA> 1323

Just like with `group_by()` you can create a new column within the `count()` command:

``` r
linelist %>% 
  count(age_class = ifelse(age >= 18, "adult", "child"), sort = T)
```

      age_class    n
    1     child 3618
    2     adult 2184
    3      <NA>   86

`count()` can be called multiple times, with the functionality “rolling up”. For example, to summarise the number of hospitals present for each gender, run the following. Note, the name of the final column is changed from default “n” for clarity (with `name =`).

``` r
linelist %>% 
  # produce counts by unique outcome-gender groups
  count(gender, hospital) %>% 
  # gather rows by gender (3) and count number of hospitals per gender (6)
  count(gender, name = "hospitals per gender" ) 
```

      gender hospitals per gender
    1      f                    6
    2      m                    6
    3   <NA>                    6

### Add counts

In contrast to `count()` and `summarise()`, you can use `add_count()` to *add* a new column `n` with the counts of rows per group *while retaining all the other data frame columns*.

This means that a group’s count number, in the new column `n`, will be printed in each row of the group. For demonstration purposes, we add this column and then re-arrange the columns for easier viewing. See the section below on [filter on group size](#group_filter_grp_size) for another example.

``` r
linelist %>% 
  as_tibble() %>%                   # convert to tibble for nicer printing 
  add_count(hospital) %>%           # add column n with counts by hospital
  select(hospital, n, everything()) # re-arrange for demo purposes
```

    # A tibble: 5,888 × 31
       hospital                       n case_id generation date_infection date_onset
       <chr>                      <int> <chr>        <dbl> <date>         <date>    
     1 Other                        885 5fe599           4 2014-05-08     2014-05-13
     2 Missing                     1469 8689b7           4 NA             2014-05-13
     3 St. Mark's Maternity Hosp…   422 11f8ea           2 NA             2014-05-16
     4 Port Hospital               1762 b8812a           3 2014-05-04     2014-05-18
     5 Military Hospital            896 893f25           3 2014-05-18     2014-05-21
     6 Port Hospital               1762 be99c8           3 2014-05-03     2014-05-22
     7 Missing                     1469 07e3e8           4 2014-05-22     2014-05-27
     8 Missing                     1469 369449           4 2014-05-28     2014-06-02
     9 Missing                     1469 f393b4           4 NA             2014-06-05
    10 Missing                     1469 1389ca           4 NA             2014-06-05
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_hospitalisation <date>, date_outcome <date>,
    #   outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>, age_years <dbl>,
    #   age_cat <fct>, age_cat5 <fct>, lon <dbl>, lat <dbl>, infector <chr>,
    #   source <chr>, wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>,
    #   chills <chr>, cough <chr>, aches <chr>, vomit <chr>, temp <dbl>,
    #   time_admission <chr>, bmi <dbl>, days_onset_hosp <dbl>

### Add totals

To easily add total *sum* rows or columns after using `tally()` or `count()`, see the **janitor** section of the [Descriptive tables](tables_descriptive.llms.md#tbl_janitor) page. This package offers functions like `adorn_totals()` and `adorn_percentages()` to add totals and convert to show percentages. Below is a brief example:

``` r
linelist %>%                                  # case linelist
  tabyl(age_cat, gender) %>%                  # cross-tabulate counts of two columns
  adorn_totals(where = "row") %>%             # add a total row
  adorn_percentages(denominator = "col") %>%  # convert to proportions with column denominator
  adorn_pct_formatting() %>%                  # convert proportions to percents
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

To add more complex totals rows that involve summary statistics other than *sums*, see [this section of the Descriptive Tables page](tables_descriptive.llms.md#tbl_dplyr_totals).

## 13.6 Grouping by date

When grouping data by date, you must have (or create) a column for the date unit of interest - for example “day”, “epiweek”, “month”, etc. You can make this column using `floor_date()` from **lubridate**, as explained in the [Epidemiological weeks section](dates.llms.md#dates_epi_wks) of the [Working with dates](dates.llms.md) page. Once you have this column, you can use `count()` from **dplyr** to group the rows by those unique date values and achieve aggregate counts.

One additional step common for date situations, is to “fill-in” any dates in the sequence that are not present in the data. Use `complete()` from **tidyr** so that the aggregated date series is *complete* including *all possible date units* within the range. Without this step, a week with no cases reported might not appear in your data!

Within `complete()` you *re-define* your date column as a *sequence* of dates `seq.Date()` from the minimum to the maximum - thus the dates are expanded. By default, the case count values in any new “expanded” rows will be `NA`. You can set them to 0 using the `fill =` argument of `complete()`, which expects a named list (if your counts column is named `n`, provide `fill = list(n = 0)`. See `?complete` for details and the [Working with dates](dates.llms.md#dates_epi_wks) page for an example.

### Linelist cases into days

Here is an example of grouping cases into days *without* using `complete()`. Note the first rows skip over dates with no cases.

``` r
daily_counts <- linelist %>% 
  drop_na(date_onset) %>%        # remove that were missing date_onset
  count(date_onset)              # count number of rows per unique date
```

Below we add the `complete()` command to ensure every day in the range is represented.

``` r
daily_counts <- linelist %>% 
  drop_na(date_onset) %>%                 # remove case missing date_onset
  count(date_onset) %>%                   # count number of rows per unique date
  complete(                               # ensure all days appear even if no cases
    date_onset = seq.Date(                # re-define date colume as daily sequence of dates
      from = min(date_onset, na.rm=T), 
      to = max(date_onset, na.rm=T),
      by = "day"),
    fill = list(n = 0))                   # set new filled-in rows to display 0 in column n (not NA as default) 
```

### Linelist cases into weeks

The same principle can be applied for weeks. First create a new column that is the week of the case using `floor_date()` with `unit = "week"`. Then, use `count()` as above to achieve weekly case counts. Finish with `complete()` to ensure that all weeks are represented, even if they contain no cases.

``` r
# Make dataset of weekly case counts
weekly_counts <- linelist %>% 
  drop_na(date_onset) %>%                 # remove cases missing date_onset
  mutate(week = lubridate::floor_date(date_onset, unit = "week")) %>%  # new column of week of onset
  count(week) %>%                         # group data by week and count rows per group
  complete(                               # ensure all days appear even if no cases
    week = seq.Date(                      # re-define date colume as daily sequence of dates
      from = min(week, na.rm=T), 
      to = max(week, na.rm=T),
      by = "week"),
    fill = list(n = 0))                   # set new filled-in rows to display 0 in column n (not NA as default) 
```

Here are the first 50 rows of the resulting data frame:

### Linelist cases into months

To aggregate cases into months, again use `floor_date()` from the **lubridate** package, but with the argument `unit = "months"`. This rounds each date down to the 1st of its month. The output will be class Date. Note that in the `complete()` step we also use `by = "month"`.

``` r
# Make dataset of monthly case counts
monthly_counts <- linelist %>% 
  drop_na(date_onset) %>% 
  mutate(month = lubridate::floor_date(date_onset, unit = "months")) %>%  # new column, 1st of month of onset
  count(month) %>%                          # count cases by month
  complete(
    month = seq.Date(
      min(month, na.rm=T),     # include all months with no cases reported
      max(month, na.rm=T),
      by="month"),
    fill = list(n = 0))
```

### Daily counts into weeks

To aggregate daily counts into weekly counts, use `floor_date()` as above. However, use `group_by()` and `summarize()` instead of `count()` because you need to `sum()` daily case counts instead of just counting the number of rows per week.

#### Daily counts into months

To aggregate daily counts into months counts, use `floor_date()` with `unit = "month"` as above. However, use `group_by()` and `summarize()` instead of `count()` because you need to `sum()` daily case counts instead of just counting the number of rows per month.

## 13.7 Arranging grouped data

Using the **dplyr** verb `arrange()` to order the rows in a data frame behaves the same when the data are grouped, *unless* you set the argument `.by_group =TRUE`. In this case the rows are ordered first by the grouping columns and then by any other columns you specify to `arrange()`.

## 13.8 Filter on grouped data

### `filter()`

When applied in conjunction with functions that evaluate the data frame (like `max()`, `min()`, `mean()`), these functions will now be applied to the groups. For example, if you want to filter and keep rows where patients are above the median age, this will now apply per group - filtering to keep rows above the *group’s* median age.

### Slice rows per group

The **dplyr** function `slice()`, which [filters rows based on their position](https://dplyr.tidyverse.org/reference/slice.html) in the data, can also be applied per group. Remember to account for sorting the data within each group to get the desired “slice”.

For example, to retrieve only the latest 5 admissions from each hospital:

1.  Group the linelist by column `hospital`  
2.  Arrange the records from latest to earliest `date_hospitalisation` *within each hospital group*  
3.  Slice to retrieve the first 5 rows from each hospital

``` r
linelist %>%
  group_by(hospital) %>%
  arrange(hospital, date_hospitalisation) %>%
  slice_head(n = 5) %>% 
  arrange(hospital) %>%                            # for display
  select(case_id, hospital, date_hospitalisation)  # for display
```

    # A tibble: 30 × 3
    # Groups:   hospital [6]
       case_id hospital          date_hospitalisation
       <chr>   <chr>             <date>              
     1 20b688  Central Hospital  2014-05-06          
     2 d58402  Central Hospital  2014-05-10          
     3 b8f2fd  Central Hospital  2014-05-13          
     4 acf422  Central Hospital  2014-05-28          
     5 275cc7  Central Hospital  2014-05-28          
     6 d1fafd  Military Hospital 2014-04-17          
     7 974bc1  Military Hospital 2014-05-13          
     8 6a9004  Military Hospital 2014-05-13          
     9 09e386  Military Hospital 2014-05-14          
    10 865581  Military Hospital 2014-05-15          
    # ℹ 20 more rows

`slice_head()` - selects n rows from the top  
`slice_tail()` - selects n rows from the end  
`slice_sample()` - randomly selects n rows  
`slice_min()` - selects n rows with highest values in `order_by =` column, use `with_ties = TRUE` to keep ties  
`slice_max()` - selects n rows with lowest values in `order_by =` column, use `with_ties = TRUE` to keep ties

See the [De-duplication](deduplication.llms.md) page for more examples and detail on `slice()`.

### Filter on group size

The function `add_count()` adds a column `n` to the original data giving the number of rows in that row’s group.

Shown below, `add_count()` is applied to the column `hospital`, so the values in the new column `n` reflect the number of rows in that row’s hospital group. Note how values in column `n` are repeated. In the example below, the column name `n` could be changed using `name =` within `add_count()`. For demonstration purposes we re-arrange the columns with `select()`.

``` r
linelist %>% 
  as_tibble() %>% 
  add_count(hospital) %>%          # add "number of rows admitted to same hospital as this row" 
  select(hospital, n, everything())
```

    # A tibble: 5,888 × 31
       hospital                       n case_id generation date_infection date_onset
       <chr>                      <int> <chr>        <dbl> <date>         <date>    
     1 Other                        885 5fe599           4 2014-05-08     2014-05-13
     2 Missing                     1469 8689b7           4 NA             2014-05-13
     3 St. Mark's Maternity Hosp…   422 11f8ea           2 NA             2014-05-16
     4 Port Hospital               1762 b8812a           3 2014-05-04     2014-05-18
     5 Military Hospital            896 893f25           3 2014-05-18     2014-05-21
     6 Port Hospital               1762 be99c8           3 2014-05-03     2014-05-22
     7 Missing                     1469 07e3e8           4 2014-05-22     2014-05-27
     8 Missing                     1469 369449           4 2014-05-28     2014-06-02
     9 Missing                     1469 f393b4           4 NA             2014-06-05
    10 Missing                     1469 1389ca           4 NA             2014-06-05
    # ℹ 5,878 more rows
    # ℹ 25 more variables: date_hospitalisation <date>, date_outcome <date>,
    #   outcome <chr>, gender <chr>, age <dbl>, age_unit <chr>, age_years <dbl>,
    #   age_cat <fct>, age_cat5 <fct>, lon <dbl>, lat <dbl>, infector <chr>,
    #   source <chr>, wt_kg <dbl>, ht_cm <dbl>, ct_blood <dbl>, fever <chr>,
    #   chills <chr>, cough <chr>, aches <chr>, vomit <chr>, temp <dbl>,
    #   time_admission <chr>, bmi <dbl>, days_onset_hosp <dbl>

It then becomes easy to filter for case rows who were hospitalized at a “small” hospital, say, a hospital that admitted fewer than 500 patients:

``` r
linelist %>% 
  add_count(hospital) %>% 
  filter(n < 500)
```

## 13.9 Mutate on grouped data

To retain all columns and rows (not summarise) and *add a new column containing group statistics*, use `mutate()` after `group_by()` instead of `summarise()`.

This is useful if you want group statistics in the original dataset *with all other columns present* - e.g. for calculations that compare one row to its group.

For example, this code below calculates the difference between a row’s delay-to-admission and the mean delay for their hospital. The steps are:

1.  Group the data by hospital  
2.  Use the column `days_onset_hosp` (delay to hospitalisation) to create a new column containing the mean delay at the hospital of *that row*  
3.  Calculate the difference between the two columns

We `select()` only certain columns to display, for demonstration purposes.

``` r
linelist %>% 
  # group data by hospital (no change to linelist yet)
  group_by(hospital) %>% 
  
  # new columns
  mutate(
    # mean days to admission per hospital (rounded to 1 decimal)
    group_delay_admit = round(mean(days_onset_hosp, na.rm=T), 1),
    
    # difference between row's delay and mean delay at their hospital (rounded to 1 decimal)
    diff_to_group     = round(days_onset_hosp - group_delay_admit, 1)) %>%
  
  # select certain rows only - for demonstration/viewing purposes
  select(case_id, hospital, days_onset_hosp, group_delay_admit, diff_to_group)
```

    # A tibble: 5,888 × 5
    # Groups:   hospital [6]
       case_id hospital              days_onset_hosp group_delay_admit diff_to_group
       <chr>   <chr>                           <dbl>             <dbl>         <dbl>
     1 5fe599  Other                               2               2             0  
     2 8689b7  Missing                             1               2.1          -1.1
     3 11f8ea  St. Mark's Maternity…               2               2.1          -0.1
     4 b8812a  Port Hospital                       2               2.1          -0.1
     5 893f25  Military Hospital                   1               2.1          -1.1
     6 be99c8  Port Hospital                       1               2.1          -1.1
     7 07e3e8  Missing                             2               2.1          -0.1
     8 369449  Missing                             1               2.1          -1.1
     9 f393b4  Missing                             1               2.1          -1.1
    10 1389ca  Missing                             2               2.1          -0.1
    # ℹ 5,878 more rows

## 13.10 Select on grouped data

The verb `select()` works on grouped data, but the grouping columns are always included (even if not mentioned in `select()`). If you do not want these grouping columns, use `ungroup()` first.

## 13.11 Resources

Here are some useful resources for more information:

You can perform any summary function on grouped data; see the [RStudio data transformation cheat sheet](https://github.com/rstudio/cheatsheets/blob/master/data-transformation.pdf)

The Data Carpentry page on [**dplyr**](https://datacarpentry.org/R-genomics/04-dplyr.html)  
The **tidyverse** reference pages on [group_by()](https://dplyr.tidyverse.org/reference/group_by.html) and [grouping](https://dplyr.tidyverse.org/articles/grouping.html)

This page on [Data manipulation](https://itsalocke.com/files/DataManipulationinR.pdf)

[Summarize with conditions in dplyr](https://stackoverflow.com/questions/23528862/summarize-with-conditions-in-dplyr)
