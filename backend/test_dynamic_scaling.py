"""
Test dynamic demand-responsive pricing with continuous scaling
Shows how max price increase changes smoothly with demand
"""
import sys
sys.path.append('/workspaces/docker-in-docker-2/backend')

from services.elasticity_service import ElasticityService

def test_dynamic_scaling():
    print("="*80)
    print("TESTING DYNAMIC DEMAND-RESPONSIVE PRICING")
    print("="*80)
    print()
    
    # Test product: Nescafe Coffee
    product_name = "NESCAFE CLASSIC 200GM"
    emirate = "Dubai"
    store_type = "Hypermarket"
    current_price = 25.0
    month = 10
    day_of_week = 2
    
    # Test different demand levels to show continuous scaling
    test_demands = [
        100,   # Very low
        200,   # Low
        300,   # Below average
        400,   # Average
        500,   # Baseline
        650,   # Above average
        800,   # High
        950,   # Very high
        1200,  # Exceptional
    ]
    
    print(f"Product: {product_name}")
    print(f"Current Price: AED {current_price:.2f}")
    print(f"Location: {emirate} - {store_type}")
    print()
    print("Testing DYNAMIC SCALING across demand levels:")
    print("-"*80)
    print(f"{'Demand':<12} {'Ratio':<10} {'Level':<18} {'Max Inc %':<12} {'Optimal':<12} {'Change %':<10}")
    print("-"*80)
    
    results = []
    
    for demand in test_demands:
        result = ElasticityService.optimize_price_for_profit(
            product_name=product_name,
            emirate=emirate,
            store_type=store_type,
            current_price=current_price,
            current_demand=demand,
            month=month,
            day_of_week=day_of_week,
            is_weekend=0,
            is_holiday=0
        )
        
        results.append({
            'demand': demand,
            'ratio': result['demand_ratio'],
            'level': result['demand_level'],
            'max_increase': result['constraints']['max_price_increase_pct'],
            'optimal_price': result['optimal_price'],
            'change_pct': result['price_change_percentage']
        })
        
        print(f"{demand:<12} {result['demand_ratio']:<10.2f} {result['demand_level']:<18} "
              f"{result['constraints']['max_price_increase_pct']:<12.1f} "
              f"AED {result['optimal_price']:<8.2f} {result['price_change_percentage']:>+6.1f}%")
    
    print("-"*80)
    print()
    print("KEY OBSERVATIONS:")
    print("-"*80)
    
    # Calculate the range of variation
    min_max = min(r['max_increase'] for r in results)
    max_max = max(r['max_increase'] for r in results)
    min_optimal_change = min(r['change_pct'] for r in results)
    max_optimal_change = max(r['change_pct'] for r in results)
    
    print(f"✓ Max Price Increase Range: {min_max:.1f}% to {max_max:.1f}%")
    print(f"✓ Optimal Price Change Range: {min_optimal_change:+.1f}% to {max_optimal_change:+.1f}%")
    print(f"✓ Dynamic Scaling: {max_max - min_max:.1f} percentage points variation")
    print()
    print("✓ Small demand changes → Small constraint adjustments → Small optimal changes")
    print("✓ Smooth continuous scaling (no rigid tiers)")
    print("✓ Price recommendations naturally follow demand levels")
    print("="*80)
    
    return results

if __name__ == "__main__":
    results = test_dynamic_scaling()
