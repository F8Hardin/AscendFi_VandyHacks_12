<template>
  <div v-if="recs.length" class="debt-rec">
    <h4 class="debt-rec__title">AI recommendation feed</h4>
    <ul>
      <li v-for="(r, i) in recs" :key="i">{{ r }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const recs = computed(() => engines?.debtRecommendations.value ?? [])
</script>

<style scoped>
.debt-rec {
  padding: 1rem 1.15rem;
  border-radius: 1.125rem;
  border: 1px solid color-mix(in srgb, var(--eng-blue) 22%, var(--color-border));
  background: linear-gradient(145deg, var(--eng-blue-dim), transparent 55%);
}
.debt-rec__title {
  margin: 0 0 0.65rem;
  font-size: 0.9rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-rec ul {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.debt-rec li + li {
  margin-top: 0.45rem;
}
</style>
