plot_epicurve <- function(data, district = "All", agegroup = "malaria_tot", facility = "All") {
     
     if (!("All" %in% district)) {
          data <- data %>%
               filter(District %in% district)
          
          plot_title_district <- stringr::str_glue("{paste0(district, collapse = ",")} districts")
          
     } else {
          
          plot_title_district <- "all districts"
          
     }
     
     # if no remaining data, return NULL
     if (nrow(data) == 0) {
          
          return(NULL)
     }
     
     data <- data %>%
          filter(age_group == agegroup)
     
     
     # if no remaining data, return NULL
     if (nrow(data) == 0) {
          
          return(NULL)
     }
     
     if (agegroup == "malaria_tot") {
          agegroup_title <- "All ages"
     } else {
          agegroup_title <- stringr::str_glue("{str_remove(agegroup, 'malaria_rdt')} years")
     }
     
     if (!("All" %in% facility)) {
          data <- data %>%
               filter(location_name == facility)
          
          plot_title_facility <- facility
          
     } else {
          
          plot_title_facility <- "all facilities"
          
     }
     
     # if no remaining data, return NULL
     if (nrow(data) == 0) {
          
          return(NULL)
     }
     
     
     
     ggplot(data, aes(x = data_date, y = cases_reported)) +
          geom_bar(stat = "identity", fill = "darkred") +
          theme_minimal() +
          labs(
               x = "date",
               y = "number of cases",
               title = stringr::str_glue("Malaria cases - {plot_title_district}; {plot_title_facility}"),
               subtitle = agegroup_title
          )
     
     
     
}
