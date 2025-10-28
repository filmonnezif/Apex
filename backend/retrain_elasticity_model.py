"""
Retrain the elasticity model using the current data (last_month_data (2).csv)
This ensures the model uses the same categorical values and features
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from econml.dml import LinearDML
import warnings
warnings.filterwarnings("ignore")

print("="*80)
print("RETRAINING ELASTICITY MODEL WITH CURRENT DATA")
print("="*80)

# Load data
print("\n1. Loading data...")
df = pd.read_csv('last_month_data (2).csv')
print(f"   ✓ Loaded {len(df)} rows")
print(f"   Columns: {df.columns.tolist()}")

# Define columns
COL_PRICE = 'price_per_sales_unit'
COL_QTY = 'sales_units'
COL_PRODUCT = 'product_name'

# Clean data
print("\n2. Cleaning data...")
df = df.copy()
df[COL_PRICE] = pd.to_numeric(df[COL_PRICE], errors='coerce')
df[COL_QTY] = pd.to_numeric(df[COL_QTY], errors='coerce')

before = len(df)
df = df[df[COL_PRICE] > 0]
df = df[df[COL_QTY] >= 0]
after = len(df)
print(f"   ✓ Rows: {before} → {after} (removed {before-after} invalid rows)")

# Log transforms for log-log model
print("\n3. Creating log-transformed variables...")
eps = 1e-6
df['T'] = np.log(df[COL_PRICE].astype(float) + eps)   # treatment: log(price)
df['Y'] = np.log(df[COL_QTY].astype(float) + eps)     # outcome: log(quantity)
print(f"   ✓ Created T (log price) and Y (log quantity)")
print(f"   T range: [{df['T'].min():.3f}, {df['T'].max():.3f}]")
print(f"   Y range: [{df['Y'].min():.3f}, {df['Y'].max():.3f}]")

# Prepare covariates
print("\n4. Preparing covariates...")
covariates = [
    'promotion', 'month', 'day_of_week', 'is_weekend', 'is_holiday',
    'category', 'brand', 'store_type',
    'rolling_7day_mean', 'rolling_7day_std'
]

# Keep only existing
covariates = [c for c in covariates if c in df.columns]
print(f"   Using covariates: {covariates}")

X = df[covariates].copy()

# Handle NaN in promotion
if 'promotion' in X.columns:
    X['promotion'] = X['promotion'].fillna('NO PROMO')

# One-hot encode categorical variables
cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
print(f"   Categorical columns: {cat_cols}")

if len(cat_cols) > 0:
    X = pd.get_dummies(X, columns=cat_cols, drop_first=True)

X = X.fillna(0)
print(f"   ✓ Final feature matrix shape: {X.shape}")
print(f"   Feature names ({len(X.columns)}):")
for i, col in enumerate(X.columns, 1):
    print(f"      {i:2d}. {col}")

# Check price variation
print("\n5. Checking price variation...")
price_var = df.groupby(COL_PRODUCT)[COL_PRICE].nunique()
print(f"   Total unique prices: {df[COL_PRICE].nunique()}")
print(f"   Per-product price unique counts:")
print(f"      Mean: {price_var.mean():.1f}")
print(f"      Min: {price_var.min()}")
print(f"      Max: {price_var.max()}")
one_price = (price_var == 1).sum()
print(f"   Products with only 1 price: {one_price}/{len(price_var)}")

# Prepare arrays for model
Y = df['Y'].values
T = df['T'].values
X_arr = X.values

print(f"\n6. Training LinearDML model...")
print(f"   Y shape: {Y.shape}")
print(f"   T shape: {T.shape}")
print(f"   X shape: {X_arr.shape}")

# Create XGBoost models
model_y = XGBRegressor(
    n_estimators=100, 
    learning_rate=0.1, 
    max_depth=5, 
    random_state=123, 
    n_jobs=-1
)
model_t = XGBRegressor(
    n_estimators=100, 
    learning_rate=0.1, 
    max_depth=5, 
    random_state=123, 
    n_jobs=-1
)

# Train LinearDML
est = LinearDML(
    model_y=model_y, 
    model_t=model_t,
    discrete_treatment=False, 
    cv=3, 
    random_state=123
)

print("   Training (this may take a minute)...")
est.fit(Y, T, X=X_arr)
print("   ✓ Model trained successfully!")

# Calculate results
print("\n7. Computing elasticities...")
ate = est.ate(X=X_arr)
hetero = est.effect(X_arr)

print(f"   Average Treatment Effect (ATE): {ate:.4f}")
print(f"   Heterogeneous effects:")
print(f"      Mean: {hetero.mean():.4f}")
print(f"      Std: {hetero.std():.4f}")
print(f"      Min: {hetero.min():.4f}")
print(f"      Max: {hetero.max():.4f}")

# Per-product summary
df['elasticity'] = hetero
prod_summary = df.groupby(COL_PRODUCT)['elasticity'].agg(['mean', 'std', 'count']).reset_index()
prod_summary = prod_summary.sort_values('mean')

print(f"\n8. Per-product elasticity summary:")
print(prod_summary.to_string(index=False))

# Save model
print("\n9. Saving model...")
model_path = 'price_elasticity_model.pkl'
joblib.dump(est, model_path)
print(f"   ✓ Model saved to: {model_path}")

# Save feature names for reference
feature_info = {
    'feature_names': X.columns.tolist(),
    'num_features': len(X.columns),
    'categorical_encoding': {
        'promotion': sorted(df['promotion'].unique()) if 'promotion' in df.columns else [],
        'category': sorted(df['category'].unique()) if 'category' in df.columns else [],
        'brand': sorted(df['brand'].unique()) if 'brand' in df.columns else [],
        'store_type': sorted(df['store_type'].unique()) if 'store_type' in df.columns else []
    },
    'covariates_used': covariates
}

joblib.dump(feature_info, 'elasticity_feature_info.pkl')
print(f"   ✓ Feature info saved to: elasticity_feature_info.pkl")

# Save product elasticity summary
prod_summary.to_csv('product_elasticity_summary.csv', index=False)
print(f"   ✓ Product summary saved to: product_elasticity_summary.csv")

# Test the saved model
print("\n10. Testing saved model...")
loaded_model = joblib.load(model_path)
loaded_features = joblib.load('elasticity_feature_info.pkl')

test_elasticity = loaded_model.effect(X_arr[:10])
print(f"   ✓ Model loads and predicts successfully!")
print(f"   Test elasticities (first 10): {test_elasticity}")

print("\n" + "="*80)
print("MODEL RETRAINING COMPLETE!")
print("="*80)
print(f"\nFiles created:")
print(f"  1. price_elasticity_model.pkl - Trained LinearDML model")
print(f"  2. elasticity_feature_info.pkl - Feature schema and encoding info")
print(f"  3. product_elasticity_summary.csv - Per-product elasticity estimates")
print(f"\nThe model is now ready to use with the current data!")
print("="*80)
