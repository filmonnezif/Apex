"""
Script to inspect the elasticity model's expected features
"""
import joblib
import pandas as pd
import numpy as np

# Load the model
model_path = 'price_elasticity_model.pkl'
model = joblib.load(model_path)

print("="*80)
print("ELASTICITY MODEL INSPECTION")
print("="*80)

print(f"\nModel type: {type(model)}")
print(f"Model class: {model.__class__.__name__}")

# Try to get feature information
print("\n" + "="*80)
print("FEATURE INSPECTION")
print("="*80)

# EconML LinearDML model structure
if hasattr(model, 'model_y'):
    print(f"\nModel Y (outcome model): {type(model.model_y)}")
    if hasattr(model.model_y, 'feature_names_in_'):
        print(f"  Features: {model.model_y.feature_names_in_}")
        print(f"  Number of features: {len(model.model_y.feature_names_in_)}")

if hasattr(model, 'model_t'):
    print(f"\nModel T (treatment model): {type(model.model_t)}")
    if hasattr(model.model_t, 'feature_names_in_'):
        print(f"  Features: {model.model_t.feature_names_in_}")
        print(f"  Number of features: {len(model.model_t.feature_names_in_)}")

# Check if we can access feature names through other attributes
print("\n" + "="*80)
print("MODEL ATTRIBUTES")
print("="*80)

for attr in dir(model):
    if not attr.startswith('_') and 'feature' in attr.lower():
        print(f"  {attr}: {getattr(model, attr, 'N/A')}")

# Try to get the models from internal structure
print("\n" + "="*80)
print("INTERNAL MODELS (CV splits)")
print("="*80)

if hasattr(model, 'models_y'):
    print(f"\nNumber of Y models (CV folds): {len(model.models_y)}")
    if len(model.models_y) > 0:
        first_y_model = model.models_y[0]
        print(f"First Y model type: {type(first_y_model)}")
        if hasattr(first_y_model, 'feature_names_in_'):
            features = first_y_model.feature_names_in_
            print(f"\nExpected features ({len(features)}):")
            for i, feat in enumerate(features, 1):
                print(f"  {i:3d}. {feat}")

if hasattr(model, 'models_t'):
    print(f"\nNumber of T models (CV folds): {len(model.models_t)}")
    if len(model.models_t) > 0:
        first_t_model = model.models_t[0]
        print(f"First T model type: {type(first_t_model)}")
        if hasattr(first_t_model, 'feature_names_in_'):
            features = first_t_model.feature_names_in_
            print(f"\nT model expected features ({len(features)}):")
            for i, feat in enumerate(features, 1):
                print(f"  {i:3d}. {feat}")

# Analyze feature patterns
print("\n" + "="*80)
print("FEATURE ANALYSIS FROM NOTEBOOK")
print("="*80)

print("""
Based on the notebook, the training used these covariates:
- promotion
- month
- day_of_week
- is_weekend
- is_holiday
- category (one-hot encoded)
- brand (one-hot encoded)
- store_type (one-hot encoded)
- rolling_7day_mean
- rolling_7day_std

NOTE: The data file used was 'final_store_daily_data_with_features.csv'
      But current API uses 'last_month_data (2).csv' which may have different columns!
""")

# Load current data to compare
print("\n" + "="*80)
print("CURRENT DATA COLUMNS")
print("="*80)

try:
    df = pd.read_csv('last_month_data (2).csv')
    print(f"\nColumns in current data ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:3d}. {col}")
    
    print(f"\nData shape: {df.shape}")
    print(f"\nSample categorical values:")
    for col in ['category', 'brand', 'store_type']:
        if col in df.columns:
            print(f"  {col}: {sorted(df[col].unique())}")
except Exception as e:
    print(f"Error loading current data: {e}")
