# global.R script

pacman::p_load("tidyverse", "lubridate", "shiny")

# read data
malaria_data <- rio::import(here::here("data", "facility_count_data.rds")) %>% 
     as_tibble()


malaria_data <- malaria_data %>%
     select(-newid) %>%
     pivot_longer(cols = starts_with("malaria_"), names_to = "age_group", values_to = "cases_reported")

all_districts <- c("All", unique(malaria_data$District))

# data frame of location names by district
facility_list <- malaria_data %>%
     group_by(location_name, District) %>%
     summarise() %>% 
     ungroup()



source(here::here("funcs", "plot_epicurve.R"), local = TRUE)



