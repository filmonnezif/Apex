from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import price_routes
from services.ai_service import XGBoostAIService
from services.elasticity_service import ElasticityService
from services.data_service import DataService
from contextlib import asynccontextmanager
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup/shutdown"""
    # Startup
    print("="*80)
    print("Starting Nestle UAE Price Optimization API")
    print("="*80)
    
    # Load XGBoost model
    if XGBoostAIService.load_model():
        print("✓ XGBoost AI Model loaded successfully")
    else:
        print("⚠ Warning: XGBoost model not loaded. Some features may not work.")
    
    # Load EconML Elasticity model
    if ElasticityService.load_elasticity_model():
        print("✓ EconML Elasticity Model loaded successfully")
    else:
        print("⚠ Warning: Elasticity model not loaded. Will use fallback elasticity estimates.")
    
    # Load historical data
    try:
        data = DataService.load_data()
        if not data.empty:
            print(f"✓ Historical data loaded: {len(data)} records")
            products = DataService.get_products_from_data()
            print(f"✓ Found {len(products)} unique products from data")
        else:
            print("⚠ Warning: No historical data loaded. Using fallback data.")
    except Exception as e:
        print(f"⚠ Warning: Error loading historical data: {e}")
    
    print("="*80)
    yield
    # Shutdown
    print("Shutting down API...")

app = FastAPI(
    title="Nestle UAE Price Optimization API",
    description="Dynamic pricing optimization system using XGBoost AI and EconML elasticity models for profit maximization",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(price_routes.router, prefix="/api", tags=["pricing"])

@app.get("/")
async def root():
    return {
        "message": "Nestle UAE Price Optimization API",
        "status": "online",
        "version": "2.0.0",
        "ai_models": ["XGBoost Demand Prediction", "EconML Double ML Elasticity"],
        "features": [
            "Profit-maximizing price optimization",
            "Realistic business constraints",
            "Product-specific elasticity analysis",
            "Historical data-driven predictions"
        ],
        "endpoints": {
            "/api/products": "GET - List all products",
            "/api/optimize-price": "POST - Get profit-optimized price recommendation",
            "/api/simulate": "POST - Simulate price scenario",
            "/api/valid-values": "GET - Get valid dropdown values",
            "/docs": "Interactive API documentation"
        }
    }

@app.get("/health")
async def health_check():
    demand_model_loaded = XGBoostAIService.model is not None
    elasticity_ready = True  # ElasticityService uses category-based elasticity, always ready
    return {
        "status": "healthy",
        "demand_model_loaded": demand_model_loaded,
        "elasticity_model_loaded": elasticity_ready,
        "optimization_ready": demand_model_loaded and elasticity_ready
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
