# 50  Data Table

The handbook focusses on the **dplyr** “verb” functions and the **magrittr** pipe operator `%>%` as a method to clean and group data, but the **data.table** package offers an alternative method that you may encounter in your R career.

## 50.1 Intro to data tables

A data table is a 2-dimensional data structure like a data frame that allows complex grouping operations to be performed. The data.table syntax is structured so that operations can be performed on rows, columns and groups.

The structure is **DT\[i, j, by\]**, separated by 3 parts; the **i, j** and **by** arguments. The **i** argument allows for subsetting of required rows, the **j** argument allows you to operate on columns and the **by** argument allows you operate on columns by groups.

This page will address the following topics:

- Importing data and use of `fread()` and `fwrite()`
- Selecting and filtering rows using the **i** argument
- Using helper functions `%like%`, `%chin%`, `%between%`
- Selecting and computing on columns using the **j** argument
- Computing by groups using the **by** argument
- Adding and updating data to data tables using `:=`

## 50.2 Load packages and import data

### Load packages

Using the `p_load()` function from **pacman**, we load (and install if necessary) packages required for this analysis.

``` r
pacman::p_load(
  data.table, # to group and clean data
  tidyverse   # allows use of pipe (%>%) function in this chapter
  ) 
```

### Import data

This page will explore some of the core functions of **data.table** using the case linelist referenced throughout the handbook.

We import the dataset of cases from a simulated Ebola epidemic. Load it directly with `appliedepidata::get_data(name = "linelist_cleaned_excel")` (see the [Download handbook and data](download.llms.md) page for details). From here we use `data.table()` to convert the data frame to a data table.

``` r
linelist <- appliedepidata::get_data(name = "linelist_cleaned_excel") %>% data.table()
```

The `fread()` function is used to directly import regular delimited files, such as .csv files, directly to a data table format. This function, and its counterpart, `fwrite()`, used for writing data.tables as regular delimited files are very fast and computationally efficient options for large databases.

The first 20 rows of `linelist`:

Base R commands such as `dim()` that are used for data frames can also be used for data tables

``` r
dim(linelist) #gives the number of rows and columns in the data table
```

    [1] 5888   30

## 50.3 The i argument: selecting and filtering rows

Recalling the **DT\[i, j, by\]** structure, we can filter rows using either row numbers or logical expressions. The i argument is first; therefore, the syntax **DT\[i\]** or **DT\[i,\]** can be used.

The first example retrieves the first 5 rows of the data table, the second example subsets cases are 18 years or over, and the third example subsets cases 18 years old or over but not diagnosed at the Central Hospital:

``` r
linelist[1:5] #returns the 1st to 5th row
linelist[age >= 18] #subsets cases are equal to or over 18 years
linelist[age >= 18 & hospital != "Central Hospital"] #subsets cases equal to or over 18 years old but not diagnosed at the Central Hospital
```

Using .N in the i argument represents the total number of rows in the data table. This can be used to subset on the row numbers:

``` r
linelist[.N] #returns the last row
linelist[15:.N] #returns the 15th to the last row
```

### Using helper functions for filtering

Data table uses helper functions that make subsetting rows easy. The `%like%` function is used to match a pattern in a column, `%chin%` is used to match a specific character, and the `%between%` helper function is used to match numeric columns within a prespecified range.

In the following examples we: \* filter rows where the hospital variable contains “Hospital” \* filter rows where the outcome is “Recover” or “Death” \* filter rows in the age range 40-60

``` r
linelist[hospital %like% "Hospital"] #filter rows where the hospital variable contains “Hospital”
linelist[outcome %chin% c("Recover", "Death")] #filter rows where the outcome is “Recover” or “Death”
linelist[age %between% c(40, 60)] #filter rows in the age range 40-60

#%between% must take a vector of length 2, whereas %chin% can take vectors of length >= 1
```

## 50.4 The j argument: selecting and computing on columns

Using the **DT\[i, j, by\]** structure, we can select columns using numbers or names. The **j** argument is second; therefore, the syntax **DT\[, j\]** is used. To facilitate computations on the **j** argument, the column is wrapped using either `list()` or `.()`.

### Selecting columns

The first example retrieves the first, third and fifth columns of the data table, the second example selects all columns except the height, weight, age and gender columns. The third example uses the `.()` wrap to select the **case_id** and **outcome** columns.

``` r
linelist[ , c(1,3,5)]
linelist[ , -c("gender", "age", "wt_kg", "ht_cm")]
linelist[ , list(case_id, outcome)] #linelist[ , .(case_id, outcome)] works just as well
```

### Computing on columns

By combining the **i** and **j** arguments it is possible to filter rows and compute on the columns. Using **.N** in the **j** argument also represents the total number of rows in the data table and can be useful to return the number of rows after row filtering.

In the following examples we: \* Count the number of cases that stayed over 7 days in hospital \* Calculate the mean age of the cases that died at the military hospital \* Calculate the standard deviation, median, mean age of the cases that recovered at the central hospital

``` r
linelist[days_onset_hosp > 7 , .N]
```

    [1] 189

``` r
linelist[hospital %like% "Military" & outcome %chin% "Death", .(mean(age, na.rm = T))] #na.rm = T removes N/A values
```

            V1
         <num>
    1: 15.9084

``` r
linelist[hospital == "Central Hospital" & outcome == "Recover", 
                 .(mean_age = mean(age, na.rm = T),
                   median_age = median(age, na.rm = T),
                   sd_age = sd(age, na.rm = T))] #this syntax does not use the helper functions but works just as well
```

       mean_age median_age   sd_age
          <num>      <num>    <num>
    1: 16.85185         14 12.93857

Remember using the .() wrap in the j argument facilitates computation, returns a data table and allows for column naming.

## 50.5 The by argument: computing by groups

The **by** argument is the third argument in the **DT\[i, j, by\]** structure. The **by** argument accepts both a character vector and the `list()` or `.()` syntax. Using the `.()` syntax in the **by** argument allows column renaming on the fly.

In the following examples we:  
\* group the number of cases by hospital \* in cases 18 years old or over, calculate the mean height and weight of cases according to gender and whether they recovered or died \* in admissions that lasted over 7 days, count the number of cases according to the month they were admitted and the hospital they were admitted to

``` r
linelist[, .N, .(hospital)] #the number of cases by hospital
```

                                   hospital     N
                                     <char> <int>
    1:                                Other   885
    2:                              Missing  1469
    3: St. Mark's Maternity Hospital (SMMH)   422
    4:                        Port Hospital  1762
    5:                    Military Hospital   896
    6:                     Central Hospital   454

``` r
linelist[age > 18, .(mean_wt = mean(wt_kg, na.rm = T),
                             mean_ht = mean(ht_cm, na.rm = T)), .(gender, outcome)] #NAs represent the categories where the data is missing
```

       gender outcome  mean_wt  mean_ht
       <char>  <char>    <num>    <num>
    1:      m Recover 71.90227 178.1977
    2:      f   Death 63.27273 159.9448
    3:      m   Death 71.61770 175.4726
    4:      f    <NA> 64.49375 162.7875
    5:      m    <NA> 72.65505 176.9686
    6:      f Recover 62.86498 159.2996
    7:   <NA> Recover 67.21429 175.2143
    8:   <NA>   Death 69.16667 170.7917
    9:   <NA>    <NA> 70.25000 175.5000

``` r
linelist[days_onset_hosp > 7, .N, .(month = month(date_hospitalisation), hospital)]
```

        month                             hospital     N
        <num>                               <char> <int>
     1:     5                    Military Hospital     3
     2:     6                        Port Hospital     4
     3:     7                        Port Hospital     8
     4:     8 St. Mark's Maternity Hospital (SMMH)     5
     5:     8                    Military Hospital     9
     6:     8                                Other    10
     7:     8                        Port Hospital    10
     8:     9                        Port Hospital    28
     9:     9                              Missing    27
    10:     9                     Central Hospital    10
    11:     9 St. Mark's Maternity Hospital (SMMH)     6
    12:    10                              Missing     2
    13:    10                    Military Hospital     3
    14:     3                        Port Hospital     1
    15:     4                    Military Hospital     1
    16:     5                                Other     2
    17:     5                     Central Hospital     1
    18:     5                              Missing     1
    19:     6                              Missing     7
    20:     6 St. Mark's Maternity Hospital (SMMH)     2
    21:     6                    Military Hospital     1
    22:     7                    Military Hospital     3
    23:     7                                Other     1
    24:     7                              Missing     2
    25:     7 St. Mark's Maternity Hospital (SMMH)     1
    26:     8                     Central Hospital     2
    27:     8                              Missing     6
    28:     9                                Other     9
    29:     9                    Military Hospital    11
    30:    10                        Port Hospital     3
    31:    10                                Other     4
    32:    10 St. Mark's Maternity Hospital (SMMH)     1
    33:    10                     Central Hospital     1
    34:    11                              Missing     2
    35:    11                        Port Hospital     1
    36:    12                        Port Hospital     1
        month                             hospital     N
        <num>                               <char> <int>

Data.table also allows the chaining expressions as follows:

``` r
linelist[, .N, .(hospital)][order(-N)][1:3] #1st selects all cases by hospital, 2nd orders the cases in descending order, 3rd subsets the 3 hospitals with the largest caseload
```

                hospital     N
                  <char> <int>
    1:     Port Hospital  1762
    2:           Missing  1469
    3: Military Hospital   896

In these examples we are following the assumption that a row in the data table is equal to a new case, and so we can use the **.N** to represent the number of rows in the data table. Another useful function to represent the number of unique cases is `uniqueN()`, which returns the number of unique values in a given input. This is illustrated here:

``` r
linelist[, .(uniqueN(gender))] #remember .() in the j argument returns a data table
```

          V1
       <int>
    1:     3

The answer is 3, as the unique values in the gender column are m, f and N/A. Compare with the base R function `unique()`, which returns all the unique values in a given input:

``` r
linelist[, .(unique(gender))]
```

           V1
       <char>
    1:      m
    2:      f
    3:   <NA>

To find the number of unique cases in a given month we would write the following:

``` r
linelist[, .(uniqueN(case_id)), .(month = month(date_hospitalisation))]
```

        month    V1
        <num> <int>
     1:     5    62
     2:     6   100
     3:     7   198
     4:     8   509
     5:     9  1170
     6:    10  1228
     7:    11   813
     8:    12   576
     9:     1   434
    10:     2   310
    11:     3   290
    12:     4   198

## 50.6 Adding and updating to data tables

The `:=` operator is used to add or update data in a data table. Adding columns to your data table can be done in the following ways:

``` r
linelist[, adult := age >= 18] #adds one column
linelist[, c("child", "wt_lbs") := .(age < 18, wt_kg*2.204)] #to add multiple columns requires c("") and list() or .() syntax
linelist[, `:=` (bmi_in_range = (bmi > 16 & bmi < 40),
                         no_infector_source_data = is.na(infector) | is.na(source))] #this method uses := as a functional operator `:=`
linelist[, adult := NULL] #deletes the column
```

Further complex aggregations are beyond the scope of this introductory chapter, but the idea is to provide a popular and viable alternative to **dplyr** for grouping and cleaning data. The **data.table** package is a great package that allows for neat and readable code.

## 50.7 Resources

Here are some useful resources for more information: \* https://cran.r-project.org/web/packages/data.table/vignettes/datatable-intro.html \* https://github.com/Rdatatable/data.table \* https://s3.amazonaws.com/assets.datacamp.com/img/blog/data+table+cheat+sheet.pdf \* https://www.machinelearningplus.com/data-manipulation/datatable-in-r-complete-guide/ \* https://www.datacamp.com/community/tutorials/data-table-r-tutorial

You can perform any summary function on grouped data; see the Cheat Sheet here for more info: https://s3.amazonaws.com/assets.datacamp.com/blog_assets/datatable_Cheat_Sheet_R.pdf
