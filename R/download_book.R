#' @title download_book
#'
#' @description Need to refer to the Epidemiology R Handbook offline in the field?
#' Easily download the handbook in advance with this function
#'
#' @param lang language for the file to download. Defaults to 'en'
#' @param save_loc **Run with no arguments to pick a directory interactively** Directory the book should be downloaded to
#'
#' @export
download_book <- function(lang = "en", save_loc = rstudioapi::selectDirectory()){

  stopifnot(!is.null("path"))

  save_file <- paste0(save_loc, "/Epi_R_Handbook_offline.html")

  url_list = c("https://github.com/appliedepi/epiRhandbook_eng/raw/master/offline_long/index.", lang, ".html")
  url = paste(url_list, collapse='')

  download.file(url = url, destfile = save_file)

  cli::cli_alert_success("Complete! The Offline version of the hanbook is available here: {save_loc}")

}
