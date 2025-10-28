export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${baseURL}/api/products`)
      if (!response.ok) throw new Error('Failed to fetch products')
      const products = await response.json()
      return products
    } catch (error) {
      console.error('Error fetching products:', error)
      throw error
    }
  }

  const fetchProduct = async (productId: string) => {
    try {
      const response = await fetch(`${baseURL}/api/products/${productId}`)
      if (!response.ok) throw new Error('Failed to fetch product')
      const product = await response.json()
      return product
    } catch (error) {
      console.error('Error fetching product:', error)
      throw error
    }
  }

  const getValidValues = async () => {
    try {
      const response = await fetch(`${baseURL}/api/valid-values`)
      if (!response.ok) throw new Error('Failed to fetch valid values')
      return await response.json()
    } catch (error) {
      console.error('Error fetching valid values:', error)
      throw error
    }
  }

  const optimizePrice = async (data: any) => {
    try {
      const response = await fetch(`${baseURL}/api/optimize-price`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Failed to optimize price')
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error optimizing price:', error)
      throw error
    }
  }

  const simulatePrice = async (data: any) => {
    try {
      const response = await fetch(`${baseURL}/api/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Failed to simulate price')
      const result = await response.json()
      return result
    } catch (error) {
      console.error('Error simulating price:', error)
      throw error
    }
  }

  const getAnalyticsSummary = async () => {
    try {
      const response = await fetch(`${baseURL}/api/analytics/summary`)
      if (!response.ok) throw new Error('Failed to fetch analytics')
      return await response.json()
    } catch (error) {
      console.error('Error fetching analytics:', error)
      throw error
    }
  }

  return {
    fetchProducts,
    fetchProduct,
    getValidValues,
    optimizePrice,
    simulatePrice,
    getAnalyticsSummary
  }
}
