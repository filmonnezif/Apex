<template>
  <div class="min-h-screen">
    <nav class="glass-card mx-4 mt-4 mb-6 p-4">
      <div class="container mx-auto flex justify-between items-center">
        <div class="flex items-center space-x-3">
          <img src="/logo.png" alt="Apex AI Logo" class="w-12 h-12 object-contain" />
          <div>
            <h1 class="text-blue-800 text-xl font-bold">Apex AI</h1>
            <p class="text-blue-600 text-xs">Dynamic Price Optimization</p>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <NuxtLink to="/" class="text-blue-700 hover:text-blue-900 transition-colors font-medium">
            Dashboard
          </NuxtLink>
        </div>
      </div>
    </nav>
    <main class="container mx-auto px-4 pb-8">
      <slot />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
</style>
