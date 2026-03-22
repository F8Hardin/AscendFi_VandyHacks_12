<template>
  <div v-if="lines.length" class="debt-behave debt-eng-card">
    <h4 class="debt-behave__title">Behavioral risk signals</h4>
    <p class="debt-behave__sub">Pattern-style flags from your spending mix and activity — not clinical diagnosis.</p>
    <ul>
      <li v-for="(line, i) in lines" :key="i">{{ line }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const lines = computed(() => engines?.riskEngine.value?.behavioralPatterns ?? [])
</script>

<style scoped>
.debt-behave {
  padding: 1rem 1.15rem 1.1rem;
}
.debt-behave__title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-behave__sub {
  margin: 0.3rem 0 0.65rem;
  font-size: 0.72rem;
  line-height: 1.45;
  color: var(--color-text-faint);
}
.debt-behave ul {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.debt-behave li + li {
  margin-top: 0.35rem;
}
</style>
