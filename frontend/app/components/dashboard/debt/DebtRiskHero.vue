<template>
  <div v-if="risk" class="debt-risk-hero debt-eng-card debt-eng-card--glow">
    <div class="debt-risk-hero__main">
      <div class="debt-risk-hero__gauge-wrap">
        <svg class="debt-risk-hero__svg" viewBox="0 0 120 120" aria-hidden="true">
          <circle class="debt-risk-hero__track" cx="60" cy="60" r="52" fill="none" stroke-width="10" />
          <circle
            class="debt-risk-hero__arc"
            cx="60"
            cy="60"
            r="52"
            fill="none"
            stroke-width="10"
            :stroke="arcColor"
            :stroke-dasharray="circ"
            :stroke-dashoffset="dashOff"
            transform="rotate(-90 60 60)"
          />
        </svg>
        <div class="debt-risk-hero__center">
          <span class="debt-risk-hero__score">{{ risk.hero.score }}</span>
          <span class="debt-risk-hero__sub">/ 100</span>
        </div>
      </div>
      <div class="debt-risk-hero__copy">
        <p class="debt-risk-hero__badge" :data-band="risk.hero.band">{{ risk.hero.bandLabel }}</p>
        <h3 class="debt-risk-hero__title">Financial Risk Score</h3>
        <p class="debt-risk-hero__ai">{{ risk.hero.aiSummary }}</p>
        <div class="debt-risk-hero__meta">
          <span class="debt-risk-hero__trend" :data-trend="risk.hero.trend">
            {{ risk.hero.trend === 'improving' ? '↑' : risk.hero.trend === 'worsening' ? '↓' : '→' }}
            {{ risk.hero.trendLabel }}
          </span>
          <span class="debt-risk-hero__sep" />
          <span class="debt-risk-hero__compare">{{ risk.hero.vsLastMonth }}</span>
        </div>
        <button type="button" class="debt-risk-hero__cta" @click="scrollToPlan">
          Reduce my risk
        </button>
      </div>
    </div>
    <ul v-if="risk.warnings.length" class="debt-risk-hero__warnings">
      <li v-for="w in risk.warnings.slice(0, 3)" :key="w.id" :data-sev="w.severity">
        <strong>{{ w.title }}</strong>
        <span>{{ w.detail }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const risk = computed(() => engines?.riskEngine.value)

const circ = 2 * Math.PI * 52
const dashOff = computed(() => {
  const pct = (risk.value?.hero.score ?? 0) / 100
  return circ * (1 - pct)
})

const arcColor = computed(() => {
  const b = risk.value?.hero.band
  if (b === 'stable') return 'var(--eng-green)'
  if (b === 'caution') return 'var(--eng-amber)'
  if (b === 'high') return '#f97316'
  return 'var(--eng-red)'
})

function scrollToPlan() {
  document.getElementById('debt-action-plan')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<style scoped>
.debt-risk-hero {
  padding: 1.35rem 1.35rem 1.25rem;
  position: relative;
  overflow: hidden;
}
.debt-risk-hero__main {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
}
.debt-risk-hero__gauge-wrap {
  position: relative;
  width: 9.5rem;
  height: 9.5rem;
  flex-shrink: 0;
}
.debt-risk-hero__svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 4px 14px rgba(15, 23, 42, 0.12));
}
.debt-risk-hero__track {
  stroke: var(--color-surface-raised);
}
.debt-risk-hero__arc {
  stroke-linecap: round;
  transition: stroke-dashoffset 0.9s ease, stroke 0.3s ease;
}
.debt-risk-hero__center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.debt-risk-hero__score {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--color-text);
  line-height: 1;
}
.debt-risk-hero__sub {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-text-faint);
}
.debt-risk-hero__copy {
  flex: 1;
  min-width: min(100%, 16rem);
}
.debt-risk-hero__badge {
  display: inline-block;
  margin: 0 0 0.35rem;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.28rem 0.55rem;
  border-radius: 9999px;
}
.debt-risk-hero__badge[data-band='stable'] {
  background: rgba(34, 197, 94, 0.15);
  color: var(--eng-green);
}
.debt-risk-hero__badge[data-band='caution'] {
  background: rgba(245, 158, 11, 0.15);
  color: var(--eng-amber);
}
.debt-risk-hero__badge[data-band='high'] {
  background: rgba(249, 115, 22, 0.15);
  color: #ea580c;
}
.debt-risk-hero__badge[data-band='critical'] {
  background: rgba(239, 68, 68, 0.15);
  color: var(--eng-red);
}
.debt-risk-hero__title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 750;
  color: var(--color-text);
  letter-spacing: -0.02em;
}
.debt-risk-hero__ai {
  margin: 0.5rem 0 0;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.debt-risk-hero__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
  margin-top: 0.85rem;
  font-size: 0.78rem;
  color: var(--color-text-muted);
}
.debt-risk-hero__trend[data-trend='improving'] {
  color: var(--eng-green);
  font-weight: 700;
}
.debt-risk-hero__trend[data-trend='worsening'] {
  color: var(--eng-red);
  font-weight: 700;
}
.debt-risk-hero__sep {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--color-border);
}
.debt-risk-hero__cta {
  margin-top: 1rem;
  padding: 0.55rem 1.1rem;
  border-radius: 0.65rem;
  border: none;
  font-weight: 700;
  font-size: 0.8125rem;
  cursor: pointer;
  background: linear-gradient(135deg, var(--eng-slate), var(--eng-navy));
  color: #fff;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.25);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.debt-risk-hero__cta:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.3);
}
.debt-risk-hero__warnings {
  list-style: none;
  margin: 1.25rem 0 0;
  padding: 0.85rem 0 0;
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.debt-risk-hero__warnings li {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-text-muted);
  padding: 0.5rem 0.65rem;
  border-radius: 0.6rem;
  background: var(--color-surface-raised);
}
.debt-risk-hero__warnings li[data-sev='critical'] {
  border-left: 3px solid var(--eng-red);
}
.debt-risk-hero__warnings li[data-sev='caution'] {
  border-left: 3px solid var(--eng-amber);
}
.debt-risk-hero__warnings li strong {
  color: var(--color-text);
  font-size: 0.8125rem;
}
</style>
