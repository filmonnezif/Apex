import pandas as pd
import os
import json
from typing import Dict, List, Tuple
from datetime import datetime

class DataService:
    """Service to load and process historical sales data"""
    
    data_cache = None
    products_cache = None
    costs_cache = None
    DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'last_month_data (2).csv')
    COSTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'product_costs.json')
    
    @classmethod
    def load_data(cls) -> pd.DataFrame:
        """Load the CSV data"""
        if cls.data_cache is None:
            try:
                cls.data_cache = pd.read_csv(cls.DATA_PATH)
                cls.data_cache['period_normalized_date'] = pd.to_datetime(cls.data_cache['period_normalized_date'])
                print(f"✓ Loaded {len(cls.data_cache)} rows of historical data")
            except Exception as e:
                print(f"Error loading data: {e}")
                cls.data_cache = pd.DataFrame()
        return cls.data_cache
    
    @classmethod
    def load_costs(cls) -> Dict:
        """Load product costs from JSON file"""
        if cls.costs_cache is None:
            try:
                with open(cls.COSTS_PATH, 'r') as f:
                    cls.costs_cache = json.load(f)
                print(f"✓ Loaded costs for {len(cls.costs_cache)} products")
            except Exception as e:
                print(f"⚠ Warning: Could not load product costs: {e}")
                cls.costs_cache = {}
        return cls.costs_cache
    
    @classmethod
    def get_product_cost(cls, product_name: str) -> float:
        """Get the cost for a specific product (85% of latest price)"""
        costs = cls.load_costs()
        if product_name in costs:
            return costs[product_name]['cost']
        
        # Fallback: calculate as 85% of latest price
        latest_price = cls.get_latest_price(product_name)
        return round(latest_price * 0.85, 2)
    
    @classmethod
    def get_products_from_data(cls) -> List[Dict]:
        """Extract unique products with their latest prices from the data (prices in USD, will be converted to AED by caller)"""
        if cls.products_cache is None:
            df = cls.load_data()
            if df.empty:
                return []
            
            # Load costs
            costs = cls.load_costs()
            
            # Get unique products
            unique_products = df.groupby('product_name').agg({
                'period_normalized_date': 'max',
                'price_per_sales_unit': 'last',
                'category': 'last'
            }).reset_index()
            
            # Create product list with IDs (prices in USD from CSV)
            products = []
            for idx, row in unique_products.iterrows():
                product_id = f"NES{str(idx+1).zfill(3)}"
                product_name = row['product_name']
                price = round(float(row['price_per_sales_unit']), 2)
                
                # Get cost from costs file or calculate as 85% of price
                if product_name in costs:
                    cost = costs[product_name]['cost']
                else:
                    cost = round(price * 0.85, 2)
                
                products.append({
                    "id": product_id,
                    "name": product_name,
                    "category": row['category'],
                    "current_price": price,
                    "cost": cost,
                    "unit": "unit",
                    "last_data_date": row['period_normalized_date'].strftime('%Y-%m-%d')
                })
            
            cls.products_cache = products
            print(f"✓ Extracted {len(products)} unique products from data")
        
        return cls.products_cache
    
    @classmethod
    def get_product_data(cls, product_name: str) -> pd.DataFrame:
        """Get all data for a specific product"""
        df = cls.load_data()
        return df[df['product_name'] == product_name].sort_values('period_normalized_date')
    
    @classmethod
    def get_latest_price(cls, product_name: str) -> float:
        """Get the latest price for a product"""
        df = cls.get_product_data(product_name)
        if df.empty:
            return 15.0  # Default fallback
        return float(df.iloc[-1]['price_per_sales_unit'])
    
    @classmethod
    def get_rolling_averages(cls, product_name: str, emirate: str = None, store_type: str = None) -> Dict:
        """
        Get the rolling averages from the latest data point for a product
        Optionally filter by emirate and store_type
        """
        df = cls.get_product_data(product_name)
        
        if df.empty:
            # Return defaults if no data
            return {
                'rolling_3day_mean': 50.0,
                'rolling_7day_mean': 50.0,
                'rolling_30day_mean': 50.0,
                'rolling_3day_std': 5.0,
                'rolling_7day_std': 5.0,
                'rolling_30day_std': 5.0
            }
        
        # Filter by emirate and store_type if provided
        if emirate:
            df = df[df['emirate'] == emirate]
        if store_type:
            df = df[df['store_type'] == store_type]
        
        # If filtering resulted in no data, use the full product data
        if df.empty:
            df = cls.get_product_data(product_name)
        
        # Get the most recent row
        latest_row = df.iloc[-1]
        
        return {
            'rolling_3day_mean': float(latest_row.get('rolling_3day_mean', 50.0)),
            'rolling_7day_mean': float(latest_row.get('rolling_7day_mean', 50.0)),
            'rolling_30day_mean': float(latest_row.get('rolling_30day_mean', 50.0)),
            'rolling_3day_std': float(latest_row.get('rolling_3day_std', 5.0)),
            'rolling_7day_std': float(latest_row.get('rolling_7day_std', 5.0)),
            'rolling_30day_std': float(latest_row.get('rolling_30day_std', 5.0))
        }
    
    @classmethod
    def get_available_locations(cls, product_name: str = None) -> Tuple[List[str], List[str]]:
        """Get available emirates and store types from the data"""
        df = cls.load_data()
        
        if not df.empty and product_name:
            df = df[df['product_name'] == product_name]
        
        if df.empty:
            # Return defaults
            emirates = ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 
                       'Ras Al Khaimah', 'Fujairah', 'Umm Al Quwain']
            store_types = ['Hypermarket', 'Supermarket', 'Mini Market', 
                          'Convenience Store', 'Traditional', 'Online']
        else:
            emirates = sorted(df['emirate'].unique().tolist())
            store_types = sorted(df['store_type'].unique().tolist())
        
        return emirates, store_types
    
    @classmethod
    def get_product_stats(cls, product_name: str) -> Dict:
        """Get comprehensive statistics for a product"""
        df = cls.get_product_data(product_name)
        
        if df.empty:
            return {}
        
        return {
            "total_records": len(df),
            "date_range": {
                "start": df['period_normalized_date'].min().strftime('%Y-%m-%d'),
                "end": df['period_normalized_date'].max().strftime('%Y-%m-%d')
            },
            "price_stats": {
                "min": float(df['price_per_sales_unit'].min()),
                "max": float(df['price_per_sales_unit'].max()),
                "mean": float(df['price_per_sales_unit'].mean()),
                "current": float(df.iloc[-1]['price_per_sales_unit'])
            },
            "sales_stats": {
                "min": float(df['sales_units'].min()),
                "max": float(df['sales_units'].max()),
                "mean": float(df['sales_units'].mean()),
                "total": float(df['sales_units'].sum())
            },
            "locations": {
                "emirates": sorted(df['emirate'].unique().tolist()),
                "store_types": sorted(df['store_type'].unique().tolist())
            }
        }
