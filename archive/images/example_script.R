#################################
###    MY EXAMPLE R SCRIPT    ###
#################################
# Write a comment after one or more hash symbols

# load packages
###############
pacman::p_load(
     rio,         
     here,        
     tidyverse,   
     lubridate,   
     incidence2     
     )

# load linelist data
####################
linelist_raw <- import(here("data", "case_linelists",
                            "linelist_cleaned.rds"))

# clean linelist
################
linelist <- linelist_raw %>% 
   mutate(
    date_onset = as.Date(date_onset),               # ensure is class Date
    epiweek_onset = floor_date(date_onset, "week")) # create epiweek column

# plot daily epicurve
#####################
daily_incidence <- incidence(linelist, "date_onset", interval = "week", groups = "age_cat", na_as_group = T)

plot(daily_incidence, fill = age_cat, col_pal = muted, title = "Epidemic curve")

ggsave(here("outputs", "epicurves", "daily_incidence.png")) # save as PNG
