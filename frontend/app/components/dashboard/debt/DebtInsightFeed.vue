<template>
  <div v-if="items.length" class="debt-insight-feed">
    <div
      v-for="it in items"
      :key="it.id"
      class="debt-insight debt-eng-card"
      :data-tone="it.tone"
    >
        <p class="debt-insight__title">{{ it.title }}</p>
        <p class="debt-insight__body">{{ it.body }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const items = computed(() => engines?.riskEngine.value?.insights ?? [])
</script>

<style scoped>
.debt-insight-feed {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.debt-insight {
  padding: 0.9rem 1.05rem;
  border-left: 3px solid var(--color-border);
}
.debt-insight[data-tone='warn'] {
  border-left-color: var(--eng-amber);
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.06), transparent);
}
.debt-insight[data-tone='positive'] {
  border-left-color: var(--eng-green);
  background: linear-gradient(90deg, rgba(34, 197, 94, 0.06), transparent);
}
.debt-insight__title {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-text);
}
.debt-insight__body {
  margin: 0.35rem 0 0;
  font-size: 0.78rem;
  line-height: 1.5;
  color: var(--color-text-muted);
}
</style>
