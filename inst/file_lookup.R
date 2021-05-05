## List files used in handbook, maintaining structure and allowing for multi-file, single call downloads


## epi r handbook files full (relative) path
all_files <- list.files(
  path = "inst/extdata/",
  full.names = FALSE,
  recursive = TRUE
  )


## epi r handbook files name only
all_file_names <- basename(all_files)


## df as lookup
erh_files <- data.frame(
  path = all_files,
  name = all_file_names
)


## load dplyr
library(dplyr, warn.conflicts = FALSE)


## get file name without extension
file_groups <- erh_files %>%
  mutate(sans_ext = gsub("\\.\\D*", "", name)) %>%
  group_by(sans_ext) %>%
  group_indices()


## full lkup df
erh_files$file_group <- file_groups


## save RDS
saveRDS(erh_files, file = "inst/file_lookup.rds")
