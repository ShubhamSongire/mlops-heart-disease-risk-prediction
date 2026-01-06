import argparse
import os
from pathlib import Path
import json
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import joblib

from src.data.preprocess import get_preprocessor, load_data


def train_and_evaluate(X, y, fast: bool = False):
    preprocessor = get_preprocessor()

    # Logistic Regression pipeline
    lr = LogisticRegression(max_iter=1000, n_jobs=None)
    lr_pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", lr)])

    # Random Forest pipeline
    rf = RandomForestClassifier(random_state=42)
    rf_pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", rf)])

    cv = StratifiedKFold(n_splits=3 if fast else 5, shuffle=True, random_state=42)

    lr_param_grid = {
        "model__C": [0.1, 1.0] if fast else [0.01, 0.1, 1.0, 10.0],
        "model__penalty": ["l2"],
        "model__solver": ["lbfgs"],
    }

    rf_param_grid = {
        "model__n_estimators": [100] if fast else [100, 200, 400],
        "model__max_depth": [None, 5] if fast else [None, 5, 10],
        "model__min_samples_split": [2, 5],
    }

    # MLflow setup - use file-based backend for compatibility
    mlflow_dir = Path(__file__).parent.parent.parent
    mlflow_uri = str(mlflow_dir.resolve() / "mlruns")
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("HeartDisease")

    best_model_name = None
    best_auc = -1.0
    best_estimator = None

    for name, pipe, param_grid in [
        ("LogisticRegression", lr_pipe, lr_param_grid),
        ("RandomForest", rf_pipe, rf_param_grid),
    ]:
        with mlflow.start_run(run_name=name):
            grid = GridSearchCV(pipe, param_grid, cv=cv, scoring="roc_auc", n_jobs=-1)
            grid.fit(X, y)
            best = grid.best_estimator_
            # Predict proba on full dataset for a quick overall ROC-AUC
            y_proba = best.predict_proba(X)[:, 1]
            auc = roc_auc_score(y, y_proba)
            mlflow.log_params(grid.best_params_)
            mlflow.log_metric("roc_auc", auc)

            # Basic metrics on a holdout split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
            best.fit(X_train, y_train)
            y_pred = best.predict(X_test)
            y_test_proba = best.predict_proba(X_test)[:, 1]

            metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred)),
                "recall": float(recall_score(y_test, y_pred)),
                "roc_auc_holdout": float(roc_auc_score(y_test, y_test_proba)),
            }
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(best, artifact_path=f"model_{name}")

            if auc > best_auc:
                best_auc = auc
                best_model_name = name
                best_estimator = best

    return best_model_name, best_auc, best_estimator


def save_best_model(best_estimator):
    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    out_path = models_dir / "model_pipeline.pkl"
    joblib.dump(best_estimator, out_path)

    # Save schema (expected feature names)
    schema_path = models_dir / "schema.json"
    from src.data.preprocess import FEATURES
    with open(schema_path, "w") as f:
        json.dump({"features": FEATURES}, f)

    print(f"Saved best pipeline to {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default="data/heart.csv", help="Path to cleaned CSV")
    parser.add_argument("--fast", action="store_true", help="Run smaller hyperparameter search for CI")
    args = parser.parse_args()

    X, y = load_data(args.data)
    best_name, best_auc, best_estimator = train_and_evaluate(X, y, fast=args.fast)
    print(f"Best model: {best_name} (ROC-AUC={best_auc:.3f})")
    save_best_model(best_estimator)


if __name__ == "__main__":
    main()
