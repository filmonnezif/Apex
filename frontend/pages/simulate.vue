<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-8">
      <h1 class="text-4xl font-bold text-blue-900 mb-2">
        Price Simulation Lab
      </h1>
      <p class="text-blue-600">
        Test different pricing scenarios across locations, stores, and dates to see real-time AI predictions
      </p>
    </div>

    <!-- Simulation Form -->
    <div class="glass-card p-6">
      <h2 class="text-2xl font-bold text-blue-900 mb-6">Simulation Parameters</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Product Selection -->
        <div>
          <label class="block text-blue-700 text-sm font-semibold mb-2">Product</label>
          <select v-model="simulation.product_name" class="glass-input w-full" @change="updateCategory">
            <option value="">Select a product...</option>
            <option v-for="product in products" :key="product.id" :value="product.name">
              {{ product.name }}
            </option>
          </select>
        </div>

        <!-- Price Input -->
        <div class="md:col-span-2">
          <label class="block text-blue-700 text-sm font-semibold mb-2">
            Price (AED): <span class="text-blue-900 text-lg font-bold">{{ simulation.price.toFixed(2) }}</span>
            <span v-if="selectedProduct" class="text-xs text-blue-500 ml-2">
              (Current: {{ selectedProduct.current_price.toFixed(2) }})
            </span>
          </label>
          <div class="flex items-center space-x-4">
            <input 
              v-model.number="simulation.price" 
              type="range" 
              :min="priceRange.min"
              :max="priceRange.max"
              step="0.5"
              @input="onPriceChange"
              class="flex-1 h-3 bg-blue-200 rounded-lg appearance-none cursor-pointer slider"
            />
            <input 
              v-model.number="simulation.price" 
              type="number" 
              step="0.5"
              :min="priceRange.min"
              :max="priceRange.max"
              @input="onPriceChange"
              class="glass-input w-24 text-center"
            />
          </div>
          <div class="flex justify-between text-xs text-blue-500 mt-1">
            <span>Min: AED {{ priceRange.min }}</span>
            <span>Max: AED {{ priceRange.max }}</span>
          </div>
          <!-- Quick Price Presets -->
          <div v-if="selectedProduct" class="flex gap-2 mt-3 flex-wrap">
            <button 
              @click="setPrice(selectedProduct.current_price * 0.8)"
              class="text-xs px-3 py-1 bg-red-100 text-red-700 rounded-full hover:bg-red-200 transition-colors"
            >
              -20%
            </button>
            <button 
              @click="setPrice(selectedProduct.current_price * 0.9)"
              class="text-xs px-3 py-1 bg-orange-100 text-orange-700 rounded-full hover:bg-orange-200 transition-colors"
            >
              -10%
            </button>
            <button 
              @click="setPrice(selectedProduct.current_price)"
              class="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors font-semibold"
            >
              Current
            </button>
            <button 
              @click="setPrice(selectedProduct.current_price * 1.1)"
              class="text-xs px-3 py-1 bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors"
            >
              +10%
            </button>
            <button 
              @click="setPrice(selectedProduct.current_price * 1.2)"
              class="text-xs px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full hover:bg-emerald-200 transition-colors"
            >
              +20%
            </button>
          </div>
        </div>

        <!-- Emirate Selection -->
        <div>
          <label class="block text-blue-700 text-sm font-semibold mb-2">Emirate</label>
          <select v-model="simulation.emirate" class="glass-input w-full">
            <option value="Dubai">Dubai</option>
            <option value="Abu Dhabi">Abu Dhabi</option>
            <option value="Sharjah">Sharjah</option>
            <option value="Ajman">Ajman</option>
            <option value="Ras Al Khaimah">Ras Al Khaimah</option>
            <option value="Fujairah">Fujairah</option>
            <option value="Umm Al Quwain">Umm Al Quwain</option>
          </select>
        </div>

        <!-- Store Type Selection -->
        <div>
          <label class="block text-blue-700 text-sm font-semibold mb-2">Store Type</label>
          <select v-model="simulation.store_type" class="glass-input w-full">
            <option value="Hypermarket">Hypermarket</option>
            <option value="Supermarket">Supermarket</option>
            <option value="Mini Market">Mini Market</option>
            <option value="Convenience Store">Convenience Store</option>
            <option value="Traditional">Traditional</option>
            <option value="Online">Online</option>
          </select>
        </div>

        <!-- Date Selection -->
        <div>
          <label class="block text-blue-700 text-sm font-semibold mb-2">Date</label>
          <input 
            v-model="simulation.date" 
            type="date" 
            class="glass-input w-full"
          />
        </div>

        <!-- Holiday Toggle -->
        <div>
          <label class="block text-blue-700 text-sm font-semibold mb-2">Special Day</label>
          <select v-model.number="simulation.is_holiday" class="glass-input w-full">
            <option :value="0">Regular Day</option>
            <option :value="1">Holiday/Special Event</option>
          </select>
        </div>

        <!-- Auto-Simulate Toggle -->
        <div class="md:col-span-2 flex items-center space-x-4 p-4 bg-blue-50 rounded-lg">
          <label class="flex items-center cursor-pointer flex-1">
            <input 
              v-model="autoSimulate" 
              type="checkbox" 
              class="mr-3 w-5 h-5 text-blue-600 rounded"
            />
            <div>
              <span class="text-blue-900 font-semibold">Auto-Simulate</span>
              <p class="text-xs text-blue-600">Automatically update predictions when price changes</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Simulate Button -->
      <button 
        @click="runSimulation"
        :disabled="!canSimulate || simulating"
        class="w-full glass-button py-3 text-lg mt-6"
      >
        {{ simulating ? 'Running AI Simulation...' : 'Run Simulation' }}
      </button>
    </div>

    <!-- Results -->
    <div v-if="result" class="space-y-6">
      <!-- Real-time Price Impact Preview -->
      <div v-if="autoSimulate" class="glass-card p-4 bg-gradient-to-r from-cyan-50 to-blue-50">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="text-2xl">⚡</div>
            <div>
              <div class="text-blue-700 text-sm font-semibold">Live Pricing Mode</div>
              <div class="text-blue-600 text-xs">Predictions update automatically as you adjust the price</div>
            </div>
          </div>
          <div v-if="simulating" class="flex items-center space-x-2 text-blue-600">
            <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span class="text-sm">Updating...</span>
          </div>
        </div>
      </div>

      <!-- Main Results Card -->
      <div class="glass-card p-6 bg-gradient-to-r from-blue-100 to-cyan-100 border-blue-300">
        <h3 class="text-2xl font-bold text-blue-900 mb-4">Simulation Results</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="glass-card p-4 bg-white">
            <div class="text-blue-600 text-sm mb-1">Predicted Demand</div>
            <div class="text-3xl font-bold gradient-text">
              {{ formatNumber(result.predicted_demand) }}
            </div>
            <div class="text-blue-500 text-xs">units/month</div>
            <div v-if="selectedProduct && baselineDemand" class="mt-2">
              <span 
                :class="getDemandChangeClass(result.predicted_demand, baselineDemand)"
                class="text-xs font-semibold"
              >
                {{ getDemandChangeText(result.predicted_demand, baselineDemand) }}
              </span>
            </div>
          </div>
          
          <div class="glass-card p-4 bg-white">
            <div class="text-blue-600 text-sm mb-1">Predicted Revenue</div>
            <div class="text-3xl font-bold gradient-text">
              AED {{ formatNumber(result.predicted_revenue) }}
            </div>
            <div class="text-green-600 text-xs">monthly</div>
          </div>

          <div class="glass-card p-4 bg-white">
            <div class="text-blue-600 text-sm mb-1">Estimated Profit</div>
            <div class="text-3xl font-bold gradient-text">
              AED {{ formatNumber(estimatedProfit) }}
            </div>
            <div class="text-purple-600 text-xs">@ {{ profitMargin }}% margin</div>
            <div v-if="baselineProfit" class="mt-2">
              <span 
                :class="estimatedProfit >= baselineProfit ? 'text-green-600' : 'text-red-600'"
                class="text-xs font-semibold"
              >
                {{ estimatedProfit >= baselineProfit ? '↑' : '↓' }}
                {{ ((estimatedProfit - baselineProfit) / baselineProfit * 100).toFixed(1) }}%
              </span>
            </div>
          </div>
          
          <div class="glass-card p-4 bg-white">
            <div class="text-blue-600 text-sm mb-1">Price Elasticity</div>
            <div class="text-3xl font-bold gradient-text">
              {{ result.elasticity_coefficient.toFixed(3) }}
            </div>
            <div class="text-blue-500 text-xs">
              {{ Math.abs(result.elasticity_coefficient) > 1 ? 'Elastic' : 'Inelastic' }}
            </div>
          </div>
        </div>

        <!-- Elasticity Impact Explanation -->
        <div class="mt-4 p-4 bg-white rounded-lg border border-blue-200">
          <div class="text-sm text-blue-900">
            <span class="font-semibold">💡 Dynamic Elasticity Impact:</span>
            <span v-if="selectedProduct">
              A <span class="font-semibold">{{ getPriceChangePercentage() }}</span> price change
              results in a <span class="font-semibold">{{ getDemandImpact() }}</span> demand change
              due to <span class="font-semibold">adjusted elasticity of {{ result.elasticity_coefficient.toFixed(2) }}</span>.
              {{ getElasticityExplanation() }}
            </span>
          </div>
          <div v-if="result.scenario.base_elasticity && result.scenario.adjusted_elasticity" class="mt-2 text-xs text-blue-700">
            <span class="font-semibold">📊 Elasticity Adjustment:</span>
            Base: {{ result.scenario.base_elasticity }} → Adjusted: {{ result.scenario.adjusted_elasticity }}
            <span v-if="Math.abs(result.scenario.adjusted_elasticity) > Math.abs(result.scenario.base_elasticity)" class="text-red-600 font-semibold">
              (More punishing due to {{ result.scenario.price_change_percent > 0 ? 'price increase with weak demand' : 'market conditions' }})
            </span>
            <span v-else-if="Math.abs(result.scenario.adjusted_elasticity) < Math.abs(result.scenario.base_elasticity)" class="text-green-600 font-semibold">
              (More forgiving due to {{ result.scenario.price_change_percent > 0 ? 'strong demand growth' : 'supporting price cuts' }})
            </span>
          </div>
        </div>
      </div>

      <!-- Scenario Details -->
      <div class="glass-card p-6">
        <h3 class="text-xl font-bold text-blue-900 mb-4">Scenario Details</h3>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span class="text-blue-600">Product:</span>
            <span class="text-blue-900 font-semibold ml-2">{{ result.product_name }}</span>
          </div>
          <div>
            <span class="text-blue-600">Price:</span>
            <span class="text-blue-900 font-semibold ml-2">AED {{ result.scenario.price.toFixed(2) }}</span>
            <span v-if="selectedProduct" class="ml-2">
              <span v-if="result.scenario.price > selectedProduct.current_price" class="text-green-600 text-xs">
                ↑ {{ ((result.scenario.price / selectedProduct.current_price - 1) * 100).toFixed(1) }}%
              </span>
              <span v-else-if="result.scenario.price < selectedProduct.current_price" class="text-red-600 text-xs">
                ↓ {{ ((1 - result.scenario.price / selectedProduct.current_price) * 100).toFixed(1) }}%
              </span>
              <span v-else class="text-blue-600 text-xs">
                = Current
              </span>
            </span>
          </div>
          <div>
            <span class="text-blue-600">Location:</span>
            <span class="text-blue-900 font-semibold ml-2">{{ result.scenario.emirate }}</span>
          </div>
          <div>
            <span class="text-blue-600">Store Type:</span>
            <span class="text-blue-900 font-semibold ml-2">{{ result.scenario.store_type }}</span>
          </div>
          <div>
            <span class="text-blue-600">Day Type:</span>
            <span class="text-blue-900 font-semibold ml-2">
              {{ result.scenario.is_weekend ? 'Weekend' : 'Weekday' }}
              {{ result.scenario.is_holiday ? '(Holiday)' : '' }}
            </span>
          </div>
          <div>
            <span class="text-blue-600">Month:</span>
            <span class="text-blue-900 font-semibold ml-2">
              {{ getMonthName(result.scenario.month) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Comparison with Different Prices -->
      <div class="glass-card p-6">
        <h3 class="text-xl font-bold text-blue-900 mb-4">Compare with Different Prices</h3>
        <p class="text-sm text-blue-600 mb-4">
          See how elasticity punishes price increases by reducing demand, and how this affects profit margins
        </p>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
          <button 
            @click="comparePrice(-20)"
            class="glass-button-secondary py-3"
          >
            <div class="text-xs text-blue-600">-20%</div>
            <div class="font-semibold">AED {{ (simulation.price * 0.8).toFixed(2) }}</div>
          </button>
          <button 
            @click="comparePrice(-10)"
            class="glass-button-secondary py-3"
          >
            <div class="text-xs text-blue-600">-10%</div>
            <div class="font-semibold">AED {{ (simulation.price * 0.9).toFixed(2) }}</div>
          </button>
          <button 
            @click="comparePrice(0)"
            class="glass-button py-3"
          >
            <div class="text-xs text-white">Current</div>
            <div class="font-semibold">AED {{ simulation.price.toFixed(2) }}</div>
          </button>
          <button 
            @click="comparePrice(10)"
            class="glass-button-secondary py-3"
          >
            <div class="text-xs text-blue-600">+10%</div>
            <div class="font-semibold">AED {{ (simulation.price * 1.1).toFixed(2) }}</div>
          </button>
          <button 
            @click="comparePrice(20)"
            class="glass-button-secondary py-3"
          >
            <div class="text-xs text-blue-600">+20%</div>
            <div class="font-semibold">AED {{ (simulation.price * 1.2).toFixed(2) }}</div>
          </button>
        </div>
      </div>

      <!-- Comparison Results -->
      <div v-if="comparisons.length > 0" class="glass-card p-6">
        <h3 class="text-xl font-bold text-blue-900 mb-4">Price Comparison Results</h3>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-blue-200">
                <th class="text-left text-blue-700 font-semibold py-3 px-4">Price</th>
                <th class="text-right text-blue-700 font-semibold py-3 px-4">Demand</th>
                <th class="text-right text-blue-700 font-semibold py-3 px-4">Revenue</th>
                <th class="text-right text-blue-700 font-semibold py-3 px-4">Profit</th>
                <th class="text-right text-blue-700 font-semibold py-3 px-4">Margin</th>
                <th class="text-right text-blue-700 font-semibold py-3 px-4">vs Current</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(comp, index) in comparisons" 
                :key="index"
                class="border-b border-blue-100"
                :class="{'bg-blue-50': comp.isCurrent, 'bg-green-50': comp.profit === Math.max(...comparisons.map(c => c.profit))}"
              >
                <td class="py-3 px-4">
                  <span class="font-semibold text-blue-900">AED {{ comp.price.toFixed(2) }}</span>
                  <span v-if="comp.isCurrent" class="ml-2 text-xs text-blue-600">(Current)</span>
                  <span v-if="comp.profit === Math.max(...comparisons.map(c => c.profit))" class="ml-2 text-xs text-green-600">⭐ Best</span>
                </td>
                <td class="py-3 px-4 text-right">
                  {{ formatNumber(comp.demand) }} units
                  <div class="text-xs" :class="comp.demandDiff >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ comp.demandDiff >= 0 ? '+' : '' }}{{ comp.demandDiff.toFixed(1) }}%
                  </div>
                </td>
                <td class="py-3 px-4 text-right">
                  AED {{ formatNumber(comp.revenue) }}
                  <div class="text-xs" :class="comp.revenueDiff >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ comp.revenueDiff >= 0 ? '+' : '' }}{{ comp.revenueDiff.toFixed(1) }}%
                  </div>
                </td>
                <td class="py-3 px-4 text-right">
                  <span class="font-semibold text-purple-900">AED {{ formatNumber(comp.profit) }}</span>
                  <div class="text-xs" :class="comp.profitDiff >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ comp.profitDiff >= 0 ? '+' : '' }}{{ comp.profitDiff.toFixed(1) }}%
                  </div>
                </td>
                <td class="py-3 px-4 text-right">
                  <span class="text-blue-700">{{ comp.margin.toFixed(1) }}%</span>
                </td>
                <td class="py-3 px-4 text-right">
                  <span 
                    :class="comp.profitDiff >= 0 ? 'text-green-600' : 'text-red-600'"
                    class="font-semibold text-lg"
                  >
                    {{ comp.profitDiff >= 0 ? '+' : '' }}{{ comp.profitDiff.toFixed(1) }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
          <div class="text-sm text-blue-900">
            <span class="font-semibold">📊 Analysis:</span>
            The table shows how elasticity punishes price increases. 
            Higher prices reduce demand (elasticity: {{ result.elasticity_coefficient.toFixed(2) }}), 
            but increase margin per unit. The optimal price balances volume and margin for maximum profit.
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!result && !simulating" class="glass-card p-12 text-center">
      <div class="text-blue-400 text-6xl mb-4">🎯</div>
      <div class="text-blue-600 text-lg">
        Configure your simulation parameters above and click "Run Simulation" to see AI predictions
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const { fetchProducts, simulatePrice } = useApi()

const products = ref([])
const simulation = ref({
  product_name: '',
  category: '',
  price: 15.0,
  emirate: 'Dubai',
  store_type: 'Hypermarket',
  date: new Date().toISOString().split('T')[0],
  is_holiday: 0
})

const result = ref(null)
const simulating = ref(false)
const comparisons = ref([])
const autoSimulate = ref(false)
const baselineDemand = ref(null)
const baselineProfit = ref(null)
let priceChangeTimeout = null

// Realistic profit margin based on product category (industry standard margins)
const profitMargin = computed(() => {
  if (!simulation.value.category) return 30
  
  const categoryMargins = {
    'Breakfast Cereals': 35,
    'BREAKFAST CEREAL': 35,
    'Hot Beverages': 40,
    'TOTAL COFFEE': 40,
    'ICE COFFEE': 38,
    'Culinary': 32,
    'Pet Care': 28,
    'PET CARE': 28,
    'MUESLI / CEREAL & NUTRITIONAL BAR': 33
  }
  
  return categoryMargins[simulation.value.category] || 30
})

// Calculate estimated profit based on realistic margin
const estimatedProfit = computed(() => {
  if (!result.value) return 0
  const revenue = result.value.predicted_revenue
  return revenue * (profitMargin.value / 100)
})

// Calculate estimated cost per unit
const estimatedCost = computed(() => {
  if (!simulation.value.price) return 0
  return simulation.value.price * (1 - profitMargin.value / 100)
})

const selectedProduct = computed(() => {
  return products.value.find(p => p.name === simulation.value.product_name)
})

const priceRange = computed(() => {
  if (!selectedProduct.value) {
    return { min: 1, max: 100 }
  }
  const basePrice = selectedProduct.value.current_price
  return {
    min: Math.max(1, Math.round(basePrice * 0.5 * 2) / 2), // 50% lower, rounded to 0.5
    max: Math.round(basePrice * 2 * 2) / 2 // 100% higher, rounded to 0.5
  }
})

const canSimulate = computed(() => {
  return simulation.value.product_name && 
         simulation.value.price > 0 &&
         simulation.value.emirate &&
         simulation.value.store_type &&
         simulation.value.date
})

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US').format(Math.round(num))
}

const getMonthName = (month) => {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return months[month - 1] || ''
}

const getDateComponents = (dateString) => {
  const date = new Date(dateString)
  return {
    month: date.getMonth() + 1,
    day_of_week: (date.getDay() + 6) % 7, // Convert Sunday=0 to Monday=0
    day_of_month: date.getDate(),
    is_weekend: [5, 6].includes(date.getDay()) ? 1 : 0
  }
}

const updateCategory = () => {
  const product = products.value.find(p => p.name === simulation.value.product_name)
  if (product) {
    simulation.value.category = product.category
    simulation.value.price = product.current_price
    // Reset results when changing product
    result.value = null
    comparisons.value = []
    baselineDemand.value = null
    baselineProfit.value = null
  }
}

const getDemandChangeClass = (current, baseline) => {
  if (current > baseline) return 'text-green-600'
  if (current < baseline) return 'text-red-600'
  return 'text-blue-600'
}

const getDemandChangeText = (current, baseline) => {
  const change = ((current - baseline) / baseline * 100)
  if (Math.abs(change) < 0.1) return '≈ Same'
  return `${change >= 0 ? '↑' : '↓'} ${Math.abs(change).toFixed(1)}%`
}

const getPriceChangePercentage = () => {
  if (!selectedProduct.value) return '0%'
  const change = ((simulation.value.price - selectedProduct.value.current_price) / selectedProduct.value.current_price * 100)
  if (Math.abs(change) < 0.1) return 'no'
  return `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`
}

const getDemandImpact = () => {
  if (!selectedProduct.value || !result.value || !baselineDemand.value) return '0%'
  const change = ((result.value.predicted_demand - baselineDemand.value) / baselineDemand.value * 100)
  return `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`
}

const getElasticityExplanation = () => {
  if (!result.value) return ''
  const elasticity = Math.abs(result.value.elasticity_coefficient)
  
  if (elasticity > 1.5) {
    return 'Highly elastic - demand is very sensitive to price changes. Price increases significantly reduce demand.'
  } else if (elasticity > 1) {
    return 'Elastic - demand responds noticeably to price changes. Consider pricing carefully.'
  } else if (elasticity > 0.5) {
    return 'Moderately inelastic - demand is somewhat resistant to price changes. Small price increases are feasible.'
  } else {
    return 'Highly inelastic - demand is very resistant to price changes. Price increases have minimal impact on volume.'
  }
}

const onPriceChange = () => {
  // Debounce the simulation when price changes
  if (!autoSimulate.value || !canSimulate.value) return
  
  if (priceChangeTimeout) {
    clearTimeout(priceChangeTimeout)
  }
  
  priceChangeTimeout = setTimeout(() => {
    runSimulation()
  }, 500) // Wait 500ms after user stops changing price
}

const setPrice = (price) => {
  simulation.value.price = Math.round(price * 2) / 2 // Round to nearest 0.5
  if (autoSimulate.value) {
    onPriceChange()
  }
}

const loadProducts = async () => {
  try {
    products.value = await fetchProducts()
  } catch (error) {
    console.error('Error loading products:', error)
  }
}

const runSimulation = async () => {
  if (!canSimulate.value) return
  
  simulating.value = true
  comparisons.value = []
  
  try {
    const dateComponents = getDateComponents(simulation.value.date)
    
    const requestData = {
      product_name: simulation.value.product_name,
      category: simulation.value.category,
      emirate: simulation.value.emirate,
      store_type: simulation.value.store_type,
      price: simulation.value.price,
      month: dateComponents.month,
      day_of_week: dateComponents.day_of_week,
      day_of_month: dateComponents.day_of_month,
      is_weekend: dateComponents.is_weekend,
      is_holiday: simulation.value.is_holiday
    }
    
    result.value = await simulatePrice(requestData)
    
    // Set baseline demand and profit if this is at the current product price
    if (selectedProduct.value && Math.abs(simulation.value.price - selectedProduct.value.current_price) < 0.1) {
      baselineDemand.value = result.value.predicted_demand
      baselineProfit.value = result.value.predicted_revenue * (profitMargin.value / 100)
    }
  } catch (error) {
    console.error('Error running simulation:', error)
    alert('Failed to run simulation. Please try again.')
  } finally {
    simulating.value = false
  }
}

const comparePrice = async (percentChange) => {
  if (!result.value) return
  
  const newPrice = simulation.value.price * (1 + percentChange / 100)
  const dateComponents = getDateComponents(simulation.value.date)
  
  try {
    const requestData = {
      product_name: simulation.value.product_name,
      category: simulation.value.category,
      emirate: simulation.value.emirate,
      store_type: simulation.value.store_type,
      price: newPrice,
      month: dateComponents.month,
      day_of_week: dateComponents.day_of_week,
      day_of_month: dateComponents.day_of_month,
      is_weekend: dateComponents.is_weekend,
      is_holiday: simulation.value.is_holiday
    }
    
    const compResult = await simulatePrice(requestData)
    
    // Calculate differences vs current simulation
    const baseDemand = result.value.predicted_demand
    const baseRevenue = result.value.predicted_revenue
    const baseProfit = baseRevenue * (profitMargin.value / 100)
    
    const demandDiff = ((compResult.predicted_demand - baseDemand) / baseDemand) * 100
    const revenueDiff = ((compResult.predicted_revenue - baseRevenue) / baseRevenue) * 100
    
    // Calculate profit for this comparison
    const compProfit = compResult.predicted_revenue * (profitMargin.value / 100)
    const profitDiff = ((compProfit - baseProfit) / baseProfit) * 100
    
    // Calculate margin (profit/revenue ratio)
    const margin = (compProfit / compResult.predicted_revenue) * 100
    
    // Add to comparisons
    const comparison = {
      price: newPrice,
      demand: compResult.predicted_demand,
      revenue: compResult.predicted_revenue,
      profit: compProfit,
      margin: margin,
      demandDiff: demandDiff,
      revenueDiff: revenueDiff,
      profitDiff: profitDiff,
      isCurrent: percentChange === 0
    }
    
    // Keep comparisons sorted by price
    comparisons.value.push(comparison)
    comparisons.value.sort((a, b) => a.price - b.price)
    
  } catch (error) {
    console.error('Error comparing price:', error)
  }
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
/* Custom slider styling */
.slider::-webkit-slider-thumb {
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
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.6);
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
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.6);
}

.slider::-webkit-slider-track {
  background: linear-gradient(to right, #dbeafe 0%, #bfdbfe 100%);
  border-radius: 8px;
}

.slider::-moz-range-track {
  background: linear-gradient(to right, #dbeafe 0%, #bfdbfe 100%);
  border-radius: 8px;
}
</style>
