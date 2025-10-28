import pickle
import pandas as pd
import numpy as np
import math
import os
from typing import List, Tuple, Optional
from models.schemas import (
    DemandPrediction,
    DemandPredictionInput,
    ElasticityData,
    PriceRecommendation,
    OptimizationResponse,
    SimulationResponse
)
from services.data_service import DataService
from services.elasticity_service import ElasticityService
from datetime import datetime

class XGBoostAIService:
    """
    AI service for price optimization using trained XGBoost model.
    Includes demand prediction, price optimization, and elasticity analysis.
    """
    
    model = None
    MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'xgboost_demand_model.pkl')
    
    @classmethod
    def load_model(cls):
        """Load the trained XGBoost model"""
        if cls.model is None:
            try:
                with open(cls.MODEL_PATH, 'rb') as f:
                    cls.model = pickle.load(f)
                print(f"✓ XGBoost model loaded successfully from {cls.MODEL_PATH}")
            except Exception as e:
                print(f"Error loading model from {cls.MODEL_PATH}: {e}")
                cls.model = None
        return cls.model is not None
    
    @staticmethod
    def prepare_features(prediction_input: DemandPredictionInput) -> pd.DataFrame:
        """Prepare features for XGBoost model prediction"""
        # Create base dataframe with numerical features
        data = {
            'price_per_sales_unit': [prediction_input.price_per_sales_unit],
            'is_weekend': [prediction_input.is_weekend],
            'is_holiday': [prediction_input.is_holiday],
            'month': [prediction_input.month],
            'day_of_week': [prediction_input.day_of_week],
            'day_of_month': [prediction_input.day_of_month],
            'rolling_3day_mean': [prediction_input.rolling_3day_mean],
            'rolling_7day_mean': [prediction_input.rolling_7day_mean],
            'rolling_30day_mean': [prediction_input.rolling_30day_mean],
            'rolling_3day_std': [prediction_input.rolling_3day_std],
            'rolling_7day_std': [prediction_input.rolling_7day_std],
            'rolling_30day_std': [prediction_input.rolling_30day_std],
        }
        
        # Add categorical variables
        categorical_data = {
            'emirate': [prediction_input.emirate],
            'store_type': [prediction_input.store_type],
            'product_name': [prediction_input.product_name],
            'category': [prediction_input.category]
        }
        
        df = pd.DataFrame(data)
        cat_df = pd.DataFrame(categorical_data)
        
        # One-hot encode categorical variables
        cat_encoded = pd.get_dummies(cat_df, drop_first=True)
        
        # Combine numerical and encoded categorical features
        result_df = pd.concat([df, cat_encoded], axis=1)
        
        # Ensure all expected columns exist
        if hasattr(XGBoostAIService.model, 'feature_names_in_'):
            expected_features = XGBoostAIService.model.feature_names_in_
            
            # Add missing columns with 0 values
            for feature in expected_features:
                if feature not in result_df.columns:
                    result_df[feature] = 0
            
            # Reorder columns to match training
            result_df = result_df[expected_features]
        
        return result_df
    
    @staticmethod
    def predict_demand(prediction_input: DemandPredictionInput) -> float:
        """Predict demand using XGBoost model"""
        if not XGBoostAIService.load_model():
            raise Exception("Model not loaded")
        
        features_df = XGBoostAIService.prepare_features(prediction_input)
        prediction = XGBoostAIService.model.predict(features_df)[0]
        
        # Ensure prediction is non-negative
        return max(0, float(prediction))
    
    @staticmethod
    def get_rolling_averages_for_prediction(
        product_name: str,
        emirate: str,
        store_type: str
    ) -> dict:
        """Get rolling averages from historical data for more accurate predictions"""
        try:
            rolling_data = DataService.get_rolling_averages(product_name, emirate, store_type)
            return rolling_data
        except Exception as e:
            print(f"Warning: Could not get rolling averages from data: {e}")
            # Return defaults if data loading fails
            return {
                'rolling_3day_mean': 50.0,
                'rolling_7day_mean': 50.0,
                'rolling_30day_mean': 50.0,
                'rolling_3day_std': 5.0,
                'rolling_7day_std': 5.0,
                'rolling_30day_std': 5.0
            }
    
    @staticmethod
    def calculate_price_elasticity(
        product_name: str,
        category: str,
        emirate: str,
        store_type: str,
        base_price: float,
        month: int,
        day_of_week: int,
        day_of_month: int,
        is_weekend: int = 0,
        is_holiday: int = 0
    ) -> float:
        """
        Calculate price elasticity of demand using the XGBoost model.
        Elasticity = (% change in quantity) / (% change in price)
        """
        if not XGBoostAIService.load_model():
            raise Exception("Model not loaded")
        
        # Calculate demand at base price
        base_input = DemandPredictionInput(
            product_name=product_name,
            category=category,
            emirate=emirate,
            store_type=store_type,
            price_per_sales_unit=base_price,
            month=month,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            is_weekend=is_weekend,
            is_holiday=is_holiday
        )
        base_demand = XGBoostAIService.predict_demand(base_input)
        
        # Calculate demand at slightly higher price (1% increase)
        new_price = base_price * 1.01
        new_input = DemandPredictionInput(
            product_name=product_name,
            category=category,
            emirate=emirate,
            store_type=store_type,
            price_per_sales_unit=new_price,
            month=month,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            is_weekend=is_weekend,
            is_holiday=is_holiday
        )
        new_demand = XGBoostAIService.predict_demand(new_input)
        
        # Calculate elasticity
        if base_demand > 0 and base_price > 0:
            percent_change_quantity = ((new_demand - base_demand) / base_demand) * 100
            percent_change_price = ((new_price - base_price) / base_price) * 100
            elasticity = percent_change_quantity / percent_change_price if percent_change_price != 0 else 0
        else:
            elasticity = -1.5  # Default elasticity
        
        return elasticity
    
    @staticmethod
    def generate_elasticity_data(
        product_name: str,
        category: str,
        emirate: str,
        store_type: str,
        current_price: float,
        month: int,
        day_of_week: int,
        day_of_month: int,
        is_weekend: int = 0,
        is_holiday: int = 0
    ) -> ElasticityData:
        """Generate elasticity data with interpretation"""
        elasticity = XGBoostAIService.calculate_price_elasticity(
            product_name, category, emirate, store_type,
            current_price, month, day_of_week, day_of_month,
            is_weekend, is_holiday
        )
        
        # Interpret elasticity
        if abs(elasticity) > 1:
            category_type = "elastic"
            interpretation = "Demand is highly responsive to price changes. Lower prices significantly increase demand."
        elif abs(elasticity) < 1:
            category_type = "inelastic"
            interpretation = "Demand is relatively insensitive to price changes. Price increases won't significantly reduce demand."
        else:
            category_type = "unitary"
            interpretation = "Demand changes proportionally with price. Revenue remains relatively stable."
        
        # Calculate optimal price range based on elasticity
        if abs(elasticity) > 1:
            # Elastic: consider lower prices
            price_range = {
                "min": current_price * 0.7,
                "max": current_price * 1.2,
                "suggested_direction": "decrease"
            }
        else:
            # Inelastic: can increase prices
            price_range = {
                "min": current_price * 0.8,
                "max": current_price * 1.4,
                "suggested_direction": "increase"
            }
        
        return ElasticityData(
            elasticity_coefficient=round(elasticity, 3),
            elasticity_category=category_type,
            interpretation=interpretation,
            price_range=price_range
        )
    
    @staticmethod
    def generate_demand_curve(
        product_name: str,
        category: str,
        emirate: str,
        store_type: str,
        current_price: float,
        month: int,
        day_of_week: int,
        day_of_month: int,
        is_weekend: int = 0,
        is_holiday: int = 0,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        num_points: int = 20
    ) -> List[DemandPrediction]:
        """Generate demand curve using XGBoost predictions with historical rolling averages"""
        if not XGBoostAIService.load_model():
            raise Exception("Model not loaded")
        
        # Get rolling averages from historical data
        rolling_data = XGBoostAIService.get_rolling_averages_for_prediction(
            product_name, emirate, store_type
        )
        
        # Define price range
        if min_price is None:
            min_price = current_price * 0.6
        if max_price is None:
            max_price = current_price * 1.4
        
        price_step = (max_price - min_price) / (num_points - 1)
        demand_curve = []
        
        for i in range(num_points):
            price = min_price + (i * price_step)
            
            # Predict demand at this price using real rolling averages
            prediction_input = DemandPredictionInput(
                product_name=product_name,
                category=category,
                emirate=emirate,
                store_type=store_type,
                price_per_sales_unit=price,
                month=month,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                is_weekend=is_weekend,
                is_holiday=is_holiday,
                **rolling_data  # Use real rolling averages
            )
            
            demand = XGBoostAIService.predict_demand(prediction_input)
            revenue = price * demand
            
            demand_curve.append(DemandPrediction(
                price=round(price, 2),
                predicted_demand=round(demand, 0),
                revenue=round(revenue, 2)
            ))
        
        return demand_curve
    
    @staticmethod
    def find_optimal_price(
        demand_curve: List[DemandPrediction],
        current_price: float
    ) -> PriceRecommendation:
        """Find the price that maximizes revenue"""
        # Find price with maximum revenue
        optimal_point = max(demand_curve, key=lambda x: x.revenue)
        
        current_point = min(demand_curve, key=lambda x: abs(x.price - current_price))
        
        price_change = ((optimal_point.price - current_price) / current_price) * 100
        
        # Generate reasoning
        if optimal_point.price > current_price:
            reasoning = f"Increase price by {abs(price_change):.1f}%. The AI model predicts this will maximize revenue based on historical demand patterns."
        elif optimal_point.price < current_price:
            reasoning = f"Decrease price by {abs(price_change):.1f}%. The AI model suggests lower pricing will drive volume and increase total revenue."
        else:
            reasoning = "Current price is near optimal. Model suggests maintaining current pricing strategy."
        
        # Confidence score based on revenue improvement potential
        revenue_improvement = ((optimal_point.revenue - current_point.revenue) / current_point.revenue) * 100 if current_point.revenue > 0 else 0
        confidence = min(95, 70 + min(revenue_improvement * 2, 25))
        
        return PriceRecommendation(
            recommended_price=optimal_point.price,
            current_price=current_price,
            price_change_percentage=round(price_change, 2),
            expected_demand=optimal_point.predicted_demand,
            expected_revenue=optimal_point.revenue,
            confidence_score=round(confidence, 1),
            reasoning=reasoning
        )
    
    @staticmethod
    def optimize_price(
        product_name: str,
        category: str,
        emirate: str,
        store_type: str,
        current_price: float,
        month: int,
        day_of_week: int,
        day_of_month: int,
        is_weekend: int = 0,
        is_holiday: int = 0,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> OptimizationResponse:
        """
        Main optimization function combining XGBoost predictions, 
        elasticity-based profit optimization using EconML model.
        """
        # Get current demand prediction using XGBoost
        rolling_data = XGBoostAIService.get_rolling_averages_for_prediction(
            product_name, emirate, store_type
        )
        
        current_input = DemandPredictionInput(
            product_name=product_name,
            category=category,
            emirate=emirate,
            store_type=store_type,
            price_per_sales_unit=current_price,
            month=month,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            is_weekend=is_weekend,
            is_holiday=is_holiday,
            **rolling_data
        )
        
        current_demand = XGBoostAIService.predict_demand(current_input)
        
        # Use elasticity-based profit optimization
        optimization_result = ElasticityService.optimize_price_for_profit(
            product_name=product_name,
            emirate=emirate,
            store_type=store_type,
            current_price=current_price,
            current_demand=current_demand,
            month=month,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_holiday=is_holiday
        )
        
        # Build response using optimization result
        optimal_price = optimization_result['optimal_price']
        
        # Generate detailed demand curve around the optimal range
        curve_min = optimization_result['constraints']['min_price']
        curve_max = optimization_result['constraints']['max_price']
        
        demand_curve = []
        # Use adjusted elasticity for demand curve generation
        elasticity_coef = optimization_result.get('adjusted_elasticity', optimization_result.get('base_elasticity', -1.0))
        
        for price in np.linspace(curve_min, curve_max, 20):
            pred_demand = ElasticityService.predict_demand_at_price(
                current_demand, elasticity_coef, current_price, price
            )
            revenue = price * pred_demand
            demand_curve.append(DemandPrediction(
                price=round(price, 2),
                predicted_demand=round(pred_demand, 1),
                revenue=round(revenue, 2)
            ))
        
        # Create recommendation
        recommendation = PriceRecommendation(
            recommended_price=optimal_price,
            current_price=current_price,
            price_change_percentage=optimization_result['price_change_percentage'],
            expected_demand=optimization_result['optimal_metrics']['demand'],
            expected_revenue=optimization_result['optimal_metrics']['revenue'],
            confidence_score=85.0,  # High confidence with econml model
            reasoning=optimization_result['reasoning']
        )
        
        # Create elasticity data using ADJUSTED elasticity
        elasticity_coef = optimization_result.get('adjusted_elasticity', optimization_result.get('base_elasticity', -1.0))
        elasticity_data = ElasticityData(
            elasticity_coefficient=elasticity_coef,
            elasticity_category=optimization_result['elasticity_type'],
            interpretation=f"Product shows {optimization_result['elasticity_type']} demand behavior. "
                          f"A 1% price change results in {abs(elasticity_coef):.2f}% demand change.",
            price_range={
                "min": curve_min,
                "max": curve_max,
                "suggested_direction": "increase" if optimal_price > current_price else "decrease"
            }
        )
        
        # Enhance current metrics with profit information
        current_metrics = {
            "price": current_price,
            "demand": optimization_result['current_metrics']['demand'],
            "revenue": optimization_result['current_metrics']['revenue'],
            "profit": optimization_result['current_metrics']['profit'],
            "margin_pct": optimization_result['current_metrics']['margin'],
            "estimated_cost": optimization_result['estimated_cost']
        }
        
        return OptimizationResponse(
            product_name=product_name,
            category=category,
            emirate=emirate,
            store_type=store_type,
            current_metrics=current_metrics,
            recommendation=recommendation,
            elasticity=elasticity_data,
            demand_curve=demand_curve,
            timestamp=datetime.now().isoformat()
        )
    
    @staticmethod
    def simulate_price_scenario(
        product_name: str,
        category: str,
        emirate: str,
        store_type: str,
        price: float,
        month: int,
        day_of_week: int,
        day_of_month: int,
        is_weekend: int = 0,
        is_holiday: int = 0
    ) -> SimulationResponse:
        """Simulate a specific price scenario using dynamic elasticity based on demand trends"""
        
        # Get rolling averages from historical data
        rolling_data = XGBoostAIService.get_rolling_averages_for_prediction(
            product_name, emirate, store_type
        )
        
        # Get current/baseline price from data
        try:
            current_price = DataService.get_latest_price(product_name)
        except:
            current_price = price  # Fallback if no data
        
        # Predict demand at CURRENT price (baseline)
        baseline_input = DemandPredictionInput(
            product_name=product_name,
            category=category,
            emirate=emirate,
            store_type=store_type,
            price_per_sales_unit=current_price,
            month=month,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            is_weekend=is_weekend,
            is_holiday=is_holiday,
            **rolling_data
        )
        baseline_demand = XGBoostAIService.predict_demand(baseline_input)
        
        # Predict demand at SIMULATED price
        prediction_input = DemandPredictionInput(
            product_name=product_name,
            category=category,
            emirate=emirate,
            store_type=store_type,
            price_per_sales_unit=price,
            month=month,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            is_weekend=is_weekend,
            is_holiday=is_holiday,
            **rolling_data
        )
        
        simulated_demand = XGBoostAIService.predict_demand(prediction_input)
        revenue = price * simulated_demand
        
        # Get base elasticity from category (more reliable than numerical calculation)
        base_elasticity = ElasticityService.get_product_elasticity(
            product_name=product_name,
            emirate=emirate,
            store_type=store_type,
            current_price=current_price,
            month=month,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_holiday=is_holiday
        )
        
        # Calculate price change percentage
        price_change_percent = ((price - current_price) / current_price * 100) if current_price > 0 else 0
        
        # Apply dynamic elasticity adjustment based on demand trend
        adjusted_elasticity = ElasticityService.get_dynamic_elasticity(
            base_elasticity=base_elasticity,
            current_demand=baseline_demand,
            predicted_demand=simulated_demand,
            price_change_percent=price_change_percent
        )
        
        # Recalculate demand using adjusted elasticity if price differs from baseline
        if abs(price - current_price) > 0.01:
            adjusted_demand = ElasticityService.predict_demand_at_price(
                current_demand=baseline_demand,
                elasticity=adjusted_elasticity,
                current_price=current_price,
                new_price=price
            )
            # Blend AI prediction with elasticity-adjusted demand (60% AI, 40% elasticity)
            final_demand = simulated_demand * 0.6 + adjusted_demand * 0.4
        else:
            final_demand = simulated_demand
        
        final_revenue = price * final_demand
        
        # Determine demand level category
        if final_demand > baseline_demand * 1.3:
            demand_level = "Exceptional"
        elif final_demand > baseline_demand * 1.15:
            demand_level = "Very High"
        elif final_demand > baseline_demand * 1.05:
            demand_level = "High"
        elif final_demand > baseline_demand * 0.95:
            demand_level = "Normal"
        elif final_demand > baseline_demand * 0.85:
            demand_level = "Below Average"
        elif final_demand > baseline_demand * 0.7:
            demand_level = "Low"
        else:
            demand_level = "Very Low"
        
        return SimulationResponse(
            product_name=product_name,
            scenario={
                "price": price,
                "emirate": emirate,
                "store_type": store_type,
                "month": month,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "is_holiday": is_holiday,
                "rolling_averages_used": rolling_data,
                "baseline_price": round(current_price, 2),
                "baseline_demand": round(baseline_demand, 1),
                "price_change_percent": round(price_change_percent, 1),
                "base_elasticity": round(base_elasticity, 3),
                "adjusted_elasticity": round(adjusted_elasticity, 3)
            },
            predicted_demand=round(final_demand, 0),
            predicted_revenue=round(final_revenue, 2),
            elasticity_coefficient=round(adjusted_elasticity, 3),
            demand_level=demand_level,
            timestamp=datetime.now().isoformat()
        )
