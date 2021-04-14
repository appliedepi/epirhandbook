#################################
###    MY EXAMPLE R SCRIPT    ###
#################################
# Write a comment after one or more hash symbols

################
# Purpose: To demonstrate an example in the R basics page of the R Handbook
# Authors: Neale Batra, Gandalf the Grey, Samwise Gamgee 
# Version control: 
#     - Feb 2020 Created (NB)
#     - March 2020 plot added by (GtG)
#################

# load packages
###############
pacman::p_load(
     rio,         # for import/export of files
     here,        # for locating files in my R project
     tidyverse,   # for data management and visualization
     lubridate,   # for working with dates
     incidence    # for making epicurves 
     )

# load linelist data
####################
linelist_raw <- import(here("data", "cases", "clean", "linelist_2020-10-05.csv"))

# clean linelist
################
linelist <- linelist_raw %>% 
   mutate(
    date_onset = as.Date(date_onset),               # ensure is class Date
    epiweek_onset = floor_date(date_onset, "week")) # create epiweek column

# plot daily epicurve
#####################
daily_incidence <- incidence(    # create incidence object
     dates    = linelist$date_onset,
     interval = "day") 

plot(daily_incidence)            # plot daily epicurve
ggsave(here("outputs", "epicurves", "daily_incidence.png")) # save as PNG

