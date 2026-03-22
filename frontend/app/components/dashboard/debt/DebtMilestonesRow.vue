<template>
  <div v-if="milestones.length" class="debt-mile debt-eng-grid debt-eng-grid--3">
    <div v-for="(m, i) in milestones" :key="i" class="debt-mile__card debt-eng-card">
      <p class="debt-mile__title">{{ m.title }}</p>
      <p class="debt-mile__value">{{ m.value }}</p>
      <p class="debt-mile__sub">{{ m.sub }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const milestones = computed(() => engines?.behavioralMilestones.value ?? [])
</script>

<style scoped>
.debt-mile__card {
  padding: 0.9rem 1rem;
  text-align: center;
}
.debt-mile__title {
  margin: 0;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-faint);
}
.debt-mile__value {
  margin: 0.45rem 0 0;
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--eng-green);
  letter-spacing: -0.02em;
}
.debt-mile__sub {
  margin: 0.35rem 0 0;
  font-size: 0.75rem;
  line-height: 1.4;
  color: var(--color-text-muted);
}
</style>
