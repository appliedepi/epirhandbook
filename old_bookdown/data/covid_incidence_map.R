## Script for updating covid incidence map data
library(dplyr)
library(ggplot2)
library(purrr)
## https://covid19.who.int/table

covid_cases <- read.csv("~/Downloads/WHO COVID-19 global table data January 9th 2021 at 8.46.06 PM.csv")

## https://geojson-maps.ash.ms
map <- geojsonio::geojson_sf("data/africa_countries.geojson")

covid_cases<- covid_cases %>% 
  select(Name, Cases...cumulative.total.per.1.million.population) %>% 
  rename(Cumulative_incidence = "Cases...cumulative.total.per.1.million.population")

covid_cases[which(!covid_cases$Name %in% map$sovereignt),"Name"]
which(!covid_cases$Name %in% map$sovereignt)
covid_cases[22,"Name"] <- "Swaziland"
covid_cases[24,"Name"] <- "Republic of Congo"
covid_cases[40,"Name"] <- "Guinea Bissau"
covid_cases[11,"Name"] <- "Ivory Coast"


map<-map %>% 
  select(id, geometry) %>% 
  left_join(covid_cases, by = c("id"="Name"))


ggplot(map, aes(fill=Cumulative_incidence, label = id))+
  geom_sf()+
  theme_minimal()+
  theme(legend.position = "bottom")

write.csv(covid_cases, file = "./data/covid_incidence.csv")