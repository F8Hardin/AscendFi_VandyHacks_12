<template>
  <Doughnut :data="chartData" :options="chartOptions" />
</template>

<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  labels: string[]
  amounts: number[]
  colors: string[]
  cutout?: string
}>()

// Resolve CSS variables to real color values at render time
function resolveColors(colors: string[]) {
  if (typeof window === 'undefined') return colors
  const style = getComputedStyle(document.documentElement)
  return colors.map(c =>
    c.startsWith('var(') ? style.getPropertyValue(c.slice(4, -1).trim()).trim() || c : c
  )
}

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [{
    data: props.amounts,
    backgroundColor: resolveColors(props.colors),
    borderColor: '#111827',
    borderWidth: 3,
    hoverOffset: 6,
  }],
}))

const chartOptions = computed(() => ({
  cutout: props.cutout ?? '68%',
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { padding: 14, boxWidth: 12, boxHeight: 12, font: { size: 12 } },
    },
    tooltip: {
      callbacks: {
        label: (ctx: any) => ` $${ctx.parsed.toLocaleString()}`,
      },
    },
  },
}))
</script>
