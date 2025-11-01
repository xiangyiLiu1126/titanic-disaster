# Minimal, stable set for data, modeling, and printing
pkgs <- c(
  "readr",      # fast CSV IO
  "dplyr",      # data wrangling
  "tidyr",      # NA handling / tidying
  "stringr",    # string helpers
  "caret",      # modeling convenience
  "e1071"       # caret dependency (for some models)
)

to_install <- setdiff(pkgs, rownames(installed.packages()))
if (length(to_install)) {
  install.packages(to_install, repos = "https://cloud.r-project.org")
}
