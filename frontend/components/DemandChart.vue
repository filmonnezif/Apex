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
  
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: props.data.map(d => d.price.toFixed(2)),
      datasets: [
        {
          label: 'Demand',
          data: props.data.map(d => d.predicted_demand),
          borderColor: 'rgb(168, 85, 247)',
          backgroundColor: 'rgba(168, 85, 247, 0.1)',
          yAxisID: 'y',
          tension: 0.4,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: 'rgb(168, 85, 247)',
          pointBorderColor: 'white',
          pointBorderWidth: 2
        },
        {
          label: 'Revenue',
          data: props.data.map(d => d.revenue),
          borderColor: 'rgb(236, 72, 153)',
          backgroundColor: 'rgba(236, 72, 153, 0.1)',
          yAxisID: 'y1',
          tension: 0.4,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: 'rgb(236, 72, 153)',
          pointBorderColor: 'white',
          pointBorderWidth: 2
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
                if (context.datasetIndex === 0) {
                  label += Math.round(context.parsed.y) + ' units'
                } else {
                  label += 'AED ' + context.parsed.y.toFixed(2)
                }
              }
              return label
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
            text: 'Demand (units)',
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
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Revenue (AED)',
            color: 'rgb(236, 72, 153)',
            font: {
              size: 14,
              weight: 'bold'
            }
          },
          ticks: {
            color: 'rgb(236, 72, 153)'
          },
          grid: {
            drawOnChartArea: false,
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
