server <- function(input, output, session) {
     
     malaria_plot <- reactive({
          plot_epicurve(malaria_data, district = input$select_district, agegroup = input$select_agegroup, facility = input$select_facility)
     })
     
     
     
     observe({
          
          if (input$select_district == "All") {
               new_choices <- facility_list$location_name
          } else {
               new_choices <- facility_list %>%
                    filter(District == input$select_district) %>%
                    pull(location_name)
          }
          
          new_choices <- c("All", new_choices)
          
          updateSelectInput(session, inputId = "select_facility",
                            choices = new_choices)
          
     })
     
     
     output$malaria_epicurve <- renderPlot(
          malaria_plot()
     )
     
     output$download_epicurve <- downloadHandler(
          
          filename = function() {
               stringr::str_glue("malaria_epicurve_{input$select_district}.png")
          },
          
          content = function(file) {
               ggsave(file, 
                      malaria_plot(),
                      width = 8, height = 5, dpi = 300)
          }
          
     )
     
     # render data table to ui
     output$raw_data <- DT::renderDT(
          malaria_data
     )
     
     
}
