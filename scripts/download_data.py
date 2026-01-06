import os
from pathlib import Path
import pandas as pd

UCI_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
HEADERS = [
    "age","sex","cp","trestbps","chol","fbs","restecg","thalach",
    "exang","oldpeak","slope","ca","thal","num"
]

def main():
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    raw_path = data_dir / "processed.cleveland.data"
    csv_path = data_dir / "heart.csv"

    print("Downloading UCI Cleveland dataset...")
    df = pd.read_csv(UCI_URL, names=HEADERS, na_values="?", header=None)
    # Convert multiclass target (num 0-4) to binary: 0 -> 0 (no disease), 1-4 -> 1 (disease)
    df["target"] = (df["num"] > 0).astype(int)
    df.drop(columns=["num"], inplace=True)

    # Save cleaned CSV
    df.to_csv(csv_path, index=False)
    print(f"Saved cleaned dataset to {csv_path}")

if __name__ == "__main__":
    main()
