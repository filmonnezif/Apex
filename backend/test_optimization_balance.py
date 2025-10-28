"""
Test the improved optimization to show it finds true optimums, not just constraint limits
"""
import sys
sys.path.insert(0, '/workspaces/docker-in-docker-2/backend')

from services.elasticity_service import ElasticityService
from services.data_service import DataService
import numpy as np

print("="*80)
print("PROFIT OPTIMIZATION WITH DEMAND-VOLUME BALANCE")
print("="*80)

# Load elasticity model
ElasticityService.load_elasticity_model()

# Test scenarios with different elasticities
test_cases = [
    {
        "name": "NESTLE NESQUIK 330GR(C) BOX",
        "emirate": "Dubai",
        "store_type": "Hypermarket",
        "current_price": 3.68,
        "current_demand": 232,
        "month": 12,
        "day_of_week": 1
    },
    {
        "name": "NESCAFE 3IN1 CLASSIC 20GX24 BOX (CM)",
        "emirate": "Abu Dhabi",
        "store_type": "Supermarket",
        "current_price": 6.18,
        "current_demand": 228,
        "month": 12,
        "day_of_week": 3
    }
]

for i, case in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"TEST CASE {i}: {case['name']}")
    print('='*80)
    
    result = ElasticityService.optimize_price_for_profit(
        product_name=case['name'],
        emirate=case['emirate'],
        store_type=case['store_type'],
        current_price=case['current_price'],
        current_demand=case['current_demand'],
        month=case['month'],
        day_of_week=case['day_of_week']
    )
    
    print(f"\nCurrent State:")
    print(f"  Price: AED {result['current_price']}")
    print(f"  Demand: {result['current_metrics']['demand']} units")
    print(f"  Revenue: AED {result['current_metrics']['revenue']}")
    print(f"  Profit: AED {result['current_metrics']['profit']}")
    print(f"  Margin: {result['current_metrics']['margin']}%")
    
    print(f"\nElasticity Analysis:")
    print(f"  Coefficient: {result['elasticity']}")
    print(f"  Type: {result['elasticity_type'].upper()}")
    print(f"  Cost Estimate: AED {result['estimated_cost']}")
    
    if 'theoretical_optimal' in result:
        print(f"  Theoretical Optimal: AED {result['theoretical_optimal']}")
    
    print(f"\nOptimal Recommendation:")
    print(f"  Optimal Price: AED {result['optimal_price']} ({result['price_change_percentage']:+.1f}%)")
    print(f"  Optimal Demand: {result['optimal_metrics']['demand']} units ({result['improvements']['demand_change']:+.1f}%)")
    print(f"  Optimal Revenue: AED {result['optimal_metrics']['revenue']} ({result['improvements']['revenue']:+.1f}%)")
    print(f"  Optimal Profit: AED {result['optimal_metrics']['profit']} ({result['improvements']['profit']:+.1f}%)")
    print(f"  Optimal Margin: {result['optimal_metrics']['margin']}%")
    
    print(f"\nConstraints:")
    print(f"  Min Price: AED {result['constraints']['min_price']}")
    print(f"  Max Price: AED {result['constraints']['max_price']}")
    print(f"  Is Constrained: {result.get('is_constrained', False)}")
    
    print(f"\nReasoning:")
    print(f"  {result['reasoning']}")
    
    # Analyze the profit curve to show the peak
    curve = result['price_demand_curve']
    max_profit_point = max(curve, key=lambda x: x['profit'])
    
    print(f"\nProfit Curve Analysis:")
    print(f"  Evaluated {len(curve)} price points")
    print(f"  Peak profit in curve: AED {max_profit_point['profit']} at price AED {max_profit_point['price']}")
    
    # Check if hitting constraint
    if result.get('is_constrained'):
        print(f"\n  ⚠️  HITTING CONSTRAINT: Optimal is at boundary")
        print(f"      True optimum likely beyond {result['constraints']['max_price']}")
        print(f"      This is expected for highly inelastic products")
    else:
        print(f"\n  ✓  INTERIOR OPTIMUM: True optimum found within constraints")
        print(f"      Price change balances profit gain vs demand loss")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
The optimization now uses a balanced approach:
1. Calculates theoretical optimal using elasticity formulas
2. Generates 100 price candidates focused around the optimum
3. Uses a balanced score: profit × √(demand_retention)
4. This penalizes excessive volume loss while maximizing profit
5. Clearly indicates when hitting constraint boundaries

For INELASTIC products (-1 < e < 0):
- Demand is relatively insensitive to price
- Higher prices almost always increase profit (within reason)
- Hitting the 15% constraint is CORRECT behavior
- The warning tells you the true optimum may be higher

For ELASTIC products (e < -1):
- Demand is very sensitive to price  
- Optimal price balances margin and volume
- Often finds interior optimum below constraint
""")
print("="*80)
