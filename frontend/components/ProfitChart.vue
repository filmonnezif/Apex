<template>
  <div class="w-full h-80">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
})

const chartCanvas = ref(null)
let chartInstance = null

const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  
  // Find the maximum revenue point
  const maxRevenuePoint = props.data.reduce((max, point) => 
    point.revenue > max.revenue ? point : max
  , props.data[0])
  
  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: props.data.map(d => d.price.toFixed(2)),
      datasets: [
        {
          label: 'Revenue',
          data: props.data.map(d => d.revenue),
          backgroundColor: props.data.map(d => 
            d.price === maxRevenuePoint.price 
              ? 'rgba(34, 197, 94, 0.8)' 
              : 'rgba(168, 85, 247, 0.6)'
          ),
          borderColor: props.data.map(d => 
            d.price === maxRevenuePoint.price 
              ? 'rgb(34, 197, 94)' 
              : 'rgb(168, 85, 247)'
          ),
          borderWidth: 2,
          borderRadius: 6,
          hoverBackgroundColor: props.data.map(d => 
            d.price === maxRevenuePoint.price 
              ? 'rgba(34, 197, 94, 1)' 
              : 'rgba(168, 85, 247, 0.8)'
          )
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: 'rgba(255, 255, 255, 0.8)',
            font: {
              size: 12,
              family: 'system-ui'
            },
            padding: 15,
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: 'white',
          bodyColor: 'rgba(255, 255, 255, 0.9)',
          borderColor: 'rgba(168, 85, 247, 0.5)',
          borderWidth: 1,
          padding: 12,
          displayColors: true,
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || ''
              if (label) {
                label += ': '
              }
              if (context.parsed.y !== null) {
                label += 'AED ' + context.parsed.y.toFixed(2)
              }
              return label
            },
            afterLabel: function(context) {
              const dataPoint = props.data[context.dataIndex]
              if (dataPoint.price === maxRevenuePoint.price) {
                return '⭐ Optimal Price'
              }
              return ''
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Price (AED)',
            color: 'rgba(255, 255, 255, 0.8)',
            font: {
              size: 14,
              weight: 'bold'
            }
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.6)',
            maxTicksLimit: 10
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.1)',
            drawBorder: false
          }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Revenue (AED)',
            color: 'rgb(168, 85, 247)',
            font: {
              size: 14,
              weight: 'bold'
            }
          },
          ticks: {
            color: 'rgb(168, 85, 247)'
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.1)',
            drawBorder: false
          }
        }
      }
    }
  })
}

onMounted(() => {
  createChart()
})

watch(() => props.data, () => {
  createChart()
}, { deep: true })
</script>
