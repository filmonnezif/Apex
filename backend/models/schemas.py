from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Product(BaseModel):
    id: str
    name: str
    category: str
    current_price: float
    cost: Optional[float] = None
    unit: str = "unit"

class DemandPredictionInput(BaseModel):
    """Input for XGBoost demand prediction"""
    product_name: str
    category: str
    emirate: str
    store_type: str
    price_per_sales_unit: float
    is_weekend: int = 0
    is_holiday: int = 0
    month: int
    day_of_week: int
    day_of_month: int
    rolling_3day_mean: Optional[float] = 50.0
    rolling_7day_mean: Optional[float] = 50.0
    rolling_30day_mean: Optional[float] = 50.0
    rolling_3day_std: Optional[float] = 5.0
    rolling_7day_std: Optional[float] = 5.0
    rolling_30day_std: Optional[float] = 5.0

class PriceOptimizationRequest(BaseModel):
    product_id: str
    product_name: str
    category: str
    emirate: str
    store_type: str
    current_price: float
    month: int
    day_of_week: int
    day_of_month: int
    is_weekend: int = 0
    is_holiday: int = 0
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class SimulationRequest(BaseModel):
    """Request for price simulation across different scenarios"""
    product_name: str
    category: str
    emirate: str
    store_type: str
    month: int
    day_of_week: int
    day_of_month: int
    is_weekend: int = 0
    is_holiday: int = 0
    price: float

class DemandPrediction(BaseModel):
    price: float
    predicted_demand: float
    revenue: float

class ElasticityData(BaseModel):
    elasticity_coefficient: float
    elasticity_category: str  # elastic, inelastic, unitary
    interpretation: str
    price_range: dict

class PriceRecommendation(BaseModel):
    recommended_price: float
    current_price: float
    price_change_percentage: float
    expected_demand: float
    expected_revenue: float
    confidence_score: float
    reasoning: str

class OptimizationResponse(BaseModel):
    product_name: str
    category: str
    emirate: str
    store_type: str
    current_metrics: dict
    recommendation: PriceRecommendation
    elasticity: ElasticityData
    demand_curve: List[DemandPrediction]
    timestamp: str

class SimulationResponse(BaseModel):
    """Response for price simulation"""
    product_name: str
    scenario: dict
    predicted_demand: float
    predicted_revenue: float
    elasticity_coefficient: float
    demand_level: Optional[str] = "Normal"
    timestamp: str
