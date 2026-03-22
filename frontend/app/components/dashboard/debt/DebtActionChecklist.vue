<template>
  <div v-if="items.length" class="debt-check debt-eng-card">
    <h4 class="debt-check__title">Action center</h4>
    <ul>
      <li v-for="(x, i) in items" :key="i">
        <span class="debt-check__cb" aria-hidden="true" />
        {{ x }}
      </li>
    </ul>
    <div v-if="refi.length" class="debt-check__refi">
      <h5 class="debt-check__refi-title">Refinance / consolidation signals</h5>
      <p v-for="(r, i) in refi" :key="i" class="debt-check__refi-line">
        <strong>{{ r.name }}</strong> — {{ r.hint }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const items = computed(() => engines?.debtChecklist.value ?? [])
const refi = computed(() => engines?.refinanceHints.value ?? [])
</script>

<style scoped>
.debt-check {
  padding: 1.1rem 1.15rem 1.15rem;
}
.debt-check__title {
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-check ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}
.debt-check li {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}
.debt-check__cb {
  width: 1rem;
  height: 1rem;
  border-radius: 0.25rem;
  border: 2px solid var(--eng-blue);
  flex-shrink: 0;
  margin-top: 0.12rem;
  opacity: 0.7;
}
.debt-check__refi {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}
.debt-check__refi-title {
  margin: 0 0 0.45rem;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--dash-accent-text);
}
.debt-check__refi-line {
  margin: 0.35rem 0 0;
  font-size: 0.78rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}
.debt-check__refi-line strong {
  color: var(--color-text);
}
</style>
