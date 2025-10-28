from fastapi import APIRouter, HTTPException, Query
from models.schemas import (
    PriceOptimizationRequest,
    OptimizationResponse,
    Product,
    SimulationRequest,
    SimulationResponse
)
from services.ai_service import XGBoostAIService
from services.data_service import DataService
from typing import List
import random

# Currency conversion rate from USD to AED
USD_TO_AED = 3.7
AED_TO_USD = 1 / USD_TO_AED

router = APIRouter()

# Load products from actual data on startup
def get_products_list():
    """Get products from CSV data"""
    # Currency conversion rate from USD to AED
    USD_TO_AED = 3.7
    
    products = DataService.get_products_from_data()
    if not products:
        # Fallback to hardcoded products if data loading fails (prices in AED)
        return [
            {"id": "NES001", "name": "NESTLE NESQUIK 330GR(C) BOX", "category": "Breakfast Cereals", "current_price": 57.35, "unit": "box"},
            {"id": "NES002", "name": "NESCAFE 3IN1 CLASSIC 20GX24 BOX (CM)", "category": "Hot Beverages", "current_price": 92.50, "unit": "box"},
            {"id": "NES003", "name": "MAGGI BBQ & GRILLS SEASONING 150G TUB", "category": "Culinary", "current_price": 44.40, "unit": "tub"},
            {"id": "NES004", "name": "NESCAFE LATTE 240ML TIN", "category": "Hot Beverages", "current_price": 31.45, "unit": "tin"},
            {"id": "NES005", "name": "PURINA FRISK.CHICKEN IN GRAVY JUNI.85G S", "category": "Pet Care", "current_price": 31.45, "unit": "pouch"},
            {"id": "NES006", "name": "NESTLE CHOCAPIC C/B 25GR (C) WRP", "category": "Breakfast Cereals", "current_price": 12.95, "unit": "wrap"}
        ]
    
    # Convert prices from USD to AED for products loaded from data
    for product in products:
        product['current_price'] = round(product['current_price'] * USD_TO_AED, 2)
        # Convert cost to AED as well
        if 'cost' in product:
            product['cost'] = round(product['cost'] * USD_TO_AED, 2)
    
    return products

PRODUCTS = []

def get_valid_values():
    """Get valid values from data"""
    if not PRODUCTS:
        return {
            "emirates": ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras Al Khaimah', 'Fujairah', 'Umm Al Quwain'],
            "store_types": ['Hypermarket', 'Supermarket', 'Mini Market', 'Convenience Store', 'Traditional', 'Online']
        }
    
    # Get from first product's data
    first_product = PRODUCTS[0]['name']
    emirates, store_types = DataService.get_available_locations(first_product)
    
    return {
        "emirates": emirates,
        "store_types": store_types
    }

VALID_VALUES = {}

@router.get("/products", response_model=List[Product])
async def get_products():
    """Get all available products from actual data."""
    global PRODUCTS
    if not PRODUCTS:
        PRODUCTS = get_products_list()
    return PRODUCTS

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID."""
    global PRODUCTS
    if not PRODUCTS:
        PRODUCTS = get_products_list()
    
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/valid-values")
async def get_valid_values_endpoint():
    """Get valid values for dropdowns from actual data"""
    global PRODUCTS, VALID_VALUES
    
    if not PRODUCTS:
        PRODUCTS = get_products_list()
    
    if not VALID_VALUES:
        VALID_VALUES = get_valid_values()
    
    return {
        "emirates": VALID_VALUES["emirates"],
        "store_types": VALID_VALUES["store_types"],
        "products": [p["name"] for p in PRODUCTS],
        "categories": list(set(p["category"] for p in PRODUCTS))
    }

@router.get("/product-stats/{product_id}")
async def get_product_statistics(product_id: str):
    """Get detailed statistics for a product"""
    global PRODUCTS
    if not PRODUCTS:
        PRODUCTS = get_products_list()
    
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    stats = DataService.get_product_stats(product["name"])
    return {
        "product": product,
        "statistics": stats
    }

@router.post("/optimize-price", response_model=OptimizationResponse)
async def optimize_price(request: PriceOptimizationRequest):
    """
    Optimize price for a given product using XGBoost AI model.
    Returns optimal price, demand predictions, and elasticity analysis.
    Backend expects prices in AED and returns results in AED.
    """
    try:
        # Load the XGBoost model
        if not XGBoostAIService.load_model():
            raise HTTPException(
                status_code=503,
                detail="AI model not available. Please ensure the XGBoost model file exists."
            )
        
        # Validate inputs
        if request.current_price <= 0:
            raise HTTPException(
                status_code=400, 
                detail="Price must be a positive number"
            )
        
        # Convert incoming AED price to USD for the model
        current_price_usd = request.current_price * AED_TO_USD
        min_price_usd = request.min_price * AED_TO_USD if request.min_price else None
        max_price_usd = request.max_price * AED_TO_USD if request.max_price else None
        
        # Get optimization results from AI service (in USD)
        result = XGBoostAIService.optimize_price(
            product_name=request.product_name,
            category=request.category,
            emirate=request.emirate,
            store_type=request.store_type,
            current_price=current_price_usd,
            month=request.month,
            day_of_week=request.day_of_week,
            day_of_month=request.day_of_month,
            is_weekend=request.is_weekend,
            is_holiday=request.is_holiday,
            min_price=min_price_usd,
            max_price=max_price_usd
        )
        
        # Convert response from USD to AED
        result_dict = result.dict()
        
        # Convert current_metrics prices and revenue
        result_dict['current_metrics']['price'] = round(result_dict['current_metrics']['price'] * USD_TO_AED, 2)
        result_dict['current_metrics']['revenue'] = round(result_dict['current_metrics']['revenue'] * USD_TO_AED, 2)
        if 'profit' in result_dict['current_metrics']:
            result_dict['current_metrics']['profit'] = round(result_dict['current_metrics']['profit'] * USD_TO_AED, 2)
        if 'estimated_cost' in result_dict['current_metrics']:
            result_dict['current_metrics']['estimated_cost'] = round(result_dict['current_metrics']['estimated_cost'] * USD_TO_AED, 2)
        
        # Convert recommendation prices and revenue
        result_dict['recommendation']['recommended_price'] = round(result_dict['recommendation']['recommended_price'] * USD_TO_AED, 2)
        result_dict['recommendation']['current_price'] = round(result_dict['recommendation']['current_price'] * USD_TO_AED, 2)
        result_dict['recommendation']['expected_revenue'] = round(result_dict['recommendation']['expected_revenue'] * USD_TO_AED, 2)
        
        # Convert demand_curve prices and revenue
        for point in result_dict['demand_curve']:
            point['price'] = round(point['price'] * USD_TO_AED, 2)
            point['revenue'] = round(point['revenue'] * USD_TO_AED, 2)
        
        # Convert elasticity price_range
        result_dict['elasticity']['price_range']['min'] = round(result_dict['elasticity']['price_range']['min'] * USD_TO_AED, 2)
        result_dict['elasticity']['price_range']['max'] = round(result_dict['elasticity']['price_range']['max'] * USD_TO_AED, 2)
        
        return OptimizationResponse(**result_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

@router.post("/simulate", response_model=SimulationResponse)
async def simulate_price(request: SimulationRequest):
    """
    Simulate a specific price scenario.
    Returns predicted demand, revenue, and elasticity for given inputs.
    Backend expects prices in AED and returns results in AED.
    """
    try:
        # Load the XGBoost model
        if not XGBoostAIService.load_model():
            raise HTTPException(
                status_code=503,
                detail="AI model not available. Please ensure the XGBoost model file exists."
            )
        
        # Validate inputs
        if request.price <= 0:
            raise HTTPException(
                status_code=400, 
                detail="Price must be a positive number"
            )
        
        # Convert incoming AED price to USD for the model
        price_usd = request.price * AED_TO_USD
        
        # Get simulation results (in USD)
        result = XGBoostAIService.simulate_price_scenario(
            product_name=request.product_name,
            category=request.category,
            emirate=request.emirate,
            store_type=request.store_type,
            price=price_usd,
            month=request.month,
            day_of_week=request.day_of_week,
            day_of_month=request.day_of_month,
            is_weekend=request.is_weekend,
            is_holiday=request.is_holiday
        )
        
        # Convert response from USD to AED
        result_dict = result.dict()
        result_dict['scenario']['price'] = round(result_dict['scenario']['price'] * USD_TO_AED, 2)
        result_dict['predicted_revenue'] = round(result_dict['predicted_revenue'] * USD_TO_AED, 2)
        
        # Convert baseline metrics if present
        if 'baseline_price' in result_dict['scenario']:
            result_dict['scenario']['baseline_price'] = round(result_dict['scenario']['baseline_price'] * USD_TO_AED, 2)
        
        return SimulationResponse(**result_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

@router.get("/analytics/summary")
async def get_analytics_summary():
    """
    Get overall analytics summary for all products.
    Returns revenue in AED.
    """
    total_revenue = sum(p["current_price"] * random.uniform(500, 1500) for p in PRODUCTS)
    
    return {
        "total_products": len(PRODUCTS),
        "total_revenue_estimate": round(total_revenue, 2),
        "categories": {
            cat: len([p for p in PRODUCTS if p["category"] == cat])
            for cat in set(p["category"] for p in PRODUCTS)
        }
    }
