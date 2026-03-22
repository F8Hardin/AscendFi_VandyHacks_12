<template>
  <div v-if="strategies.length" class="debt-strat">
    <h4 class="debt-strat__title">Strategy comparison</h4>
    <p class="debt-strat__sub">Illustrative timelines from a simplified month-by-month model — your real payoff depends on APR changes, fees, and discipline.</p>
    <div class="debt-strat__grid">
      <div
        v-for="s in strategies"
        :key="s.id"
        class="debt-strat__card debt-eng-card"
        :class="{ 'debt-strat__card--hi': hi?.id === s.id }"
      >
        <p class="debt-strat__name">{{ s.label }}</p>
        <p class="debt-strat__blurb">{{ s.blurb }}</p>
        <dl class="debt-strat__dl">
          <div>
            <dt>Payoff (mo)</dt>
            <dd>{{ s.months }}</dd>
          </div>
          <div>
            <dt>Total interest</dt>
            <dd>${{ s.totalInterest.toLocaleString('en-US') }}</dd>
          </div>
          <div>
            <dt>Stress index</dt>
            <dd>{{ Math.round(s.monthlyStress) }}</dd>
          </div>
          <div v-if="s.motivation != null">
            <dt>Motivation</dt>
            <dd>{{ s.motivation }}</dd>
          </div>
          <div v-if="s.consistency != null">
            <dt>Consistency</dt>
            <dd>{{ s.consistency }}</dd>
          </div>
          <div v-if="s.creditImpact != null">
            <dt>Credit impact</dt>
            <dd>{{ s.creditImpact }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const strategies = computed(() => engines?.strategiesBase.value ?? [])
const hi = computed(() => engines?.highlightedStrategy.value)
</script>

<style scoped>
.debt-strat__title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-strat__sub {
  margin: 0.35rem 0 1rem;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-text-muted);
  max-width: 44rem;
}
.debt-strat__grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}
.debt-strat__card {
  padding: 0.9rem 1rem;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
.debt-strat__card--hi {
  border-color: color-mix(in srgb, var(--eng-blue) 45%, var(--color-border));
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--eng-blue) 18%, transparent);
}
.debt-strat__name {
  margin: 0;
  font-size: 0.82rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-strat__blurb {
  margin: 0.4rem 0 0.65rem;
  font-size: 0.68rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}
.debt-strat__dl {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}
.debt-strat__dl > div {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
  font-size: 0.72rem;
}
.debt-strat__dl dt {
  color: var(--color-text-faint);
  font-weight: 600;
}
.debt-strat__dl dd {
  margin: 0;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}
</style>
