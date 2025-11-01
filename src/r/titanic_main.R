suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(stringr)
  library(caret)
})

# --------- arg parsing (simple, no extra packages) ----------
args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  hit <- which(args == flag)
  if (length(hit) == 0 || hit == length(args)) return(default)
  args[hit + 1]
}

mode <- get_arg("--mode", "check")
data_dir <- get_arg("--data_dir", "src/data")

message("[ARGS] mode=", mode, "  data_dir=", data_dir)

# --------- helpers ----------
fp_train <- file.path(data_dir, "train.csv")
fp_test  <- file.path(data_dir, "test.csv")
fp_gender <- file.path(data_dir, "gender_submission.csv") # optional

env_check <- function() {
  ok <- TRUE
  message("[CHECK] Looking for CSVs under: ", normalizePath(data_dir))
  if (file.exists(fp_train)) message("[OK]  Found: ", normalizePath(fp_train)) else {message("[ERROR] Missing: train.csv"); ok <- FALSE}
  if (file.exists(fp_test))  message("[OK]  Found: ", normalizePath(fp_test))  else {message("[ERROR] Missing: test.csv"); ok <- FALSE}
  if (file.exists(fp_gender)) message("[INFO] Found optional gender_submission.csv (for approx test accuracy).")
  if (!ok) message("[EXIT] Missing files.")
  ok
}

load_train <- function() {
  message("[LOAD] Reading train.csv")
  df <- readr::read_csv(fp_train, show_col_types = FALSE)
  message("[LOAD] train shape: ", nrow(df), " x ", ncol(df))
  message("[LOAD] columns: ", paste(names(df), collapse=", "))
  df
}

load_test <- function() {
  message("[LOAD] Reading test.csv")
  df <- readr::read_csv(fp_test, show_col_types = FALSE)
  message("[LOAD] test shape: ", nrow(df), " x ", ncol(df))
  message("[LOAD] columns: ", paste(names(df), collapse=", "))
  df
}

load_gender <- function() {
  if (file.exists(fp_gender)) {
    message("[LOAD] Reading gender_submission.csv")
    readr::read_csv(fp_gender, show_col_types = FALSE)
  } else NULL
}

run_summary <- function(train) {
  message("[SUMMARY] glimpse:")
  print(utils::head(train, 5))
  message("[SUMMARY] NAs per column:")
  print(sapply(train, function(x) sum(is.na(x))))
}

# Basic preprocessing aligned with your Python pipeline
prep_data <- function(df, is_train = TRUE) {
  # coerce types
  df <- df %>%
    mutate(
      Pclass = factor(Pclass),
      Sex = factor(Sex),
      Embarked = factor(Embarked)
    )

  # impute
  med_age  <- median(df$Age, na.rm = TRUE)
  med_fare <- median(df$Fare, na.rm = TRUE)
  mode_emb <- names(sort(table(df$Embarked), decreasing = TRUE))[1]

  df$Age[is.na(df$Age)]       <- med_age
  df$Fare[is.na(df$Fare)]     <- med_fare
  df$Embarked[is.na(df$Embarked)] <- mode_emb

  # drop columns not used
  drop_cols <- c("Cabin","Ticket","Name")
  drop_cols <- intersect(drop_cols, names(df))
  df <- df[, setdiff(names(df), drop_cols)]

  message("[PREP] After preprocess: rows=", nrow(df), " cols=", ncol(df))
  message("[PREP] Columns: ", paste(names(df), collapse=", "))
  df
}

train_model <- function(train) {
  # features/target
  y <- factor(train$Survived)
  X <- train %>% select(-Survived)

  # caret logistic regression via glm (binomial)
  ctrl <- trainControl(method = "none")
  message("[MODEL] Training logistic regression (glm binomial)...")
  fit <- caret::train(
    x = X, y = y,
    method = "glm",
    family = binomial(),
    trControl = ctrl
  )

  # resubstitution accuracy
  pred_train <- predict(fit, X)
  acc <- mean(pred_train == y)
  message(sprintf("[METRIC] Training accuracy (resubstitution): %.4f", acc))
  fit
}

predict_and_report <- function(model, test, gender) {
  preds <- predict(model, test)
  out <- data.frame(PassengerId = test$PassengerId, PredictedSurvived = as.integer(preds) - 1L)
  message("[PREDICT] First 10 predictions:")
  print(utils::head(out, 10))

  if (!is.null(gender)) {
    merged <- merge(out, gender, by = "PassengerId")
    approx_acc <- mean(merged$PredictedSurvived == merged$Survived)
    message(sprintf("[METRIC] Approx. test accuracy vs gender_submission.csv: %.4f", approx_acc))
    message("[NOTE] This is only a check; Kaggle test labels are not public.")
  } else {
    message("[INFO] Skipping test accuracy: gender_submission.csv not found.")
  }
}

# --------- run modes ----------
if (!env_check()) quit(status = 1)

if (mode %in% c("summary", "all")) {
  tr <- load_train()
  run_summary(tr)
}

if (mode %in% c("train", "all")) {
  tr <- load_train() %>% prep_data(is_train = TRUE)
  model <- train_model(tr)
}

if (mode %in% c("predict", "all")) {
  # if not trained in this session, train now
  if (!exists("model")) {
    tr <- load_train() %>% prep_data(is_train = TRUE)
    model <- train_model(tr)
  }
  te <- load_test() %>% prep_data(is_train = FALSE)
  gs <- load_gender()
  predict_and_report(model, te, gs)
}
