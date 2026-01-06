"""
FastAPI REST API for Heart Disease Prediction Model
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("heart-disease-api")

# Initialize FastAPI app
app = FastAPI(
    title="Heart Disease Prediction API",
    description="API for predicting heart disease risk using machine learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expected features
FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
    "exang", "oldpeak", "slope", "ca", "thal"
]

# Model path
MODEL_PATH = Path("models/model_pipeline.pkl")

# Global variable to store the model
model = None


class HeartDiseaseInput(BaseModel):
    """Input schema for heart disease prediction"""
    age: int = Field(..., ge=1, le=150, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="Sex (0 = Female, 1 = Male)")
    cp: int = Field(..., ge=0, le=3, description="Chest pain type (0-3)")
    trestbps: int = Field(..., ge=80, le=200, description="Resting blood pressure (mmHg)")
    chol: int = Field(..., ge=100, le=600, description="Serum cholesterol (mg/dl)")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120 mg/dl (0 = No, 1 = Yes)")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG results (0-2)")
    thalach: int = Field(..., ge=60, le=220, description="Maximum heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise induced angina (0 = No, 1 = Yes)")
    oldpeak: float = Field(..., ge=0.0, le=10.0, description="ST depression induced by exercise")
    slope: int = Field(..., ge=0, le=2, description="Slope of peak exercise ST segment (0-2)")
    ca: int = Field(..., ge=0, le=4, description="Number of major vessels colored by fluoroscopy (0-4)")
    thal: int = Field(..., ge=0, le=3, description="Thalassemia (0 = Normal, 1 = Fixed defect, 2 = Reversible defect, 3 = Unknown)")

    class Config:
        schema_extra = {
            "example": {
                "age": 63,
                "sex": 1,
                "cp": 3,
                "trestbps": 145,
                "chol": 233,
                "fbs": 1,
                "restecg": 0,
                "thalach": 150,
                "exang": 0,
                "oldpeak": 2.3,
                "slope": 0,
                "ca": 0,
                "thal": 1
            }
        }


class HeartDiseaseOutput(BaseModel):
    """Output schema for heart disease prediction"""
    prediction: int = Field(..., description="Predicted class (0 = No disease, 1 = Disease)")
    probability: float = Field(..., description="Probability of heart disease")
    risk_level: str = Field(..., description="Risk level (Low/Medium/High)")
    message: str = Field(..., description="Interpretation message")


class BatchPredictionInput(BaseModel):
    """Input schema for batch predictions"""
    instances: List[HeartDiseaseInput]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_path: str


def load_model():
    """Load the trained model pipeline"""
    global model
    try:
        if not MODEL_PATH.exists():
            logger.error(f"Model file not found at {MODEL_PATH}")
            return None
        
        model = joblib.load(MODEL_PATH)
        logger.info(f"Model loaded successfully from {MODEL_PATH}")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None


def get_risk_level(probability: float) -> str:
    """Determine risk level based on probability"""
    if probability < 0.3:
        return "Low"
    elif probability < 0.7:
        return "Medium"
    else:
        return "High"


def get_message(prediction: int, probability: float) -> str:
    """Generate interpretation message"""
    if prediction == 0:
        return f"Low risk of heart disease detected (Probability: {probability:.2%}). Continue maintaining a healthy lifestyle."
    else:
        risk = get_risk_level(probability)
        return f"{risk} risk of heart disease detected (Probability: {probability:.2%}). Consider consulting a healthcare professional."


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    logger.info("Starting Heart Disease Prediction API...")
    load_model()
    if model is None:
        logger.warning("⚠️ Model not loaded! Predictions will fail until model is available.")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Heart Disease Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH)
    }


@app.post("/predict", response_model=HeartDiseaseOutput, tags=["Prediction"])
async def predict(input_data: HeartDiseaseInput):
    """
    Predict heart disease risk for a single patient
    
    Args:
        input_data: Patient medical data
        
    Returns:
        Prediction result with probability and risk level
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please ensure the model file exists at models/model_pipeline.pkl"
        )
    
    try:
        # Convert input to DataFrame
        input_dict = input_data.dict()
        df = pd.DataFrame([input_dict], columns=FEATURES)
        
        # Make prediction
        prediction = model.predict(df)[0]
        probability = model.predict_proba(df)[0][1]  # Probability of class 1 (disease)
        
        # Get risk level and message
        risk_level = get_risk_level(probability)
        message = get_message(prediction, probability)
        
        logger.info(f"Prediction made: {prediction}, Probability: {probability:.4f}")
        
        return HeartDiseaseOutput(
            prediction=int(prediction),
            probability=float(probability),
            risk_level=risk_level,
            message=message
        )
    
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during prediction: {str(e)}"
        )


@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(batch_input: BatchPredictionInput):
    """
    Predict heart disease risk for multiple patients
    
    Args:
        batch_input: List of patient medical data
        
    Returns:
        List of prediction results
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please ensure the model file exists at models/model_pipeline.pkl"
        )
    
    try:
        # Convert inputs to DataFrame
        inputs = [item.dict() for item in batch_input.instances]
        df = pd.DataFrame(inputs, columns=FEATURES)
        
        # Make predictions
        predictions = model.predict(df)
        probabilities = model.predict_proba(df)[:, 1]
        
        # Prepare results
        results = []
        for pred, prob in zip(predictions, probabilities):
            risk_level = get_risk_level(prob)
            message = get_message(pred, prob)
            
            results.append({
                "prediction": int(pred),
                "probability": float(prob),
                "risk_level": risk_level,
                "message": message
            })
        
        logger.info(f"Batch prediction made for {len(results)} instances")
        
        return {"predictions": results}
    
    except Exception as e:
        logger.error(f"Error during batch prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during batch prediction: {str(e)}"
        )


@app.get("/model/info", tags=["Model"])
async def model_info():
    """Get information about the loaded model"""
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    return {
        "model_type": str(type(model).__name__),
        "features": FEATURES,
        "num_features": len(FEATURES),
        "model_path": str(MODEL_PATH)
    }


if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
