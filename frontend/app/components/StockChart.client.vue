<template>
  <div class="sc-wrap">
    <!-- Chart type + period toggles -->
    <div class="sc-toolbar">
      <div class="sc-type-btns" role="group" aria-label="Chart type">
        <button
          v-for="t in TYPES"
          :key="t.id"
          class="sc-btn"
          :class="{ 'sc-btn--active': chartType === t.id }"
          @click="setType(t.id)"
        >{{ t.label }}</button>
      </div>
      <div class="sc-period-btns" role="group" aria-label="Time period">
        <button
          v-for="p in PERIODS"
          :key="p"
          class="sc-btn"
          :class="{ 'sc-btn--active': activePeriod === p }"
          @click="$emit('period', p)"
        >{{ p }}</button>
      </div>
    </div>

    <!-- Chart canvas -->
    <div class="sc-canvas-wrap">
      <div v-if="isLoading" class="sc-loading">
        <div class="sc-skeleton" />
      </div>
      <div v-else-if="!candles.length" class="sc-empty">
        No price data available
      </div>
      <div v-else ref="chartEl" class="sc-canvas" />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  createChart,
  ColorType,
  CrosshairMode,
  AreaSeries,
  CandlestickSeries,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp,
} from 'lightweight-charts'

export interface OHLCBar {
  time:  string | number
  open:  number
  high:  number
  low:   number
  close: number
  value: number
}

const props = defineProps<{
  candles:      OHLCBar[]
  activePeriod: string
  isLoading:    boolean
  isUp:         boolean   // true when day change ≥ 0 (controls colour)
}>()

const emit = defineEmits<{ (e: 'period', p: string): void }>()

const TYPES   = [{ id: 'area', label: 'Line' }, { id: 'candle', label: 'Candle' }] as const
const PERIODS = ['1D', '1W', '1M', '3M', '6M', '1Y'] as const
type ChartTypeId = 'area' | 'candle'

const chartType = ref<ChartTypeId>('area')
const chartEl   = ref<HTMLElement | null>(null)

let chart:  IChartApi | null = null
let series: ISeriesApi<'Area' | 'Candlestick'> | null = null

// ── Colour tokens ────────────────────────────────────────────────────────────
const UP_COLOR   = '#22c55e'
const DOWN_COLOR = '#ef4444'
const GRID_COLOR = 'rgba(0,0,0,0.06)'
const TEXT_COLOR = '#86868b'
const BG_COLOR   = 'transparent'

function lineColor() { return props.isUp ? UP_COLOR : DOWN_COLOR }
function areaTop()   { return props.isUp ? 'rgba(34,197,94,0.18)'  : 'rgba(239,68,68,0.18)' }
function areaBot()   { return props.isUp ? 'rgba(34,197,94,0.01)'  : 'rgba(239,68,68,0.01)' }

// ── Chart lifecycle ──────────────────────────────────────────────────────────
function buildChart() {
  if (!chartEl.value) return

  chart?.remove()
  chart = null
  series = null

  chart = createChart(chartEl.value, {
    layout: {
      background:  { type: ColorType.Solid, color: BG_COLOR },
      textColor:   TEXT_COLOR,
      fontFamily:  '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
      fontSize:    11,
    },
    grid: {
      vertLines:   { color: GRID_COLOR },
      horzLines:   { color: GRID_COLOR },
    },
    crosshair: {
      mode: CrosshairMode.Normal,
    },
    rightPriceScale: {
      borderVisible: false,
      scaleMargins:  { top: 0.08, bottom: 0.08 },
    },
    timeScale: {
      borderVisible:      false,
      timeVisible:        props.activePeriod === '1D' || props.activePeriod === '1W',
      secondsVisible:     false,
      rightOffset:        5,
      barSpacing:         props.activePeriod === '1D' ? 3 : 6,
      fixLeftEdge:        true,
      fixRightEdge:       true,
    },
    handleScroll: true,
    handleScale:  true,
    width:  chartEl.value.clientWidth,
    height: chartEl.value.clientHeight,
  })

  attachSeries()
  setData()

  chart.timeScale().fitContent()
}

function attachSeries() {
  if (!chart) return
  if (chartType.value === 'candle') {
    series = chart.addSeries(CandlestickSeries, {
      upColor:         UP_COLOR,
      downColor:       DOWN_COLOR,
      borderUpColor:   UP_COLOR,
      borderDownColor: DOWN_COLOR,
      wickUpColor:     UP_COLOR,
      wickDownColor:   DOWN_COLOR,
    })
  } else {
    series = chart.addSeries(AreaSeries, {
      lineColor:   lineColor(),
      topColor:    areaTop(),
      bottomColor: areaBot(),
      lineWidth:   2,
      priceLineVisible: false,
      lastValueVisible: true,
    })
  }
}

function setData() {
  if (!series || !props.candles.length) return

  if (chartType.value === 'candle') {
    ;(series as ISeriesApi<'Candlestick'>).setData(
      props.candles.map(c => ({
        time:  c.time as any,
        open:  c.open,
        high:  c.high,
        low:   c.low,
        close: c.close,
      }))
    )
  } else {
    ;(series as ISeriesApi<'Area'>).setData(
      props.candles.map(c => ({ time: c.time as UTCTimestamp & string, value: c.close }))
    )
  }
}

function setType(t: ChartTypeId) {
  chartType.value = t
  buildChart()
}

// ── Responsive resize ────────────────────────────────────────────────────────
let ro: ResizeObserver | null = null

function startResize() {
  if (!chartEl.value || !chart) return
  ro = new ResizeObserver(entries => {
    const e = entries[0]
    if (e && chart) {
      chart.applyOptions({
        width:  e.contentRect.width,
        height: e.contentRect.height,
      })
      chart.timeScale().fitContent()
    }
  })
  ro.observe(chartEl.value)
}

// ── Watch props for rebuilds ─────────────────────────────────────────────────
// When chartEl becomes available (v-else div is mounted), build chart if data ready
watch(chartEl, (el) => {
  if (el && !props.isLoading && props.candles.length) {
    buildChart()
    startResize()
  }
})

// When candles / color / period change and chart div is already visible
watch(
  () => [props.candles, props.isUp, props.activePeriod] as const,
  () => {
    if (!props.isLoading && props.candles.length) {
      nextTick(() => {
        if (chartEl.value) { buildChart(); startResize() }
      })
    }
  },
  { deep: false }
)

// When loading finishes — DOM flips from skeleton → chart div in next tick
watch(() => props.isLoading, (loading) => {
  if (!loading && props.candles.length) {
    nextTick(() => {
      if (chartEl.value) { buildChart(); startResize() }
    })
  }
})

onMounted(() => {
  nextTick(() => {
    if (!props.isLoading && props.candles.length && chartEl.value) {
      buildChart()
      startResize()
    }
  })
})

onUnmounted(() => {
  ro?.disconnect()
  chart?.remove()
})
</script>

<style scoped>
.sc-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  height: 100%;
}

/* ── Toolbar ─── */
.sc-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.sc-type-btns,
.sc-period-btns {
  display: flex;
  gap: 0.2rem;
}

.sc-btn {
  padding: 0.3rem 0.65rem;
  font-size: 0.72rem;
  font-weight: 700;
  border: 1px solid var(--color-border);
  border-radius: 0.45rem;
  background: var(--color-surface);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: background 0.1s, color 0.1s, border-color 0.1s;
  line-height: 1;
}

.sc-btn--active {
  background: var(--color-primary);
  color: var(--color-on-primary);
  border-color: var(--color-primary);
}

.sc-btn:hover:not(.sc-btn--active) {
  background: var(--color-surface-raised);
  color: var(--color-text);
}

/* ── Canvas ─── */
.sc-canvas-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
  border-radius: 0.5rem;
  overflow: hidden;
}

.sc-canvas {
  width: 100%;
  height: 100%;
}

.sc-loading {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: stretch;
}

.sc-skeleton {
  flex: 1;
  border-radius: 0.5rem;
  background: var(--color-surface-raised);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

.sc-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8125rem;
  color: var(--color-text-faint);
}
</style>
