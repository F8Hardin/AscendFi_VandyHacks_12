<template>
  <Line :data="chartData" :options="chartOptions" :plugins="extraPlugins" />
</template>

<script setup lang="ts">
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

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
  yPrefix?: string
  showLegend?: boolean
  showZeroLine?: boolean
}>()

function hexToRgba(hex: string, alpha: number) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}

const chartData = computed(() => ({
  labels: props.labels,
  datasets: props.datasets.map(ds => ({
    label: ds.label,
    data: ds.data,
    borderColor: ds.color,
    backgroundColor: ds.fill !== false ? hexToRgba(ds.color, 0.08) : 'transparent',
    fill: ds.fill !== false,
    tension: 0.4,
    pointBackgroundColor: ds.color,
    pointRadius: 4,
    pointHoverRadius: 6,
    borderDash: ds.dashed ? [5, 4] : [],
  })),
}))

const prefix = computed(() => props.yPrefix ?? '')

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index' as const, intersect: false },
  plugins: {
    legend: {
      display: props.showLegend ?? (props.datasets.length > 1),
      labels: { boxWidth: 12, boxHeight: 12, padding: 16, font: { size: 12 } },
    },
    tooltip: {
      callbacks: {
        label: (ctx: any) => {
          const val = ctx.parsed.y
          const sign = val < 0 ? '-' : ''
          return ` ${ctx.dataset.label}: ${sign}${prefix.value}${Math.abs(val).toLocaleString()}`
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
        callback: (v: any) => {
          const n = Number(v)
          return n < 0 ? `-${prefix.value}${Math.abs(n).toLocaleString()}` : `${prefix.value}${n.toLocaleString()}`
        },
      },
    },
  },
}))

const extraPlugins = computed(() => {
  if (!props.showZeroLine) return []
  return [{
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
  }]
})
</script>
