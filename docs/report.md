# End-to-End MLOps Report: Heart Disease Classifier

## Overview
- Objective: Predict heart disease risk and deploy a production-ready API using MLOps best practices.
- Dataset: UCI Cleveland Heart Disease (cleaned to CSV).

## Setup / Install
- Python 3.10+, `pip install -r requirements.txt`.
- Download dataset: `python scripts/download_data.py`.
- Train: `python src/models/train.py --fast`.
- Serve API: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

## EDA Summary
- Class balance reported in notebooks.
- Histograms for key numeric features.
- Correlation heatmap.

## Feature Engineering & Modeling
- Numeric: impute median + standard scale.
- Categorical: impute most frequent + one-hot.
- Models: Logistic Regression and Random Forest with CV grid search.
- Metrics: Accuracy, Precision, Recall, ROC-AUC (holdout & overall).

## Experiment Tracking
- MLflow local tracking in `mlruns/`.
- Logged params, metrics, models for both algorithms.
- Start UI: `mlflow ui --backend-store-uri mlruns --port 5000`.

## Packaging & Reproducibility
- Saved best pipeline to `models/model_pipeline.pkl`.
- Preprocessor embedded in pipeline; schema saved in `models/schema.json`.
- Requirements listed in `requirements.txt`.

## CI/CD
- GitHub Actions: Lint, tests, data download, fast training, upload artifacts.
- Pipeline fails fast on errors and shows logs in Actions UI.

## Containerization
- Dockerfile runs FastAPI app; exposes `/predict`, `/health`, `/metrics`.
- Sample request body provided in README.

## Deployment
- Kubernetes manifests for Deployment, Service (NodePort 30080), optional Ingress.
- Validate via Service URL or Ingress.

## Monitoring & Logging
- Basic request logging.
- Prometheus metrics via `/metrics` endpoint.
- Grafana/Loki can be added; instructions noted in README.

## Architecture Diagram (Text)
- scripts/download_data.py -> data/heart.csv
- src/data/preprocess.py -> ColumnTransformer
- src/models/train.py -> MLflow (mlruns/) + models/model_pipeline.pkl
- app/main.py (FastAPI) -> Docker -> Kubernetes Service -> Ingress (optional)

## Screenshots & Video
- Place CI run screenshots and kubectl outputs in `screenshots/`.
- See `docs/video_instructions.md` to record end-to-end demo.

## Repository Link
- Add your GitHub repo URL here.
