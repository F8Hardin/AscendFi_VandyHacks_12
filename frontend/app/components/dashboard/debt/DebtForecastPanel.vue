<template>
  <div class="debt-forecast debt-eng-card">
    <div class="debt-forecast__head">
      <div>
        <h4 class="debt-forecast__title">Forecast lab</h4>
        <p class="debt-forecast__hint">
          Risk score is absolute (0–100). Checking and debt series are min–max indexed so direction is comparable on one chart — not dollar values.
        </p>
      </div>
      <div class="debt-forecast__tabs" role="tablist" aria-label="Forecast horizon">
        <button
          v-for="h in horizons"
          :key="h"
          type="button"
          role="tab"
          :aria-selected="fh === h"
          class="debt-forecast__tab"
          :class="{ 'debt-forecast__tab--on': fh === h }"
          @click="setH(h)"
        >
          {{ h === '30d' ? '30 days' : h === '3m' ? '3 months' : '6 months' }}
        </button>
      </div>
    </div>
    <ClientOnly>
      <div v-if="chart.datasets.length" class="dash-chart-block">
        <LineChart
          :labels="chart.labels"
          :datasets="chart.datasets"
          :show-legend="true"
          :show-zero-line="false"
        />
      </div>
      <template #fallback>
        <div class="dash-chart-fallback dash-chart-fallback--line" aria-hidden="true" />
      </template>
    </ClientOnly>
    <p v-if="engines?.forecastRaw" class="debt-forecast__shortfall">
      Modeled checking trajectory suggests watching the
      <strong>{{ fh === '30d' ? 'next two weeks' : 'next quarter' }}</strong>
      for margin compression if spending holds steady.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const horizons = ['30d', '3m', '6m'] as const

const fh = computed(() => engines?.forecastHorizon.value ?? '30d')
const chart = computed(() => engines?.forecastChart.value ?? { labels: [], datasets: [] })

function setH(h: (typeof horizons)[number]) {
  if (engines?.forecastHorizon) engines.forecastHorizon.value = h
}
</script>

<style scoped>
.debt-forecast {
  padding: 1.15rem 1.2rem 1.25rem;
}
.debt-forecast__head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
}
.debt-forecast__title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-forecast__hint {
  margin: 0.35rem 0 0;
  font-size: 0.72rem;
  line-height: 1.45;
  color: var(--color-text-faint);
  max-width: 38rem;
}
.debt-forecast__tabs {
  display: flex;
  gap: 0.35rem;
  flex-shrink: 0;
}
.debt-forecast__tab {
  padding: 0.4rem 0.75rem;
  border-radius: 9999px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-raised);
  font-size: 0.72rem;
  font-weight: 650;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}
.debt-forecast__tab--on {
  background: var(--eng-blue-dim);
  border-color: color-mix(in srgb, var(--eng-blue) 35%, var(--color-border));
  color: var(--eng-blue);
}
.debt-forecast__shortfall {
  margin: 0.75rem 0 0;
  font-size: 0.78rem;
  line-height: 1.5;
  color: var(--color-text-muted);
}
.debt-forecast__shortfall strong {
  color: var(--color-text);
}
</style>
