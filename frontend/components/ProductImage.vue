<template>
  <div class="product-image-container">
    <img 
      :src="imageSrc" 
      :alt="alt"
      @error="handleImageError"
      :class="['product-image', animationClass]"
      loading="lazy"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  productId: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: 'Product Image'
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  animated: {
    type: Boolean,
    default: true
  }
})

const imageError = ref(false)

const imageSrc = computed(() => {
  if (imageError.value) {
    return '/backup.png'
  }
  // Try images/products folder first, fallback to root public folder
  return `/${props.productId}.png`
})

const animationClass = computed(() => {
  if (!props.animated) return ''
  return `animate-${props.size}`
})

const handleImageError = () => {
  imageError.value = true
}
</script>

<style scoped>
.product-image-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Small size animations */
.animate-small {
  animation: float-small 3s ease-in-out infinite;
}

.animate-small:hover {
  transform: scale(1.1) translateY(-5px);
  filter: drop-shadow(0 10px 20px rgba(59, 130, 246, 0.3));
}

/* Medium size animations */
.animate-medium {
  animation: float-medium 4s ease-in-out infinite;
}

.animate-medium:hover {
  transform: scale(1.15) rotate(5deg);
  filter: drop-shadow(0 15px 30px rgba(59, 130, 246, 0.4));
}

/* Large size animations */
.animate-large {
  animation: float-large 5s ease-in-out infinite;
}

.animate-large:hover {
  transform: scale(1.08) translateY(-10px);
  filter: drop-shadow(0 20px 40px rgba(59, 130, 246, 0.5));
}

/* Floating animations */
@keyframes float-small {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes float-medium {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-12px) rotate(2deg);
  }
}

@keyframes float-large {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-15px);
  }
}

/* Pulse effect for loading states */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.product-image-container:empty::before {
  content: '';
  display: block;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    #e0e7ff 25%,
    #dbeafe 50%,
    #e0e7ff 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
</style>
