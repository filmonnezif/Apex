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
                @input="onPriceSliderChange" 
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

          <!-- Price Cards: AI Optimal + Test Price -->
          <div class="grid grid-cols-2 gap-3">
            <!-- AI Optimal Price Card -->
                        <!-- AI Optimal Price Card -->
            <div v-if="optimization" class="glass-card p-4 bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 relative">
              <!-- Recalculating Overlay -->
              <div v-if="recalculatingOptimal" class="absolute inset-0 bg-blue-50 bg-opacity-90 flex items-center justify-center rounded-lg z-10">
                <div class="flex items-center gap-2 text-blue-600">
                  <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    /* Lines 145-147 omitted */
                  </svg>
                  <span class="text-sm font-semibold">Recalculating...</span>
                </div>
              </div>
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-xl">⭐</span>
                  <h3 class="font-semibold text-blue-900 text-sm">AI Optimal Price</h3>
                </div>
                <!-- Demand-Adjusted Constraint Badge -->
                <div v-if="optimization.constraints && optimization.constraints.dynamic_scaling" 
                     class="text-[10px] font-semibold px-2 py-1 rounded bg-purple-100 text-purple-700 flex items-center gap-1">
                  <span>📊</span>
                  <span>Max: +{{ optimization.constraints.max_price_increase_pct.toFixed(3) }}%</span>
                </div>
              </div>
              <div class="flex items-baseline gap-2 mb-1">
                <div class="text-3xl font-bold text-blue-900">
                  AED {{ optimization.recommendation.recommended_price.toFixed(2) }}
                </div>
                <div :class="['text-sm font-medium', optimization.recommendation.price_change_percentage > 0 ? 'text-green-600' : 'text-red-600']">
                  {{ optimization.recommendation.price_change_percentage > 0 ? '+' : '' }}{{ optimization.recommendation.price_change_percentage.toFixed(1) }}%
                </div>
              </div>
            </div>

            <!-- Current Test Price -->
            <div class="glass-card p-4">
              <div class="text-blue-600 text-sm font-semibold mb-2">Testing Price</div>
              <div class="flex items-baseline gap-3 mb-2">
                <div class="text-3xl font-bold text-blue-900">AED {{ params.price.toFixed(2) }}</div>
                <div :class="['text-sm font-bold px-3 py-1 rounded', 
                  getPriceChangePct() > 0 ? 'text-green-600 bg-green-50' : 
                  getPriceChangePct() < 0 ? 'text-red-600 bg-red-50' : 
                  'text-blue-600 bg-blue-50']">
                  {{ getPriceChangePct() > 0 ? '+' : '' }}{{ getPriceChangePct().toFixed(1) }}%
                </div>
              </div>
              <div class="text-xs text-blue-500">
                vs Current: AED {{ product.current_price.toFixed(2) }}
              </div>
            </div>
          </div>
          <!-- Main Grid: Profit Animation + Metrics -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
            
            <!-- Profit Animation Card (Takes 2 columns on large screens) -->
            <div class="lg:col-span-2 glass-card p-6 relative overflow-hidden" style="min-height: 400px;">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-bold text-blue-900">Profit Simulator</h3>
                <div class="text-sm text-blue-600">
                  <span v-if="getProfitVsCurrent() > 0" class="text-green-600">↑ Increasing</span>
                  <span v-else-if="getProfitVsCurrent() < 0" class="text-red-600">↓ Decreasing</span>
                  <span v-else class="text-gray-600">= Stable</span>
                </div>
              </div>
              
              <!-- Money Stack Visualization -->
              <div class="relative h-80 flex items-end justify-center">
                <!-- Center Stack (Base) - Grows/Shrinks with profit -->
                <div class="absolute left-1/2 transform -translate-x-1/2 z-10">
                  <div class="flex flex-col items-center">
                    <!-- Stack of money bills that scales with profit -->
                    <div class="relative flex items-end justify-center" style="min-height: 240px; min-width: 240px;">
                      <div
                        class="money-stack-animated"
                        :style="{ 
                          transform: `scale(${stackScale})`,
                          transition: 'transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)'
                        }"
                      >
                        <img src="/money-stack.png" alt="Money Stack" class="w-48 h-auto block" style="display: block !important;" />
                      </div>
                    </div>
                    <!-- Profit amount below the stack -->
                    <div class="text-center mt-6">
                      <div class="text-3xl font-bold text-green-600">
                        AED {{ formatNumber(estimatedProfit) }}
                      </div>
                      <div class="text-xs text-gray-500 mt-1">Estimated Profit</div>
                    </div>
                  </div>
                </div>

                <!-- Falling Money Bills (Left Side) -->
                <div
                  v-for="bill in fallingBills.filter(b => b.side === 'left')"
                  :key="bill.id"
                  class="money-bill absolute"
                  :style="{
                    left: bill.x + '%',
                    top: bill.y + 'px',
                    transform: `rotate(${bill.rotation}deg)`,
                    opacity: bill.opacity,
                    transition: bill.transition
                  }"
                >
                  <img src="/left-stack.png" alt="Money" class="w-20 h-auto" />
                </div>

                <!-- Falling Money Bills (Right Side) -->
                <div
                  v-for="bill in fallingBills.filter(b => b.side === 'right')"
                  :key="bill.id"
                  class="money-bill absolute"
                  :style="{
                    left: bill.x + '%',
                    top: bill.y + 'px',
                    transform: `rotate(${bill.rotation}deg)`,
                    opacity: bill.opacity,
                    transition: bill.transition
                  }"
                >
                  <img src="/right-stack.png" alt="Money" class="w-20 h-auto" />
                </div>

                <!-- Rising Money Bills (for decreasing profit) -->
                <div
                  v-for="bill in risingBills"
                  :key="bill.id"
                  class="money-bill absolute"
                  :style="{
                    left: bill.x + '%',
                    bottom: bill.y + 'px',
                    transform: `rotate(${bill.rotation}deg)`,
                    opacity: bill.opacity,
                    transition: bill.transition
                  }"
                >
                  <img :src="bill.side === 'left' ? '/left-stack.png' : '/right-stack.png'" alt="Money" class="w-16 h-auto" />
                </div>
              </div>

              <!-- Profit Change Indicator -->
              <div class="mt-4 text-center">
                <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full"
                     :class="getProfitVsCurrent() > 0 ? 'bg-green-50 text-green-700' : getProfitVsCurrent() < 0 ? 'bg-red-50 text-red-700' : 'bg-gray-50 text-gray-700'">
                  <span class="text-lg font-semibold">
                    {{ getProfitVsCurrent() > 0 ? '+' : '' }}{{ getProfitVsCurrent().toFixed(1) }}%
                  </span>
                  <span class="text-sm">vs Current</span>
                </div>
              </div>
            </div>

            <!-- Metrics Column (Demand + Profit Stats) -->
            <div class="space-y-4">
              
              <!-- Demand Card -->
              <div class="glass-card p-5">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-sm font-semibold text-blue-900 uppercase tracking-wide">Demand</h4>
                  <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                  </svg>
                </div>
                <div class="space-y-3">
                  <div>
                    <div class="text-3xl font-bold text-blue-900">
                      {{ formatNumber(predictions.predicted_demand) }}
                    </div>
                    <div class="text-xs text-gray-500 mt-1">units/day</div>
                  </div>
                  <div class="flex items-center gap-2 text-sm">
                    <span :class="getDemandVsCurrent() >= 0 ? 'text-green-600' : 'text-red-600'" class="font-semibold">
                      {{ getDemandVsCurrent() >= 0 ? '+' : '' }}{{ getDemandVsCurrent().toFixed(1) }}%
                    </span>
                    <span class="text-gray-500">vs Current</span>
                  </div>
                  <div class="pt-2 border-t border-gray-200">
                    <div class="text-xs text-gray-500 mb-1">Demand Level</div>
                    <span class="inline-block px-2 py-1 rounded-full text-xs font-medium" :class="getDemandLevelClass(predictions.demand_level)">
                      {{ predictions.demand_level }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Profit Stats Card -->
              <div class="glass-card p-5">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-sm font-semibold text-blue-900 uppercase tracking-wide">Profit Stats</h4>
                  <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div class="space-y-3">
                  <div>
                    <div class="text-xs text-gray-500 mb-1">Current</div>
                    <div class="text-lg font-bold text-gray-700">
                      AED {{ formatNumber(currentProfit) }}
                    </div>
                  </div>
                  <div>
                    <div class="text-xs text-gray-500 mb-1">Optimal</div>
                    <div class="text-lg font-bold text-green-600">
                      AED {{ formatNumber(optimalProfit) }}
                    </div>
                  </div>
                  <div class="pt-2 border-t border-gray-200">
                    <div class="text-xs text-gray-500 mb-1">Change</div>
                    <div class="flex items-baseline gap-2">
                      <span :class="getProfitChangeAbs() >= 0 ? 'text-green-600' : 'text-red-600'" class="text-lg font-bold">
                        {{ getProfitChangeAbs() >= 0 ? '+' : '' }}{{ formatNumber(getProfitChangeAbs()) }}
                      </span>
                      <span class="text-xs text-gray-500">AED</span>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>

          

          <!-- Current vs Test Price Comparison -->
          <div class="glass-card p-4 bg-gradient-to-br from-slate-50 to-gray-50 border border-slate-200">
            <h4 class="font-semibold text-slate-900 mb-3 text-sm flex items-center gap-2">
              <span>📊</span>
              <span>Price Impact Analysis</span>
            </h4>
            <div class="grid grid-cols-3 gap-3 text-xs">
              <div>
                <div class="text-slate-600 mb-1">Current Price</div>
                <div class="font-bold text-slate-900">AED {{ product.current_price.toFixed(2) }}</div>
              </div>
              <div>
                <div class="text-slate-600 mb-1">Test Price</div>
                <div class="font-bold text-blue-900">AED {{ params.price.toFixed(2) }}</div>
              </div>
              <div>
                <div class="text-slate-600 mb-1">Price Change</div>
                <div :class="['font-bold', getPriceChangePct() >= 0 ? 'text-green-600' : 'text-red-600']">
                  {{ getPriceChangePct() >= 0 ? '+' : '' }}{{ getPriceChangePct().toFixed(1) }}%
                </div>
              </div>
            </div>
            <div class="mt-3 pt-3 border-t border-slate-200">
              <div class="grid grid-cols-3 gap-3">
                <div>
                  <div class="text-[10px] text-slate-500 mb-1">Demand Change</div>
                  <div :class="['font-semibold', getDemandVsCurrent() >= 0 ? 'text-green-600' : 'text-red-600']">
                    {{ getDemandVsCurrent() >= 0 ? '+' : '' }}{{ getDemandVsCurrent().toFixed(1) }}%
                  </div>
                  <div class="text-[9px] text-slate-400">
                    {{ formatNumber(currentDemand) }} → {{ formatNumber(predictions.predicted_demand) }}
                  </div>
                </div>
                <div>
                  <div class="text-[10px] text-slate-500 mb-1">Revenue Change</div>
                  <div :class="['font-semibold', getRevenueVsCurrent() >= 0 ? 'text-green-600' : 'text-red-600']">
                    {{ getRevenueVsCurrent() >= 0 ? '+' : '' }}{{ getRevenueVsCurrent().toFixed(1) }}%
                  </div>
                  <div class="text-[9px] text-slate-400">
                    {{ formatNumber(currentRevenue) }} → {{ formatNumber(predictions.predicted_revenue) }}
                  </div>
                </div>
                <div>
                  <div class="text-[10px] text-slate-500 mb-1">Profit Change</div>
                  <div :class="['font-semibold', getProfitVsCurrent() >= 0 ? 'text-green-600' : 'text-red-600']">
                    {{ getProfitVsCurrent() >= 0 ? '+' : '' }}{{ getProfitVsCurrent().toFixed(1) }}%
                  </div>
                  <div class="text-[9px] text-slate-400">
                    {{ formatNumber(currentProfit) }} → {{ formatNumber(estimatedProfit) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Smart Insights -->
          <div v-if="optimization" class="glass-card p-4 bg-amber-50 border border-amber-200">
            <h4 class="font-semibold text-amber-900 mb-2 text-sm flex items-center gap-2">
              <span>💡</span>
              <span>Smart Insights</span>
            </h4>
            <div class="space-y-1.5 text-xs text-amber-800">
              <div v-if="Math.abs(getProfitVsCurrent()) > 2" class="flex items-start gap-2">
                <span class="text-amber-600">•</span>
                <span>
                  <strong>Profit Impact:</strong> This price would 
                  {{ getProfitVsCurrent() >= 0 ? 'increase' : 'decrease' }} profit by 
                  <strong>{{ Math.abs(getProfitVsCurrent()).toFixed(1) }}%</strong> 
                  ({{ getProfitChangeAbs() >= 0 ? '+' : '' }}AED {{ formatNumber(Math.abs(getProfitChangeAbs())) }}) 
                  compared to current pricing.
                </span>
              </div>
              <div v-if="Math.abs(getDemandVsCurrent()) > 5" class="flex items-start gap-2">
                <span class="text-amber-600">•</span>
                <span>
                  <strong>Demand Shift:</strong> Expect demand to 
                  {{ getDemandVsCurrent() >= 0 ? 'increase' : 'decrease' }} by 
                  {{ formatNumber(Math.abs(getDemandChangeAbs())) }} units 
                  ({{ Math.abs(getDemandVsCurrent()).toFixed(1) }}%).
                </span>
              </div>
              <div v-if="Math.abs(getRevenueVsCurrent()) > 5" class="flex items-start gap-2">
                <span class="text-amber-600">•</span>
                <span>
                  <strong>Revenue Impact:</strong> Revenue would 
                  {{ getRevenueVsCurrent() >= 0 ? 'increase' : 'decrease' }} by 
                  AED {{ formatNumber(Math.abs(getRevenueChangeAbs())) }} 
                  ({{ Math.abs(getRevenueVsCurrent()).toFixed(1) }}%).
                </span>
              </div>
              <div v-if="optimization && params.price > optimization.recommendation.recommended_price * 1.05" class="flex items-start gap-2">
                <span class="text-red-600">⚠</span>
                <span class="text-red-700">
                  <strong>Above Optimal:</strong> Price is {{ ((params.price - optimization.recommendation.recommended_price) / optimization.recommendation.recommended_price * 100).toFixed(1) }}% 
                  above AI optimal. Higher prices typically reduce profit due to demand loss exceeding margin gains.
                </span>
              </div>
              <div v-if="Math.abs(params.price - product.current_price) > product.current_price * 0.15" class="flex items-start gap-2">
                <span class="text-amber-600">•</span>
                <span><strong>Large Price Change:</strong> Test price differs significantly from current; large price jumps may impact customer perception.</span>
              </div>
              <div v-if="Math.abs(predictions.elasticity_coefficient) > 1.5" class="flex items-start gap-2">
                <span class="text-amber-600">•</span>
                <span><strong>High Sensitivity:</strong> Highly elastic product. Demand is very sensitive to price changes.</span>
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
          <span>�</span>
          <span>Revenue Optimization Analysis</span>
        </h3>
        <p class="text-sm text-blue-600 mb-4">Compare revenue across different price points</p>
        <div class="relative">
          <canvas ref="revenueOptimizationChart" class="w-full" style="max-height: 400px;"></canvas>
        </div>
        <div class="flex items-center justify-center flex-wrap gap-4 mt-4 text-sm">
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded bg-blue-500"></div>
            <span class="text-gray-700">Demand</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-1 bg-orange-600"></div>
            <span class="text-gray-700">Profit Curve</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded bg-green-500"></div>
            <span class="text-gray-700">Optimal Price</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded bg-orange-500"></div>
            <span class="text-gray-700">Current Test Price</span>
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
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const route = useRoute()
const router = useRouter()
const { fetchProducts, optimizePrice, simulatePrice } = useApi()

const revenueOptimizationChart = ref(null)
let chartInstance = null

const product = ref(null)
const optimization = ref(null)
const predictions = ref(null)
const loading = ref(true)
const calculating = ref(false)
const recalculatingOptimal = ref(false)
const autoUpdate = ref(true)

const params = ref({
  price: 15.0,
  emirate: 'Dubai',
  store_type: 'Hypermarket',
  date: new Date().toISOString().split('T')[0],
  is_holiday: 0
})

let changeTimeout = null

// Money animation state
const fallingBills = ref([])
const risingBills = ref([])
let billIdCounter = 0
let animationInterval = null
let previousProfit = null

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
  if (!predictions.value || !productCost.value || !optimization.value) return 0
  
  // Basic profit calculation: (Price - Cost) × Demand
  const basicProfit = (params.value.price - productCost.value) * predictions.value.predicted_demand
  
  // Get optimal price and profit from backend
  const optimalPrice = optimization.value.recommendation.recommended_price
  const optimalProfit = optimization.value.optimal_metrics?.profit || 
                       (optimalPrice - productCost.value) * optimization.value.recommendation.expected_demand
  
  // If price is above optimal, apply diminishing returns penalty
  if (params.value.price > optimalPrice) {
    const priceDeviation = (params.value.price - optimalPrice) / optimalPrice
    
    // Apply exponential penalty for prices above optimal
    // The further above optimal, the steeper the profit decline
    const penaltyFactor = Math.exp(-priceDeviation * 5) // Aggressive penalty
    
    // Profit should never exceed optimal, and should decline rapidly above it
    const cappedProfit = Math.min(basicProfit, optimalProfit * penaltyFactor)
    
    return cappedProfit
  }
  
  // If price is below optimal, use basic calculation but cap at optimal
  return Math.min(basicProfit, optimalProfit * 1.05) // Allow 5% variance for calculation differences
})

const stackScale = computed(() => {
  const profit = estimatedProfit.value || 0
  const current = currentProfit.value || 0
  
  if (current === 0) return 1
  
  // Calculate profit change percentage
  const profitChangePercent = ((profit - current) / current) * 100
  
  // Base scale is 1.0 (100%)
  // Scale changes by 1% for every 5% profit change
  // Min scale: 0.5 (50%), Max scale: 2.0 (200%)
  const scaleChange = profitChangePercent / 5 * 0.01
  const scale = 1 + scaleChange
  
  return Math.max(0.5, Math.min(scale, 2.0))
})

const optimalProfit = computed(() => {
  if (!optimization.value || !productCost.value) return 0
  
  // Use optimal_metrics.profit from backend if available
  if (optimization.value.optimal_metrics && optimization.value.optimal_metrics.profit) {
    return optimization.value.optimal_metrics.profit
  }
  
  // Fallback: Calculate from optimal price and demand
  return (optimization.value.recommendation.recommended_price - productCost.value) * optimization.value.recommendation.expected_demand
})

const priceRange = computed(() => {
  if (!product.value) return { min: 1, max: 100 }
  const basePrice = product.value.current_price
  const min = Math.max(1, Math.round(basePrice * 0.5 * 2) / 2)
  const max = Math.round(basePrice * 2 * 2) / 2
  const range = max - min
  const step = Math.round((range * 0.001) * 1000) / 1000 // 0.1% of range for high precision
  return { min, max, step: Math.max(0.001, step) }
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

// Calculate changes vs CURRENT (not optimal)
const currentDemand = computed(() => {
  if (!optimization.value) return 0
  return optimization.value.current_metrics.demand
})

const currentRevenue = computed(() => {
  if (!optimization.value) return 0
  return optimization.value.current_metrics.revenue
})

const currentProfit = computed(() => {
  if (!optimization.value) return 0
  
  // Use current_metrics.profit from backend if available
  if (optimization.value.current_metrics && optimization.value.current_metrics.profit) {
    return optimization.value.current_metrics.profit
  }
  
  // Fallback calculation
  if (!product.value || !product.value.cost) return 0
  return (product.value.current_price - product.value.cost) * currentDemand.value
})

const getDemandVsCurrent = () => {
  if (!predictions.value || !currentDemand.value) return 0
  return ((predictions.value.predicted_demand - currentDemand.value) / currentDemand.value) * 100
}

const getRevenueVsCurrent = () => {
  if (!predictions.value || !currentRevenue.value) return 0
  return ((predictions.value.predicted_revenue - currentRevenue.value) / currentRevenue.value) * 100
}

const getProfitVsCurrent = () => {
  if (!estimatedProfit.value || !currentProfit.value) return 0
  return ((estimatedProfit.value - currentProfit.value) / currentProfit.value) * 100
}

// Absolute changes
const getDemandChangeAbs = () => {
  if (!predictions.value || !currentDemand.value) return 0
  return predictions.value.predicted_demand - currentDemand.value
}

const getRevenueChangeAbs = () => {
  if (!predictions.value || !currentRevenue.value) return 0
  return predictions.value.predicted_revenue - currentRevenue.value
}

const getProfitChangeAbs = () => {
  if (!estimatedProfit.value || !currentProfit.value) return 0
  return estimatedProfit.value - currentProfit.value
}

const getElasticityExplanation = () => {
  if (!predictions.value) return ''
  const elasticity = Math.abs(predictions.value.elasticity_coefficient)
  if (elasticity > 1.5) return 'Highly elastic - demand is very sensitive to price changes.'
  if (elasticity > 1) return 'Elastic - demand responds noticeably to price changes.'
  if (elasticity > 0.5) return 'Moderately inelastic - demand is somewhat resistant to price changes.'
  return 'Highly inelastic - demand is very resistant to price changes.'
}

const getDemandLevelClass = (level) => {
  const levelUpper = level?.toUpperCase() || ''
  if (levelUpper.includes('EXCEPTIONAL') || levelUpper.includes('VERY HIGH')) {
    return 'bg-green-100 text-green-700'
  } else if (levelUpper.includes('HIGH')) {
    return 'bg-emerald-100 text-emerald-700'
  } else if (levelUpper.includes('ABOVE')) {
    return 'bg-blue-100 text-blue-700'
  } else if (levelUpper.includes('AVERAGE') || levelUpper.includes('NORMAL')) {
    return 'bg-slate-100 text-slate-700'
  } else if (levelUpper.includes('BELOW')) {
    return 'bg-amber-100 text-amber-700'
  } else if (levelUpper.includes('LOW')) {
    return 'bg-orange-100 text-orange-700'
  } else if (levelUpper.includes('VERY LOW')) {
    return 'bg-red-100 text-red-700'
  }
  return 'bg-gray-100 text-gray-700'
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
  if (autoUpdate.value) onPriceSliderChange()
}

const onPriceSliderChange = () => {
  // When only price changes, don't recalculate optimal
  if (!autoUpdate.value || !product.value) return
  if (changeTimeout) clearTimeout(changeTimeout)
  changeTimeout = setTimeout(async () => {
    await calculatePredictions()
  }, 500)
}

const onParamsChange = (recalculateOptimal = true) => {
  if (!autoUpdate.value || !product.value) return
  if (changeTimeout) clearTimeout(changeTimeout)
  changeTimeout = setTimeout(async () => {
    // Always recalculate optimization when context parameters change
    // This ensures optimal price is calculated for the specific scenario
    recalculatingOptimal.value = true
    await runOptimization()
    recalculatingOptimal.value = false
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
    
    // Render initial chart after everything is loaded
    await nextTick()
    renderRevenueChart()
  } catch (error) {
    console.error('Error loading product:', error)
    router.push('/')
  } finally {
    loading.value = false
  }
}

const runOptimization = async () => {
  if (!product.value) return
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
    
    // Trigger money animation based on profit change
    // If this is the first prediction, store profit but don't animate
    if (previousProfit === null) {
      previousProfit = estimatedProfit.value
    } else {
      const profitDiff = estimatedProfit.value - previousProfit
      // Animate for any meaningful change; lower threshold so users see feedback
      const threshold = 10 // AED
      if (Math.abs(profitDiff) >= threshold) {
        triggerMoneyAnimation(profitDiff)
      }
      previousProfit = estimatedProfit.value
    }
  } catch (error) {
    console.error('Error calculating predictions:', error)
    alert('Failed to calculate predictions. Please try again.')
  } finally {
    calculating.value = false
  }
}

const triggerMoneyAnimation = (profitDiff) => {
  const isIncreasing = profitDiff > 0
  // More bills for better visual effect: 1 bill per ~200 AED, minimum 3, max 15
  const baseBillCount = Math.abs(Math.floor(profitDiff / 200))
  const billCount = Math.min(Math.max(3, baseBillCount), 15)
  
  for (let i = 0; i < billCount; i++) {
    setTimeout(() => {
      if (isIncreasing) {
        createFallingBill()
      } else {
        createRisingBill()
      }
    }, i * 100) // Faster stagger for more dynamic effect
  }
}

const createFallingBill = () => {
  const side = Math.random() > 0.5 ? 'left' : 'right'
  const bill = {
    id: `fall-${billIdCounter++}`,
    side: side,
    // Wider spread for more dramatic effect - bills fall from across the top
    x: side === 'left' ? 15 + Math.random() * 25 : 60 + Math.random() * 25,
    y: -100 - Math.random() * 40, // Vary starting height for staggered appearance
    rotation: (Math.random() - 0.5) * 80, // More dramatic rotation range
    opacity: 0.9 + Math.random() * 0.1,
    transition: 'none'
  }
  
  fallingBills.value.push(bill)
  
  // Animate falling with physics
  setTimeout(() => {
    const billIndex = fallingBills.value.findIndex(b => b.id === bill.id)
    if (billIndex !== -1) {
      // Calculate landing position (center stack area) with more variety
      const landingY = 180 + Math.random() * 70
      const landingX = 40 + (Math.random() - 0.5) * 20
      const bounceRotation = bill.rotation + (Math.random() - 0.5) * 40
      
      fallingBills.value[billIndex] = {
        ...bill,
        y: landingY,
        x: landingX,
        rotation: bounceRotation,
        transition: 'all 1.0s cubic-bezier(0.34, 1.56, 0.64, 1)' // Slightly faster bounce
      }
      
      // Bounce effect
      setTimeout(() => {
        const idx = fallingBills.value.findIndex(b => b.id === bill.id)
        if (idx !== -1) {
          fallingBills.value[idx].y = landingY - 20
          fallingBills.value[idx].transition = 'all 0.15s ease-out'
        }
      }, 1000)
      
      // Settle down
      setTimeout(() => {
        const idx = fallingBills.value.findIndex(b => b.id === bill.id)
        if (idx !== -1) {
          fallingBills.value[idx].y = landingY
          fallingBills.value[idx].transition = 'all 0.25s ease-in'
        }
      }, 1150)
      
      // Fade out and remove
      setTimeout(() => {
        const idx = fallingBills.value.findIndex(b => b.id === bill.id)
        if (idx !== -1) {
          fallingBills.value[idx].opacity = 0
          fallingBills.value[idx].transition = 'opacity 0.4s ease-out'
        }
      }, 1800)
      
      setTimeout(() => {
        fallingBills.value = fallingBills.value.filter(b => b.id !== bill.id)
      }, 2200)
    }
  }, 50)
}

const createRisingBill = () => {
  const side = Math.random() > 0.5 ? 'left' : 'right'
  const bill = {
    id: `rise-${billIdCounter++}`,
    side: side,
    // Start from wider area around the center stack
    x: 35 + Math.random() * 30,
    y: 80 + Math.random() * 40, // Vary starting position
    rotation: (Math.random() - 0.5) * 50,
    opacity: 0.8 + Math.random() * 0.2,
    transition: 'none'
  }
  
  risingBills.value.push(bill)
  
  // Animate rising (money flying away)
  setTimeout(() => {
    const billIndex = risingBills.value.findIndex(b => b.id === bill.id)
    if (billIndex !== -1) {
      // Bills fly up and outward with more dramatic spread
      const horizontalSpread = (Math.random() - 0.5) * 50
      risingBills.value[billIndex] = {
        ...bill,
        y: 450 + Math.random() * 50, // Fly higher
        x: bill.x + horizontalSpread,
        rotation: bill.rotation + (Math.random() - 0.5) * 240, // More spinning
        opacity: 0,
        transition: 'all 1.8s cubic-bezier(0.22, 1, 0.36, 1)' // Slightly longer animation
      }
      
      setTimeout(() => {
        risingBills.value = risingBills.value.filter(b => b.id !== bill.id)
      }, 1900)
    }
  }, 50)
}

const generateChartDataPoints = () => {
  if (!optimization.value || !product.value || !productCost.value) return []
  
  const optimalPrice = optimization.value.recommendation.recommended_price
  const optimalDemand = optimization.value.recommendation.expected_demand
  const optimalProfit = (optimalPrice - productCost.value) * optimalDemand
  const currentPrice = product.value.current_price
  const elasticity = Math.abs(predictions.value?.elasticity_coefficient || -1.2)
  
  // Generate price points around the optimal price (20 data points for smooth curve)
  const pricePoints = []
  const numPoints = 20
  
  // Price range: 50% below to 100% above optimal price
  const minPrice = optimalPrice * 0.5
  const maxPrice = optimalPrice * 2.0
  const priceStep = (maxPrice - minPrice) / (numPoints - 1)
  
  for (let i = 0; i < numPoints; i++) {
    const testPrice = minPrice + (priceStep * i)
    
    // Calculate demand using elasticity formula
    // Demand = OptimalDemand * (OptimalPrice / TestPrice) ^ Elasticity
    const priceRatio = optimalPrice / testPrice
    const demandMultiplier = Math.pow(priceRatio, elasticity)
    const estimatedDemand = optimalDemand * demandMultiplier
    
    // Calculate revenue and profit
    const revenue = testPrice * estimatedDemand
    let profit = (testPrice - productCost.value) * estimatedDemand
    
    // CRITICAL FIX: Ensure profit never exceeds optimal profit
    // Apply penalty for prices above optimal to create proper bell curve
    if (testPrice > optimalPrice) {
      const priceDeviation = (testPrice - optimalPrice) / optimalPrice
      // Exponential decay for prices above optimal
      const penaltyFactor = Math.exp(-priceDeviation * 3)
      profit = Math.min(profit, optimalProfit * penaltyFactor)
    } else {
      // For prices below optimal, cap at optimal profit
      profit = Math.min(profit, optimalProfit)
    }
    
    pricePoints.push({
      price: testPrice,
      demand: estimatedDemand,
      revenue: revenue,
      profit: profit
    })
  }
  
  return pricePoints
}

const renderRevenueChart = async () => {
  await nextTick()
  
  if (!revenueOptimizationChart.value || !optimization.value || !product.value) return
  
  // Destroy existing chart
  if (chartInstance) {
    chartInstance.destroy()
  }
  
  const ctx = revenueOptimizationChart.value.getContext('2d')
  
  // Generate data points on the frontend
  const chartData = generateChartDataPoints()
  
  if (chartData.length === 0) {
    console.warn('No chart data generated')
    return
  }
  
  const optimalPrice = optimization.value.recommendation.recommended_price
  const currentTestPrice = params.value.price
  
  // Prepare chart data
  const labels = chartData.map(d => `${d.price.toFixed(2)}`)
  const demands = chartData.map(d => d.demand)
  
  // Create background colors - green for optimal, orange for current test, blue for others
  const backgroundColors = chartData.map(d => {
    const priceDiff = Math.abs(d.price - optimalPrice)
    const testPriceDiff = Math.abs(d.price - currentTestPrice)
    
    // Tolerance: 3% of optimal price
    const tolerance = optimalPrice * 0.03
    
    if (priceDiff < tolerance) return 'rgba(34, 197, 94, 0.8)' // Green for optimal
    if (testPriceDiff < tolerance) return 'rgba(249, 115, 22, 0.8)' // Orange for current test
    return 'rgba(59, 130, 246, 0.6)' // Blue for others
  })
  
  const borderColors = chartData.map(d => {
    const priceDiff = Math.abs(d.price - optimalPrice)
    const testPriceDiff = Math.abs(d.price - currentTestPrice)
    
    const tolerance = optimalPrice * 0.03
    
    if (priceDiff < tolerance) return 'rgba(34, 197, 94, 1)' // Green for optimal
    if (testPriceDiff < tolerance) return 'rgba(249, 115, 22, 1)' // Orange for current test
    return 'rgba(59, 130, 246, 1)' // Blue for others
  })
  
  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Demand (Units)',
          data: demands,
          backgroundColor: backgroundColors,
          borderColor: borderColors,
          borderWidth: 2,
          borderRadius: 6,
          borderSkipped: false,
          yAxisID: 'y',
          order: 2
        },
        {
          label: 'Profit (AED)',
          data: chartData.map(d => d.profit),
          type: 'line',
          borderColor: 'rgba(234, 88, 12, 0.9)',
          backgroundColor: 'rgba(234, 88, 12, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: 'rgba(234, 88, 12, 1)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointHoverRadius: 6,
          yAxisID: 'y1',
          order: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2.5,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          titleFont: {
            size: 14,
            weight: 'bold'
          },
          bodyFont: {
            size: 13
          },
          callbacks: {
            title: function(context) {
              return `Price: AED ${chartData[context[0].dataIndex].price.toFixed(2)}`
            },
            label: function(context) {
              const dataPoint = chartData[context.dataIndex]
              const revenue = dataPoint.revenue || 0
              const demand = dataPoint.demand || 0
              const profit = dataPoint.profit || 0
              
              return [
                `Demand: ${formatNumber(demand)} units`,
                `Profit: AED ${formatNumber(profit)}`,
                `Revenue: AED ${formatNumber(revenue)}`
              ]
            }
          }
        }
      },
      scales: {
        y: {
          type: 'linear',
          position: 'left',
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)',
            drawBorder: false
          },
          ticks: {
            callback: function(value) {
              return formatNumber(value) + ' units'
            },
            font: {
              size: 11
            }
          },
          title: {
            display: true,
            text: 'Demand (Units)',
            font: {
              size: 13,
              weight: 'bold'
            },
            color: '#1e40af'
          }
        },
        y1: {
          type: 'linear',
          position: 'right',
          beginAtZero: true,
          grid: {
            drawOnChartArea: false,
            drawBorder: false
          },
          ticks: {
            callback: function(value) {
              return 'AED ' + formatNumber(value)
            },
            font: {
              size: 11
            }
          },
          title: {
            display: true,
            text: 'Profit (AED)',
            font: {
              size: 13,
              weight: 'bold'
            },
            color: '#ea580c'
          }
        },
        x: {
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            font: {
              size: 10
            },
            maxRotation: 45,
            minRotation: 45,
            callback: function(value, index) {
              return 'AED ' + this.getLabelForValue(value)
            }
          },
          title: {
            display: true,
            text: 'Price Point',
            font: {
              size: 13,
              weight: 'bold'
            },
            color: '#1e40af'
          }
        }
      }
    }
  })
}

// Watch for changes in optimization to update chart (not price slider)
watch(optimization, () => {
  if (optimization.value && predictions.value) {
    renderRevenueChart()
  }
}, { deep: true })

onMounted(() => {
  loadProduct()
  // Set initial profit reference after data loads
  setTimeout(() => {
    if (estimatedProfit.value) {
      previousProfit = estimatedProfit.value
    }
  }, 1000)
})

onUnmounted(() => {
  // Cleanup chart instance
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>

<style scoped>
/* Money Animation Styles */
.money-stack-animated {
  position: relative;
  display: inline-block;
  filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.15));
  will-change: transform;
}

.money-stack-animated img {
  display: block;
  width: 100%;
  height: auto;
}

.money-stack-base {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  animation: stackPop 0.3s ease-out;
}

@keyframes stackPop {
  0% {
    transform: translateX(-50%) scale(0.8);
    opacity: 0;
  }
  50% {
    transform: translateX(-50%) scale(1.1);
  }
  100% {
    transform: translateX(-50%) scale(1);
    opacity: 1;
  }
}

.money-bill {
  pointer-events: none;
  will-change: transform, opacity, top, bottom, left;
  z-index: 20; /* Ensure bills appear above other elements */
}

.money-bill img {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
  backface-visibility: hidden; /* Smoother animations */
  transform: translateZ(0); /* Hardware acceleration */
}

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
