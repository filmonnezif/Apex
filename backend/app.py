"""
FastAPI application for Nestle UAE Product Demand Prediction
Serves predictions using the trained XGBoost model
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI(
    title="Nestle UAE Demand Prediction API",
    description="API for predicting product demand based on various features",
    version="1.0.0"
)

# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'xgboost_demand_model.pkl')
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print(f"✓ Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model from {MODEL_PATH}: {e}")
    model = None

# Define request schema
class DemandPredictionRequest(BaseModel):
    """Input features for demand prediction"""
    
    # Product information
    product_name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    emirate: str = Field(..., description="UAE Emirate (Dubai, Abu Dhabi, etc.)")
    store_type: str = Field(..., description="Store type (Hypermarket, Supermarket, etc.)")
    
    # Price
    price_per_sales_unit: float = Field(..., description="Price per sales unit", gt=0)
    
    # Time features
    is_weekend: int = Field(0, description="Is weekend (0 or 1)", ge=0, le=1)
    is_holiday: int = Field(0, description="Is holiday (0 or 1)", ge=0, le=1)
    month: int = Field(..., description="Month (1-12)", ge=1, le=12)
    day_of_week: int = Field(..., description="Day of week (0=Monday, 6=Sunday)", ge=0, le=6)
    day_of_month: int = Field(..., description="Day of month (1-31)", ge=1, le=31)
    
    # Rolling features (optional - will use defaults if not provided)
    rolling_3day_mean: Optional[float] = Field(None, description="3-day rolling mean of sales")
    rolling_7day_mean: Optional[float] = Field(None, description="7-day rolling mean of sales")
    rolling_30day_mean: Optional[float] = Field(None, description="30-day rolling mean of sales")
    rolling_3day_std: Optional[float] = Field(None, description="3-day rolling std of sales")
    rolling_7day_std: Optional[float] = Field(None, description="7-day rolling std of sales")
    rolling_30day_std: Optional[float] = Field(None, description="30-day rolling std of sales")
    
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "product_name": "NESTLE NESQUIK 330GR(C) BOX",
                "category": "Breakfast Cereals",
                "emirate": "Dubai",
                "store_type": "Hypermarket",
                "price_per_sales_unit": 15.5,
                "is_weekend": 0,
                "is_holiday": 0,
                "month": 10,
                "day_of_week": 1,
                "day_of_month": 27,
                "rolling_3day_mean": 50.0,
                "rolling_7day_mean": 48.5,
                "rolling_30day_mean": 52.0,
                "rolling_3day_std": 5.2,
                "rolling_7day_std": 6.8,
                "rolling_30day_std": 8.1
            }
        }
    )

class DemandPredictionResponse(BaseModel):
    """Response with predicted demand"""
    predicted_demand: float = Field(..., description="Predicted sales units")
    input_features: dict = Field(..., description="Input features used for prediction")
    model_info: dict = Field(..., description="Model information")

# Valid values for categorical variables
VALID_PRODUCTS = [
    'NESTLE NESQUIK 330GR(C) BOX',
    'NESCAFE 3IN1 CLASSIC 20GX24 BOX (CM)',
    'MAGGI BBQ & GRILLS SEASONING 150G TUB',
    'NESCAFE LATTE 240ML TIN',
    'PURINA FRISK.CHICKEN IN GRAVY JUNI.85G S',
    'NESTLE CHOCAPIC C/B 25GR (C) WRP'
]

VALID_CATEGORIES = [
    'Breakfast Cereals', 'Hot Beverages', 'Culinary', 'Pet Care',
    'BREAKFAST CEREAL', 'Culinary Products', 'CULINARY',
    'BREAKFAST CEREALS', 'HOT BEVERAGES', 'PET CARE',  # Add uppercase variations
    'TOTAL COFFEE', 'ICE COFFEE', 'MUESLI / CEREAL & NUTRITIONAL BAR'  # From actual data
]

VALID_EMIRATES = [
    'Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 
    'Ras Al Khaimah', 'Fujairah', 'Umm Al Quwain'
]

VALID_STORE_TYPES = [
    'Hypermarket', 'Supermarket', 'Mini Market', 
    'Convenience Store', 'Traditional', 'Online'
]

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Nestle UAE Demand Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "/predict": "POST - Get demand prediction",
            "/health": "GET - Check API health",
            "/model-info": "GET - Get model information",
            "/valid-values": "GET - Get valid categorical values",
            "/docs": "Interactive API documentation"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "status": "healthy",
        "model_loaded": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/model-info")
def model_info():
    """Get information about the loaded model"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": "XGBoost Regressor",
        "target_variable": "sales_units",
        "features_count": model.n_features_in_ if hasattr(model, 'n_features_in_') else "unknown",
        "model_params": model.get_params() if hasattr(model, 'get_params') else {}
    }

@app.get("/valid-values")
def get_valid_values():
    """Get valid categorical values"""
    return {
        "products": VALID_PRODUCTS,
        "categories": VALID_CATEGORIES,
        "emirates": VALID_EMIRATES,
        "store_types": VALID_STORE_TYPES
    }

def prepare_features(request: DemandPredictionRequest) -> pd.DataFrame:
    """Prepare features for model prediction with one-hot encoding"""
    
    # Create base dataframe with numerical features
    data = {
        'price_per_sales_unit': [request.price_per_sales_unit],
        'is_weekend': [request.is_weekend],
        'is_holiday': [request.is_holiday],
        'month': [request.month],
        'day_of_week': [request.day_of_week],
        'day_of_month': [request.day_of_month],
        'rolling_3day_mean': [request.rolling_3day_mean or 50.0],
        'rolling_7day_mean': [request.rolling_7day_mean or 50.0],
        'rolling_30day_mean': [request.rolling_30day_mean or 50.0],
        'rolling_3day_std': [request.rolling_3day_std or 5.0],
        'rolling_7day_std': [request.rolling_7day_std or 5.0],
        'rolling_30day_std': [request.rolling_30day_std or 5.0],
    }
    
    # Add categorical variables
    categorical_data = {
        'emirate': [request.emirate],
        'store_type': [request.store_type],
        'product_name': [request.product_name],
        'category': [request.category]
    }
    
    df = pd.DataFrame(data)
    cat_df = pd.DataFrame(categorical_data)
    
    # One-hot encode categorical variables
    cat_encoded = pd.get_dummies(cat_df, drop_first=True)
    
    # Combine numerical and encoded categorical features
    result_df = pd.concat([df, cat_encoded], axis=1)
    
    # The model expects specific columns - we need to ensure all expected columns exist
    # Get the feature names the model was trained on
    if hasattr(model, 'feature_names_in_'):
        expected_features = model.feature_names_in_
        
        # Add missing columns with 0 values
        for feature in expected_features:
            if feature not in result_df.columns:
                result_df[feature] = 0
        
        # Reorder columns to match training
        result_df = result_df[expected_features]
    
    return result_df

@app.post("/predict", response_model=DemandPredictionResponse)
def predict_demand(request: DemandPredictionRequest):
    """
    Predict product demand based on input features
    
    - **product_name**: Name of the product
    - **category**: Product category
    - **emirate**: UAE Emirate
    - **store_type**: Type of retail store
    - **price_per_sales_unit**: Price per unit
    - **is_weekend**: 1 if weekend, 0 otherwise
    - **is_holiday**: 1 if holiday, 0 otherwise
    - **month**: Month (1-12)
    - **day_of_week**: Day of week (0=Monday, 6=Sunday)
    - **day_of_month**: Day of month (1-31)
    - **rolling features**: Historical sales statistics (optional)
    """
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Validate categorical values
    if request.product_name not in VALID_PRODUCTS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid product_name. Must be one of: {VALID_PRODUCTS}"
        )
    
    if request.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {VALID_CATEGORIES}"
        )
    
    if request.emirate not in VALID_EMIRATES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid emirate. Must be one of: {VALID_EMIRATES}"
        )
    
    if request.store_type not in VALID_STORE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid store_type. Must be one of: {VALID_STORE_TYPES}"
        )
    
    try:
        # Prepare features
        features_df = prepare_features(request)
        
        # Make prediction
        prediction = model.predict(features_df)[0]
        
        # Ensure prediction is non-negative
        prediction = max(0, prediction)
        
        return DemandPredictionResponse(
            predicted_demand=float(prediction),
            input_features=request.dict(),
            model_info={
                "model_type": "XGBoost Regressor",
                "prediction_unit": "sales_units",
                "features_used": len(features_df.columns)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    # Run the API server
    print("="*80)
    print("Starting Nestle UAE Demand Prediction API")
    print("="*80)
    print("API Documentation: http://localhost:8000/docs")
    print("="*80)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
