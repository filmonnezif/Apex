"""
Debug script to discover the exact features the model expects
"""
import joblib
import pandas as pd
import numpy as np

# Load model
model = joblib.load('price_elasticity_model.pkl')

# Load current data
df = pd.read_csv('last_month_data (2).csv')

print("="*80)
print("DISCOVERING MODEL'S EXPECTED FEATURES")
print("="*80)

# Prepare data exactly as in training
covariates = [
    'promotion', 'month', 'day_of_week', 'is_weekend', 'is_holiday',
    'category', 'brand', 'store_type',
    'rolling_7day_mean', 'rolling_7day_std'
]

print(f"\nBase covariates: {covariates}")

# Keep only existing
covariates = [c for c in covariates if c in df.columns]
print(f"Available covariates: {covariates}")

# Take a sample
sample = df.head(100).copy()

# Fill NaN in promotion
if 'promotion' in sample.columns:
    sample['promotion'] = sample['promotion'].fillna('NO PROMO')

X = sample[covariates].copy()

print(f"\nBefore encoding - shape: {X.shape}")
print(f"Categorical columns: {X.select_dtypes(include=['object', 'category']).columns.tolist()}")

# One-hot encode
cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
if len(cat_cols) > 0:
    X = pd.get_dummies(X, columns=cat_cols, drop_first=True)

X = X.fillna(0)

print(f"\nAfter encoding - shape: {X.shape}")
print(f"\nColumn names ({len(X.columns)}):")
for i, col in enumerate(X.columns, 1):
    print(f"  {i:3d}. {col}")

# Try to use the model
print("\n" + "="*80)
print("TESTING MODEL PREDICTION")
print("="*80)

try:
    X_arr = X.values
    result = model.effect(X_arr)
    print(f"✓ Success! Model prediction worked with {X.shape[1]} features")
    print(f"  Sample elasticities: {result[:5]}")
except Exception as e:
    print(f"✗ Error: {e}")
    
    # Try to get more info
    print("\nTrying to extract expected features from model...")
    
    # Try accessing internal models
    if hasattr(model, 'models_t'):
        print(f"  models_t length: {len(model.models_t)}")
        if len(model.models_t) > 0:
            fold_0 = model.models_t[0]
            print(f"  First fold type: {type(fold_0)}")
            
            if isinstance(fold_0, list):
                print(f"  First fold is a list with {len(fold_0)} elements")
                if len(fold_0) > 0:
                    model_0 = fold_0[0]
                    print(f"  First model type: {type(model_0)}")
                    
                    if hasattr(model_0, 'feature_names_in_'):
                        features = model_0.feature_names_in_
                        print(f"\n  ✓ FOUND EXPECTED FEATURES ({len(features)}):")
                        for i, feat in enumerate(features, 1):
                            print(f"    {i:3d}. {feat}")
                        
                        # Now try with correct features
                        print(f"\n  Attempting to align features...")
                        for col in features:
                            if col not in X.columns:
                                X[col] = 0
                                print(f"    Added missing: {col}")
                        
                        X_aligned = X[features]
                        print(f"\n  Aligned shape: {X_aligned.shape}")
                        
                        result = model.effect(X_aligned.values)
                        print(f"  ✓✓ SUCCESS with aligned features!")
                        print(f"  Sample elasticities: {result[:5]}")

print("\n" + "="*80)
print("COMPARISON: OUR FEATURES vs MODEL FEATURES")
print("="*80)

if hasattr(model, 'models_t') and len(model.models_t) > 0:
    fold_0 = model.models_t[0]
    if isinstance(fold_0, list) and len(fold_0) > 0:
        model_0 = fold_0[0]
        if hasattr(model_0, 'feature_names_in_'):
            expected = set(model_0.feature_names_in_)
            current = set(X.columns)
            
            missing = expected - current
            extra = current - expected
            
            print(f"\nOur features: {len(current)}")
            print(f"Model expects: {len(expected)}")
            print(f"Missing: {len(missing)}")
            print(f"Extra: {len(extra)}")
            
            if missing:
                print(f"\nMissing features (need to add):")
                for feat in sorted(missing):
                    print(f"  - {feat}")
            
            if extra:
                print(f"\nExtra features (need to remove):")
                for feat in sorted(extra):
                    print(f"  - {feat}")
