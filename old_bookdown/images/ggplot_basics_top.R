

linelist <- rio::import(here::here("data", "case_linelists", "linelist_cleaned.rds"))



ggplot()

p <- ggplot(data = linelist %>% drop_na(age, wt_kg, gender))+
     geom_point(aes(x = age, y = wt_kg, color = gender))+
     theme_minimal()+
     labs(title = "Patient weight by age and gender",
          caption = "Data as of 12 February 2014, n = 5862",
          subtitle = "Among patients admitted during a fictional Ebola outbreak",
          color = "Gender",
          x = "Age (years)",
          y = "Weight (kg)")+
     theme(legend.position = "bottom", 
           axis.text = element_text(size = 15, face = "bold"),
           axis.title = element_text(size = 15, face = "bold"),
           plot.title = element_text(size = 22, face = "bold"))

ggExtra::ggMarginal(p, type = "density", groupFill = T)
