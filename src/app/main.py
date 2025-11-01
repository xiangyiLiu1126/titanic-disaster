
import argparse
from pathlib import Path
import sys

def parse_args():
    p = argparse.ArgumentParser(description="Titanic pipeline env check + loader")
    p.add_argument("--data_dir", type=str, default="src/data", help="Folder containing train.csv/test.csv")
    p.add_argument("--mode", choices=["check", "summary"], default="check",
                   help="check=verify files exist; summary=print simple counts")
    return p.parse_args()

def main():
    args = parse_args()
    data_dir = Path(args.data_dir)

    train = data_dir / "train.csv"
    test = data_dir / "test.csv"

    if not train.exists() or not test.exists():
        print(f"[ERROR] Expected train.csv and test.csv under: {data_dir.resolve()}")
        print("Place your downloaded Kaggle files locally (do not commit them).")
        sys.exit(1)

    if args.mode == "check":
        print("[OK] Environment looks good. Found:")
        print(f" - {train.resolve()}")
        print(f" - {test.resolve()}")
        return

    if args.mode == "summary":
        import pandas as pd
        df = pd.read_csv(train)
        print("[SUMMARY]")
        print(f"Rows: {len(df)}  |  Columns: {len(df.columns)}")
        print("Columns:", ", ".join(df.columns))
        print(df.head(3).to_string(index=False))

if __name__ == "__main__":
    main()
