<template>
  <div v-if="ov && hi" class="debt-opt-hero debt-eng-card debt-eng-card--glow">
    <div class="debt-opt-hero__grid">
      <div>
        <p class="debt-opt-hero__eyebrow">Debt optimization engine</p>
        <h3 class="debt-opt-hero__title">Your debt war room</h3>
        <p class="debt-opt-hero__strat">
          <span>Recommended lens</span>
          <strong>{{ hi.label }}</strong>
        </p>
        <p class="debt-opt-hero__blurb">{{ hi.blurb }}</p>
        <div class="debt-opt-hero__modes" role="group" aria-label="Payoff stress mode">
          <button
            v-for="m in modes"
            :key="m.id"
            type="button"
            class="debt-opt-hero__mode"
            :class="{ 'debt-opt-hero__mode--on': payoffMode === m.id }"
            @click="setMode(m.id)"
          >
            {{ m.label }}
          </button>
        </div>
      </div>
      <div class="debt-opt-hero__stats">
        <div class="debt-opt-hero__stat">
          <span class="debt-opt-hero__stat-label">Total debt</span>
          <strong>${{ ov.total.toLocaleString('en-US') }}</strong>
        </div>
        <div class="debt-opt-hero__stat">
          <span class="debt-opt-hero__stat-label">Weighted APR</span>
          <strong>{{ ov.wapr.toFixed(2) }}%</strong>
        </div>
        <div class="debt-opt-hero__stat">
          <span class="debt-opt-hero__stat-label">Monthly minimums</span>
          <strong>${{ ov.mins.toLocaleString('en-US') }}</strong>
        </div>
        <div class="debt-opt-hero__stat">
          <span class="debt-opt-hero__stat-label">Interest (12 mo est.)</span>
          <strong>${{ ov.interest12.toLocaleString('en-US') }}</strong>
        </div>
        <div class="debt-opt-hero__stat debt-opt-hero__stat--wide">
          <span class="debt-opt-hero__stat-label">Modeled payoff (hybrid)</span>
          <strong>{{ ov.payoffLabel }}</strong>
          <span class="debt-opt-hero__stat-hint">~{{ ov.hybrid?.months ?? '—' }} months at current minimums + modeled extras</span>
        </div>
      </div>
    </div>
    <div class="debt-opt-hero__actions">
      <button type="button" class="debt-opt-hero__btn debt-opt-hero__btn--primary" @click="scrollSim">
        Simulate extra payment
      </button>
      <button type="button" class="debt-opt-hero__btn" @click="cycleStrategy">
        Switch strategy highlight
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PayoffStressMode } from '~/types/debtEngines'
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const payoffModeRef = inject<Ref<PayoffStressMode> | null>('debtPayoffMode', null)

const ov = computed(() => engines?.debtOverview.value)
const hi = computed(() => engines?.highlightedStrategy.value)

const payoffMode = computed({
  get: () => payoffModeRef?.value ?? 'balanced',
  set: (v: PayoffStressMode) => {
    if (payoffModeRef) payoffModeRef.value = v
  },
})

const modes: { id: PayoffStressMode; label: string }[] = [
  { id: 'aggressive', label: 'Aggressive payoff' },
  { id: 'balanced', label: 'Balanced' },
  { id: 'stability', label: 'Stability first' },
  { id: 'credit_repair', label: 'Credit repair first' },
]

const modeCycle: PayoffStressMode[] = ['aggressive', 'balanced', 'stability', 'credit_repair']

function setMode(id: PayoffStressMode) {
  payoffMode.value = id
}

function cycleStrategy() {
  const i = modeCycle.indexOf(payoffMode.value)
  payoffMode.value = modeCycle[(i + 1) % modeCycle.length]!
}

function scrollSim() {
  document.getElementById('debt-extra-pay-sim')?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.debt-opt-hero {
  padding: 1.35rem 1.35rem 1.25rem;
}
.debt-opt-hero__grid {
  display: grid;
  gap: 1.5rem;
}
@media (min-width: 900px) {
  .debt-opt-hero__grid {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }
}
.debt-opt-hero__eyebrow {
  margin: 0;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--dash-accent-text);
}
.debt-opt-hero__title {
  margin: 0.35rem 0 0;
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--color-text);
}
.debt-opt-hero__strat {
  margin: 0.85rem 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
.debt-opt-hero__strat strong {
  font-size: 0.95rem;
  color: var(--eng-blue);
}
.debt-opt-hero__blurb {
  margin: 0.5rem 0 0;
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.debt-opt-hero__modes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 1rem;
}
.debt-opt-hero__mode {
  padding: 0.38rem 0.65rem;
  border-radius: 9999px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-raised);
  font-size: 0.68rem;
  font-weight: 650;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease, color 0.15s ease;
}
.debt-opt-hero__mode--on {
  border-color: color-mix(in srgb, var(--eng-blue) 40%, var(--color-border));
  background: var(--eng-blue-dim);
  color: var(--eng-blue);
}
.debt-opt-hero__stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
.debt-opt-hero__stat {
  padding: 0.75rem 0.85rem;
  border-radius: 0.75rem;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
}
.debt-opt-hero__stat--wide {
  grid-column: 1 / -1;
}
.debt-opt-hero__stat-label {
  display: block;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-faint);
}
.debt-opt-hero__stat strong {
  display: block;
  margin-top: 0.25rem;
  font-size: 1.1rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}
.debt-opt-hero__stat-hint {
  display: block;
  margin-top: 0.2rem;
  font-size: 0.68rem;
  color: var(--color-text-faint);
}
.debt-opt-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}
.debt-opt-hero__btn {
  padding: 0.5rem 1rem;
  border-radius: 0.65rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  font-size: 0.78rem;
  font-weight: 650;
  color: var(--color-text);
  cursor: pointer;
}
.debt-opt-hero__btn--primary {
  background: linear-gradient(135deg, #1e3a5f, var(--eng-navy));
  color: #fff;
  border-color: transparent;
}
</style>
