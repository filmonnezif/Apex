"""
Script to calculate product costs from historical data.
Takes the most recent price for each product and calculates cost as 85% of price.
"""
import pandas as pd
import json
from datetime import datetime

def calculate_costs_from_data(csv_path='last_month_data (2).csv'):
    """
    Extract most recent prices and calculate costs (85% of price)
    """
    # Load the data
    df = pd.read_csv(csv_path)
    
    # Convert date column to datetime
    df['period_normalized_date'] = pd.to_datetime(df['period_normalized_date'])
    
    # Sort by date to get most recent first
    df = df.sort_values('period_normalized_date', ascending=False)
    
    # Group by product_name and take the first (most recent) entry
    latest_products = df.groupby('product_name').first().reset_index()
    
    # Calculate cost as 85% of the most recent price
    product_costs = {}
    
    for _, row in latest_products.iterrows():
        product_name = row['product_name']
        price = row['price_per_sales_unit']
        cost = round(price * 0.85, 2)  # 85% of price, rounded to 2 decimals
        
        product_costs[product_name] = {
            'product_name': product_name,
            'category': row['category'],
            'brand': row['brand'],
            'latest_price': round(price, 2),
            'cost': cost,
            'margin_percentage': 15.0,  # 100% - 85% = 15% margin
            'latest_date': row['period_normalized_date'].strftime('%Y-%m-%d')
        }
    
    return product_costs

def save_costs_to_json(product_costs, output_path='product_costs.json'):
    """Save calculated costs to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(product_costs, f, indent=2)
    print(f"✓ Saved product costs to {output_path}")
    print(f"✓ Total products: {len(product_costs)}")

def print_sample_costs(product_costs, n=5):
    """Print sample of calculated costs"""
    print("\n" + "="*80)
    print("SAMPLE PRODUCT COSTS")
    print("="*80)
    for i, (product_name, data) in enumerate(list(product_costs.items())[:n]):
        print(f"\n{i+1}. {product_name}")
        print(f"   Category: {data['category']}")
        print(f"   Latest Price: AED {data['latest_price']}")
        print(f"   Calculated Cost: AED {data['cost']}")
        print(f"   Margin: {data['margin_percentage']}%")
        print(f"   Latest Date: {data['latest_date']}")
    print("="*80)

if __name__ == "__main__":
    print("Calculating product costs from historical data...")
    print("Using formula: Cost = Price × 0.85")
    print("-" * 80)
    
    # Calculate costs
    product_costs = calculate_costs_from_data()
    
    # Print samples
    print_sample_costs(product_costs)
    
    # Save to JSON
    save_costs_to_json(product_costs)
    
    print("\n✓ Cost calculation complete!")
