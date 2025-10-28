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
    MAX_PRICE_CHANGE = 0.10  # Maximum 10% price increase (realistic business constraint)
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
            # VERY HEAVY exponential punishment for ANY price increases
            # Formula: factor = 1 + (price_change/X)^Y where Y >= 2.5 for EXTREMELY aggressive curve
            # Goal: Make increases above 10% essentially unprofitable
            
            if abs_price_change > 20:  # >20% increase - CATASTROPHIC
                # DEVASTATING punishment: 15x to 25x more elastic (demand will COLLAPSE)
                base_punishment = 1.0 + (abs_price_change / 8) ** 3.0
                adjustment_factor = min(25.0, base_punishment)
                adjustment_reason = f"CATASTROPHIC price increase (+{abs_price_change:.0f}%) - DEVASTATING exponential punishment (market will reject)"
                
            elif abs_price_change > 15:  # 15-20% increase - EXTREME
                # Massive punishment: 8x to 15x more elastic
                base_punishment = 1.0 + (abs_price_change / 10) ** 2.8
                adjustment_factor = min(15.0, base_punishment)
                adjustment_reason = f"EXTREME price increase (+{abs_price_change:.0f}%) - massive exponential punishment"
                
            elif abs_price_change > 12:  # 12-15% increase - VERY AGGRESSIVE
                # Very heavy punishment: 5x to 8x more elastic
                base_punishment = 1.0 + (abs_price_change / 12) ** 2.6
                adjustment_factor = min(8.0, base_punishment)
                adjustment_reason = f"Very aggressive price increase (+{abs_price_change:.0f}%) - very heavy exponential punishment"
                
            elif abs_price_change > 10:  # 10-12% increase - AGGRESSIVE (target threshold)
                # Heavy exponential punishment: 3.5x to 5x more elastic
                base_punishment = 1.0 + (abs_price_change / 14) ** 2.4
                adjustment_factor = min(5.0, base_punishment)
                adjustment_reason = f"Aggressive price increase (+{abs_price_change:.0f}%) - heavy exponential punishment (above 10% threshold)"
                
            elif abs_price_change > 8:  # 8-10% increase - MODERATE-HIGH
                # Strong exponential punishment: 2.5x to 3.5x more elastic
                base_punishment = 1.0 + (abs_price_change / 16) ** 2.2
                adjustment_factor = min(3.5, base_punishment)
                adjustment_reason = f"Moderate-high price increase (+{abs_price_change:.0f}%) - strong exponential punishment"
                
            elif abs_price_change > 6:  # 6-8% increase - MODERATE
                # Moderate exponential punishment: 1.8x to 2.5x more elastic
                base_punishment = 1.0 + (abs_price_change / 20) ** 2.0
                adjustment_factor = min(2.5, base_punishment)
                adjustment_reason = f"Moderate price increase (+{abs_price_change:.0f}%) - moderate exponential punishment"
                
            elif abs_price_change > 4:  # 4-6% increase - LOW-MODERATE
                # Noticeable exponential punishment: 1.5x to 1.8x more elastic
                base_punishment = 1.0 + (abs_price_change / 25) ** 1.8
                adjustment_factor = min(1.8, base_punishment)
                adjustment_reason = f"Low-moderate price increase (+{abs_price_change:.0f}%) - noticeable exponential punishment"
                
            else:  # <4% increase - SMALL
                # Quadratic punishment even for small increases
                base_punishment = 1.0 + (abs_price_change / 30) ** 1.6
                adjustment_factor = min(1.4, base_punishment)
                
                # Minor modulation based on demand trend
                if demand_change_percent > 8:
                    adjustment_factor *= 0.85  # Strong demand = slight relief
                    adjustment_reason = f"Small increase (+{abs_price_change:.0f}%) with very strong demand - reduced punishment"
                elif demand_change_percent > 3:
                    adjustment_factor *= 0.95  # Some demand = minimal relief
                    adjustment_reason = f"Small increase (+{abs_price_change:.0f}%) with good demand - slight punishment"
                else:
                    adjustment_reason = f"Small increase (+{abs_price_change:.0f}%) - quadratic punishment"
            
            # Modulate based on demand trend for ALL price increases
            if abs_price_change > 4:  # Only modulate for increases above 4%
                if demand_change_percent > 10:  # Very strong demand
                    adjustment_factor *= 0.75  # Reduce punishment by 25%
                    adjustment_reason += " | Very strong demand reduces punishment by 25%"
                elif demand_change_percent > 5:  # Strong demand
                    adjustment_factor *= 0.90  # Reduce punishment by 10%
                    adjustment_reason += " | Strong demand reduces punishment by 10%"
                elif demand_change_percent < -10:  # Declining demand
                    adjustment_factor *= 1.5  # Increase punishment by 50%
                    adjustment_reason += " | Declining demand SEVERELY AMPLIFIES punishment by 50%"
                elif demand_change_percent < -5:  # Weak demand
                    adjustment_factor *= 1.25  # Increase punishment by 25%
                    adjustment_reason += " | Weak demand amplifies punishment by 25%"
                    
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
        DEMAND-RESPONSIVE: Higher demand locations allow higher price increases
        """
        # Get BASE elasticity for this product category
        base_elasticity = cls.get_product_elasticity(
            product_name, emirate, store_type, current_price,
            month, day_of_week, is_weekend, is_holiday
        )
        
        # Estimate cost
        estimated_cost = cls.estimate_cost(product_name, current_price)
        
        # DYNAMIC DEMAND-BASED PRICING FLEXIBILITY
        # Calculate demand level relative to a baseline (500 units as reference)
        baseline_demand = 500
        demand_ratio = current_demand / baseline_demand
        
        # CONTINUOUS SCALING: Price increase allowance grows smoothly with demand
        # Formula: max_increase = min_rate + (demand_ratio - min_ratio) * scale_factor
        # This creates a smooth curve instead of rigid tiers
        
        if demand_ratio >= 2.0:
            # Exceptional demand (1000+ units): Allow up to 10% increase
            max_price_increase = 0.10
            demand_context = "EXCEPTIONAL"
        elif demand_ratio >= 0.4:
            # Dynamic scaling between 0.4x and 2.0x demand
            # Range: 2% (very low) to 10% (exceptional)
            # Linear interpolation for smooth transitions
            min_increase = 0.02  # Floor at 2% for very low demand
            max_increase = 0.10  # Ceiling at 10% for exceptional demand
            
            # Normalize demand_ratio to 0-1 range
            normalized_ratio = (demand_ratio - 0.4) / (2.0 - 0.4)
            normalized_ratio = max(0, min(1, normalized_ratio))  # Clamp to [0,1]
            
            # Apply smooth scaling with slight curve (power of 0.9 for gradual acceleration)
            max_price_increase = min_increase + (max_increase - min_increase) * (normalized_ratio ** 0.9)
            
            # Descriptive context based on ratio
            if demand_ratio >= 1.5:
                demand_context = "VERY HIGH"
            elif demand_ratio >= 1.2:
                demand_context = "HIGH"
            elif demand_ratio >= 0.9:
                demand_context = "ABOVE AVERAGE"
            elif demand_ratio >= 0.7:
                demand_context = "AVERAGE"
            elif demand_ratio >= 0.5:
                demand_context = "BELOW AVERAGE"
            else:
                demand_context = "LOW"
        else:
            # Extremely low demand (<200 units): Severely restrict to 2%
            max_price_increase = 0.02
            demand_context = "VERY LOW"
        
        # Define price search range with DEMAND-ADJUSTED maximum increase
        strict_max_price = current_price * (1 + max_price_increase)
        
        min_price = max(
            estimated_cost * (1 + cls.MIN_MARGIN),  # Must maintain minimum margin
            current_price * (1 + cls.MIN_PRICE_CHANGE)  # Can't drop more than 50%
        )
        max_price = strict_max_price
        
        # If minimum margin requirement conflicts with demand-adjusted cap, prioritize demand cap
        if min_price > max_price:
            print(f"  ⚠️ WARNING: Margin requirement conflicts with demand-adjusted cap.")
            print(f"  ⚠️ Accepting lower margin to respect demand-based pricing constraint.")
            min_price = current_price * 0.95  # At least search from -5% to adjusted max
        
        print(f"\n🎯 Starting DYNAMIC DEMAND-RESPONSIVE optimization for {product_name}")
        print(f"  Location: {emirate} - {store_type}")
        print(f"  Current demand: {current_demand:.0f} units (Demand level: {demand_context})")
        print(f"  Demand ratio: {demand_ratio:.2f}x baseline")
        print(f"  Max price increase allowed: +{max_price_increase*100:.1f}% (dynamically scaled)")
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
                reasoning += f" (Hitting upper price limit of +{max_price_increase*100:.0f}% for {demand_context} demand - location-specific constraint.)"
            elif best_price <= min_price + 0.01:
                reasoning += f" (Limited by minimum {cls.MIN_MARGIN*100:.0f}% margin requirement - lower prices would be unprofitable.)"
        else:
            reasoning += f" (True optimum found within demand-adjusted range.)"
        
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
            'demand_level': demand_context,
            'demand_ratio': round(demand_ratio, 2),
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
                'max_price_increase_pct': round(max_price_increase * 100, 1),  # Dynamic demand-adjusted
                'max_price_decrease_pct': abs(cls.MIN_PRICE_CHANGE) * 100,
                'demand_adjusted': True,
                'dynamic_scaling': True
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
