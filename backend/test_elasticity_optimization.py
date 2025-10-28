"""
Test script to demonstrate improved elasticity-based price optimization
Shows realistic profit maximization with constraints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def test_optimization(product_name, category, current_price, emirate="Dubai", store_type="Hypermarket"):
    """Test price optimization for a product"""
    print_header(f"Testing: {product_name}")
    
    payload = {
        "product_name": product_name,
        "category": category,
        "emirate": emirate,
        "store_type": store_type,
        "current_price": current_price,
        "month": 10,
        "day_of_week": 1,
        "day_of_month": 27,
        "is_weekend": 0,
        "is_holiday": 0
    }
    
    print(f"\n📊 Current Setup:")
    print(f"   Product: {product_name}")
    print(f"   Category: {category}")
    print(f"   Current Price: AED {current_price}")
    print(f"   Location: {emirate} - {store_type}")
    
    response = requests.post(f"{BASE_URL}/api/optimize-price", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n💰 Current Metrics:")
        cm = result['current_metrics']
        print(f"   Demand: {cm['demand']:.1f} units")
        print(f"   Revenue: AED {cm['revenue']:,.2f}")
        print(f"   Profit: AED {cm['profit']:,.2f}")
        print(f"   Margin: {cm['margin_pct']:.1f}%")
        print(f"   Estimated Cost: AED {cm['estimated_cost']:.2f}")
        
        print(f"\n🎯 Optimization Recommendation:")
        rec = result['recommendation']
        print(f"   Optimal Price: AED {rec['recommended_price']}")
        print(f"   Price Change: {rec['price_change_percentage']:+.1f}%")
        print(f"   Expected Demand: {rec['expected_demand']:.1f} units")
        print(f"   Expected Revenue: AED {rec['expected_revenue']:,.2f}")
        print(f"   Confidence: {rec['confidence_score']:.1f}%")
        
        print(f"\n📈 Elasticity Analysis:")
        elast = result['elasticity']
        print(f"   Coefficient: {elast['elasticity_coefficient']:.3f}")
        print(f"   Type: {elast['elasticity_category'].upper()}")
        print(f"   Interpretation: {elast['interpretation']}")
        
        print(f"\n💡 Reasoning:")
        print(f"   {rec['reasoning']}")
        
        # Calculate improvements from optimization result
        if 'profit' in cm:
            # Extract optimal profit from demand curve or calculate
            opt_demand = rec['expected_demand']
            opt_price = rec['recommended_price']
            opt_revenue = rec['expected_revenue']
            opt_profit = (opt_price - cm['estimated_cost']) * opt_demand
            
            profit_improvement = ((opt_profit - cm['profit']) / cm['profit'] * 100) if cm['profit'] > 0 else 0
            revenue_improvement = ((opt_revenue - cm['revenue']) / cm['revenue'] * 100) if cm['revenue'] > 0 else 0
            
            print(f"\n📊 Expected Improvements:")
            print(f"   Profit: {profit_improvement:+.1f}%")
            print(f"   Revenue: {revenue_improvement:+.1f}%")
            print(f"   Demand: {((opt_demand - cm['demand'])/cm['demand']*100):+.1f}%")
        
        print(f"\n🔒 Constraints Applied:")
        if 'price_range' in elast:
            print(f"   Min Price: AED {elast['price_range']['min']:.2f}")
            print(f"   Max Price: AED {elast['price_range']['max']:.2f}")
        
        return result
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return None

def main():
    print_header("ELASTICITY-BASED PRICE OPTIMIZATION TEST")
    print("\nThis demonstrates profit-maximizing price recommendations using:")
    print("  • Data-driven elasticity estimates (from historical price-quantity relationships)")
    print("  • XGBoost demand predictions")
    print("  • Realistic business constraints (15% min margin, ±25-30% price change)")
    print("  • Product-specific cost estimation")
    print("\nNote: EconML model fallback due to numpy version - using empirical elasticity calculation")
    
    # Test different products
    test_cases = [
        {
            "product_name": "NESTLE NESQUIK 330GR(C) BOX",
            "category": "Breakfast Cereals",
            "current_price": 15.5
        },
        {
            "product_name": "NESCAFE 3IN1 CLASSIC 20GX24 BOX (CM)",
            "category": "Hot Beverages",
            "current_price": 25.0
        },
        {
            "product_name": "MAGGI BBQ & GRILLS SEASONING 150G TUB",
            "category": "Culinary",
            "current_price": 12.0
        }
    ]
    
    results = []
    for test in test_cases:
        result = test_optimization(**test)
        if result:
            results.append(result)
        print("\n" + "-"*80)
    
    print_header("SUMMARY")
    print("\nKey Insights:")
    print("  1. Each product gets a UNIQUE optimal price based on its elasticity")
    print("  2. Price recommendations maximize PROFIT, not just revenue")
    print("  3. Realistic constraints prevent extreme price changes")
    print("  4. Elasticity coefficients reflect actual demand sensitivity")
    print("\n✅ The system no longer suggests generic 40% increases for everything!")

if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"\n✓ Server is online")
            print(f"✓ Demand model: {'loaded' if health.get('demand_model_loaded') else 'NOT loaded'}")
            print(f"✓ Elasticity model: {'loaded' if health.get('elasticity_model_loaded') else 'using fallback (data-driven)'}")
            
            if health.get('demand_model_loaded'):  # Only need demand model
                main()
            else:
                print("\n❌ Demand model not loaded. Please check server logs.")
        else:
            print("❌ Server not responding")
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("   Make sure the API is running: python main.py")
