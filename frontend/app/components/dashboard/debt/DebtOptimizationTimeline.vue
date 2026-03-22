<template>
  <div v-if="items.length" class="debt-tl">
    <h4 class="debt-tl__title">Optimization timeline</h4>
    <div class="debt-tl__track">
      <div v-for="(it, i) in items" :key="i" class="debt-tl__node">
        <span class="debt-tl__dot" />
        <div class="debt-tl__card debt-eng-card">
          <span class="debt-tl__phase">{{ it.phase }}</span>
          <p class="debt-tl__node-title">{{ it.title }}</p>
          <p class="debt-tl__detail">{{ it.detail }}</p>
          <span class="debt-tl__mo">~Month {{ it.month }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const items = computed(() => engines?.optimizationTimeline.value ?? [])
</script>

<style scoped>
.debt-tl__title {
  margin: 0 0 1rem;
  font-size: 0.95rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-tl__track {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
  padding-left: 0.5rem;
}
.debt-tl__node {
  position: relative;
  padding-left: 1.35rem;
  padding-bottom: 1.15rem;
}
.debt-tl__node:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 0.45rem;
  top: 0.55rem;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, var(--eng-blue), color-mix(in srgb, var(--dash-accent) 40%, var(--eng-blue)));
  border-radius: 2px;
  opacity: 0.35;
}
.debt-tl__dot {
  position: absolute;
  left: 0.2rem;
  top: 0.35rem;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--eng-blue);
  box-shadow: 0 0 0 3px var(--eng-blue-dim);
}
.debt-tl__card {
  padding: 0.75rem 0.9rem;
}
.debt-tl__phase {
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--dash-accent-text);
}
.debt-tl__node-title {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-text);
}
.debt-tl__detail {
  margin: 0.3rem 0 0;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}
.debt-tl__mo {
  display: inline-block;
  margin-top: 0.45rem;
  font-size: 0.65rem;
  font-weight: 650;
  color: var(--color-text-faint);
}
</style>
