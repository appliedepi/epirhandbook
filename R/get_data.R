#' @title get_data
#'
#' Access data used in examples in the Handbook
#'
#' @param path Path on your computer where the file(s) should be saved to *string*
#' @param file Name and file extension of the data to be downloaded *string*
#' @param all Save all the handbook data files? *Boolean (TRUE/FALSE)*
#'
#' @export
get_data <- function(path = NULL, file = NULL, all = FALSE){

  stopifnot(!is.null(path))

  path <- normalizePath(path)



}
