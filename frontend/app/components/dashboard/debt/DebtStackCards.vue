<template>
  <div v-if="ranked.length" class="debt-stack">
    <h4 class="debt-stack__title">Debt stack</h4>
    <div class="debt-stack__list">
      <article v-for="d in ranked" :key="d.name" class="debt-stack__card debt-eng-card">
        <header class="debt-stack__head">
          <div>
            <p class="debt-stack__name">{{ d.name }}</p>
            <p class="debt-stack__type">{{ d.type }} · {{ d.rate }}% APR</p>
          </div>
          <span class="debt-stack__tag" :data-p="tagTone(d.priorityTag)">{{ d.priorityTag }}</span>
        </header>
        <p class="debt-stack__detail">{{ d.priorityDetail }}</p>
        <div class="debt-stack__nums">
          <div>
            <span class="debt-stack__lbl">Balance</span>
            <strong>${{ d.balance.toLocaleString('en-US') }}</strong>
          </div>
          <div>
            <span class="debt-stack__lbl">Min / mo</span>
            <strong>${{ d.min }}</strong>
          </div>
          <div>
            <span class="debt-stack__lbl">Est. interest / mo</span>
            <strong>${{ d.interestThisMonth.toFixed(0) }}</strong>
          </div>
          <div v-if="d.dueInDays != null">
            <span class="debt-stack__lbl">Due in</span>
            <strong>{{ d.dueInDays }}d</strong>
          </div>
        </div>
        <div v-if="d.utilization != null" class="debt-stack__util">
          <span class="debt-stack__lbl">Utilization</span>
          <div class="debt-stack__bar">
            <div class="debt-stack__fill" :style="{ width: Math.min(100, d.utilization) + '%' }" />
          </div>
          <span>{{ d.utilization }}%</span>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const ranked = computed(() => engines?.debtRanked.value ?? [])

function tagTone(tag: string) {
  if (/attack|due/i.test(tag)) return 'hot'
  if (/credit|cash/i.test(tag)) return 'mid'
  if (/keep|low/i.test(tag)) return 'cool'
  return 'mid'
}
</script>

<style scoped>
.debt-stack__title {
  margin: 0 0 0.85rem;
  font-size: 0.95rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-stack__list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.debt-stack__card {
  padding: 1rem 1.1rem;
}
.debt-stack__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}
.debt-stack__name {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--color-text);
}
.debt-stack__type {
  margin: 0.2rem 0 0;
  font-size: 0.72rem;
  color: var(--color-text-muted);
}
.debt-stack__tag {
  flex-shrink: 0;
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 0.28rem 0.5rem;
  border-radius: 9999px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
}
.debt-stack__tag[data-p='hot'] {
  background: rgba(249, 115, 22, 0.12);
  color: #c2410c;
  border-color: rgba(249, 115, 22, 0.25);
}
.debt-stack__tag[data-p='mid'] {
  background: var(--eng-blue-dim);
  color: var(--eng-blue);
}
.debt-stack__tag[data-p='cool'] {
  background: rgba(34, 197, 94, 0.1);
  color: var(--eng-green);
}
.debt-stack__detail {
  margin: 0.5rem 0 0;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}
.debt-stack__nums {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.65rem;
  margin-top: 0.85rem;
}
@media (min-width: 560px) {
  .debt-stack__nums {
    grid-template-columns: repeat(4, 1fr);
  }
}
.debt-stack__lbl {
  display: block;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-faint);
}
.debt-stack__nums strong {
  font-size: 0.88rem;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}
.debt-stack__util {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: 0.75rem;
  font-size: 0.72rem;
  color: var(--color-text-muted);
}
.debt-stack__bar {
  flex: 1;
  height: 6px;
  border-radius: 9999px;
  background: var(--color-surface-raised);
  overflow: hidden;
}
.debt-stack__fill {
  height: 100%;
  border-radius: 9999px;
  background: linear-gradient(90deg, var(--eng-amber), var(--eng-red));
}
</style>
