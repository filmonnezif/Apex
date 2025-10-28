"""
Test script for the Demand Prediction API
Run this after starting the FastAPI server to test predictions
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("="*80)
    print("Testing Health Check")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_model_info():
    """Test the model info endpoint"""
    print("="*80)
    print("Testing Model Info")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/model-info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_valid_values():
    """Test the valid values endpoint"""
    print("="*80)
    print("Testing Valid Values")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/valid-values")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_prediction(data):
    """Test a prediction"""
    print("="*80)
    print("Testing Prediction")
    print("="*80)
    print("Input:")
    print(json.dumps(data, indent=2))
    print()
    
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Prediction successful!")
        print(f"Predicted Demand: {result['predicted_demand']:.2f} units")
        print(f"\nFull Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("Nestle UAE Demand Prediction API - Test Suite")
    print("="*80 + "\n")
    
    # Test basic endpoints
    test_health()
    test_model_info()
    test_valid_values()
    
    # Test Case 1: Dubai Hypermarket on Weekday
    print("TEST CASE 1: Dubai Hypermarket - Weekday")
    test_prediction({
        "product_name": "NESTLE NESQUIK 330GR(C) BOX",
        "category": "Breakfast Cereals",
        "emirate": "Dubai",
        "store_type": "Hypermarket",
        "price_per_sales_unit": 15.5,
        "is_weekend": 0,
        "is_holiday": 0,
        "month": 10,
        "day_of_week": 1,
        "day_of_month": 27,
        "rolling_3day_mean": 50.0,
        "rolling_7day_mean": 48.5,
        "rolling_30day_mean": 52.0,
        "rolling_3day_std": 5.2,
        "rolling_7day_std": 6.8,
        "rolling_30day_std": 8.1
    })
    
    # Test Case 2: Dubai Hypermarket on Weekend
    print("TEST CASE 2: Dubai Hypermarket - Weekend")
    test_prediction({
        "product_name": "NESTLE NESQUIK 330GR(C) BOX",
        "category": "Breakfast Cereals",
        "emirate": "Dubai",
        "store_type": "Hypermarket",
        "price_per_sales_unit": 15.5,
        "is_weekend": 1,
        "is_holiday": 0,
        "month": 10,
        "day_of_week": 5,  # Saturday
        "day_of_month": 27,
        "rolling_3day_mean": 50.0,
        "rolling_7day_mean": 48.5,
        "rolling_30day_mean": 52.0,
        "rolling_3day_std": 5.2,
        "rolling_7day_std": 6.8,
        "rolling_30day_std": 8.1
    })
    
    # Test Case 3: Abu Dhabi Supermarket
    print("TEST CASE 3: Abu Dhabi Supermarket")
    test_prediction({
        "product_name": "NESCAFE 3IN1 CLASSIC 20GX24 BOX (CM)",
        "category": "Hot Beverages",
        "emirate": "Abu Dhabi",
        "store_type": "Supermarket",
        "price_per_sales_unit": 25.0,
        "is_weekend": 0,
        "is_holiday": 0,
        "month": 12,
        "day_of_week": 2,
        "day_of_month": 15,
        "rolling_3day_mean": 35.0,
        "rolling_7day_mean": 38.0,
        "rolling_30day_mean": 40.0,
        "rolling_3day_std": 4.5,
        "rolling_7day_std": 5.5,
        "rolling_30day_std": 6.2
    })
    
    # Test Case 4: Holiday Effect
    print("TEST CASE 4: Holiday Effect - Dubai")
    test_prediction({
        "product_name": "MAGGI BBQ & GRILLS SEASONING 150G TUB",
        "category": "Culinary",
        "emirate": "Dubai",
        "store_type": "Hypermarket",
        "price_per_sales_unit": 12.0,
        "is_weekend": 0,
        "is_holiday": 1,
        "month": 12,
        "day_of_week": 3,
        "day_of_month": 2,
        "rolling_3day_mean": 45.0,
        "rolling_7day_mean": 42.0,
        "rolling_30day_mean": 40.0,
        "rolling_3day_std": 6.0,
        "rolling_7day_std": 7.0,
        "rolling_30day_std": 8.5
    })
    
    # Test Case 5: Online Store
    print("TEST CASE 5: Online Store - Sharjah")
    test_prediction({
        "product_name": "PURINA FRISK.CHICKEN IN GRAVY JUNI.85G S",
        "category": "Pet Care",
        "emirate": "Sharjah",
        "store_type": "Online",
        "price_per_sales_unit": 8.5,
        "is_weekend": 1,
        "is_holiday": 0,
        "month": 10,
        "day_of_week": 4,  # Friday
        "day_of_month": 25,
        "rolling_3day_mean": 15.0,
        "rolling_7day_mean": 14.5,
        "rolling_30day_mean": 16.0,
        "rolling_3day_std": 2.5,
        "rolling_7day_std": 3.0,
        "rolling_30day_std": 3.8
    })
    
    # Test Case 6: Different Price Point
    print("TEST CASE 6: Price Sensitivity Test")
    print("Same product, same conditions, but different price")
    print("\nLower Price (10.0):")
    test_prediction({
        "product_name": "NESTLE NESQUIK 330GR(C) BOX",
        "category": "Breakfast Cereals",
        "emirate": "Dubai",
        "store_type": "Hypermarket",
        "price_per_sales_unit": 10.0,  # Lower price
        "is_weekend": 0,
        "is_holiday": 0,
        "month": 10,
        "day_of_week": 1,
        "day_of_month": 27,
        "rolling_3day_mean": 50.0,
        "rolling_7day_mean": 48.5,
        "rolling_30day_mean": 52.0,
        "rolling_3day_std": 5.2,
        "rolling_7day_std": 6.8,
        "rolling_30day_std": 8.1
    })
    
    print("Higher Price (20.0):")
    test_prediction({
        "product_name": "NESTLE NESQUIK 330GR(C) BOX",
        "category": "Breakfast Cereals",
        "emirate": "Dubai",
        "store_type": "Hypermarket",
        "price_per_sales_unit": 20.0,  # Higher price
        "is_weekend": 0,
        "is_holiday": 0,
        "month": 10,
        "day_of_week": 1,
        "day_of_month": 27,
        "rolling_3day_mean": 50.0,
        "rolling_7day_mean": 48.5,
        "rolling_30day_mean": 52.0,
        "rolling_3day_std": 5.2,
        "rolling_7day_std": 6.8,
        "rolling_30day_std": 8.1
    })
    
    print("\n" + "="*80)
    print("Test Suite Completed!")
    print("="*80)
