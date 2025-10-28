"""
Extract and save feature info from the existing trained model
This needs to be done once so the API can use the correct features
"""
import pandas as pd
import joblib

# Load the data that matches the model
df = pd.read_csv('last_month_data (2).csv')

# Prepare features exactly as in training
covariates = [
    'promotion', 'month', 'day_of_week', 'is_weekend', 'is_holiday',
    'category', 'brand', 'store_type',
    'rolling_7day_mean', 'rolling_7day_std'
]

covariates = [c for c in covariates if c in df.columns]
X = df[covariates].copy()

# Handle NaN in promotion
if 'promotion' in X.columns:
    X['promotion'] = X['promotion'].fillna('NO PROMO')

# One-hot encode
cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
if len(cat_cols) > 0:
    X = pd.get_dummies(X, columns=cat_cols, drop_first=True)

X = X.fillna(0)

# Save feature info
feature_info = {
    'feature_names': X.columns.tolist(),
    'num_features': len(X.columns),
    'categorical_encoding': {
        'promotion': sorted(df['promotion'].fillna('NO PROMO').unique()) if 'promotion' in df.columns else [],
        'category': sorted(df['category'].unique()) if 'category' in df.columns else [],
        'brand': sorted(df['brand'].unique()) if 'brand' in df.columns else [],
        'store_type': sorted(df['store_type'].unique()) if 'store_type' in df.columns else []
    },
    'covariates_used': covariates
}

joblib.dump(feature_info, 'elasticity_feature_info.pkl')

print("="*80)
print("Feature info extracted and saved!")
print("="*80)
print(f"\nNumber of features: {feature_info['num_features']}")
print(f"\nFeature names:")
for i, feat in enumerate(feature_info['feature_names'], 1):
    print(f"  {i:2d}. {feat}")

print(f"\nCategorical encodings:")
for cat, values in feature_info['categorical_encoding'].items():
    print(f"  {cat}: {values}")

print(f"\nFile saved: elasticity_feature_info.pkl")
print("="*80)
