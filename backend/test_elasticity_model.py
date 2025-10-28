"""
Comprehensive test script for elasticity model and price optimization
Tests model loading, elasticity calculations, and profit optimization
"""
import sys
import os
import joblib
import pandas as pd
import numpy as np
from services.elasticity_service import ElasticityService
from services.data_service import DataService
from services.ai_service import XGBoostAIService

def test_model_loading():
    """Test if the elasticity system initializes correctly"""
    print("\n" + "="*80)
    print("TEST 1: Elasticity System Initialization")
    print("="*80)
    
    print("Testing category-based elasticity framework...")
    
    # Try to load the system
    success = ElasticityService.load_elasticity_model()
    
    if success:
        print("✓ Elasticity system initialized successfully!")
        print(f"Number of categories: {len(ElasticityService.CATEGORY_ELASTICITIES)}")
        print("Category elasticities:")
        for category, elasticity in ElasticityService.CATEGORY_ELASTICITIES.items():
            print(f"  - {category}: {elasticity}")
        return True
    else:
        print("✗ Failed to initialize elasticity system!")
        return False

def test_data_loading():
    """Test if historical data loads correctly"""
    print("\n" + "="*80)
    print("TEST 2: Historical Data Loading")
    print("="*80)
    
    df = DataService.load_data()
    
    if not df.empty:
        print(f"✓ Data loaded: {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}")
        print(f"\nDate range: {df['period_normalized_date'].min()} to {df['period_normalized_date'].max()}")
        print(f"Unique products: {df['product_name'].nunique()}")
        print(f"Unique emirates: {df['emirate'].nunique()}")
        print(f"Unique store types: {df['store_type'].nunique()}")
        
        # Check price variation
        price_variation = df.groupby('product_name')['price_per_sales_unit'].agg(['min', 'max', 'nunique', 'std'])
        print(f"\nPrice variation per product:")
        print(price_variation.head(10))
        
        return True, df
    else:
        print("✗ No data loaded!")
        return False, None

def test_elasticity_calculation():
    """Test elasticity calculation for sample products"""
    print("\n" + "="*80)
    print("TEST 4: Elasticity Calculation")
    print("="*80)
    
    # Test products
    test_cases = [
        {
            "product_name": "NESTLE NESQUIK 330GR(C) BOX",
            "emirate": "Dubai",
            "store_type": "Hypermarket",
            "current_price": 15.5,
            "month": 10,
            "day_of_week": 1
        },
        {
            "product_name": "NESCAFE 3IN1 CLASSIC 20GX24 BOX (CM)",
            "emirate": "Abu Dhabi",
            "store_type": "Supermarket",
            "current_price": 25.0,
            "month": 10,
            "day_of_week": 3
        }
    ]
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {case['product_name']}")
        print("-" * 80)
        
        try:
            elasticity = ElasticityService.get_product_elasticity(
                product_name=case['product_name'],
                emirate=case['emirate'],
                store_type=case['store_type'],
                current_price=case['current_price'],
                month=case['month'],
                day_of_week=case['day_of_week']
            )
            
            print(f"✓ Elasticity calculated: {elasticity:.4f}")
            
            # Validate elasticity is reasonable
            if elasticity < 0:
                print(f"  ✓ Elasticity is negative (follows law of demand)")
            else:
                print(f"  ⚠ Warning: Elasticity is positive (unusual)")
            
            if -5.0 <= elasticity <= -0.1:
                print(f"  ✓ Elasticity is within realistic range [-5, -0.1]")
            else:
                print(f"  ⚠ Warning: Elasticity outside typical range")
            
            # Classify elasticity
            if abs(elasticity) > 1:
                print(f"  → Product is ELASTIC (|e| > 1): Demand is sensitive to price changes")
            elif abs(elasticity) < 1:
                print(f"  → Product is INELASTIC (|e| < 1): Demand is less sensitive to price changes")
            else:
                print(f"  → Product is UNIT ELASTIC (|e| ≈ 1): Proportional response")
            
            results.append({
                'product': case['product_name'],
                'elasticity': elasticity,
                'success': True
            })
            
        except Exception as e:
            print(f"✗ Error calculating elasticity: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'product': case['product_name'],
                'elasticity': None,
                'success': False
            })
    
    # Summary
    print("\n" + "-" * 80)
    print("ELASTICITY CALCULATION SUMMARY:")
    successful = sum(1 for r in results if r['success'])
    print(f"Successful: {successful}/{len(results)}")
    
    if successful > 0:
        elasticities = [r['elasticity'] for r in results if r['success']]
        print(f"Elasticity range: [{min(elasticities):.3f}, {max(elasticities):.3f}]")
        print(f"Mean elasticity: {np.mean(elasticities):.3f}")
    
    return successful > 0

def test_demand_prediction():
    """Test demand prediction at different price points"""
    print("\n" + "="*80)
    print("TEST 5: Demand Prediction at Different Prices")
    print("="*80)
    
    base_demand = 100.0
    elasticity = -1.5
    base_price = 15.0
    
    print(f"Base scenario: Demand={base_demand}, Price={base_price}, Elasticity={elasticity}")
    print("\nPredicting demand at different prices:")
    print("-" * 80)
    
    test_prices = [10, 12, 15, 18, 20, 25]
    
    for price in test_prices:
        predicted_demand = ElasticityService.predict_demand_at_price(
            current_demand=base_demand,
            elasticity=elasticity,
            current_price=base_price,
            new_price=price
        )
        
        price_change = ((price - base_price) / base_price) * 100
        demand_change = ((predicted_demand - base_demand) / base_demand) * 100
        
        print(f"Price: AED {price:5.2f} ({price_change:+6.1f}%) → Demand: {predicted_demand:6.1f} ({demand_change:+6.1f}%)")
    
    return True

def test_profit_optimization():
    """Test complete profit optimization pipeline"""
    print("\n" + "="*80)
    print("TEST 6: Profit Optimization")
    print("="*80)
    
    # Test case
    test_case = {
        "product_name": "NESTLE NESQUIK 330GR(C) BOX",
        "emirate": "Dubai",
        "store_type": "Hypermarket",
        "current_price": 15.5,
        "current_demand": 100.0,
        "month": 10,
        "day_of_week": 1
    }
    
    print(f"Product: {test_case['product_name']}")
    print(f"Current Price: AED {test_case['current_price']}")
    print(f"Current Demand: {test_case['current_demand']} units")
    print("\nRunning optimization...")
    print("-" * 80)
    
    try:
        result = ElasticityService.optimize_price_for_profit(
            product_name=test_case['product_name'],
            emirate=test_case['emirate'],
            store_type=test_case['store_type'],
            current_price=test_case['current_price'],
            current_demand=test_case['current_demand'],
            month=test_case['month'],
            day_of_week=test_case['day_of_week']
        )
        
        print(f"\n✓ Optimization successful!")
        print(f"\nResults:")
        print(f"  Optimal Price: AED {result['optimal_price']} ({result['price_change_percentage']:+.1f}%)")
        print(f"  Elasticity: {result['elasticity']:.3f} ({result['elasticity_type']})")
        print(f"  Estimated Cost: AED {result['estimated_cost']:.2f}")
        
        print(f"\nCurrent Metrics:")
        print(f"  Demand: {result['current_metrics']['demand']:.1f} units")
        print(f"  Revenue: AED {result['current_metrics']['revenue']:.2f}")
        print(f"  Profit: AED {result['current_metrics']['profit']:.2f}")
        print(f"  Margin: {result['current_metrics']['margin']:.1f}%")
        
        print(f"\nOptimal Metrics:")
        print(f"  Demand: {result['optimal_metrics']['demand']:.1f} units")
        print(f"  Revenue: AED {result['optimal_metrics']['revenue']:.2f}")
        print(f"  Profit: AED {result['optimal_metrics']['profit']:.2f}")
        print(f"  Margin: {result['optimal_metrics']['margin']:.1f}%")
        
        print(f"\nImprovements:")
        print(f"  Profit: {result['improvements']['profit']:+.1f}%")
        print(f"  Revenue: {result['improvements']['revenue']:+.1f}%")
        print(f"  Demand: {result['improvements']['demand_change']:+.1f}%")
        
        print(f"\nConstraints:")
        print(f"  Min Price: AED {result['constraints']['min_price']:.2f}")
        print(f"  Max Price: AED {result['constraints']['max_price']:.2f}")
        print(f"  Min Margin: {result['constraints']['min_margin_pct']:.0f}%")
        
        print(f"\nReasoning:")
        print(f"  {result['reasoning']}")
        
        # Validate results
        print(f"\n" + "-" * 80)
        print("VALIDATION:")
        
        checks = []
        
        # Check 1: Optimal price within constraints
        if result['constraints']['min_price'] <= result['optimal_price'] <= result['constraints']['max_price']:
            print("  ✓ Optimal price within constraints")
            checks.append(True)
        else:
            print("  ✗ Optimal price outside constraints")
            checks.append(False)
        
        # Check 2: Optimal profit >= current profit
        if result['optimal_metrics']['profit'] >= result['current_metrics']['profit']:
            print("  ✓ Optimal profit >= current profit")
            checks.append(True)
        else:
            print("  ✗ Optimal profit < current profit")
            checks.append(False)
        
        # Check 3: Elasticity is negative
        if result['elasticity'] < 0:
            print("  ✓ Elasticity is negative (law of demand)")
            checks.append(True)
        else:
            print("  ✗ Elasticity is positive (violation of law of demand)")
            checks.append(False)
        
        # Check 4: Margin above minimum
        if result['optimal_metrics']['margin'] >= result['constraints']['min_margin_pct']:
            print("  ✓ Margin above minimum threshold")
            checks.append(True)
        else:
            print("  ✗ Margin below minimum threshold")
            checks.append(False)
        
        return all(checks)
        
    except Exception as e:
        print(f"✗ Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_integration():
    """Test integration with API service"""
    print("\n" + "="*80)
    print("TEST 7: API Integration (XGBoost + Elasticity)")
    print("="*80)
    
    # Load XGBoost model
    xgb_loaded = XGBoostAIService.load_model()
    print(f"XGBoost Model: {'✓ Loaded' if xgb_loaded else '✗ Not loaded'}")
    
    if not xgb_loaded:
        print("⚠ Skipping integration test - XGBoost model not available")
        return False
    
    # Test optimization through API service
    test_case = {
        "product_name": "NESTLE NESQUIK 330GR(C) BOX",
        "category": "Breakfast Cereals",
        "emirate": "Dubai",
        "store_type": "Hypermarket",
        "current_price": 15.5,
        "month": 10,
        "day_of_week": 1,
        "day_of_month": 27,
        "is_weekend": 0,
        "is_holiday": 0
    }
    
    print(f"\nTesting full optimization pipeline...")
    print(f"Product: {test_case['product_name']}")
    print(f"Price: AED {test_case['current_price']}")
    
    try:
        result = XGBoostAIService.optimize_price(**test_case)
        
        print(f"\n✓ API Integration successful!")
        print(f"\nRecommendation:")
        print(f"  Recommended Price: AED {result.recommendation.recommended_price}")
        print(f"  Price Change: {result.recommendation.price_change_percentage:+.1f}%")
        print(f"  Expected Demand: {result.recommendation.expected_demand:.0f} units")
        print(f"  Expected Revenue: AED {result.recommendation.expected_revenue:.2f}")
        print(f"  Confidence: {result.recommendation.confidence_score:.1f}%")
        
        print(f"\nElasticity:")
        print(f"  Coefficient: {result.elasticity.elasticity_coefficient:.3f}")
        print(f"  Category: {result.elasticity.elasticity_category}")
        
        print(f"\nCurrent Metrics:")
        print(f"  Demand: {result.current_metrics['demand']:.1f} units")
        print(f"  Revenue: AED {result.current_metrics['revenue']:.2f}")
        print(f"  Profit: AED {result.current_metrics['profit']:.2f}")
        
        print(f"\nReasoning:")
        print(f"  {result.recommendation.reasoning}")
        
        return True
        
    except Exception as e:
        print(f"✗ API integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("ELASTICITY MODEL & OPTIMIZATION TEST SUITE")
    print("="*80)
    
    test_results = []
    
    # Run all tests
    test_results.append(("System Initialization", test_model_loading()))
    test_results.append(("Data Loading", test_data_loading()[0]))
    test_results.append(("Elasticity Calculation", test_elasticity_calculation()))
    test_results.append(("Demand Prediction", test_demand_prediction()))
    test_results.append(("Profit Optimization", test_profit_optimization()))
    test_results.append(("API Integration", test_api_integration()))
    
    # Final Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print("\n" + "="*80)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*80)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
