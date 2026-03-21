<template>
  <div class="donut-wrap">
    <canvas ref="canvasEl" />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  labels: string[]
  amounts: number[]
  colors: string[]
  cutout?: string
}>()

const canvasEl = ref<HTMLCanvasElement>()
let chartInstance: any = null

onMounted(async () => {
  const {
    Chart,
    DoughnutController,
    ArcElement,
    Tooltip,
    Legend,
  } = await import('chart.js')
  Chart.register(DoughnutController, ArcElement, Tooltip, Legend)

  // Resolve CSS variable colors
  const style = getComputedStyle(document.documentElement)
  const resolvedColors = props.colors.map(c =>
    c.startsWith('var(') ? style.getPropertyValue(c.slice(4, -1).trim()).trim() : c
  )

  chartInstance = new Chart(canvasEl.value!, {
    type: 'doughnut',
    data: {
      labels: props.labels,
      datasets: [{
        data: props.amounts,
        backgroundColor: resolvedColors,
        borderColor: '#111827',
        borderWidth: 3,
        hoverOffset: 6,
      }],
    },
    options: {
      cutout: props.cutout ?? '68%',
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 14,
            boxWidth: 12,
            boxHeight: 12,
            font: { size: 12 },
          },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` $${ctx.parsed.toLocaleString()}`,
          },
        },
      },
    },
  })
})

onBeforeUnmount(() => chartInstance?.destroy())
</script>

<style scoped>
.donut-wrap {
  position: relative;
  width: 100%;
  max-width: 320px;
  margin: 0 auto;
}
</style>
