ui <- fluidPage(
     
     titlePanel("Malaria facility visualisation app"),
     
     sidebarLayout(
          
          sidebarPanel(
               # selector for district
               selectInput(
                    inputId = "select_district",
                    label = "Select district",
                    choices = all_districts,
                    selected = "All",
                    multiple = FALSE
               ),
               # selector for age group
               selectInput(
                    inputId = "select_agegroup",
                    label = "Select age group",
                    choices = c(
                         "All ages" = "malaria_tot",
                         "0-4 yrs" = "malaria_rdt_0-4",
                         "5-14 yrs" = "malaria_rdt_5-14",
                         "15+ yrs" = "malaria_rdt_15"
                    ), 
                    selected = "All",
                    multiple = FALSE
               ),
               # selector for facility
               selectInput(
                    inputId = "select_facility",
                    label = "Select Facility",
                    choices = c("All", facility_list$location_name),
                    selected = "All"
               ),
               
               # horizontal line
               hr(),
               downloadButton(
                    outputId = "download_epicurve",
                    label = "Download plot"
               )
               
          ),
          
          mainPanel(
               tabsetPanel(
                    type = "tabs",
                    tabPanel(
                         "Epidemic Curves",
                         plotOutput("malaria_epicurve")
                    ),
                    tabPanel(
                         "Data",
                         DT::dataTableOutput("raw_data")
                    )
               ),
               br(),
               hr(),
               p("Welcome to the malaria facility visualisation app! To use this app, manipulate the widgets on the side to change the epidemic curve according to your preferences! To download a high quality image of the plot you've created, you can also download it with the download button. To see the raw data, use the raw data tab for an interactive form of the table. The data dictionary is as follows:"),
               tags$ul(
                    tags$li(tags$b("location_name"), " - the facility that the data were collected at"),
                    tags$li(tags$b("data_date"), " - the date the data were collected at"),
                    tags$li(tags$b("submitted_daate"), " - the date the data were submitted at"),
                    tags$li(tags$b("Province"), " - the province the data were collected at (all 'North' for this dataset)"),
                    tags$li(tags$b("District"), " - the district the data were collected at"),
                    tags$li(tags$b("age_group"), " - the age group the data were collected for (0-5, 5-14, 15+, and all ages)"),
                    tags$li(tags$b("cases_reported"), " - the number of cases reported for the facility/age group on the given date")
               )
               
               
          )
     )
)
