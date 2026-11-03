# 21  Standardised rates

This page will show you how to standardize an outcome, such as hospitalizations or mortality, by characteristics such as age and sex.

This page uses the **PHEindicatormethods** package.

We begin by extensively demonstrating the processes of data preparation/cleaning/joining, as this is common when combining population data from multiple countries, standard population data, deaths, etc.

## 21.1 Overview

There are two main ways to standardize: direct and indirect standardization. Let’s say we would like to the standardize mortality rate by age and sex for country A and country B, and compare the standardized rates between these countries.

- For direct standardization, you will have to know the number of the at-risk population and the number of deaths for each stratum of age and sex, for country A and country B. One stratum in our example could be females between ages 15-44.  
- For indirect standardization, you only need to know the total number of deaths and the age- and sex structure of each country. This option is therefore feasible if age- and sex-specific mortality rates or population numbers are not available. Indirect standardization is furthermore preferable in case of small numbers per stratum, as estimates in direct standardization would be influenced by substantial sampling variation.

## 21.2 Preparation

To show how standardization is done, we will use fictitious population counts and death counts from country A and country B, by age (in 5 year categories) and sex (female, male). To make the datasets ready for use, we will perform the following preparation steps:

1.  Load packages  
2.  Load datasets  
3.  Join the population and death data from the two countries
4.  Pivot longer so there is one row per age-sex stratum
5.  Clean the reference population (world standard population) and join it to the country data

In your scenario, your data may come in a different format. Perhaps your data are by province, city, or other catchment area. You may have one row for each death and information on age and sex for each (or a significant proportion) of these deaths. In this case, see the pages on [Grouping data](grouping.llms.md), [Pivoting data](pivoting.llms.md), and [Descriptive tables](tables_descriptive.llms.md) to create a dataset with event and population counts per age-sex stratum.

We also need a reference population, the standard population. For the purposes of this exercise we will use the `world_standard_population_by_sex`. The World standard population is based on the populations of 46 countries and was developed in 1960. There are many “standard” populations - as one example, the website of [NHS Scotland](https://www.opendata.nhs.scot/dataset/standard-populations) is quite informative on the European Standard Population, World Standard Population and Scotland Standard Population.

### Load packages

This code chunk shows the loading of packages required for the analyses. In this handbook we emphasize `p_load()` from **pacman**, which installs the package if necessary *and* loads it for use. You can also load installed packages with `library()` from **base** R. See the page on [R basics](basics.llms.md) for more information on R packages.

``` r
pacman::p_load(
     rio,                 # import/export data
     here,                # locate files
     stringr,             # cleaning characters and strings
     PHEindicatormethods, # alternative for rate standardisation
     tidyverse,           # data management and visualization
     appliedepidata)      # example datasets used in this handbook
```

### Load population data

See the [Download handbook and data](download.llms.md) page for instructions on how to download all the example data in the handbook. You can load the Standardisation page data directly into R with the following `appliedepidata::get_data()` calls:

``` r
# demographics for country A
A_demo <- appliedepidata::get_data(name = "country_demographics")

# deaths for country A
A_deaths <- appliedepidata::get_data(name = "deaths_countryA")

# demographics for country B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")

# deaths for country B
B_deaths <- appliedepidata::get_data(name = "deaths_countryB")

# reference (world standard) population
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

First we load the demographic data (counts of males and females by 5-year age category) for the two countries that we will be comparing, “Country A” and “Country B”.

``` r
# Country A
A_demo <- appliedepidata::get_data(name = "country_demographics")
```

``` r
# Country B
B_demo <- appliedepidata::get_data(name = "country_demographics_2")
```

### Load death counts

Conveniently, we also have the counts of deaths during the time period of interest, by age and sex. Each country’s counts are in a separate file, shown below.

Deaths in Country A

Deaths in Country B

### Clean populations and deaths

We need to join and transform these data in the following ways:

- Combine country populations into one dataset and pivot “long” so that each age-sex stratum is one row  
- Combine country death counts into one dataset and pivot “long” so each age-sex stratum is one row  
- Join the deaths to the populations

First, we combine the country populations datasets, pivot longer, and do minor cleaning. See the page on [Pivoting data](pivoting.llms.md) for more detail.

``` r
pop_countries <- A_demo %>%  # begin with country A dataset
     bind_rows(B_demo) %>%        # bind rows, because cols are identically named
     pivot_longer(                       # pivot longer
          cols = c(m, f),                   # columns to combine into one
          names_to = "Sex",                 # name for new column containing the category ("m" or "f") 
          values_to = "Population") %>%     # name for new column containing the numeric values pivoted
     mutate(Sex = recode(Sex,            # re-code values for clarity
          "m" = "Male",
          "f" = "Female"))
```

The combined population data now look like this (click through to see countries A and B):

And now we perform similar operations on the two deaths datasets.

``` r
deaths_countries <- A_deaths %>%    # begin with country A deaths dataset
     bind_rows(B_deaths) %>%        # bind rows with B dataset, because cols are identically named
     pivot_longer(                  # pivot longer
          cols = c(Male, Female),        # column to transform into one
          names_to = "Sex",              # name for new column containing the category ("m" or "f") 
          values_to = "Deaths") %>%      # name for new column containing the numeric values pivoted
     rename(age_cat5 = AgeCat)      # rename for clarity
```

The deaths data now look like this, and contain data from both countries:

We now join the deaths and population data based on common columns `Country`, `age_cat5`, and `Sex`. This adds the column `Deaths`.

``` r
country_data <- pop_countries %>% 
     left_join(deaths_countries, by = c("Country", "age_cat5", "Sex"))
```

We can now classify `Sex`, `age_cat5`, and `Country` as factors and set the level order using `fct_relevel()` function from the **forcats** package, as described in the page on [Factors](factors.llms.md). Note, classifying the factor levels doesn’t visibly change the data, but the `arrange()` command does sort it by Country, age category, and sex.

``` r
country_data <- country_data %>% 
  mutate(
    Country = fct_relevel(Country, "A", "B"),
      
    Sex = fct_relevel(Sex, "Male", "Female"),
        
    age_cat5 = fct_relevel(
      age_cat5,
      "0-4", "5-9", "10-14", "15-19",
      "20-24", "25-29",  "30-34", "35-39",
      "40-44", "45-49", "50-54", "55-59",
      "60-64", "65-69", "70-74",
      "75-79", "80-84", "85")) %>% 
          
  arrange(Country, age_cat5, Sex)
```

***CAUTION:*** If you have few deaths per stratum, consider using 10-, or 15-year categories, instead of 5-year categories for age.

### Load reference population

Lastly, for the direct standardisation, we import the reference population (world “standard population” by sex)

``` r
# Reference population
standard_pop_data <- appliedepidata::get_data(name = "world_standard_population_by_sex")
```

### Clean reference population

The age category values in the `country_data` and `standard_pop_data` data frames will need to be aligned.

Currently, the values of the column `age_cat5` from the `standard_pop_data` data frame contain the word “years” and “plus”, while those of the `country_data` data frame do not. We will have to make the age category values match. We use `str_replace_all()` from the **stringr** package, as described in the page on [Characters and strings](characters_strings.llms.md), to replace these patterns with no space `""`.

The function `calculate_dsr()` takes the standard population through its `stdpop =` argument, so the column can have any name. We rename it to `"pop"` because the code below uses `stdpop = pop`.

``` r
# Remove specific string from column values
standard_pop_clean <- standard_pop_data %>%
     mutate(
          age_cat5 = str_replace_all(age_cat5, "years", ""),   # remove "year"
          age_cat5 = str_replace_all(age_cat5, "plus", ""),    # remove "plus"
          age_cat5 = str_replace_all(age_cat5, " ", "")) %>%   # remove " " space
     
     rename(pop = WorldStandardPopulation)   # change col name to "pop", the column given to stdpop = in calculate_dsr()
```

***CAUTION:*** If you try to use `str_replace_all()` to remove a plus *symbol*, it won’t work because it is a special symbol. “Escape” the specialnes by putting two back slashes in front, as in `str_replace_call(column, "\\+", "")`.

### Create dataset with standard population

Finally, the package **PHEindicatormethods**, detailed [below](#standard_phe), expects the standard populations joined to the country event and population counts. So, we will create a dataset `all_data` for that purpose.

``` r
all_data <- left_join(country_data, standard_pop_clean, by=c("age_cat5", "Sex"))
```

This complete dataset looks like this:

## 21.3 **PHEindicatormethods** package

We calculate standardized rates with the **PHEindicatormethods** package. This package allows you to calculate directly as well as indirectly standardized rates. We will show both.

This section will use the `all_data` data frame created at the end of the Preparation section. This data frame includes the country populations, death events, and the world standard reference population. You can view it [here](#standard_all).

### Directly standardized rates

Below, we first group the data by Country and then pass it to the function `calculate_dsr()` to get directly standardized rates per country.

Of note - `calculate_dsr()` needs the reference (standard) population as a **column within the country-specific data frame**. Give the name of that column to the `stdpop =` argument. In our example below, this column is `pop`.

See the help with `?calculate_dsr` or the links in the References section for more information.

``` r
# Calculate rates per country directly standardized for age and sex
mortality_ds_rate_phe <- all_data %>%
     group_by(Country) %>%
     PHEindicatormethods::calculate_dsr(
          x = Deaths,                 # column with observed number of events
          n = Population,             # column with non-standard pops for each stratum
          stdpop = pop)               # standard populations for each stratum

# Print table
knitr::kable(mortality_ds_rate_phe)
```

| Country | total_count | total_pop | value | lowercl | uppercl | confidence | statistic | method |
|:---|---:|---:|---:|---:|---:|:---|:---|:---|
| A | 11344 | 86790567 | 23.56686 | 23.08107 | 24.05944 | 95% | dsr per 100000 | Dobson |
| B | 9955 | 52898281 | 19.32549 | 18.45516 | 20.20882 | 95% | dsr per 100000 | Dobson |

### Indirectly standardized rates

For indirect standardization, you need a reference population with the number of deaths and number of population per stratum. In this example, we will be calculating rates for country A *using country B as the reference population*, as the `standard_pop_clean` reference population does not include number of deaths per stratum.

Below, we first create the reference population from country B. Then, we pass mortality and population data for country A, combine it with the reference population, and pass it to the function `calculate_ISRate()`, to get indirectly standardized rates. Of course, you can do it also vice versa.

Of note - in our example below, the reference population is provided as a separate data frame. In this case, we make sure that `x =`, `n =`, `x_ref =` and `n_ref =` vectors are all ordered by the same standardization category (stratum) values as that in our country-specific data frame, as records will be matched by position.

See the help with `?phr_isr` or the links in the References section for more information.

``` r
# Create reference population
refpopCountryB <- country_data %>% 
  filter(Country == "B") 

# Calculate rates for country A indirectly standardized by age and sex
mortality_is_rate_phe_A <- country_data %>%
     filter(Country == "A") %>%
     PHEindicatormethods::calculate_ISRate(
          x = Deaths,                 # column with observed number of events
          n = Population,             # column with non-standard pops for each stratum
          x_ref = refpopCountryB$Deaths,  # reference number of deaths for each stratum
          n_ref = refpopCountryB$Population)  # reference population for each stratum

# Print table
knitr::kable(mortality_is_rate_phe_A)
```

| observed | expected | ref_rate | value | lowercl | uppercl | confidence | statistic | method |
|---:|---:|---:|---:|---:|---:|:---|:---|:---|
| 11344 | 15847.42 | 18.81914 | 13.47123 | 13.22446 | 13.72145 | 95% | indirectly standardised rate per 100000 | Byars |

## 21.4 Resources

For another example using **PHEindicatormethods**, please go to [this website](https://mran.microsoft.com/snapshot/2018-10-22/web/packages/PHEindicatormethods/vignettes/IntroductiontoPHEindicatormethods.html)

See the **PHEindicatormethods** [reference pdf file](https://cran.r-project.org/web/packages/PHEindicatormethods/PHEindicatormethods.pdf)
