<template>
  <div class="line-wrap">
    <canvas ref="canvasEl" />
  </div>
</template>

<script setup lang="ts">
export interface LineDataset {
  label: string
  data: number[]
  color: string
  fill?: boolean
  dashed?: boolean
}

const props = defineProps<{
  labels: string[]
  datasets: LineDataset[]
  yPrefix?: string       // e.g. '$' — prepended to y-axis tick labels and tooltips
  showLegend?: boolean
  showZeroLine?: boolean // draw a reference line at y=0
}>()

const canvasEl = ref<HTMLCanvasElement>()
let chartInstance: any = null

onMounted(async () => {
  const { default: Chart } = await import('chart.js/auto')

  const prefix = props.yPrefix ?? ''

  chartInstance = new Chart(canvasEl.value!, {
    type: 'line',
    data: {
      labels: props.labels,
      datasets: props.datasets.map((ds) => ({
        label: ds.label,
        data: ds.data,
        borderColor: ds.color,
        backgroundColor: ds.fill !== false
          ? hexToRgba(ds.color, 0.08)
          : 'transparent',
        fill: ds.fill !== false,
        tension: 0.4,
        pointBackgroundColor: ds.color,
        pointRadius: 4,
        pointHoverRadius: 6,
        borderDash: ds.dashed ? [5, 4] : [],
      })),
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
          display: props.showLegend ?? props.datasets.length > 1,
          labels: { boxWidth: 12, boxHeight: 12, padding: 16, font: { size: 12 } },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const val = ctx.parsed.y
              const sign = val < 0 ? '-' : ''
              return ` ${ctx.dataset.label}: ${sign}${prefix}${Math.abs(val).toLocaleString()}`
            },
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
            callback: (v) => {
              const n = Number(v)
              return n < 0 ? `-${prefix}${Math.abs(n).toLocaleString()}` : `${prefix}${n.toLocaleString()}`
            },
          },
        },
      },
    },
    plugins: props.showZeroLine ? [zeroLinePlugin()] : [],
  })
})

onBeforeUnmount(() => chartInstance?.destroy())

// ── Helpers ─────────────────────────────────────────────────────────────

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}

function zeroLinePlugin() {
  return {
    id: 'zeroLine',
    afterDraw(chart: any) {
      const { ctx, scales } = chart
      if (!scales.y) return
      const y = scales.y.getPixelForValue(0)
      ctx.save()
      ctx.strokeStyle = 'rgba(255,255,255,0.15)'
      ctx.lineWidth = 1
      ctx.setLineDash([4, 4])
      ctx.beginPath()
      ctx.moveTo(scales.x.left, y)
      ctx.lineTo(scales.x.right, y)
      ctx.stroke()
      ctx.restore()
    },
  }
}
</script>

<style scoped>
.line-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
