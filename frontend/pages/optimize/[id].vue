<template>
  <div class="min-h-screen py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Compact Header -->
    <div class="mb-4">
      <button @click="goBack" class="glass-button-secondary flex items-center space-x-2 mb-3">
        <span>←</span>
        <span>Back to Dashboard</span>
      </button>

      <!-- Compact Product Info -->
      <div v-if="product" class="glass-card p-4">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-lg overflow-hidden bg-blue-50 shadow flex items-center justify-center flex-shrink-0">
            <ProductImage :productId="product.id" :alt="product.name" size="small" class="w-full h-full p-2" />
          </div>
          <div class="flex-1 min-w-0">
            <h1 class="text-lg font-bold text-blue-900 mb-0.5 truncate">{{ product.name }}</h1>
            <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">{{ product.category }}</span>
          </div>
          <div class="flex gap-4 text-sm">
            <div class="text-right">
              <div class="text-blue-600 text-xs">Current Price</div>
              <div class="text-lg font-semibold text-blue-900">AED {{ product.current_price.toFixed(2) }}</div>
            </div>
            <div class="text-right">
              <div class="text-blue-600 text-xs">Demand</div>
              <div class="text-lg font-semibold text-blue-900">{{ formatNumber(product.monthly_demand) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Optimal Price Card -->
      <div v-if="optimization" class="glass-card p-4 bg-gradient-to-br from-blue-50 to-cyan-50 mt-4">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-2xl">⭐</span>
              <h3 class="font-semibold text-blue-900">AI Optimal Price</h3>
              <span class="text-xs text-blue-600 bg-white px-2 py-0.5 rounded">
                {{ optimization.recommendation.confidence_score }}% confidence
              </span>
            </div>
            <div class="flex items-baseline gap-3">
              <div class="text-4xl font-bold text-blue-900">
                AED {{ optimization.recommendation.recommended_price.toFixed(2) }}
              </div>
              <div :class="['text-lg font-medium', optimization.recommendation.price_change_percentage > 0 ? 'text-green-600' : 'text-red-600']">
                {{ optimization.recommendation.price_change_percentage > 0 ? '+' : '' }}{{ optimization.recommendation.price_change_percentage.toFixed(1) }}%
              </div>
            </div>
            <p class="text-xs text-blue-700 mt-2 leading-relaxed">{{ optimization.recommendation.reasoning }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Layout: Left Parameters + Right Results -->
    <div v-if="product" class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- LEFT SIDE: Parameters Panel -->
      <div class="lg:col-span-4">
        <div class="glass-card p-5 sticky top-4">
          <div class="mb-4">
            <h3 class="text-lg font-semibold text-blue-900 mb-1 flex items-center gap-2">
              <span>�</span>
              <span>Simulate Different Prices</span>
            </h3>
            <p class="text-sm text-blue-500">Adjust parameters to see real-time predictions</p>
          </div>
          <div class="space-y-3">
            <!-- Price Slider -->
            <div>
              <div class="flex items-center justify-between mb-3">
                <label class="block text-blue-700 text-base font-semibold">Price (AED)</label>
                <span class="text-3xl font-bold text-blue-900">{{ params.price.toFixed(2) }}</span>
              </div>
              <input 
                v-model.number="params.price" 
                type="range" 
                :min="priceRange.min" 
                :max="priceRange.max" 
                :step="priceRange.step" 
                @input="onParamsChange(false)" 
                class="w-full h-3 bg-blue-200 rounded-lg appearance-none cursor-pointer slider" 
              />
              <div class="flex justify-between text-xs text-blue-500 mt-2">
                <span>{{ priceRange.min }}</span>
                <span>{{ priceRange.max }}</span>
              </div>
              <div class="flex gap-2 mt-3">
                <button @click="setPrice(product.current_price)" class="w-full px-4 py-2 text-sm font-semibold text-blue-700 bg-blue-100 rounded hover:bg-blue-200 transition-colors">
                  Reset to Current
                </button>
              </div>
            </div>

            <!-- Context Inputs -->
            <div class="space-y-3">
              <div>
                <label class="block text-blue-700 text-sm font-semibold mb-2">Emirate</label>
                <select v-model="params.emirate" @change="onParamsChange" class="glass-input w-full text-sm py-2.5">
                  <option value="Dubai">Dubai</option>
                  <option value="Abu Dhabi">Abu Dhabi</option>
                  <option value="Sharjah">Sharjah</option>
                  <option value="Ajman">Ajman</option>
                  <option value="Ras Al Khaimah">Ras Al Khaimah</option>
                  <option value="Fujairah">Fujairah</option>
                  <option value="Umm Al Quwain">Umm Al Quwain</option>
                </select>
              </div>

              <div>
                <label class="block text-blue-700 text-sm font-semibold mb-2">Store Type</label>
                <select v-model="params.store_type" @change="onParamsChange" class="glass-input w-full text-sm py-2.5">
                  <option value="Hypermarket">Hypermarket</option>
                  <option value="Supermarket">Supermarket</option>
                  <option value="Mini Market">Mini Market</option>
                  <option value="Convenience Store">Convenience Store</option>
                  <option value="Traditional">Traditional</option>
                  <option value="Online">Online</option>
                </select>
              </div>

              <div>
                <label class="block text-blue-700 text-sm font-semibold mb-2">Date</label>
                <input v-model="params.date" type="date" @change="onParamsChange" class="glass-input w-full text-sm py-2.5" />
              </div>

              <div>
                <label class="block text-blue-700 text-sm font-semibold mb-2">Special Day</label>
                <select v-model.number="params.is_holiday" @change="onParamsChange" class="glass-input w-full text-sm py-2.5">
                  <option :value="0">Regular Day</option>
                  <option :value="1">Holiday/Special Event</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT SIDE: Results Panel -->
      <div class="lg:col-span-8">
        <div class="space-y-4">
        
        <!-- Loading State -->
        <div v-if="calculating && !predictions" class="glass-card p-8">
          <div class="flex flex-col items-center justify-center text-blue-600">
            <svg class="animate-spin h-8 w-8 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <div class="text-sm font-semibold">Calculating AI predictions...</div>
          </div>
        </div>

        <!-- Results Content -->
        <div v-else-if="predictions" class="space-y-4">
          
          <!-- Current Test Price -->
          <div class="glass-card p-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-blue-600 text-sm font-semibold">Testing Price</div>
                <div class="text-3xl font-bold text-blue-900 mt-1">AED {{ params.price.toFixed(2) }}</div>
              </div>
              <div :class="['text-2xl font-bold px-4 py-2 rounded-lg', 
                getPriceChangePct() > 0 ? 'text-green-600 bg-green-50' : 
                getPriceChangePct() < 0 ? 'text-red-600 bg-red-50' : 
                'text-blue-600 bg-blue-50']">
                {{ getPriceChangePct() > 0 ? '+' : '' }}{{ getPriceChangePct().toFixed(1) }}%
              </div>
            </div>
          </div>

          <!-- Key Metrics Grid -->
          <div class="grid grid-cols-2 gap-3">
            <!-- Demand -->
            <div class="glass-card p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-blue-700 text-sm font-semibold">📊 Demand</span>
                <span :class="['px-2 py-0.5 rounded text-[10px] font-semibold', 
                  getDemandVsOptimal() >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">
                  {{ getDemandVsOptimal() >= 0 ? '↑' : '↓' }} {{ Math.abs(getDemandVsOptimal()).toFixed(1) }}%
                </span>
              </div>
              <div class="text-2xl font-bold text-blue-900">{{ formatNumber(predictions.predicted_demand) }}</div>
            </div>

            <!-- Revenue -->
            <div class="glass-card p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-green-700 text-sm font-semibold">💰 Revenue</span>
                <span :class="['px-2 py-0.5 rounded text-[10px] font-semibold', 
                  getRevenueVsOptimal() >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">
                  {{ getRevenueVsOptimal() >= 0 ? '↑' : '↓' }} {{ Math.abs(getRevenueVsOptimal()).toFixed(1) }}%
                </span>
              </div>
              <div class="text-2xl font-bold text-green-700">{{ formatNumber(predictions.predicted_revenue) }}</div>
            </div>

            <!-- Profit -->
            <div class="glass-card p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-purple-700 text-sm font-semibold">📈 Profit</span>
                <span :class="['px-2 py-0.5 rounded text-[10px] font-semibold', 
                  getProfitVsOptimal() >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">
                  {{ getProfitVsOptimal() >= 0 ? '↑' : '↓' }} {{ Math.abs(getProfitVsOptimal()).toFixed(1) }}%
                </span>
              </div>
              <div class="text-2xl font-bold text-purple-700">{{ formatNumber(estimatedProfit) }}</div>
              <div class="text-xs text-blue-500 mt-1">Margin: {{ profitMargin }}%</div>
            </div>

            <!-- Elasticity -->
            <div class="glass-card p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-blue-700 text-sm font-semibold">⚡ Elasticity</span>
                <span class="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                  {{ Math.abs(predictions.elasticity_coefficient) > 1 ? 'Elastic' : 'Inelastic' }}
                </span>
              </div>
              <div class="text-2xl font-bold text-blue-900">{{ predictions.elasticity_coefficient.toFixed(2) }}</div>
              <div class="text-xs text-blue-500 mt-1">{{ getElasticityExplanation() }}</div>
            </div>
          </div>

          <!-- Smart Insights -->
          <div v-if="optimization" class="glass-card p-4 bg-amber-50 border border-amber-200">
            <h4 class="font-semibold text-amber-900 mb-2 text-sm flex items-center gap-2">
              <span>💡</span>
              <span>Smart Insights</span>
            </h4>
            <div class="space-y-1.5 text-xs text-amber-800">
              <div v-if="Math.abs(getProfitVsOptimal()) > 5" class="flex items-start gap-2">
                <span class="text-amber-600">•</span>
                <span>
                  <strong>Profit Gap:</strong> {{ Math.abs(getProfitVsOptimal()).toFixed(1) }}% 
                  {{ getProfitVsOptimal() > 0 ? 'more' : 'less' }} profit than optimal.
                  {{ getProfitVsOptimal() < -10 ? ' Consider moving closer to AI price.' : '' }}
                </span>
              </div>
              <div v-if="Math.abs(params.price - optimization.recommendation.recommended_price) > product.current_price * 0.15" class="flex items-start gap-2">
                <span class="text-amber-600">•</span>
                <span><strong>Price Deviation:</strong> Test price is far from AI suggestion; large jumps can disrupt demand.</span>
              </div>
              <div v-if="Math.abs(predictions.elasticity_coefficient) > 1.5" class="flex items-start gap-2">
                <span class="text-amber-600">•</span>
                <span><strong>High Sensitivity:</strong> Highly elastic product. Favor modest, incremental changes.</span>
              </div>
            </div>
          </div>

          <!-- Scenario Context -->
          <div class="glass-card p-3">
            <h4 class="font-semibold text-blue-900 mb-2 text-xs flex items-center gap-1">
              <span>📋</span>
              <span>Scenario Context</span>
            </h4>
            <div class="grid grid-cols-4 gap-3 text-xs">
              <div>
                <span class="text-blue-500">Location</span>
                <div class="text-blue-900 font-semibold">{{ predictions.scenario.emirate }}</div>
              </div>
              <div>
                <span class="text-blue-500">Store</span>
                <div class="text-blue-900 font-semibold">{{ predictions.scenario.store_type }}</div>
              </div>
              <div>
                <span class="text-blue-500">Day Type</span>
                <div class="text-blue-900 font-semibold">{{ predictions.scenario.is_weekend ? 'Weekend' : 'Weekday' }}</div>
              </div>
              <div>
                <span class="text-blue-500">Month</span>
                <div class="text-blue-900 font-semibold">{{ getMonthName(predictions.scenario.month) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="glass-card p-12">
          <div class="flex flex-col items-center justify-center text-center text-blue-500">
            <div class="text-5xl mb-3">📊</div>
            <div class="font-semibold text-blue-700 text-lg">Ready to simulate</div>
            <div class="text-sm mt-2">
              Adjust any parameter to see real-time predictions.
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>

    <!-- BOTTOM: Charts Section -->
    <div v-if="optimization && predictions" class="mt-6">
      <div class="glass-card p-5">
        <h3 class="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
          <span>📈</span>
          <span>Performance Analysis</span>
        </h3>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 class="text-sm font-semibold text-blue-700 mb-3">Demand Curve</h4>
            <DemandChart :data="optimization.demand_curve" />
          </div>
          <div>
            <h4 class="text-sm font-semibold text-blue-700 mb-3">Revenue Trend</h4>
            <ProfitChart :data="optimization.demand_curve" />
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="glass-card p-12 text-center">
      <svg class="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <div class="text-blue-600 font-semibold">Loading product data...</div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const { fetchProducts, optimizePrice, simulatePrice } = useApi()

const product = ref(null)
const optimization = ref(null)
const predictions = ref(null)
const loading = ref(true)
const calculating = ref(false)
const autoUpdate = ref(true)

const params = ref({
  price: 15.0,
  emirate: 'Dubai',
  store_type: 'Hypermarket',
  date: new Date().toISOString().split('T')[0],
  is_holiday: 0
})

let changeTimeout = null

const productCost = computed(() => {
  if (!product.value || !product.value.cost) return 0
  return product.value.cost
})

const profitMargin = computed(() => {
  if (!product.value || !product.value.cost || !product.value.current_price) return 15
  // Calculate actual margin percentage from cost and price
  return ((product.value.current_price - product.value.cost) / product.value.current_price * 100)
})

const estimatedProfit = computed(() => {
  if (!predictions.value || !productCost.value) return 0
  // Profit = (Price - Cost) × Demand
  return (params.value.price - productCost.value) * predictions.value.predicted_demand
})

const optimalProfit = computed(() => {
  if (!optimization.value || !productCost.value) return 0
  // Use expected_profit from API if available, otherwise calculate
  if (optimization.value.recommendation.expected_profit) {
    return optimization.value.recommendation.expected_profit
  }
  // Calculate: (Optimal Price - Cost) × Optimal Demand
  return (optimization.value.recommendation.recommended_price - productCost.value) * optimization.value.recommendation.expected_demand
})

const priceRange = computed(() => {
  if (!product.value) return { min: 1, max: 100 }
  const basePrice = product.value.current_price
  const min = Math.max(1, Math.round(basePrice * 0.5 * 2) / 2)
  const max = Math.round(basePrice * 2 * 2) / 2
  const range = max - min
  const step = Math.round((range * 0.05) * 100) / 100 // 5% of range
  return { min, max, step: Math.max(0.01, step) }
})

const roundToStep = (value) => {
  if (!priceRange.value) return Math.round(value * 2) / 2
  const step = priceRange.value.step
  return Math.round(value / step) * step
}
const formatNumber = (num) => new Intl.NumberFormat('en-US').format(Math.round(num))
const getMonthName = (month) => ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month - 1] || ''

const getPriceChangePct = () => {
  if (!product.value) return 0
  return ((params.value.price - product.value.current_price) / product.value.current_price) * 100
}

const getDemandVsOptimal = () => {
  if (!optimization.value || !predictions.value) return 0
  return ((predictions.value.predicted_demand - optimization.value.recommendation.expected_demand) / optimization.value.recommendation.expected_demand) * 100
}

const getRevenueVsOptimal = () => {
  if (!optimization.value || !predictions.value) return 0
  return ((predictions.value.predicted_revenue - optimization.value.recommendation.expected_revenue) / optimization.value.recommendation.expected_revenue) * 100
}

const getProfitVsOptimal = () => {
  if (!optimization.value || !predictions.value) return 0
  return ((estimatedProfit.value - optimalProfit.value) / optimalProfit.value) * 100
}

const getElasticityExplanation = () => {
  if (!predictions.value) return ''
  const elasticity = Math.abs(predictions.value.elasticity_coefficient)
  if (elasticity > 1.5) return 'Highly elastic - demand is very sensitive to price changes.'
  if (elasticity > 1) return 'Elastic - demand responds noticeably to price changes.'
  if (elasticity > 0.5) return 'Moderately inelastic - demand is somewhat resistant to price changes.'
  return 'Highly inelastic - demand is very resistant to price changes.'
}

const getDateComponents = (dateString) => {
  const date = new Date(dateString)
  return {
    month: date.getMonth() + 1,
    day_of_week: (date.getDay() + 6) % 7,
    day_of_month: date.getDate(),
    is_weekend: [5, 6].includes(date.getDay()) ? 1 : 0
  }
}

const setPrice = (price) => {
  params.value.price = roundToStep(price)
  if (autoUpdate.value) onParamsChange(false)
}

const onParamsChange = (recalculateOptimal = true) => {
  if (!autoUpdate.value || !product.value) return
  if (changeTimeout) clearTimeout(changeTimeout)
  changeTimeout = setTimeout(async () => {
    if (recalculateOptimal) {
      // Recalculate optimization when context parameters change
      await runOptimization()
    }
    await calculatePredictions()
  }, 500)
}

const goBack = () => router.push('/')

const loadProduct = async () => {
  loading.value = true
  try {
    const products = await fetchProducts()
    const productId = route.params.id
    product.value = products.find(p => p.id === productId)
    if (!product.value) {
      console.error('Product not found')
      router.push('/')
      return
    }
    // First get the optimization to find AI optimal price
    await runOptimization()
    // Set the starting price to AI optimal if available, otherwise current price
    if (optimization.value && optimization.value.recommendation) {
      params.value.price = roundToStep(optimization.value.recommendation.recommended_price)
    } else {
      params.value.price = product.value.current_price
    }
    // Calculate initial predictions
    await calculatePredictions()
  } catch (error) {
    console.error('Error loading product:', error)
    router.push('/')
  } finally {
    loading.value = false
  }
}

const runOptimization = async () => {
  if (!product.value) return
  calculating.value = true
  try {
    const dateComponents = getDateComponents(params.value.date)
    const result = await optimizePrice({
      product_id: product.value.id,
      product_name: product.value.name,
      category: product.value.category,
      emirate: params.value.emirate,
      store_type: params.value.store_type,
      current_price: product.value.current_price,
      month: dateComponents.month,
      day_of_week: dateComponents.day_of_week,
      day_of_month: dateComponents.day_of_month,
      is_weekend: dateComponents.is_weekend,
      is_holiday: params.value.is_holiday
    })
    optimization.value = result
    return result
  } catch (error) {
    console.error('Error optimizing price:', error)
  } finally {
    calculating.value = false
  }
}

const optimizeAndApply = async () => {
  if (!product.value) return
  if (changeTimeout) {
    clearTimeout(changeTimeout)
    changeTimeout = null
  }
  const result = await runOptimization()
  if (result && result.recommendation) {
    params.value.price = roundToStep(result.recommendation.recommended_price)
    await calculatePredictions()
  }
}

const calculatePredictions = async () => {
  if (!product.value) return
  calculating.value = true
  try {
    const dateComponents = getDateComponents(params.value.date)
    const requestData = {
      product_name: product.value.name,
      category: product.value.category,
      emirate: params.value.emirate,
      store_type: params.value.store_type,
      price: params.value.price,
      month: dateComponents.month,
      day_of_week: dateComponents.day_of_week,
      day_of_month: dateComponents.day_of_month,
      is_weekend: dateComponents.is_weekend,
      is_holiday: params.value.is_holiday
    }
    predictions.value = await simulatePrice(requestData)
  } catch (error) {
    console.error('Error calculating predictions:', error)
    alert('Failed to calculate predictions. Please try again.')
  } finally {
    calculating.value = false
  }
}

onMounted(() => loadProduct())
</script>

<style scoped>
/* Custom Slider Styling */
.slider {
  -webkit-appearance: none;
  appearance: none;
  background: linear-gradient(to right, #dbeafe 0%, #bfdbfe 100%);
  border-radius: 8px;
  outline: none;
  transition: all 0.3s ease;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
  transition: all 0.2s ease;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.6);
}

.slider::-webkit-slider-thumb:active {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.8);
}

.slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
  transition: all 0.2s ease;
}

.slider::-moz-range-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.6);
}

.slider::-moz-range-thumb:active {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.8);
}

/* Smooth animations */
.glass-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(59, 130, 246, 0.12);
}

/* Sticky sidebar on larger screens */
@media (min-width: 1024px) {
  .sticky {
    position: sticky;
    max-height: calc(100vh - 6rem);
    overflow-y: auto;
  }
}

/* Custom scrollbar */
.sticky::-webkit-scrollbar {
  width: 6px;
}

.sticky::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 10px;
}

.sticky::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

.sticky::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
