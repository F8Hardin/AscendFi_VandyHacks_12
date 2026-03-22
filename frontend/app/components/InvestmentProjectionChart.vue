<template>
  <div class="investment-chart">
    <canvas ref="chartRef" aria-label="Investment growth projection chart" role="img" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps<{
  years: number
  monthlyContribution: number
  annualReturn: number
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

// Generate projection data
function generateData(years: number, monthly: number, annualRate: number) {
  const labels: string[] = []
  const investedData: number[] = []
  const valueData: number[] = []
  const interestData: number[] = []

  const monthlyRate = annualRate / 100 / 12
  let totalInvested = 0
  let totalValue = 0

  for (let year = 0; year <= years; year++) {
    labels.push(`Year ${year}`)
    investedData.push(totalInvested)
    valueData.push(totalValue)
    interestData.push(totalValue - totalInvested)

    // Calculate next year
    for (let month = 0; month < 12; month++) {
      totalInvested += monthly
      totalValue = (totalValue + monthly) * (1 + monthlyRate)
    }
  }

  return { labels, investedData, valueData, interestData }
}

// Format currency
function formatCurrency(value: number): string {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(1)}M`
  }
  if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}K`
  }
  return `$${value.toFixed(0)}`
}

function createChart() {
  if (!chartRef.value) return

  const ctx = chartRef.value.getContext('2d')
  if (!ctx) return

  const { labels, investedData, valueData } = generateData(
    props.years,
    props.monthlyContribution,
    props.annualReturn
  )

  // Destroy existing chart
  if (chart) {
    chart.destroy()
  }

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Total Value',
          data: valueData,
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 6,
          borderWidth: 3,
        },
        {
          label: 'Total Invested',
          data: investedData,
          borderColor: '#3b82f6',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          fill: false,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 4,
          borderWidth: 2,
        },
      ],
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
            usePointStyle: true,
            pointStyle: 'line',
            padding: 15,
            font: {
              size: 12,
              weight: '500',
            },
          },
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          titleColor: '#f8fafc',
          bodyColor: '#f8fafc',
          padding: 12,
          cornerRadius: 8,
          displayColors: true,
          callbacks: {
            label: (context) => {
              const value = context.parsed.y
              const label = context.dataset.label
              return `${label}: ${formatCurrency(value)}`
            },
            afterBody: (context) => {
              const value = context[0]?.parsed?.y ?? 0
              const invested = context[1]?.parsed?.y ?? 0
              const interest = value - invested
              return `\nInterest Earned: ${formatCurrency(interest)}`
            },
          },
        },
      },
      scales: {
        x: {
          grid: {
            display: false,
          },
          ticks: {
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 10,
            font: {
              size: 11,
            },
            color: '#64748b',
          },
        },
        y: {
          grid: {
            color: 'rgba(226, 232, 240, 0.5)',
          },
          ticks: {
            callback: (value) => formatCurrency(Number(value)),
            font: {
              size: 11,
            },
            color: '#64748b',
          },
          border: {
            display: false,
          },
        },
      },
    },
  })
}

// Watch for prop changes
watch(
  () => [props.years, props.monthlyContribution, props.annualReturn],
  () => {
    createChart()
  },
  { deep: true }
)

// Create chart on mount
onMounted(() => {
  createChart()
})
</script>

<style scoped>
.investment-chart {
  width: 100%;
  height: 300px;
  position: relative;
}
</style>
