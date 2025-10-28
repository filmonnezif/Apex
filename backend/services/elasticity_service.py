"""
Simple Profit Optimization Service using category-based price elasticity
Provides realistic pricing recommendations based on product categories
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from services.data_service import DataService

class ElasticityService:
    """Service for category-based pricing optimization"""
    
    # Realistic business constraints
    MIN_MARGIN = 0.15  # Minimum 15% profit margin
    MAX_PRICE_CHANGE = 2.0  # Maximum 200% price change (essentially uncapped for finding true optimum)
    MIN_PRICE_CHANGE = -0.50  # Maximum 50% price decrease (reasonable floor)
    
    # Realistic price elasticities by category (based on industry research)
    CATEGORY_ELASTICITIES = {
        'BREAKFAST CEREAL': -1.2,      # Moderately elastic (many substitutes)
        'TOTAL COFFEE': -0.8,           # Inelastic (loyal customers, habit)
        'ICE COFFEE': -1.0,             # Unit elastic
        'MUESLI / CEREAL & NUTRITIONAL BAR': -1.3,  # Elastic (premium/discretionary)
        'PET CARE': -0.7,               # Inelastic (pet owners committed)
        'CONFECTIONERY': -1.5,          # Elastic (impulse purchase)
        'DAIRY': -0.6,                  # Very inelastic (staple)
        'HOT BEVERAGES': -0.8,          # Inelastic
        'DEFAULT': -1.0                 # Unit elastic default
    }
    
    # Typical cost margins by category (for cost estimation)
    CATEGORY_MARGINS = {
        'BREAKFAST CEREAL': 0.35,
        'TOTAL COFFEE': 0.40,
        'ICE COFFEE': 0.35,
        'MUESLI / CEREAL & NUTRITIONAL BAR': 0.38,
        'PET CARE': 0.35,
        'CONFECTIONERY': 0.38,
        'DAIRY': 0.25,
        'HOT BEVERAGES': 0.40,
        'DEFAULT': 0.30
    }
    
    @classmethod
    def load_elasticity_model(cls):
        """Compatibility method - no model loading needed"""
        print("✓ Using category-based elasticity framework (no model file needed)")
        return True
    
    @classmethod
    def get_product_elasticity(
        cls,
        product_name: str,
        emirate: str,
        store_type: str,
        current_price: float,
        month: int,
        day_of_week: int,
        is_weekend: int = 0,
        is_holiday: int = 0,
        promotion: str = "NO PROMO"
    ) -> float:
        """
        Get price elasticity based on product category
        Returns realistic elasticity coefficient (negative value)
        """
        # Get product data to determine category
        df = DataService.get_product_data(product_name)
        
        if not df.empty and 'category' in df.columns:
            category = df['category'].iloc[0]
            elasticity = cls.CATEGORY_ELASTICITIES.get(category, cls.CATEGORY_ELASTICITIES['DEFAULT'])
        else:
            # Fallback: infer from product name
            elasticity = cls._infer_elasticity_from_name(product_name)
        
        # Add small random variation to make it more realistic
        variation = np.random.uniform(-0.05, 0.05)
        elasticity = elasticity + variation
        
        # Ensure it's negative and within realistic bounds
        elasticity = max(-2.0, min(-0.5, elasticity))
        
        print(f"Product: {product_name}, Category-based Elasticity: {elasticity:.3f}")
        return elasticity
    
    @classmethod
    def get_dynamic_elasticity(
        cls,
        base_elasticity: float,
        current_demand: float,
        predicted_demand: float,
        price_change_percent: float
    ) -> float:
        """
        Apply dynamic EXPONENTIAL elasticity adjustment based on demand trends and price direction
        
        Logic with exponential punishment/reward:
        - Large price INCREASES (>50%) get EXPONENTIALLY punished (much more elastic)
        - Large price DECREASES create EXPONENTIAL demand influx (more responsive)
        - Small changes have linear adjustments
        - Demand trend modulates the base adjustment
        
        Args:
            base_elasticity: Base elasticity coefficient (negative)
            current_demand: Current/baseline demand level
            predicted_demand: Predicted demand at current conditions
            price_change_percent: Intended price change as percentage (positive = increase)
        
        Returns:
            Adjusted elasticity coefficient (negative, more negative = more elastic)
        """
        # Calculate demand trend
        demand_change_percent = ((predicted_demand - current_demand) / current_demand * 100) if current_demand > 0 else 0
        
        # Base adjustment factor
        adjustment_factor = 1.0
        adjustment_reason = ""
        
        # Get absolute price change for exponential calculations
        abs_price_change = abs(price_change_percent)
        
        if price_change_percent > 0:  # Price INCREASE
            # Exponential punishment for large price increases
            # Formula: factor = 1 + (price_change/X)^Y where Y > 1.5 for aggressive curve
            # This creates VERY aggressive punishment for unrealistic increases
            
            if abs_price_change > 100:  # >100% increase - COMPLETELY UNREALISTIC
                # DEVASTATING punishment: 8x to 12x more elastic (demand will collapse)
                base_punishment = 1.0 + (abs_price_change / 30) ** 2.2
                adjustment_factor = min(12.0, base_punishment)
                adjustment_reason = f"CATASTROPHIC price increase (+{abs_price_change:.0f}%) - DEVASTATING punishment (demand collapse)"
                
            elif abs_price_change > 70:  # 70-100% increase - EXTREMELY UNREALISTIC
                # Massive punishment: 5x to 8x more elastic
                base_punishment = 1.0 + (abs_price_change / 35) ** 2.0
                adjustment_factor = min(8.0, base_punishment)
                adjustment_reason = f"EXTREME price increase (+{abs_price_change:.0f}%) - massive exponential punishment"
                
            elif abs_price_change > 50:  # 50-70% increase - VERY UNREALISTIC
                # Very heavy punishment: 3x to 5x more elastic
                base_punishment = 1.0 + (abs_price_change / 40) ** 1.8
                adjustment_factor = min(5.5, base_punishment)
                adjustment_reason = f"Very high price increase (+{abs_price_change:.0f}%) - very heavy exponential punishment"
                
            elif abs_price_change > 30:  # 30-50% increase - UNREALISTIC
                # Heavy exponential punishment: 2x to 3.5x more elastic
                base_punishment = 1.0 + (abs_price_change / 50) ** 1.6
                adjustment_factor = min(3.5, base_punishment)
                adjustment_reason = f"High price increase (+{abs_price_change:.0f}%) - heavy exponential punishment"
                
            elif abs_price_change > 20:  # 20-30% increase - AGGRESSIVE
                # Strong exponential punishment: 1.5x to 2.2x more elastic
                base_punishment = 1.0 + (abs_price_change / 60) ** 1.4
                adjustment_factor = min(2.2, base_punishment)
                adjustment_reason = f"Aggressive price increase (+{abs_price_change:.0f}%) - strong exponential punishment"
                
            elif abs_price_change > 15:  # 15-20% increase - MODERATE
                # Moderate exponential punishment: 1.3x to 1.6x more elastic
                base_punishment = 1.0 + (abs_price_change / 80) ** 1.3
                adjustment_factor = min(1.6, base_punishment)
                adjustment_reason = f"Moderate price increase (+{abs_price_change:.0f}%) - moderate exponential punishment"
                
            else:  # <15% increase
                # Linear adjustment based on demand trend
                if demand_change_percent > 5:
                    adjustment_factor = 0.7  # Strong demand = less punishment
                    adjustment_reason = f"Small increase (+{abs_price_change:.0f}%) with strong demand - forgiving"
                elif demand_change_percent > 0:
                    adjustment_factor = 0.85
                    adjustment_reason = f"Small increase (+{abs_price_change:.0f}%) with growing demand - slightly forgiving"
                else:
                    adjustment_factor = 1.1
                    adjustment_reason = f"Small increase (+{abs_price_change:.0f}%) with weak demand - slight punishment"
            
            # Modulate based on demand trend for large increases
            if abs_price_change > 15:
                if demand_change_percent > 10:  # Very strong demand
                    adjustment_factor *= 0.7  # Reduce punishment by 30%
                    adjustment_reason += " | Strong demand reduces punishment by 30%"
                elif demand_change_percent > 5:  # Strong demand
                    adjustment_factor *= 0.85  # Reduce punishment by 15%
                    adjustment_reason += " | Good demand reduces punishment by 15%"
                elif demand_change_percent < -10:  # Declining demand
                    adjustment_factor *= 1.3  # Increase punishment by 30%
                    adjustment_reason += " | Declining demand AMPLIFIES punishment by 30%"
                elif demand_change_percent < -5:  # Weak demand
                    adjustment_factor *= 1.15  # Increase punishment by 15%
                    adjustment_reason += " | Weak demand amplifies punishment by 15%"
                    
        elif price_change_percent < 0:  # Price DECREASE
            # Exponential REWARD for large price cuts = explosive demand influx
            # Formula: factor = 1 - (abs(price_change)/X)^Y
            # This creates MASSIVE demand response for deep discounts
            
            if abs_price_change > 60:  # >60% decrease - FIRE SALE
                # EXPLOSIVE demand influx: 5-10x MORE responsive
                reward_factor = (abs_price_change / 40) ** 1.8
                adjustment_factor = max(0.15, 1.0 - reward_factor)
                adjustment_reason = f"FIRE SALE discount (-{abs_price_change:.0f}%) - EXPLOSIVE demand influx (customers rushing in)"
                
            elif abs_price_change > 40:  # 40-60% decrease - MEGA SALE
                # Massive demand influx: 3-5x more responsive
                reward_factor = (abs_price_change / 50) ** 1.6
                adjustment_factor = max(0.25, 1.0 - reward_factor)
                adjustment_reason = f"MEGA SALE discount (-{abs_price_change:.0f}%) - massive demand influx (exponential)"
                
            elif abs_price_change > 30:  # 30-40% decrease - BIG SALE
                # Very strong demand influx: 2-3x more responsive
                reward_factor = (abs_price_change / 60) ** 1.5
                adjustment_factor = max(0.35, 1.0 - reward_factor)
                adjustment_reason = f"Big discount (-{abs_price_change:.0f}%) - very strong demand influx (exponential)"
                
            elif abs_price_change > 20:  # 20-30% decrease - SALE
                # Strong demand response: 1.5-2x more responsive
                reward_factor = (abs_price_change / 80) ** 1.4
                adjustment_factor = max(0.5, 1.0 - reward_factor)
                adjustment_reason = f"Good discount (-{abs_price_change:.0f}%) - strong demand response"
                
            elif abs_price_change > 10:  # 10-20% decrease
                # Moderate response
                adjustment_factor = 0.8
                adjustment_reason = f"Small discount (-{abs_price_change:.0f}%) - moderate demand response"
                
            else:  # <10% decrease
                # Minimal response
                adjustment_factor = 0.95
                adjustment_reason = f"Minor discount (-{abs_price_change:.0f}%) - slight demand response"
            
            # Modulate based on demand trend for price cuts
            if abs_price_change > 15:
                if demand_change_percent < -10:  # Declining demand
                    adjustment_factor *= 0.8  # Even MORE responsive when demand is weak
                    adjustment_reason += " | Weak demand makes customers MORE price-sensitive"
                elif demand_change_percent < -5:
                    adjustment_factor *= 0.9
                    adjustment_reason += " | Declining demand increases price sensitivity"
                elif demand_change_percent > 5:  # Strong demand
                    adjustment_factor *= 1.1  # Less responsive when demand already strong
                    adjustment_reason += " | Strong demand reduces need for discounts"
        else:
            adjustment_reason = "No price change"
        
        # Apply adjustment to base elasticity
        # Remember: elasticity is negative
        # - Factor > 1 makes elasticity MORE negative (MORE elastic/sensitive)
        # - Factor < 1 makes elasticity LESS negative (LESS elastic/sensitive)
        adjusted_elasticity = base_elasticity * adjustment_factor
        
        # Ensure realistic bounds (increased upper bound for extreme punishments)
        adjusted_elasticity = max(-15.0, min(-0.2, adjusted_elasticity))
        
        # Calculate effective multiplier for logging
        elasticity_multiplier = abs(adjusted_elasticity / base_elasticity) if base_elasticity != 0 else 1.0
        
        print(f"  🎯 Dynamic Elasticity Adjustment (Exponential):")
        print(f"    📊 Demand trend: {demand_change_percent:+.1f}%")
        print(f"    💰 Price change: {price_change_percent:+.1f}%")
        print(f"    📉 Base elasticity: {base_elasticity:.3f}")
        print(f"    ⚡ Adjustment: {adjustment_factor:.2f}x")
        print(f"    🎪 Result: {adjusted_elasticity:.3f} ({elasticity_multiplier:.1f}x sensitivity)")
        print(f"    💡 Reason: {adjustment_reason}")
        
        return adjusted_elasticity
    
    @classmethod
    def _infer_elasticity_from_name(cls, product_name: str) -> float:
        """Infer elasticity from product name keywords"""
        name_lower = product_name.lower()
        
        if any(word in name_lower for word in ['cereal', 'nesquik', 'chocapic']):
            return -1.2
        elif any(word in name_lower for word in ['coffee', 'nescafe']):
            return -0.8
        elif any(word in name_lower for word in ['pet', 'purina', 'frisk']):
            return -0.7
        elif any(word in name_lower for word in ['chocolate', 'kitkat', 'candy']):
            return -1.5
        elif any(word in name_lower for word in ['milk', 'dairy', 'nido']):
            return -0.6
        else:
            return -1.0  # Default unit elastic
    
    @classmethod
    def estimate_cost(cls, product_name: str, current_price: float) -> float:
        """Get actual product cost from data (85% of latest price) or estimate from typical margins"""
        # First try to get actual cost from data service
        actual_cost = DataService.get_product_cost(product_name)
        if actual_cost > 0:
            return actual_cost
        
        # Fallback to margin-based estimation
        df = DataService.get_product_data(product_name)
        
        if not df.empty and 'category' in df.columns:
            category = df['category'].iloc[0]
            typical_margin = cls.CATEGORY_MARGINS.get(category, cls.CATEGORY_MARGINS['DEFAULT'])
        else:
            typical_margin = cls.CATEGORY_MARGINS['DEFAULT']
        
        # Cost = Price * (1 - margin)
        estimated_cost = current_price * (1 - typical_margin)
        return max(estimated_cost, current_price * 0.5)  # Cost at least 50% of price
    
    @classmethod
    def predict_demand_at_price(
        cls,
        current_demand: float,
        elasticity: float,
        current_price: float,
        new_price: float
    ) -> float:
        """
        Predict demand at a new price using elasticity formula
        Demand_new = Demand_current * (Price_new / Price_current) ^ elasticity
        """
        if current_price <= 0 or new_price <= 0:
            return current_demand
        
        price_ratio = new_price / current_price
        demand_multiplier = price_ratio ** elasticity
        new_demand = current_demand * demand_multiplier
        
        return max(0, new_demand)  # Demand can't be negative
    
    @classmethod
    def optimize_price_for_profit(
        cls,
        product_name: str,
        emirate: str,
        store_type: str,
        current_price: float,
        current_demand: float,
        month: int,
        day_of_week: int,
        is_weekend: int = 0,
        is_holiday: int = 0
    ) -> Dict:
        """
        Find the profit-maximizing price using ADJUSTED elasticity
        Uses iterative optimization that accounts for dynamic elasticity changes
        """
        # Get BASE elasticity for this product category
        base_elasticity = cls.get_product_elasticity(
            product_name, emirate, store_type, current_price,
            month, day_of_week, is_weekend, is_holiday
        )
        
        # Estimate cost
        estimated_cost = cls.estimate_cost(product_name, current_price)
        
        # Define price search range
        min_price = max(
            estimated_cost * (1 + cls.MIN_MARGIN),  # Must maintain minimum margin
            current_price * (1 + cls.MIN_PRICE_CHANGE)  # Can't drop more than 15%
        )
        max_price = current_price * (1 + cls.MAX_PRICE_CHANGE)  # Can't increase more than 15%
        
        print(f"\n🎯 Starting ADJUSTED ELASTICITY optimization for {product_name}")
        print(f"  Base elasticity: {base_elasticity:.3f}")
        print(f"  Price range: AED {min_price:.2f} - {max_price:.2f}")
        
        # Grid search with ADJUSTED ELASTICITY for each price point
        # This is more accurate than using a single theoretical optimal
        price_candidates = np.linspace(min_price, max_price, 50)  # More granular search
        best_price = current_price
        best_profit = (current_price - estimated_cost) * current_demand
        best_demand = current_demand
        best_adjusted_elasticity = base_elasticity
        
        all_results = []
        
        for test_price in price_candidates:
            # Calculate price change percentage
            price_change_pct = ((test_price - current_price) / current_price) * 100
            
            # Get ADJUSTED elasticity for this specific price change
            adjusted_elasticity = cls.get_dynamic_elasticity(
                base_elasticity=base_elasticity,
                current_demand=current_demand,
                predicted_demand=current_demand,  # Use current as baseline
                price_change_percent=price_change_pct
            )
            
            # Predict demand using ADJUSTED elasticity
            test_demand = cls.predict_demand_at_price(
                current_demand, adjusted_elasticity, current_price, test_price
            )
            
            # Calculate profit
            test_profit = (test_price - estimated_cost) * test_demand
            test_revenue = test_price * test_demand
            
            all_results.append({
                'price': test_price,
                'demand': test_demand,
                'profit': test_profit,
                'revenue': test_revenue,
                'adjusted_elasticity': adjusted_elasticity,
                'price_change_pct': price_change_pct
            })
            
            # Track best
            if test_profit > best_profit:
                best_profit = test_profit
                best_price = test_price
                best_demand = test_demand
                best_adjusted_elasticity = adjusted_elasticity
        
        print(f"\n  ✅ Optimal price found: AED {best_price:.2f}")
        print(f"  ✅ Using adjusted elasticity: {best_adjusted_elasticity:.3f}")
        print(f"  ✅ Expected profit: AED {best_profit:.2f}")
        
        is_constrained = (abs(best_price - min_price) < 0.01) or (abs(best_price - max_price) < 0.01)
        
        is_constrained = (abs(best_price - min_price) < 0.01) or (abs(best_price - max_price) < 0.01)
        
        # Calculate metrics
        current_profit = (current_price - estimated_cost) * current_demand
        current_revenue = current_price * current_demand
        
        best_revenue = best_price * best_demand
        
        profit_improvement = ((best_profit - current_profit) / current_profit * 100) if current_profit > 0 else 0
        revenue_improvement = ((best_revenue - current_revenue) / current_revenue * 100) if current_revenue > 0 else 0
        
        # Generate reasoning using ADJUSTED elasticity
        price_change_pct = ((best_price - current_price) / current_price) * 100
        demand_change_pct = ((best_demand - current_demand) / current_demand) * 100
        
        elasticity_type = "elastic" if abs(best_adjusted_elasticity) > 1 else "inelastic"
        
        if abs(price_change_pct) < 1:
            reasoning = (
                f"Current price of AED {current_price:.2f} is near-optimal. "
                f"With {elasticity_type} demand (adjusted elasticity: {best_adjusted_elasticity:.2f}), "
                f"the current price achieves the best profit-volume balance."
            )
        elif price_change_pct > 0:
            reasoning = (
                f"Increase price by {price_change_pct:.1f}% to AED {best_price:.2f}. "
                f"With {elasticity_type} demand (adjusted elasticity: {best_adjusted_elasticity:.2f}), "
                f"demand decreases {abs(demand_change_pct):.1f}% to {best_demand:.0f} units, "
                f"but the margin gain ({((best_price - estimated_cost) / estimated_cost * 100):.1f}% markup) "
                f"outweighs volume loss, increasing profit by {profit_improvement:.1f}%."
            )
        else:
            reasoning = (
                f"Decrease price by {abs(price_change_pct):.1f}% to AED {best_price:.2f}. "
                f"With {elasticity_type} demand (adjusted elasticity: {best_adjusted_elasticity:.2f}), "
                f"demand increases {demand_change_pct:.1f}% to {best_demand:.0f} units. "
                f"Volume gain compensates for lower margins, "
                f"increasing profit by {profit_improvement:.1f}%."
            )
        
        # Add constraint note with more detail
        if is_constrained:
            if best_price >= max_price - 0.01:
                reasoning += f" (Hitting upper price limit of +{cls.MAX_PRICE_CHANGE*100:.0f}% - extreme price increase detected.)"
            elif best_price <= min_price + 0.01:
                reasoning += f" (Limited by minimum {cls.MIN_MARGIN*100:.0f}% margin requirement - lower prices would be unprofitable.)"
        else:
            reasoning += f" (True optimum found within feasible range.)"
        
        # Prepare curve data (subsample for efficiency)
        curve_data = all_results[::2]  # Every other point
        
        return {
            'optimal_price': round(best_price, 2),
            'current_price': round(current_price, 2),
            'price_change_percentage': round(price_change_pct, 2),
            'base_elasticity': round(base_elasticity, 3),
            'adjusted_elasticity': round(best_adjusted_elasticity, 3),
            'elasticity_type': elasticity_type,
            'estimated_cost': round(estimated_cost, 2),
            'is_constrained': is_constrained,
            'current_metrics': {
                'demand': round(current_demand, 1),
                'revenue': round(current_revenue, 2),
                'profit': round(current_profit, 2),
                'margin': round((current_price - estimated_cost) / current_price * 100, 1)
            },
            'optimal_metrics': {
                'demand': round(best_demand, 1),
                'revenue': round(best_revenue, 2),
                'profit': round(best_profit, 2),
                'margin': round((best_price - estimated_cost) / best_price * 100, 1)
            },
            'improvements': {
                'profit': round(profit_improvement, 1),
                'revenue': round(revenue_improvement, 1),
                'demand_change': round(demand_change_pct, 1)
            },
            'reasoning': reasoning,
            'constraints': {
                'min_price': round(min_price, 2),
                'max_price': round(max_price, 2),
                'min_margin_pct': cls.MIN_MARGIN * 100,
                'max_price_increase_pct': cls.MAX_PRICE_CHANGE * 100,
                'max_price_decrease_pct': abs(cls.MIN_PRICE_CHANGE) * 100
            },
            'price_demand_curve': [
                {
                    'price': round(r['price'], 2),
                    'demand': round(r['demand'], 1),
                    'revenue': round(r['revenue'], 2),
                    'profit': round(r['profit'], 2)
                }
                for r in curve_data
            ]
        }
