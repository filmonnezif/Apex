<template>
  <div class="min-h-screen py-4 sm:py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="space-y-4 sm:space-y-6">
        <!-- Header -->
        <div class="glass-card p-4 sm:p-6 lg:p-8">
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-blue-900 mb-2">
            Price Optimization Dashboard
          </h1>
          <p class="text-sm sm:text-base text-blue-600">
            AI-powered dynamic pricing for Nestle products in UAE
          </p>
        </div>

        <!-- Products Grid -->
        <div class="glass-card p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-0 mb-4 sm:mb-6">
            <h2 class="text-xl sm:text-2xl font-bold text-blue-900">Product Portfolio</h2>
            <button @click="refreshData" class="glass-button-secondary w-full sm:w-auto">
              <span v-if="!loading">Refresh</span>
              <span v-else>Loading...</span>
            </button>
          </div>

          <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 justify-items-center">
            <div v-for="i in 6" :key="i" class="glass-card p-6 shimmer w-full max-w-sm">
              <div class="h-4 bg-blue-200 rounded mb-2"></div>
              <div class="h-6 bg-blue-200 rounded mb-4"></div>
              <div class="h-10 bg-blue-200 rounded"></div>
            </div>
          </div>

                    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 justify-items-center">
            <div 
              v-for="product in products" 
              :key="product.id"
              class="glass-card-hover p-4 sm:p-6 cursor-pointer w-full max-w-sm"
              @click="selectProduct(product)"
            >
              <!-- Product Image -->
              <div class="w-full h-40 sm:h-48 mb-3 sm:mb-4 rounded-lg overflow-hidden bg-gradient-to-br from-blue-50 to-cyan-50 flex items-center justify-center">
                <ProductImage 
                  :productId="product.id" 
                  :alt="product.name"
                  size="medium"
                  class="w-full h-full"
                />
              </div>
              
              <div class="flex items-start justify-between mb-3">
                <div class="flex-1 min-w-0">
                  <div class="text-blue-600 text-xs uppercase tracking-wide mb-1">
                    {{ product.category }}
                  </div>
                  <h3 class="text-blue-900 font-semibold text-base sm:text-lg truncate">{{ product.name }}</h3>
                </div>
                <div class="w-10 h-10 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-lg flex items-center justify-center flex-shrink-0 ml-2">
                  <span class="text-white text-xs">{{ product.id.slice(-2) }}</span>
                </div>
              </div>
              
              <div class="space-y-2 mb-4">
                <div class="flex justify-between text-sm">
                  <span class="text-blue-600">Current Price</span>
                  <span class="text-blue-900 font-semibold">AED {{ product.current_price.toFixed(2) }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-blue-600">Category</span>
                  <span class="text-blue-700 truncate ml-2">{{ product.category }}</span>
                </div>
              </div>

              <button class="w-full glass-button text-sm py-2">
                Optimize Price →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const { fetchProducts, getAnalyticsSummary } = useApi()

const products = ref([])
const analytics = ref(null)
const loading = ref(true)

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US').format(Math.round(num))
}

const loadData = async () => {
  loading.value = true
  try {
    const [productsData, analyticsData] = await Promise.all([
      fetchProducts(),
      getAnalyticsSummary()
    ])
    products.value = productsData
    analytics.value = analyticsData
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadData()
}

const selectProduct = (product) => {
  navigateTo(`/optimize/${product.id}`)
}

onMounted(() => {
  loadData()
})
</script>
