<template>
  <div class="line-wrap">
    <canvas ref="canvasEl" />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  labels: string[]
  balances: number[]
}>()

const canvasEl = ref<HTMLCanvasElement>()
let chartInstance: any = null

onMounted(async () => {
  const { Chart } = await import('chart.js')

  chartInstance = new Chart(canvasEl.value!, {
    type: 'line',
    data: {
      labels: props.labels,
      datasets: [{
        label: 'Total Debt',
        data: props.balances,
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34,197,94,0.08)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#22c55e',
        pointRadius: 4,
        pointHoverRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` $${ctx.parsed.y.toLocaleString()}`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { font: { size: 11 } },
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            font: { size: 11 },
            callback: (v) => `$${Number(v).toLocaleString()}`,
          },
        },
      },
    },
  })
})

onBeforeUnmount(() => chartInstance?.destroy())
</script>

<style scoped>
.line-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
