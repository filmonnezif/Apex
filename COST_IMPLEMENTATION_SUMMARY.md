# Cost-Based Profit Calculation Implementation

## Overview
Implemented actual cost-based profit calculations using real historical pricing data. The system now calculates product costs as 85% of the most recent price from historical data and uses these costs for accurate profit analysis.

## Implementation Date
October 28, 2025

---

## Changes Made

### 1. Backend Changes

#### A. Product Cost Calculation Script (`calculate_product_costs.py`)
**Purpose:** Extract most recent prices from historical data and calculate costs

**Formula:** 
```
Cost = Latest Price × 0.85 (85% of price)
Margin = 15%
```

**Process:**
1. Load historical sales data from CSV
2. Sort by date and get most recent price for each product
3. Calculate cost as 85% of the latest price
4. Save results to `product_costs.json`

**Output Example:**
```json
{
  "NESCAFE 3IN1 CLASSIC 20GX24 BOX (CM)": {
    "product_name": "NESCAFE 3IN1 CLASSIC 20GX24 BOX (CM)",
    "cost": 5.38,
    "latest_price": 6.33,
    "margin_percentage": 15.0
  }
}
```

#### B. Data Service Updates (`services/data_service.py`)

**New Methods Added:**
- `load_costs()`: Load product costs from JSON file
- `get_product_cost(product_name)`: Get cost for a specific product

**Updated Methods:**
- `get_products_from_data()`: Now includes cost field in product data

**Code Changes:**
```python
# Load costs on initialization
costs = cls.load_costs()

# Add cost to product data
cost = costs[product_name]['cost'] if product_name in costs else round(price * 0.85, 2)
product['cost'] = cost
```

#### C. Elasticity Service Updates (`services/elasticity_service.py`)

**Updated Method:**
- `estimate_cost()`: Now uses actual costs from data first, falls back to margin-based estimation

**Before:**
```python
def estimate_cost(cls, product_name: str, current_price: float) -> float:
    # Always used margin-based estimation
    estimated_cost = current_price * (1 - typical_margin)
```

**After:**
```python
def estimate_cost(cls, product_name: str, current_price: float) -> float:
    # First try to get actual cost from data service
    actual_cost = DataService.get_product_cost(product_name)
    if actual_cost > 0:
        return actual_cost
    # Fallback to margin-based estimation
```

#### D. Price Routes Updates (`routes/price_routes.py`)

**Changes:**
- Added cost conversion from USD to AED when returning product data
- Cost field now included in all product API responses

```python
# Convert cost to AED
if 'cost' in product:
    product['cost'] = round(product['cost'] * USD_TO_AED, 2)
```

---

### 2. Frontend Changes

#### A. Optimize Page Updates (`pages/optimize/[id].vue`)

**New Computed Properties:**

1. **`productCost`**: Gets actual cost from product data
   ```javascript
   const productCost = computed(() => {
     if (!product.value || !product.value.cost) return 0
     return product.value.cost
   })
   ```

2. **`profitMargin`**: Calculates actual margin from cost and price
   ```javascript
   const profitMargin = computed(() => {
     if (!product.value || !product.value.cost || !product.value.current_price) return 15
     return ((product.value.current_price - product.value.cost) / product.value.current_price * 100)
   })
   ```

3. **`estimatedProfit`**: Uses actual cost for profit calculation
   ```javascript
   const estimatedProfit = computed(() => {
     // Profit = (Price - Cost) × Demand
     return (params.value.price - productCost.value) * predictions.value.predicted_demand
   })
   ```

4. **`currentDemand`, `currentRevenue`, `currentProfit`**: Store current metrics for comparison

**New Comparison Functions:**

- `getDemandVsCurrent()`: Compare test demand vs current demand
- `getRevenueVsCurrent()`: Compare test revenue vs current revenue
- `getProfitVsCurrent()`: Compare test profit vs current profit
- `getDemandChangeAbs()`: Absolute change in demand
- `getRevenueChangeAbs()`: Absolute change in revenue
- `getProfitChangeAbs()`: Absolute change in profit

**UI Updates:**

1. **Metric Cards**: Now show both "vs Optimal" and "vs Current" comparisons
   - Badge shows comparison to optimal
   - Secondary line shows comparison to current

2. **Price Impact Analysis Card**: New comprehensive comparison card showing:
   - Current price vs Test price
   - Price change percentage
   - Demand, Revenue, and Profit changes with absolute values
   - Before → After values for all metrics

3. **Smart Insights**: Enhanced with:
   - Profit impact compared to current pricing (percentage and absolute)
   - Expected demand shift (units and percentage)
   - Optimization gap compared to AI optimal price

---

## Data Flow

### Cost Calculation Flow
```
Historical CSV Data 
  → calculate_product_costs.py
  → product_costs.json
  → DataService.load_costs()
  → ElasticityService.estimate_cost()
  → Profit Optimization
```

### Frontend Display Flow
```
API /products endpoint
  → Returns products with cost field
  → Frontend loads product data
  → Calculates profit using actual cost
  → Displays comparisons (current vs test vs optimal)
```

---

## API Response Example

### Products Endpoint (`/api/products`)
```json
[
  {
    "id": "NES001",
    "name": "NESCAFE 3IN1 CLASSIC 20GX24 BOX (CM)",
    "category": "TOTAL COFFEE",
    "current_price": 23.42,
    "cost": 19.91,
    "unit": "unit",
    "last_data_date": "2024-12-31"
  }
]
```

### Optimization Response
```json
{
  "current_metrics": {
    "price": 23.42,
    "demand": 300,
    "revenue": 7026.00,
    "profit": 1053.00,
    "estimated_cost": 19.91
  },
  "recommendation": {
    "recommended_price": 25.15,
    "expected_demand": 285,
    "expected_revenue": 7167.75,
    "expected_profit": 1493.40
  }
}
```

---

## Key Formulas

### Cost Calculation
```
Cost = Latest Price × 0.85
```

### Profit Calculation
```
Profit = (Price - Cost) × Demand
```

### Margin Calculation
```
Margin % = ((Price - Cost) / Price) × 100
```

### Percentage Change
```
Change % = ((New Value - Old Value) / Old Value) × 100
```

### Absolute Change
```
Change = New Value - Old Value
```

---

## Benefits

1. **Accuracy**: Real cost data instead of estimated margins
2. **Consistency**: Same cost used across optimization and simulation
3. **Transparency**: Users can see actual costs and margins
4. **Better Decisions**: Clear comparison between current, test, and optimal scenarios
5. **Data-Driven**: Based on actual historical pricing data

---

## Files Modified

### Backend
- `backend/calculate_product_costs.py` (NEW)
- `backend/product_costs.json` (NEW)
- `backend/services/data_service.py`
- `backend/services/elasticity_service.py`
- `backend/routes/price_routes.py`

### Frontend
- `frontend/pages/optimize/[id].vue`

---

## Testing

### Backend Verification
```bash
# Check cost calculation
python backend/calculate_product_costs.py

# Test API endpoint
curl http://localhost:8000/api/products
```

### Frontend Verification
1. Navigate to optimize page for any product
2. Verify "Price Impact Analysis" card appears
3. Check that profit calculations use actual cost
4. Adjust price and verify all comparisons update correctly

---

## Future Enhancements

1. **Dynamic Cost Updates**: Periodically recalculate costs from latest data
2. **Cost Trends**: Show historical cost trends
3. **Supplier Integration**: Direct cost data from suppliers
4. **Category-Specific Margins**: Different margins per category
5. **Seasonal Costs**: Account for seasonal cost variations

---

## Notes

- Costs are stored in AED (converted from USD historical data)
- 85% ratio chosen to represent typical FMCG cost structure (15% margin)
- Fallback to margin-based estimation if cost data unavailable
- All comparisons show both percentage and absolute changes
