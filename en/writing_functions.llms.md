# 44  Writing functions

## 44.1 Preparation

### Load packages

This code chunk shows the loading of packages required for the analyses. In this handbook we emphasize `p_load()` from **pacman**, which installs the package if necessary *and* loads it for use. You can also load installed packages with `library()` from **base** R. See the page on [R basics](basics.llms.md) for more information on R packages.

### Import data

We import the dataset of cases from a simulated Ebola epidemic. If you want to download the data to follow step-by-step, see instructions in the [Download book and data](download.llms.md) page. The dataset is imported using the `import()` function from the **rio** package. See the page on [Import and export](importing.llms.md) for various ways to import data.

We will also use in the last part of this page some data on H7N9 flu from 2013.

## 44.2 Functions

Functions are helpful in programming since they allow to make codes easier to understand, somehow shorter and less prone to errors (given there were no errors in the function itself).

If you have come so far to this handbook, it means you have came across endless functions since in R, every operation is a function call `+, for, if, [, $, { …`. For example `x + y` is the same as`'+'(x, y)`

R is one the languages that offers the most possibility to work with functions and give enough tools to the user to easily write them. We should not think about functions as fixed at the top or at the end of the programming chain, R offers the possibility to use them as if they were vectors and even to use them inside other functions, lists…

Lot of very advanced resources on functional programming exist and we will only give here an insight to help you start with functional programming with short practical examples. You are then encouraged to visit the links on references to read more about it.

## 44.3 Why would you use a function?

Before answering this question, it is important to note that you have already had tips to get to write your very first R functions in the page on [Iteration, loops, and lists](iteration.llms.md) of this handbook. In fact, use of “if/else” and loops is often a core part of many of our functions since they easily help to either broaden the application of our code allowing multiple conditions or to iterate codes for repeating tasks.

- I am repeating multiple times the same block of code to apply it to a different variable or data?

- Getting rid of it will it substantially shorten my overall code and make it run quicker?

- Is it possible that the code I have written is used again but with a different value at many places of the code?

If the answer to one of the previous questions is “YES”, then you probably need to write a function

## 44.4 How does R build functions?

Functions in R have three main components:

- the `formals()` which is the list of arguments which controls how we can call the function

- the `body()` that is the code inside the function i.e. within the brackets or following the parenthesis depending on how we write it

and,

- the `environment()` which will help locate the function’s variables and determines how the function finds value.

Once you have created your function, you can verify each of these components by calling the function associated.

## 44.5 Basic syntax and structure

- A function will need to be named properly so that its job is easily understandable as soon as we read its name. Actually this is already the case with majority of the base R architecture. Functions like `mean()`, `print()`, `summary()` have names that are very straightforward

- A function will need arguments, such as the data to work on and other objects that can be static values among other options

- And finally a function will give an output based on its core task and the arguments it has been given. Usually we will use the built-in functions as `print()`, `return()`… to produce the output. The output can be a logical value, a number, a character, a data frame…in short any kind of R object.

Basically this is the composition of a function:

``` r
function_name <- function(argument_1, argument_2, argument_3){
  
           function_task
  
           return(output)
}
```

We can create our first function that will be called `contain_covid19()`.

``` r
contain_covid19 <- function(barrier_gest, wear_mask, get_vaccine){
  
                            if(barrier_gest == "yes" & wear_mask == "yes" & get_vaccine == "yes" ) 
       
                            return("success")
  
  else("please make sure all are yes, this pandemic has to end!")
}
```

We can then verify the components of our newly created function.

``` r
formals(contain_covid19)
```

    $barrier_gest


    $wear_mask


    $get_vaccine

``` r
body(contain_covid19)
```

    {
        if (barrier_gest == "yes" & wear_mask == "yes" & get_vaccine == 
            "yes") 
            return("success")
        else ("please make sure all are yes, this pandemic has to end!")
    }

``` r
environment(contain_covid19)
```

    <environment: R_GlobalEnv>

Now we will test our function. To call our written function, you use it as you use all R functions i.e by writing the function name and adding the required arguments.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "yes")
```

    [1] "success"

We can write again the name of each argument for precautionary reasons. But without specifying them, the code should work since R has in memory the positioning of each argument. So as long as you put the values of the arguments in the correct order, you can skip writing the arguments names when calling the functions.

``` r
contain_covid19("yes", "yes", "yes")
```

    [1] "success"

Then let’s look what happens if one of the values is `"no"` or **not** `"yes"`.

``` r
contain_covid19(barrier_gest = "yes", wear_mask = "yes", get_vaccine = "no")
```

    [1] "please make sure all are yes, this pandemic has to end!"

If we provide an argument that is not recognized, we get an error:

``` r
contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", get_vaccine = "no")
```

`Error in contain_covid19(barrier_gest = "sometimes", wear_mask = "yes", : could not find function "contain_covid19"`

***NOTE:*** Some functions (most of time very short and straightforward) may not need a name and can be used directly on a line of code or inside another function to do quick task. They are called **anonymous functions** .

For instance below is a first anonymous function that keeps only character variables the dataset.

``` r
linelist %>% 
  dplyr::slice_head(n=10) %>%  #equivalent to R base "head" function and that return first n observation of the  dataset
  select(function(x) is.character(x)) 
```

Then another function that selects every second observation of our dataset (may be relevant when we have longitudinal data with many records per patient for instance after having ordered by date or visit). In this case, the proper function writing outside dplyr would be `function (x) (x%%2 == 0)` to apply to the vector containing all row numbers.

``` r
linelist %>%   
   slice_head(n=20) %>% 
   tibble::rownames_to_column() %>% # add indices of each obs as rownames to clearly see the final selection
   filter(row_number() %%2 == 0)
```

A possible base R code for the same task would be:

``` r
linelist_firstobs <- head(linelist, 20)

linelist_firstobs[base::Filter(function(x) (x%%2 == 0), seq(nrow(linelist_firstobs))),]
```

***CAUTION:*** Though it is true that using functions can help us with our code, it can nevertheless be time consuming to write some functions or to fix one if it has not been thought thoroughly, written adequately and is returning errors as a result. For this reason it is often recommended to first write the R code, make sure it does what we intend it to do, and then transform it into a function with its three main components as listed above.

## 44.6 Examples

### Return proportion tables for several columns

Yes, we already have nice functions in many packages allowing to summarize information in a very easy and nice way. But we will still try to make our own, in our first steps to getting used to writing functions.

In this example we want to show how writing a simple function would avoid you copy-pasting the same code multiple times.

``` r
proptab_multiple <- function(my_data, var_to_tab){
  
  #print the name of each variable of interest before doing the tabulation
  print(var_to_tab)

  with(my_data,
       rbind( #bind the results of the two following function by row
        #tabulate the variable of interest: gives only numbers
          table(my_data[[var_to_tab]], useNA = "no"),
          #calculate the proportions for each variable of interest and round the value to 2 decimals
         round(prop.table(table(my_data[[var_to_tab]]))*100,2)
         )
       )
}


proptab_multiple(linelist, "gender")
```

    [1] "gender"

               f       m
    [1,] 2807.00 2803.00
    [2,]   50.04   49.96

``` r
proptab_multiple(linelist, "age_cat")
```

    [1] "age_cat"

             0-4     5-9  10-14  15-19   20-29 30-49 50-69 70+
    [1,] 1095.00 1095.00 941.00 743.00 1073.00   754 95.00 6.0
    [2,]   18.87   18.87  16.22  12.81   18.49    13  1.64 0.1

``` r
proptab_multiple(linelist, "outcome")
```

    [1] "outcome"

           Death Recover
    [1,] 2582.00 1983.00
    [2,]   56.56   43.44

***TIP:*** As shown above, it is very important to comment your functions as you would do for the general programming. Bear in mind that a function’s aim is to make a code ready to read, shorter and more efficient. Then one should be able to understand what the function does just by reading its name and should have more details reading the comments.

A second option is to use this function in another one via a loop to make the process at once:

``` r
for(var_to_tab in c("gender","age_cat",  "outcome")){
  
  print(proptab_multiple(linelist, var_to_tab))
  
}
```

    [1] "gender"
               f       m
    [1,] 2807.00 2803.00
    [2,]   50.04   49.96
    [1] "age_cat"
             0-4     5-9  10-14  15-19   20-29 30-49 50-69 70+
    [1,] 1095.00 1095.00 941.00 743.00 1073.00   754 95.00 6.0
    [2,]   18.87   18.87  16.22  12.81   18.49    13  1.64 0.1
    [1] "outcome"
           Death Recover
    [1,] 2582.00 1983.00
    [2,]   56.56   43.44

A simpler way could be using the base R “apply” instead of a “for loop” as expressed below:

***TIP:*** R is often defined as a functional programming language and almost anytime you run a line of code you are using some built-in functions. A good habit to be more comfortable with writing functions is to often have an internal look at how the basic functions you are using daily are built. The shortcut to do so is selecting the function name and then clicking on`Ctrl+F2` or `fn+F2` or `Cmd+F2` (depending on your computer) .

## 44.7 Using **purrr**: writing functions that can be iteratively applied

### Modify class of multiple columns in a dataset

Let’s say many character variables in the original `linelist` data need to be changes to “factor” for analysis and plotting purposes. Instead of repeating the step several times, we can just use `lapply()` to do the transformation of all variables concerned on a single line of code.

***CAUTION:*** `lapply()` returns a list, thus its use may require an additional modification as a last step.

The same step can be done using `map_if()` function from the **purrr** package

``` r
linelist_factor2 <- linelist %>%
  purrr::map_if(is.character, as.factor)


linelist_factor2 %>%
        glimpse()
```

    List of 30
     $ case_id             : Factor w/ 5888 levels "00031d","00086d",..: 2134 3022 396 4203 3084 4347 179 1241 5594 430 ...
     $ generation          : num [1:5888] 4 4 2 3 3 3 4 4 4 4 ...
     $ date_infection      : Date[1:5888], format: "2014-05-08" NA ...
     $ date_onset          : Date[1:5888], format: "2014-05-13" "2014-05-13" ...
     $ date_hospitalisation: Date[1:5888], format: "2014-05-15" "2014-05-14" ...
     $ date_outcome        : Date[1:5888], format: NA "2014-05-18" ...
     $ outcome             : Factor w/ 2 levels "Death","Recover": NA 2 2 NA 2 2 2 1 2 1 ...
     $ gender              : Factor w/ 2 levels "f","m": 2 1 2 1 2 1 1 1 2 1 ...
     $ age                 : num [1:5888] 2 3 56 18 3 16 16 0 61 27 ...
     $ age_unit            : Factor w/ 2 levels "months","years": 2 2 2 2 2 2 2 2 2 2 ...
     $ age_years           : num [1:5888] 2 3 56 18 3 16 16 0 61 27 ...
     $ age_cat             : Factor w/ 8 levels "0-4","5-9","10-14",..: 1 1 7 4 1 4 4 1 7 5 ...
     $ age_cat5            : Factor w/ 18 levels "0-4","5-9","10-14",..: 1 1 12 4 1 4 4 1 13 6 ...
     $ hospital            : Factor w/ 6 levels "Central Hospital",..: 4 3 6 5 2 5 3 3 3 3 ...
     $ lon                 : num [1:5888] -13.2 -13.2 -13.2 -13.2 -13.2 ...
     $ lat                 : num [1:5888] 8.47 8.45 8.46 8.48 8.46 ...
     $ infector            : Factor w/ 2697 levels "00031d","002e6c",..: 2594 NA NA 2635 180 1799 1407 195 NA NA ...
     $ source              : Factor w/ 2 levels "funeral","other": 2 NA NA 2 2 2 2 2 NA NA ...
     $ wt_kg               : num [1:5888] 27 25 91 41 36 56 47 0 86 69 ...
     $ ht_cm               : num [1:5888] 48 59 238 135 71 116 87 11 226 174 ...
     $ ct_blood            : num [1:5888] 22 22 21 23 23 21 21 22 22 22 ...
     $ fever               : Factor w/ 2 levels "no","yes": 1 NA NA 1 1 1 NA 1 1 1 ...
     $ chills              : Factor w/ 2 levels "no","yes": 1 NA NA 1 1 1 NA 1 1 1 ...
     $ cough               : Factor w/ 2 levels "no","yes": 2 NA NA 1 2 2 NA 2 2 2 ...
     $ aches               : Factor w/ 2 levels "no","yes": 1 NA NA 1 1 1 NA 1 1 1 ...
     $ vomit               : Factor w/ 2 levels "no","yes": 2 NA NA 1 2 2 NA 2 2 1 ...
     $ temp                : num [1:5888] 36.8 36.9 36.9 36.8 36.9 37.6 37.3 37 36.4 35.9 ...
     $ time_admission      : Factor w/ 1072 levels "00:10","00:29",..: NA 308 746 415 514 589 609 297 409 387 ...
     $ bmi                 : num [1:5888] 117.2 71.8 16.1 22.5 71.4 ...
     $ days_onset_hosp     : num [1:5888] 2 1 2 2 1 1 2 1 1 2 ...

### Iteratively produce graphs for different levels of a variable

We will produce here pie chart to look at the distribution of patient’s outcome in China during the H7N9 outbreak for each province. Instead of repeating the code for each of them, we will just apply a function that we will create.

``` r
#precising options for the use of highchart
options(highcharter.theme =   highcharter::hc_theme_smpl(tooltip = list(valueDecimals = 2)))


#create a function called "chart_outcome_province" that takes as argument the dataset and the name of the province for which to plot the distribution of the outcome.

chart_outcome_province <- function(data_used, prov){
  
  tab_prov <- data_used %>% 
    filter(province == prov,
           !is.na(outcome))%>% 
    group_by(outcome) %>% 
    count() %>%
    adorn_totals(where = "row") %>% 
    adorn_percentages(denominator = "col", )%>%
    mutate(
        perc_outcome= round(n*100,2))
  
  
  tab_prov %>%
    filter(outcome != "Total") %>% 
  highcharter::hchart(
    "pie", hcaes(x = outcome, y = perc_outcome),
    name = paste0("Distibution of the outcome in:", prov)
    )
  
}

chart_outcome_province(flu_china, "Shanghai")
```

``` r
chart_outcome_province(flu_china,"Zhejiang")
```

``` r
chart_outcome_province(flu_china,"Jiangsu")
```

### Iteratively produce tables for different levels of a variable

Here we will create three indicators to summarize in a table and we would like to produce this table for each of the provinces. Our indicators are the delay between onset and hospitalization, the percentage of recovery and the median age of cases.

``` r
indic_1 <- flu_china %>% 
  group_by(province) %>% 
  mutate(
    date_hosp= strptime(date_of_hospitalisation, format = "%m/%d/%Y"),
    date_ons= strptime(date_of_onset, format = "%m/%d/%Y"), 
    delay_onset_hosp= as.numeric(date_hosp - date_ons)/86400,
    mean_delay_onset_hosp = round(mean(delay_onset_hosp, na.rm=TRUE ), 0)) %>%
  select(province, mean_delay_onset_hosp)  %>% 
  distinct()
     

indic_2 <-  flu_china %>% 
            filter(!is.na(outcome)) %>% 
            group_by(province, outcome) %>% 
            count() %>%
            pivot_wider(names_from = outcome, values_from = n) %>% 
    adorn_totals(where = "col") %>% 
    mutate(
        perc_recovery= round((Recover/Total)*100,2))%>% 
  select(province, perc_recovery)
    
    
    
indic_3 <-  flu_china %>% 
            group_by(province) %>% 
            mutate(
                    median_age_cases = median(as.numeric(na_if(age, "?")), na.rm = TRUE)
            ) %>% 
  select(province, median_age_cases)  %>% 
  distinct()

#join the three indicator datasets

table_indic_all <- indic_1 %>% 
  dplyr::left_join(indic_2, by = "province") %>% 
        left_join(indic_3, by = "province")


#print the indicators in a flextable


print_indic_prov <-  function(table_used, prov){
  
  #first transform a bit the dataframe for printing ease
  indic_prov <- table_used %>%
    filter(province==prov) %>%
    pivot_longer(names_to = "Indicateurs", cols = 2:4) %>% 
   mutate( indic_label = factor(Indicateurs,
   levels= c("mean_delay_onset_hosp","perc_recovery","median_age_cases"),
   labels=c("Mean delay onset-hosp","Percentage of recovery", "Median age of the cases"))
   ) %>% 
    ungroup(province) %>% 
    select(indic_label, value)
  

    tab_print <- flextable(indic_prov)  %>%
    theme_vanilla() %>% 
    flextable::fontsize(part = "body", size = 10) 
    
    
     tab_print <- tab_print %>% 
                  autofit()   %>%
                  set_header_labels( 
                indic_label= "Indicateurs", value= "Estimation") %>%
    flextable::bg( bg = "darkblue", part = "header") %>%
    flextable::bold(part = "header") %>%
    flextable::color(color = "white", part = "header") %>% 
    add_header_lines(values = paste0("Indicateurs pour la province de: ", prov)) %>% 
bold(part = "header")
 
 tab_print <- colformat_double(tab_print,
   digits = 2,
   na_str = "-")

tab_print 
    
}




print_indic_prov(table_indic_all, "Shanghai")
```

| Indicateurs pour la province de: Shanghai |            |
|-------------------------------------------|------------|
| Indicateurs                               | Estimation |
| Mean delay onset-hosp                     | 4.00       |
| Percentage of recovery                    | 46.67      |
| Median age of the cases                   | 67.00      |

``` r
print_indic_prov(table_indic_all, "Jiangsu")
```

| Indicateurs pour la province de: Jiangsu |            |
|------------------------------------------|------------|
| Indicateurs                              | Estimation |
| Mean delay onset-hosp                    | 6.00       |
| Percentage of recovery                   | 71.43      |
| Median age of the cases                  | 55.00      |

## 44.8 Tips and best Practices for well functioning functions

Functional programming is meant to ease code and facilitates its reading. It should produce the contrary. The tips below will help you having a clean code and easy to read code.

### Naming and syntax

- Avoid using character that could have been easily already taken by other functions already existing in your environment

- It is recommended for the function name to be short and straightforward to understand for another reader

- It is preferred to use verbs as the function name and nouns for the argument names.

### Column names and tidy evaluation

If you want to know how to reference *column names* that are provided to your code as arguments, read this [tidyverse programming guidance](https://dplyr.tidyverse.org/articles/programming.html). Among the topics covered are *tidy evaluation* and use of the *embrace* `{ }` “double braces”

For example, here is a quick skeleton template code from page tutorial mentioned just above:

``` r
var_summary <- function(data, var) {
  data %>%
    summarise(n = n(), min = min({{ var }}), max = max({{ var }}))
}
mtcars %>% 
  group_by(cyl) %>% 
  var_summary(mpg)
```

### Testing and Error handling

The more complicated a function’s task the higher the possibility of errors. Thus it is sometimes necessary to add some verification within the funtion to help quickly understand where the error is from and find a way t fix it.

- It can be more than recommended to introduce a check on the missingness of one argument using `missing(argument)`. This simple check can return “TRUE” or “FALSE” value.

``` r
contain_covid19_missing <- function(barrier_gest, wear_mask, get_vaccine){
  
  if (missing(barrier_gest)) (print("please provide arg1"))
  if (missing(wear_mask)) print("please provide arg2")
  if (missing(get_vaccine)) print("please provide arg3")


  if (!barrier_gest == "yes" | wear_mask =="yes" | get_vaccine == "yes" ) 
       
       return ("you can do better")
  
  else("please make sure all are yes, this pandemic has to end!")
}


contain_covid19_missing(get_vaccine = "yes")
```

    [1] "please provide arg1"
    [1] "please provide arg2"

    Error in `contain_covid19_missing()`:
    ! argument "barrier_gest" is missing, with no default

- Use `stop()` for more detectable errors.

``` r
contain_covid19_stop <- function(barrier_gest, wear_mask, get_vaccine){
  
  if(!is.character(barrier_gest)) (stop("arg1 should be a character, please enter the value with `yes`, `no` or `sometimes"))
  
  if (barrier_gest == "yes" & wear_mask =="yes" & get_vaccine == "yes" ) 
       
       return ("success")
  
  else("please make sure all are yes, this pandemic has to end!")
}


contain_covid19_stop(barrier_gest=1, wear_mask="yes", get_vaccine = "no")
```

    Error in `contain_covid19_stop()`:
    ! arg1 should be a character, please enter the value with `yes`, `no` or `sometimes

- As we see when we run most of the built-in functions, there are messages and warnings that can pop-up in certain conditions. We can integrate those in our written functions by using the functions `message()` and `warning()`.

- We can handle errors also by using `safely()` which takes one function as an argument and executes it in a safe way. In fact the function will execute without stopping if it encounters an error. `safely()` returns as output a **list** with two objects which are the results and the error it “skipped”.

We can verify by first running the `mean()` as function, then run it with `safely()`.

``` r
linelist %>% 
  select(where(is.numeric)) %>% 
  map(mean)
```

    $generation
    [1] 16.56165

    $age
    [1] NA

    $age_years
    [1] NA

    $lon
    [1] -13.23381

    $lat
    [1] 8.469638

    $wt_kg
    [1] 52.64487

    $ht_cm
    [1] 124.9633

    $ct_blood
    [1] 21.20686

    $temp
    [1] NA

    $bmi
    [1] 46.89023

    $days_onset_hosp
    [1] NA

``` r
safe_mean <- safely(mean)
linelist %>% 
  select(where(is.numeric)) %>% 
  map(safe_mean)
```

    $generation
    $generation$result
    [1] 16.56165

    $generation$error
    NULL


    $age
    $age$result
    [1] NA

    $age$error
    NULL


    $age_years
    $age_years$result
    [1] NA

    $age_years$error
    NULL


    $lon
    $lon$result
    [1] -13.23381

    $lon$error
    NULL


    $lat
    $lat$result
    [1] 8.469638

    $lat$error
    NULL


    $wt_kg
    $wt_kg$result
    [1] 52.64487

    $wt_kg$error
    NULL


    $ht_cm
    $ht_cm$result
    [1] 124.9633

    $ht_cm$error
    NULL


    $ct_blood
    $ct_blood$result
    [1] 21.20686

    $ct_blood$error
    NULL


    $temp
    $temp$result
    [1] NA

    $temp$error
    NULL


    $bmi
    $bmi$result
    [1] 46.89023

    $bmi$error
    NULL


    $days_onset_hosp
    $days_onset_hosp$result
    [1] NA

    $days_onset_hosp$error
    NULL

As said previously, well commenting our codes is already a good way for having documentation in our work.

## 44.9 Resources

[R for Data Science link](https://r4ds.had.co.nz/functions.html)

[Cheatsheet advance R programming](https://www.rstudio.com/wp-content/uploads/2016/02/advancedR.pdf)

[Cheatsheet purr Package](https://purrr.tidyverse.org/)

[Video-ACM talk by Hadley Wickham: The joy of functional programming (how does map_dbl work)](https://youtube.videoken.com/embed/bzUmK0Y07ck)
