<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-8">
      <h1 class="text-4xl font-bold text-blue-900 mb-2">
        Product Portfolio
      </h1>
      <p class="text-blue-600">
        Manage and optimize pricing for all Nestle products
      </p>
    </div>

    <!-- Products Table -->
    <div class="glass-card p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-blue-900">All Products</h2>
        <div class="flex space-x-3">
          <select class="glass-input">
            <option value="all">All Categories</option>
            <option value="premium">Premium</option>
            <option value="standard">Standard</option>
            <option value="basic">Basic</option>
          </select>
          <button @click="refreshProducts" class="glass-button-secondary">
            Refresh
          </button>
        </div>
      </div>

      <div v-if="loading" class="space-y-3">
        <div v-for="i in 5" :key="i" class="glass-card p-4 shimmer h-20"></div>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-blue-200">
              <th class="text-left text-blue-700 font-semibold py-3 px-4">Product</th>
              <th class="text-left text-blue-700 font-semibold py-3 px-4">Category</th>
              <th class="text-right text-blue-700 font-semibold py-3 px-4">Current Price</th>
              <th class="text-center text-blue-700 font-semibold py-3 px-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="product in products" 
              :key="product.id"
              class="border-b border-blue-100 hover:bg-blue-50 transition-colors"
            >
              <td class="py-4 px-4">
                <div class="flex items-center space-x-3">
                  <div class="w-16 h-16 rounded-lg overflow-hidden bg-gradient-to-br from-blue-50 to-cyan-50 flex items-center justify-center flex-shrink-0">
                    <ProductImage 
                      :productId="product.id" 
                      :alt="product.name"
                      size="small"
                      class="w-full h-full p-2"
                    />
                  </div>
                  <div>
                    <div class="text-blue-900 font-medium">{{ product.name }}</div>
                    <div class="text-blue-500 text-sm">{{ product.id }}</div>
                  </div>
                </div>
              </td>
              <td class="py-4 px-4">
                <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm capitalize">
                  {{ product.category }}
                </span>
              </td>
              <td class="py-4 px-4 text-right">
                <span class="text-blue-900 font-semibold">AED {{ product.current_price.toFixed(2) }}</span>
              </td>
              <td class="py-4 px-4 text-center">
                <button 
                  @click="optimizeProduct(product)"
                  class="glass-button-secondary text-sm py-1 px-4"
                >
                  Optimize
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const { fetchProducts } = useApi()

const products = ref([])
const loading = ref(true)

const loadProducts = async () => {
  loading.value = true
  try {
    products.value = await fetchProducts()
  } catch (error) {
    console.error('Error loading products:', error)
  } finally {
    loading.value = false
  }
}

const refreshProducts = () => {
  loadProducts()
}

const optimizeProduct = (product) => {
  navigateTo(`/optimize/${product.id}`)
}

onMounted(() => {
  loadProducts()
})
</script>
