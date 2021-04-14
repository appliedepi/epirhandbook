#' @title download_book
#'
#' @description Need to refer to the Epidemiology R Handbook offline in the field?
#' Easily download the handbook in advance with this function
#'
#' @param save_loc Directory the book should be downloaded to
#'
#' @importFrom utils download.file
#'
#' @export
download_book <- function(save_loc = getwd()){

  save_file <- paste0(save_loc, "Epi_R_Handbook_offline.html")
  download.file(url = "https://github.com/epirhandbook/Epi_R_handbook/raw/master/offline_long/Epi_R_Handbook_offline.html",
                destfile = save_file)

}
