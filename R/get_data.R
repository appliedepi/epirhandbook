#' @title get_data
#'
#' Access data used in examples in the Handbook
#'
#' @param file Name and file extension of the data to be downloaded *string* or "ALL" which will save all Epidemiology R Handbook example files
#' @param path **Default opens a directory picker interactively**. Path on your computer where the file(s) should be saved to *string*
#'
#' @export
get_data <- function(file = NULL, path = rstudioapi::selectDirectory()){

  ## must select a file
  stopifnot(!is.null(file))

  ## normalise in case given manually
  path <- normalizePath(path)

  ## load file_lkup
  file_lkup <- readRDS(system.file(package = "epirhandbook", "file_lookup.rds"))

  ## check file looked for is in file_lkup
  if(file %in% file_lkup$name){

    ## file group
    group <- file_lkup[which(file_lkup$name == file), "file_group"]

    ## path to file
    files_to_copy <- file_lkup[which(file_lkup$file_group == group), "path"]

  } else if (file == "all") {

    files_to_copy <- file_lkup$path

  } else stop("You must choose a filename shown in the handbook or \"all\"")

  # files_to_copy <- lapply(files_to_copy, system.file, package = "epirhandbook")

  files_to_copy <- system.file(package = "epirhandbook", "extdata", files_to_copy)

  success <- lapply(files_to_copy, file.copy, to = path, overwrite = TRUE)

  if(all(as.logical(success))) cli::cli_alert_success("File(s) successfully saved here: {path}")

}
