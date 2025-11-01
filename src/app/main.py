import argparse
from pathlib import Path
import sys
import pandas as pd

# sklearn
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score


def parse_args():
    p = argparse.ArgumentParser(description="Titanic pipeline: env check, summary, train, predict")
    p.add_argument("--data_dir", type=str, default="src/data",
                   help="Folder containing train.csv/test.csv (and optionally gender_submission.csv)")
    p.add_argument("--mode", choices=["check", "summary", "train", "predict", "all"], default="check",
                   help="check=verify files; summary=print dataset info; train=train & report train accuracy; "
                        "predict=load test.csv, predict, and report accuracy vs gender_submission.csv if present; "
                        "all=summary+train+predict")
    return p.parse_args()


# --------------------------
# Helper functions
# --------------------------
def _expected_paths(data_dir: Path):
    train = data_dir / "train.csv"
    test = data_dir / "test.csv"
    gender = data_dir / "gender_submission.csv"  # optional; used to approximate test accuracy
    return train, test, gender


def env_check(data_dir: Path) -> bool:
    train, test, gender = _expected_paths(data_dir)
    ok = True
    print("[CHECK] Looking for CSVs under:", data_dir.resolve())
    for p in [train, test]:
        if p.exists():
            print(f"[OK]  Found: {p.resolve()}")
        else:
            ok = False
            print(f"[ERROR] Missing: {p.resolve()}")
    if gender.exists():
        print(f"[INFO] Found optional file for test evaluation: {gender.resolve()}")
    else:
        print("[INFO] Optional 'gender_submission.csv' not found; test accuracy will be skipped.")
    return ok


def load_train(data_dir: Path) -> pd.DataFrame:
    fp = data_dir / "train.csv"
    print(f"[LOAD] Reading {fp.resolve()}")
    df = pd.read_csv(fp)
    print(f"[LOAD] train shape={df.shape} columns={list(df.columns)}")
    return df


def load_test(data_dir: Path) -> pd.DataFrame:
    fp = data_dir / "test.csv"
    print(f"[LOAD] Reading {fp.resolve()}")
    df = pd.read_csv(fp)
    print(f"[LOAD] test shape={df.shape} columns={list(df.columns)}")
    return df


def load_gender_submission(data_dir: Path) -> pd.DataFrame | None:
    fp = data_dir / "gender_submission.csv"
    if fp.exists():
        print(f"[LOAD] Reading {fp.resolve()} (used only to approximate test accuracy)")
        df = pd.read_csv(fp)
        print(f"[LOAD] gender_submission shape={df.shape}")
        return df
    return None


def build_model_pipeline() -> Pipeline:
    """
    Features we’ll use:
      - Numeric: Age, SibSp, Parch, Fare  (median-imputed)
      - Categorical: Pclass, Sex, Embarked (most-freq-imputed + one-hot)
    """
    numeric_features = ["Age", "SibSp", "Parch", "Fare"]
    categorical_features = ["Pclass", "Sex", "Embarked"]

    numeric_tf = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median"))
    ])

    categorical_tf = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ohe", OneHotEncoder(handle_unknown="ignore"))
    ])

    pre = ColumnTransformer(
        transformers=[
            ("num", numeric_tf, numeric_features),
            ("cat", categorical_tf, categorical_features),
        ]
    )

    clf = LogisticRegression(max_iter=1000)

    pipe = Pipeline(steps=[
        ("preprocess", pre),
        ("clf", clf)
    ])

    print("[MODEL] Built sklearn Pipeline with numeric+categorical preprocessing and LogisticRegression.")
    print("[MODEL] Numeric features:", numeric_features)
    print("[MODEL] Categorical features:", categorical_features)
    return pipe


def train_and_report(train_df: pd.DataFrame) -> Pipeline:
    # Target & features
    y = train_df["Survived"]
    X = train_df.drop(columns=["Survived", "Cabin", "Ticket", "Name"])  # drop noisy/high-missing cols

    print(f"[TRAIN] Using {X.shape[0]} rows, {X.shape[1]} features (after drops).")
    print(f"[TRAIN] Columns now: {list(X.columns)}")

    pipe = build_model_pipeline()
    pipe.fit(X, y)

    # Resubstitution accuracy (accuracy on the training rows)
    yhat_train = pipe.predict(X)
    train_acc = accuracy_score(y, yhat_train)
    print(f"[METRIC] Training accuracy (resubstitution): {train_acc:.4f}")

    return pipe


def predict_test_and_report(pipe: Pipeline, test_df: pd.DataFrame, gender_df: pd.DataFrame | None):
    # Ensure the same feature drops as during training
    X_test = test_df.drop(columns=["Cabin", "Ticket", "Name"], errors="ignore")
    print(f"[PREDICT] Test rows={X_test.shape[0]} cols={X_test.shape[1]}")
    preds = pipe.predict(X_test)
    out = pd.DataFrame({"PassengerId": test_df["PassengerId"], "PredictedSurvived": preds})
    print("[PREDICT] First 10 predictions:")
    print(out.head(10).to_string(index=False))

    # “Accuracy” against gender_submission (NOTE: this is NOT the ground truth; it’s Kaggle’s baseline)
    if gender_df is not None:
        merged = out.merge(gender_df, on="PassengerId", how="inner")
        approx_acc = accuracy_score(merged["Survived"], merged["PredictedSurvived"])
        print(f"[METRIC] Approx. test accuracy vs gender_submission.csv: {approx_acc:.4f}")
        print("         (This is ONLY for local checking; Kaggle ground truth is not provided.)")
    else:
        print("[INFO] Skipping test accuracy: gender_submission.csv not found.")


def run_summary(train_df: pd.DataFrame):
    print("[SUMMARY] train .info():")
    print(train_df.info())
    print("\n[SUMMARY] train .describe(include='all') (top 8 columns):")
    with pd.option_context('display.max_columns', 50, 'display.width', 200):
        print(train_df.describe(include='all').iloc[:, :8])


def main():
    args = parse_args()
    data_dir = Path(args.data_dir)

    if not env_check(data_dir):
        print("[EXIT] Missing files. See above errors.")
        sys.exit(1)

    if args.mode in ("summary", "all"):
        train_df = load_train(data_dir)
        run_summary(train_df)

    if args.mode in ("train", "all"):
        train_df = load_train(data_dir)
        pipe = train_and_report(train_df)
        # Persist model to disk if you want (optional), but not required by the assignment.

    if args.mode in ("predict", "all"):
        # If we already trained in this run ('all'), reuse that pipe; otherwise train quickly now.
        try:
            pipe
        except NameError:
            train_df = load_train(data_dir)
            pipe = train_and_report(train_df)

        test_df = load_test(data_dir)
        gender_df = load_gender_submission(data_dir)
        predict_test_and_report(pipe, test_df, gender_df)


if __name__ == "__main__":
    main()

