# 15  De-duplication

[![](../../images/deduplication.png)](../../images/deduplication.png)

This page covers the following de-duplication techniques:

1.  Identifying and removing duplicate rows  
2.  “Slicing” rows to keep only certain rows (e.g. min or max) from each group of rows  
3.  “Rolling-up”, or combining values from multiple rows into one row

## 15.1 Preparation

### Load packages

This code chunk shows the loading of packages required for the analyses. In this handbook we emphasize `p_load()` from **pacman**, which installs the package if necessary *and* loads it for use. You can also load installed packages with `library()` from **base** R. See the page on [R basics](basics.llms.md) for more information on R packages.

``` r
pacman::p_load(
  tidyverse,   # deduplication, grouping, and slicing functions
  janitor,     # function for reviewing duplicates
  stringr)      # for string searches, can be used in "rolling-up" values
```

### Import data

For demonstration, we will use an example dataset that is created with the R code below.

The data are records of COVID-19 phone encounters, including encounters with contacts and with cases. The columns include `recordID` (computer-generated), `personID`, `name`, `date` of encounter, `time` of encounter, the `purpose` of the encounter (either to interview as a case or as a contact), and `symptoms_ever` (whether the person in that encounter reported *ever* having symptoms).

Here is the code to create the `obs` dataset:

``` r
obs <- data.frame(
  recordID  = c(1,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18),
  personID  = c(1,1,2,2,3,2,4,5,6,7,2,1,3,3,4,5,5,7,8),
  name      = c("adam", "adam", "amrish", "amrish", "mariah", "amrish", "nikhil", "brian", "smita", "raquel", "amrish",
                "adam", "mariah", "mariah", "nikhil", "brian", "brian", "raquel", "natalie"),
  date      = c("1/1/2020", "1/1/2020", "2/1/2020", "2/1/2020", "5/1/2020", "5/1/2020", "5/1/2020", "5/1/2020", "5/1/2020","5/1/2020", "2/1/2020",
                "5/1/2020", "6/1/2020", "6/1/2020", "6/1/2020", "6/1/2020", "7/1/2020", "7/1/2020", "7/1/2020"),
  time      = c("09:00", "09:00", "14:20", "14:20", "12:00", "16:10", "13:01", "15:20", "14:20", "12:30", "10:24",
                "09:40", "07:25", "08:32", "15:36", "15:31", "07:59", "11:13", "17:12"),
  encounter = c(1,1,1,1,1,3,1,1,1,1,2,
                2,2,3,2,2,3,2,1),
  purpose   = c("contact", "contact", "contact", "contact", "case", "case", "contact", "contact", "contact", "contact", "contact",
                "case", "contact", "contact", "contact", "contact", "case", "contact", "case"),
  symptoms_ever = c(NA, NA, "No", "No", "No", "Yes", "Yes", "No", "Yes", NA, "Yes",
                    "No", "No", "No", "Yes", "Yes", "No","No", "No")) %>% 
  mutate(date = as.Date(date, format = "%d/%m/%Y"))
```

#### Here is the data frame

Use the filter boxes along the top to review the encounters for each person.

A few things to note as you review the data:

- The first two records are 100% complete duplicates including duplicate `recordID` (must be a computer glitch!)  
- The second two rows are duplicates, in all columns *except for `recordID`*  
- Several people had multiple phone encounters, at various dates and times, and as contacts and/or cases  
- At each encounter, the person was asked if they had **ever** had symptoms, and some of this information is missing.

And here is a quick summary of the people and the purposes of their encounters, using `tabyl()` from **janitor**:

``` r
obs %>% 
  tabyl(name, purpose)
```

        name case contact
        adam    1       2
      amrish    1       3
       brian    1       2
      mariah    1       2
     natalie    1       0
      nikhil    0       2
      raquel    0       2
       smita    0       1

## 15.2 Deduplication

This section describes how to review and remove duplicate rows in a data frame. It also show how to handle duplicate elements in a vector.

### Examine duplicate rows

To quickly review rows that have duplicates, you can use `get_dupes()` from the **janitor** package. *By default*, all columns are considered when duplicates are evaluated - rows returned by the function are 100% duplicates considering the values in *all* columns.

In the `obs` data frame, the first two rows are *100% duplicates* - they have the same value in every column (including the `recordID` column, which is *supposed* to be unique - it must be some computer glitch). The returned data frame automatically includes a new column `dupe_count` on the right side, showing the number of rows with that combination of duplicate values.

``` r
# 100% duplicates across all columns
obs %>% 
  janitor::get_dupes()
```

See the [original data](#dedup_data)

However, if we choose to ignore `recordID`, the 3rd and 4th rows rows are also duplicates of each other. That is, they have the same values in all columns *except* for `recordID`. You can specify specific columns to be ignored in the function using a `-` minus symbol.

``` r
# Duplicates when column recordID is not considered
obs %>% 
  janitor::get_dupes(-recordID)         # if multiple columns, wrap them in c()
```

You can also positively specify the columns to consider. Below, only rows that have the same values in the `name` and `purpose` columns are returned. Notice how “amrish” now has `dupe_count` equal to 3 to reflect his three “contact” encounters.

\*Scroll left for more rows\*\*

``` r
# duplicates based on name and purpose columns ONLY
obs %>% 
  janitor::get_dupes(name, purpose)
```

See the [original data](#dedup_data).

See `?get_dupes` for more details, or see this [online reference](https://cran.r-project.org/web/packages/janitor/vignettes/janitor.html#explore-records-with-duplicated-values-for-specific-combinations-of-variables-with-get_dupes)

### Keep only unique rows

To keep only unique rows of a data frame, use `distinct()` from **dplyr** (as demonstrated in the [Cleaning data and core functions](cleaning.llms.md) page). Rows that are duplicates are removed such that only the first of such rows is kept. By default, “first” means the highest `rownumber` (order of rows top-to-bottom). Only unique rows remain.

In the example below, we run `distinct()` such that the column `recordID` is excluded from consideration - thus **two duplicate rows are removed**. The first row (for “adam”) was 100% duplicated and has been removed. Also row 3 (for “amrish”) was a duplicate in every column *except* `recordID` (which is not being considered) and so is also removed. The `obs` dataset n is now `nrow(obs)-2`, not `nrow(obs)` rows).

*Scroll to the left to see the entire data frame*

``` r
# added to a chain of pipes (e.g. data cleaning)
obs %>% 
  distinct(across(-recordID), # reduces data frame to only unique rows (keeps first one of any duplicates)
           .keep_all = TRUE) 

# if outside pipes, include the data as first argument 
# distinct(obs)
```

***CAUTION:*** If using `distinct()` on grouped data, the function will apply to each group.

**Deduplicate based on specific columns**

You can also specify columns to be the basis for de-duplication. In this way, the de-duplication only applies to rows that are duplicates within the specified columns. Unless you set `.keep_all = TRUE`, all columns not mentioned will be dropped.

In the example below, the de-duplication only applies to rows that have identical values for `name` and `purpose` columns. Thus, “brian” has only 2 rows instead of 3 - his *first* “contact” encounter and his only “case” encounter. To adjust so that brian’s *latest* encounter of each purpose is kept, see the tab on Slicing within groups.

*Scroll to the left to see the entire data frame*

``` r
# added to a chain of pipes (e.g. data cleaning)
obs %>% 
  distinct(name, purpose, .keep_all = TRUE) %>%  # keep rows unique by name and purpose, retain all columns
  arrange(name)                                  # arrange for easier viewing
```

See the [original data](#dedup_data).

### Deduplicate elements in a vector

The function `duplicated()` from **base** R will evaluate a vector (column) and return a logical vector of the same length (TRUE/FALSE). The first time a value appears, it will return FALSE (not a duplicate), and subsequent times that value appears it will return TRUE. Note how `NA` is treated the same as any other value.

``` r
x <- c(1, 1, 2, NA, NA, 4, 5, 4, 4, 1, 2)
duplicated(x)
```

     [1] FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE

To return only the duplicated elements, you can use brackets to subset the original vector:

``` r
x[duplicated(x)]
```

    [1]  1 NA  4  4  1  2

To return only the unique elements, use `unique()` from **base** R. To remove `NA`s from the output, nest `na.omit()` within `unique()`.

``` r
unique(x)           # alternatively, use x[!duplicated(x)]
```

    [1]  1  2 NA  4  5

``` r
unique(na.omit(x))  # remove NAs 
```

    [1] 1 2 4 5

### Using **base** R

**To return duplicate rows**

In **base** R, you can also see which rows are 100% duplicates in a data frame `df` with the command `duplicated(df)` (returns a logical vector of the rows).

Thus, you can also use the base subset `[ ]` on the data frame to see the *duplicated* rows with `df[duplicated(df),]` (don’t forget the comma, meaning that you want to see all columns!).

**To return unique rows**

See the notes above. To see the *unique* rows you add the logical negator `!` in front of the `duplicated()` function:  
`df[!duplicated(df),]`

**To return rows that are duplicates of only certain columns**

Subset the `df` that is *within the `duplicated()` parentheses*, so this function will operate on only certain columns of the `df`.

To specify the columns, provide column numbers or names after a comma (remember, all this is *within* the `duplicated()` function).

Be sure to keep the comma `,` *outside* after the `duplicated()` function as well!

For example, to evaluate only columns 2 through 5 for duplicates: `df[!duplicated(df[, 2:5]),]`  
To evaluate only columns `name` and `purpose` for duplicates: `df[!duplicated(df[, c("name", "purpose)]),]`

## 15.3 Slicing

To “slice” a data frame to apply a filter on the rows by row number/position. This becomes particularly useful if you have multiple rows per functional group (e.g. per “person”) and you only want to keep one or some of them.

The basic `slice()` function accepts numbers and returns rows in those positions. If the numbers provided are positive, only they are returned. If negative, those rows are *not* returned. Numbers must be either all positive or all negative.

``` r
obs %>% slice(4)  # return the 4th row
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        3        2 amrish 2020-01-02 14:20         1 contact            No

``` r
obs %>% slice(c(2,4))  # return rows 2 and 4
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        1        1   adam 2020-01-01 09:00         1 contact          <NA>
    2        3        2 amrish 2020-01-02 14:20         1 contact            No

``` r
#obs %>% slice(c(2:4))  # return rows 2 through 4
```

See the [original data](#dedup_data).

There are several variations: These should be provided with a column and a number of rows to return (to `n =`).

- `slice_min()` and `slice_max()` keep only the row(s) with the minimium or maximum value(s) of the specified column. This also works to return the “min” and “max” of ordered factors.  
- `slice_head()` and `slice_tail()` - keep only the *first* or *last* row(s).  
- `slice_sample()` - keep only a random sample of the rows.

``` r
obs %>% slice_max(encounter, n = 1)  # return rows with the largest encounter number
```

      recordID personID   name       date  time encounter purpose symptoms_ever
    1        5        2 amrish 2020-01-05 16:10         3    case           Yes
    2       13        3 mariah 2020-01-06 08:32         3 contact            No
    3       16        5  brian 2020-01-07 07:59         3    case            No

Use arguments `n =` or `prop =` to specify the number or proportion of rows to keep. If not using the function in a pipe chain, provide the data argument first (e.g. `slice(data, n = 2)`). See `?slice` for more information.

Other arguments:

`.order_by =` used in `slice_min()` and `slice_max()` this is a column to order by before slicing.  
`with_ties =` TRUE by default, meaning ties are kept.  
`.preserve =` FALSE by default. If TRUE then the grouping structure is re-calculated after slicing.  
`weight_by =` Optional, numeric column to weight by (bigger number more likely to get sampled). Also `replace =` for whether sampling is done with/without replacement.

***TIP:*** When using `slice_max()` and `slice_min()`, be sure to specify/write the `n =` (e.g. `n = 2`, not just `2`). Otherwise you may get an error `Error:`…`is not empty.`

***NOTE:*** You may encounter the function [`top_n()`](https://dplyr.tidyverse.org/reference/top_n.html), which has been superseded by the `slice` functions.

### Slice with groups

The `slice_*()` functions can be very useful if applied to a grouped data frame because the slice operation is performed on each group separately. Use the **function** `group_by()` in conjunction with `slice()` to group the data to take a slice from each group.

This is helpful for de-duplication if you have multiple rows per person but only want to keep one of them. You first use `group_by()` with key columns that are the same per person, and then use a slice function on a column that will differ among the grouped rows.

In the example below, to keep only the *latest* encounter *per person*, we group the rows by `name` and then use `slice_max()` with `n = 1` on the `date` column. Be aware! To apply a function like `slice_max()` on dates, the date column must be class Date.

By default, “ties” (e.g. same date in this scenario) are kept, and we would still get multiple rows for some people (e.g. adam). To avoid this we set `with_ties = FALSE`. We get back only one row per person.

***CAUTION:*** If using `arrange()`, specify `.by_group = TRUE` to have the data arranged within each group.

***DANGER:*** If `with_ties = FALSE`, the first row of a tie is kept. This may be deceptive. See how for Mariah, she has two encounters on her latest date (6 Jan) and the first (earliest) one was kept. Likely, we want to keep her later encounter on that day. See how to “break” these ties in the next example.

``` r
obs %>% 
  group_by(name) %>%       # group the rows by 'name'
  slice_max(date,          # keep row per group with maximum date value 
            n = 1,         # keep only the single highest row 
            with_ties = F) # if there's a tie (of date), take the first row
```

Above, for example we can see that only Amrish’s row on 5 Jan was kept, and only Brian’s row on 7 Jan was kept. See the [original data](#dedup_data).

**Breaking “ties”**

Multiple slice statements can be run to “break ties”. In this case, if a person has multiple encounters on their latest *date*, the encounter with the latest *time* is kept (`lubridate::hm()` is used to convert the character times to a sortable time class).  
Note how now, the one row kept for “Mariah” on 6 Jan is encounter 3 from 08:32, not encounter 2 at 07:25.

``` r
# Example of multiple slice statements to "break ties"
obs %>%
  group_by(name) %>%
  
  # FIRST - slice by latest date
  slice_max(date, n = 1, with_ties = TRUE) %>% 
  
  # SECOND - if there is a tie, select row with latest time; ties prohibited
  slice_max(lubridate::hm(time), n = 1, with_ties = FALSE)
```

*In the example above, it would also have been possible to slice by `encounter` number, but we showed the slice on `date` and `time` for example purposes.*

***TIP:*** To use `slice_max()` or `slice_min()` on a “character” column, mutate it to an *ordered* factor class!

See the [original data](#dedup_data).

### Keep all but mark them

If you want to keep all records but mark only some for analysis, consider a two-step approach utilizing a unique recordID/encounter number:

1.  Reduce/slice the orginal data frame to only the rows for analysis. Save/retain this reduced data frame.  
2.  In the original data frame, mark rows as appropriate with `case_when()`, based on whether their record unique identifier (recordID in this example) is present in the reduced data frame.

``` r
# 1. Define data frame of rows to keep for analysis
obs_keep <- obs %>%
  group_by(name) %>%
  slice_max(encounter, n = 1, with_ties = FALSE) # keep only latest encounter per person


# 2. Mark original data frame
obs_marked <- obs %>%

  # make new dup_record column
  mutate(dup_record = case_when(
    
    # if record is in obs_keep data frame
    recordID %in% obs_keep$recordID ~ "For analysis", 
    
    # all else marked as "Ignore" for analysis purposes
    TRUE                            ~ "Ignore"))

# print
obs_marked
```

       recordID personID    name       date  time encounter purpose symptoms_ever
    1         1        1    adam 2020-01-01 09:00         1 contact          <NA>
    2         1        1    adam 2020-01-01 09:00         1 contact          <NA>
    3         2        2  amrish 2020-01-02 14:20         1 contact            No
    4         3        2  amrish 2020-01-02 14:20         1 contact            No
    5         4        3  mariah 2020-01-05 12:00         1    case            No
    6         5        2  amrish 2020-01-05 16:10         3    case           Yes
    7         6        4  nikhil 2020-01-05 13:01         1 contact           Yes
    8         7        5   brian 2020-01-05 15:20         1 contact            No
    9         8        6   smita 2020-01-05 14:20         1 contact           Yes
    10        9        7  raquel 2020-01-05 12:30         1 contact          <NA>
    11       10        2  amrish 2020-01-02 10:24         2 contact           Yes
    12       11        1    adam 2020-01-05 09:40         2    case            No
    13       12        3  mariah 2020-01-06 07:25         2 contact            No
    14       13        3  mariah 2020-01-06 08:32         3 contact            No
    15       14        4  nikhil 2020-01-06 15:36         2 contact           Yes
    16       15        5   brian 2020-01-06 15:31         2 contact           Yes
    17       16        5   brian 2020-01-07 07:59         3    case            No
    18       17        7  raquel 2020-01-07 11:13         2 contact            No
    19       18        8 natalie 2020-01-07 17:12         1    case            No
         dup_record
    1        Ignore
    2        Ignore
    3        Ignore
    4        Ignore
    5        Ignore
    6  For analysis
    7        Ignore
    8        Ignore
    9  For analysis
    10       Ignore
    11       Ignore
    12 For analysis
    13       Ignore
    14 For analysis
    15 For analysis
    16       Ignore
    17 For analysis
    18 For analysis
    19 For analysis

See the [original data](#dedup_data).

### Calculate row completeness

Create a column that contains a metric for the row’s completeness (non-missingness). This could be helpful when deciding which rows to prioritize over others when de-duplicating/slicing.

In this example, “key” columns over which you want to measure completeness are saved in a vector of column names.

Then the new column `key_completeness` is created with `mutate()`. The new value in each row is defined as a calculated fraction: the number of non-missing values in that row among the key columns, divided by the number of key columns.

This involves the function `rowSums()` from **base** R. Also used is `.`, which within piping refers to the data frame at that point in the pipe (in this case, it is being subset with brackets `[]`).

\*Scroll to the right to see more rows\*\*

``` r
# create a "key variable completeness" column
# this is a *proportion* of the columns designated as "key_cols" that have non-missing values

key_cols = c("personID", "name", "symptoms_ever")

obs %>% 
  mutate(key_completeness = rowSums(!is.na(.[,key_cols]))/length(key_cols)) 
```

See the [original data](#dedup_data).

## 15.4 Roll-up values

This section describes:

1.  How to “roll-up” values from multiple rows into just one row, with some variations  
2.  Once you have “rolled-up” values, how to overwrite/prioritize the values in each cell

This tab uses the example dataset from the Preparation tab.

### Roll-up values into one row

The code example below uses `group_by()` and `summarise()` to group rows by person, and then paste together all unique values within the grouped rows. Thus, you get one summary row per person. A few notes:

- A suffix is appended to all new columns (“\_roll” in this example)  
- If you want to show only unique values per cell, then wrap the `na.omit()` with `unique()`  
- `na.omit()` removes `NA` values, but if this is not desired it can be removed `paste0(.x)`…

``` r
# "Roll-up" values into one row per group (per "personID") 
cases_rolled <- obs %>% 
  
  # create groups by name
  group_by(personID) %>% 
  
  # order the rows within each group (e.g. by date)
  arrange(date, .by_group = TRUE) %>% 
  
  # For each column, paste together all values within the grouped rows, separated by ";"
  summarise(
    across(everything(),                           # apply to all columns
           ~paste0(na.omit(.x), collapse = "; "))) # function is defined which combines non-NA values
```

The result is one row per group (`ID`), with entries arranged by date and pasted together. *Scroll to the left to see more rows*

See the [original data](#dedup_data).

**This variation shows unique values only:**

``` r
# Variation - show unique values only 
cases_rolled <- obs %>% 
  group_by(personID) %>% 
  arrange(date, .by_group = TRUE) %>% 
  summarise(
    across(everything(),                                   # apply to all columns
           ~paste0(unique(na.omit(.x)), collapse = "; "))) # function is defined which combines unique non-NA values
```

**This variation appends a suffix to each column.**  
In this case “\_roll” to signify that it has been rolled:

``` r
# Variation - suffix added to column names 
cases_rolled <- obs %>% 
  group_by(personID) %>% 
  arrange(date, .by_group = TRUE) %>% 
  summarise(
    across(everything(),                
           list(roll = ~paste0(na.omit(.x), collapse = "; ")))) # _roll is appended to column names
```

### Overwrite values/hierarchy

If you then want to evaluate all of the rolled values, and keep only a specific value (e.g. “best” or “maximum” value), you can use `mutate()` across the desired columns, to implement `case_when()`, which uses `str_detect()` from the **stringr** package to sequentially look for string patterns and overwrite the cell content.

``` r
# CLEAN CASES
#############
cases_clean <- cases_rolled %>% 
    
    # clean Yes-No-Unknown vars: replace text with "highest" value present in the string
    mutate(across(c(contains("symptoms_ever")),                     # operates on specified columns (Y/N/U)
             list(mod = ~case_when(                                 # adds suffix "_mod" to new cols; implements case_when()
               
               str_detect(.x, "Yes")       ~ "Yes",                 # if "Yes" is detected, then cell value converts to yes
               str_detect(.x, "No")        ~ "No",                  # then, if "No" is detected, then cell value converts to no
               str_detect(.x, "Unknown")   ~ "Unknown",             # then, if "Unknown" is detected, then cell value converts to Unknown
               TRUE                        ~ as.character(.x)))),   # then, if anything else if it kept as is
      .keep = "unused")                                             # old columns removed, leaving only _mod columns
```

Now you can see in the column `symptoms_ever` that if the person EVER said “Yes” to symptoms, then only “Yes” is displayed.

See the [original data](#dedup_data).

## 15.5 Probabilistic de-duplication

Sometimes, you may want to identify “likely” duplicates based on similarity (e.g. string “distance”) across several columns such as name, age, sex, date of birth, etc. You can apply a probabilistic matching algorithm to identify likely duplicates.

See the page on [Joining data](joining_matching.llms.md) for an explanation on this method. The section on Probabilistic Matching contains an example of applying these algorithms to compare a data frame to *itself*, thus performing probabilistic de-duplication.

## 15.6 Resources

Much of the information in this page is adapted from these resources and vignettes online:

[datanovia](https://www.datanovia.com/en/lessons/identify-and-remove-duplicate-data-in-r/)

[dplyr tidyverse reference](https://dplyr.tidyverse.org/reference/slice.html)

[cran janitor vignette](https://cran.r-project.org/web/packages/janitor/vignettes/janitor.html#explore-records-with-duplicated-values-for-specific-combinations-of-variables-with-get_dupes)
