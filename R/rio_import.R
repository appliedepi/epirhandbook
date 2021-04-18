#' @title import_erh
#'
#' Epi R Handbook data drop-in replacement for rio::import, as used in the handbook
#'
#' @param data
#'
#' @export
import_erh <- function(path = NULL){

  new_path <- system.file("extdata", path, package = "epirhandbook", mustWork = T)

}
