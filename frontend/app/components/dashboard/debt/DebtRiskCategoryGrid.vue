<template>
  <div v-if="cats.length" class="debt-eng-grid debt-eng-grid--3">
    <button
      v-for="c in cats"
      :key="c.id"
      type="button"
      class="debt-cat debt-eng-card"
      :class="{ 'debt-cat--open': expanded === c.id }"
      @click="toggle(c.id)"
    >
      <div class="debt-cat__top">
        <span class="debt-cat__label">{{ c.label }}</span>
        <span class="debt-cat__score" :data-z="zone(c.score)">{{ c.score }}</span>
      </div>
      <div class="debt-cat__bar" aria-hidden="true">
        <div class="debt-cat__fill" :style="{ width: c.score + '%', background: barColor(c.score) }" />
      </div>
      <p class="debt-cat__one">{{ c.explanation }}</p>
      <p v-if="expanded === c.id" class="debt-cat__more">
        Scores are modeled from your dashboard inputs (income, balances, spending mix, and risk signals). Not a credit bureau score.
      </p>
    </button>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const cats = computed(() => engines?.riskEngine.value?.categories ?? [])
const expanded = ref<string | null>(null)

function toggle(id: string) {
  expanded.value = expanded.value === id ? null : id
}

function zone(s: number) {
  if (s <= 30) return 'low'
  if (s <= 55) return 'mid'
  if (s <= 75) return 'high'
  return 'crit'
}

function barColor(s: number) {
  if (s <= 30) return 'var(--eng-green)'
  if (s <= 55) return 'var(--eng-amber)'
  if (s <= 75) return '#f97316'
  return 'var(--eng-red)'
}
</script>

<style scoped>
.debt-cat {
  text-align: left;
  padding: 1rem 1.05rem;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.debt-cat:hover {
  border-color: color-mix(in srgb, var(--dash-accent) 28%, var(--color-border));
}
.debt-cat--open {
  border-color: color-mix(in srgb, var(--dash-accent) 40%, var(--color-border));
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--dash-accent) 15%, transparent);
}
.debt-cat__top {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
}
.debt-cat__label {
  font-size: 0.78rem;
  font-weight: 650;
  color: var(--color-text);
}
.debt-cat__score {
  font-size: 1.25rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}
.debt-cat__score[data-z='low'] {
  color: var(--eng-green);
}
.debt-cat__score[data-z='mid'] {
  color: var(--eng-amber);
}
.debt-cat__score[data-z='high'] {
  color: #ea580c;
}
.debt-cat__score[data-z='crit'] {
  color: var(--eng-red);
}
.debt-cat__bar {
  height: 6px;
  border-radius: 9999px;
  background: var(--color-surface-raised);
  margin-top: 0.65rem;
  overflow: hidden;
}
.debt-cat__fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.5s ease;
}
.debt-cat__one {
  margin: 0.65rem 0 0;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--color-text-muted);
}
.debt-cat__more {
  margin: 0.65rem 0 0;
  font-size: 0.7rem;
  line-height: 1.45;
  color: var(--color-text-faint);
}
</style>
