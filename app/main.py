import time
from pathlib import Path
from typing import Dict

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("heart-api")

# Prometheus metrics
REQUEST_COUNT = Counter("requests_total", "Total requests", ["endpoint"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", ["endpoint"])

# Expected features
FEATURES = [
    "age","sex","cp","trestbps","chol","fbs","restecg","thalach",
    "exang","oldpeak","slope","ca","thal"
]

class HeartInput(BaseModel):
    age: float
    sex: int
    cp: int
    trestbps: float
    chol: float
    fbs: int
    restecg: int
    thalach: float
    exang: int
    oldpeak: float
    slope: int
    ca: float
    thal: int

app = FastAPI(title="Heart Disease Risk API")

# Add CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model pipeline
MODEL_PATH = Path("models/model_pipeline.pkl")
if not MODEL_PATH.exists():
    logger.warning("Model not found at models/model_pipeline.pkl. Train first: python src/models/train.py --fast")
PIPELINE = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

@app.get("/health")
def health():
    REQUEST_COUNT.labels(endpoint="/health").inc()
    return {"status": "ok", "model_loaded": PIPELINE is not None}

@app.post("/predict")
def predict(input_data: HeartInput):
    start = time.time()
    REQUEST_COUNT.labels(endpoint="/predict").inc()

    if PIPELINE is None:
        return {"error": "Model not loaded. Train and place models/model_pipeline.pkl."}

    data = pd.DataFrame([{k: getattr(input_data, k) for k in FEATURES}])
    proba = float(PIPELINE.predict_proba(data)[:, 1][0])
    pred = int(proba >= 0.5)

    REQUEST_LATENCY.labels(endpoint="/predict").observe(time.time() - start)
    logger.info(f"Prediction made - Risk: {pred}, Probability: {proba}")
    return {"prediction": pred, "probability": proba}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
