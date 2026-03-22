<template>
  <div class="behavior">
    <!-- Snapshot: score + trend + AI voice -->
    <div class="behavior__snapshot">
      <div class="behavior__score-block">
        <p class="behavior__kicker">Financial Behavior Score</p>
        <div class="behavior__dial">
          <div
            class="behavior__ring"
            :style="{
              '--score-pct': Math.min(100, Math.max(0, behavior.score)),
              '--score-color': scoreColor,
            }"
            aria-hidden="true"
          />
          <div class="behavior__score-center">
            <span class="behavior__score-num">{{ behavior.score }}</span>
            <span class="behavior__score-cap">/ 100</span>
          </div>
        </div>
        <span class="behavior__badge" :class="`behavior__badge--${behavior.scoreBand}`">
          {{ scoreBandLabel }}
        </span>
      </div>
      <div class="behavior__snapshot-main">
        <p class="behavior__trend" :class="`behavior__trend--${behavior.trend.direction}`">
          <span class="behavior__trend-arrow" aria-hidden="true">{{ trendArrow }}</span>
          {{ behavior.trend.text }}
        </p>
        <div class="behavior__ai-card">
          <p class="behavior__ai-label">Summary</p>
          <p class="behavior__ai-text">{{ behavior.aiSummary }}</p>
        </div>
      </div>
    </div>

    <!-- Pattern detection -->
    <div class="behavior__section">
      <h3 class="behavior__h3">Patterns</h3>
      <div class="behavior__grid-2">
        <div class="behavior__card">
          <div class="behavior__card-head">
            <span class="behavior__icon" aria-hidden="true">🕒</span>
            <div>
              <h4 class="behavior__h4">Time-based spending</h4>
              <p class="behavior__card-sub">{{ behavior.patterns.timeOfDay.headline }}</p>
            </div>
          </div>
          <div class="behavior__bars" role="img" :aria-label="'Spending by time of day'">
            <div
              v-for="row in behavior.patterns.timeOfDay.byHour"
              :key="row.label"
              class="behavior__bar-col"
            >
              <div class="behavior__bar-track">
                <div
                  class="behavior__bar-fill"
                  :style="{ height: hourBarPct(row.amount) + '%' }"
                />
              </div>
              <span class="behavior__bar-lbl">{{ row.label }}</span>
            </div>
          </div>
        </div>
        <div class="behavior__card">
          <div class="behavior__card-head">
            <span class="behavior__icon" aria-hidden="true">📅</span>
            <div>
              <h4 class="behavior__h4">Day-based patterns</h4>
              <p class="behavior__card-sub">{{ behavior.patterns.dayPattern.headline }}</p>
            </div>
          </div>
          <p class="behavior__p">{{ behavior.patterns.dayPattern.detail }}</p>
        </div>
        <div class="behavior__card behavior__card--wide">
          <div class="behavior__card-head">
            <span class="behavior__icon" aria-hidden="true">🧠</span>
            <div>
              <h4 class="behavior__h4">Triggers</h4>
            </div>
          </div>
          <ul class="behavior__bullets behavior__bullets--tight">
            <li v-for="(t, i) in triggersShown" :key="i">{{ t }}</li>
          </ul>
        </div>
        <div
          v-for="(c, i) in categoriesShown"
          :key="'cat-' + i"
          class="behavior__card"
        >
          <div class="behavior__card-head">
            <span class="behavior__icon" aria-hidden="true">🛍️</span>
            <div>
              <h4 class="behavior__h4">{{ c.headline }}</h4>
            </div>
          </div>
          <p class="behavior__p behavior__p--compact">{{ c.detail }}</p>
        </div>
      </div>
    </div>

    <!-- Risks -->
    <div class="behavior__section">
      <h3 class="behavior__h3 behavior__h3--risk">Risks</h3>
      <div class="behavior__risk-grid">
        <div
          v-for="r in risksShown"
          :key="r.id"
          class="behavior__risk-card"
          :class="`behavior__risk-card--${r.level}`"
        >
          <div class="behavior__risk-top">
            <span class="behavior__risk-emoji" aria-hidden="true">{{ riskEmoji(r.level) }}</span>
            <div class="behavior__risk-meta">
              <span class="behavior__risk-badge" :class="`behavior__risk-badge--${r.level}`">
                {{ r.level }}
              </span>
              <span class="behavior__risk-prob">{{ Math.round(r.probability * 100) }}%</span>
            </div>
          </div>
          <h4 class="behavior__risk-title">{{ r.title }}</h4>
          <p class="behavior__risk-body">{{ r.body }}</p>
        </div>
      </div>
    </div>

    <!-- Forecast -->
    <div class="behavior__section">
      <h3 class="behavior__h3">Next 7 days</h3>
      <div class="behavior__forecast-grid">
        <div class="behavior__card behavior__forecast-stat">
          <p class="behavior__forecast-label">Est. spend</p>
          <p class="behavior__forecast-big">
            ${{ behavior.forecast.next7Spend.toLocaleString('en-US') }}
            <span
              class="behavior__forecast-delta"
              :class="{ 'behavior__forecast-delta--up': behavior.forecast.changePct > 0 }"
            >
              (↑ {{ behavior.forecast.changePct }}%)
            </span>
          </p>
          <ul class="behavior__alerts behavior__alerts--tight">
            <li v-for="(a, i) in alertsShown" :key="i">{{ a }}</li>
          </ul>
        </div>
        <div class="behavior__card behavior__chart-card">
          <h4 class="behavior__h4">Daily projection</h4>
          <ClientOnly>
            <div class="behavior__line-h">
              <LineChart
                :labels="behavior.forecast.labels"
                :datasets="forecastDataset"
                y-prefix="$"
              />
            </div>
            <template #fallback>
              <div class="dash-chart-fallback dash-chart-fallback--line" aria-hidden="true" />
            </template>
          </ClientOnly>
        </div>
      </div>
      <div class="behavior__ai-card behavior__ai-card--tint">
        <p class="behavior__ai-label">Note</p>
        <p class="behavior__ai-text behavior__ai-text--compact">{{ behavior.forecast.aiMessage }}</p>
      </div>
    </div>

    <!-- Recommendations -->
    <div class="behavior__section">
      <h3 class="behavior__h3">Suggestions</h3>
      <div class="behavior__rec-grid">
        <div v-for="rec in recsShown" :key="rec.id" class="behavior__rec-card">
          <p class="behavior__rec-title">{{ rec.title }}</p>
          <p class="behavior__rec-detail">{{ rec.detail }}</p>
          <button type="button" class="behavior__btn" @click="onAgentAction(rec.id, rec.actionLabel)">
            {{ rec.actionLabel }}
          </button>
        </div>
      </div>
    </div>

    <!-- Controls -->
    <div class="behavior__section">
      <h3 class="behavior__h3">Controls</h3>
      <div class="behavior__controls">
        <label class="behavior__toggle">
          <input v-model="spendingGuard" type="checkbox" />
          <span>Block purchases after 10PM</span>
        </label>
        <label class="behavior__toggle">
          <input v-model="impulseDelay" type="checkbox" />
          <span>5-minute delay on new charges</span>
        </label>
        <div class="behavior__limits">
          <p class="behavior__limits-title">Monthly caps</p>
          <div v-for="lim in categoryLimits" :key="lim.category" class="behavior__limit-row">
            <span class="behavior__limit-name">{{ lim.category }}</span>
            <div class="behavior__limit-input-wrap">
              <span class="behavior__limit-prefix">$</span>
              <input v-model.number="lim.max" class="behavior__limit-input" type="number" min="0" step="10" />
            </div>
          </div>
        </div>
        <label class="behavior__alert-row">
          <span>Alert if daily spend over</span>
          <div class="behavior__limit-input-wrap behavior__limit-input-wrap--sm">
            <span class="behavior__limit-prefix">$</span>
            <input v-model.number="dailyAlertThreshold" class="behavior__limit-input" type="number" min="0" step="5" />
          </div>
        </label>
      </div>
    </div>

    <!-- Trends -->
    <div class="behavior__section">
      <h3 class="behavior__h3">Score trend</h3>
      <p class="behavior__lead behavior__lead--inline">{{ behavior.trends.disciplineNote }}</p>
      <div class="behavior__card behavior__chart-card">
        <h4 class="behavior__h4">Weekly score</h4>
        <ClientOnly>
          <div class="behavior__line-h behavior__line-h--tall">
            <LineChart
              :labels="behavior.trends.weekLabels"
              :datasets="trendsDataset"
              y-prefix=""
              :show-legend="false"
            />
          </div>
          <template #fallback>
            <div class="dash-chart-fallback dash-chart-fallback--line-tall" aria-hidden="true" />
          </template>
        </ClientOnly>
      </div>
    </div>

    <!-- Goals -->
    <div class="behavior__section">
      <h3 class="behavior__h3">Goals</h3>
      <ul class="behavior__goal-list">
        <li v-for="(g, i) in behavior.goals.items" :key="i" class="behavior__goal-row">
          <span class="behavior__goal-icon" :class="g.aligned ? 'behavior__goal-icon--ok' : 'behavior__goal-icon--bad'">
            {{ g.aligned ? '✓' : '✕' }}
          </span>
          <span>
            <strong>{{ g.name }}</strong>
            — {{ g.aligned ? 'on track' : 'needs attention' }}
          </span>
        </li>
      </ul>
      <div class="behavior__progress-block">
        <div class="behavior__progress-row">
          <span>Debt reduction</span>
          <div class="behavior__progress-track">
            <div class="behavior__progress-fill behavior__progress-fill--debt" :style="{ width: pct(behavior.goals.debtProgress) }" />
          </div>
          <span class="behavior__progress-pct">{{ pct(behavior.goals.debtProgress) }}</span>
        </div>
        <div class="behavior__progress-row">
          <span>Savings</span>
          <div class="behavior__progress-track">
            <div class="behavior__progress-fill behavior__progress-fill--save" :style="{ width: pct(behavior.goals.savingsProgress) }" />
          </div>
          <span class="behavior__progress-pct">{{ pct(behavior.goals.savingsProgress) }}</span>
        </div>
        <div class="behavior__progress-row">
          <span>Investment readiness</span>
          <div class="behavior__progress-track">
            <div class="behavior__progress-fill behavior__progress-fill--inv" :style="{ width: pct(behavior.goals.investmentReadiness) }" />
          </div>
          <span class="behavior__progress-pct">{{ pct(behavior.goals.investmentReadiness) }}</span>
        </div>
      </div>
    </div>

    <!-- Profile -->
    <div class="behavior__section behavior__section--last">
      <h3 class="behavior__h3">Your profile</h3>
      <div class="behavior__profile">
        <div class="behavior__profile-avatar" aria-hidden="true">{{ behavior.profile.emoji }}</div>
        <div class="behavior__profile-body">
          <h4 class="behavior__profile-title">{{ behavior.profile.title }}</h4>
          <p class="behavior__p behavior__p--compact">{{ behavior.profile.description }}</p>
          <div class="behavior__profile-cols">
            <div>
              <p class="behavior__mini-h">Strengths</p>
              <ul class="behavior__mini-list">
                <li v-for="(s, i) in behavior.profile.strengths" :key="'s' + i">{{ s }}</li>
              </ul>
            </div>
            <div>
              <p class="behavior__mini-h">Watch-outs</p>
              <ul class="behavior__mini-list">
                <li v-for="(w, i) in behavior.profile.weaknesses" :key="'w' + i">{{ w }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BehaviorCategoryLimit, BehaviorInsightsPayload } from '~/types/behaviorInsights'

/** Mirrors LineChart.client.vue — keep in sync when adding chart props */
interface LineDs {
  label: string
  data: number[]
  color: string
  fill?: boolean
  dashed?: boolean
}

const props = defineProps<{
  behavior: BehaviorInsightsPayload
}>()

const emit = defineEmits<{
  'agent-action': [payload: { actionId: string; actionLabel: string }]
}>()

/** Cap list length so long API payloads don’t overwhelm the UI */
const MAX_TRIGGERS = 2
const MAX_CATEGORIES = 2
const MAX_RISKS = 2
const MAX_ALERTS = 1
const MAX_RECS = 3

const triggersShown = computed(() => props.behavior.patterns.triggers.slice(0, MAX_TRIGGERS))
const categoriesShown = computed(() => props.behavior.patterns.categories.slice(0, MAX_CATEGORIES))
const risksShown = computed(() => props.behavior.risks.slice(0, MAX_RISKS))
const alertsShown = computed(() => props.behavior.forecast.alerts.slice(0, MAX_ALERTS))
const recsShown = computed(() => props.behavior.recommendations.slice(0, MAX_RECS))

const maxHour = computed(() =>
  Math.max(...props.behavior.patterns.timeOfDay.byHour.map((h) => h.amount), 1),
)

function hourBarPct(amount: number) {
  return Math.round((amount / maxHour.value) * 100)
}

const scoreColor = computed(() => {
  const b = props.behavior.scoreBand
  if (b === 'disciplined') return '#16a34a'
  if (b === 'unstable') return '#ca8a04'
  return '#dc2626'
})

const scoreBandLabel = computed(() => {
  const m: Record<string, string> = {
    disciplined: 'Disciplined',
    unstable: 'Unstable',
    risky: 'Risky',
  }
  return m[props.behavior.scoreBand] ?? props.behavior.scoreBand
})

const trendArrow = computed(() => {
  const d = props.behavior.trend.direction
  if (d === 'up') return '↑'
  if (d === 'down') return '↓'
  return '→'
})

function riskEmoji(level: string) {
  if (level === 'high') return '🚨'
  return '⚠️'
}

const forecastDataset = computed<LineDs[]>(() => [
  {
    label: 'Projected daily spend',
    data: props.behavior.forecast.projectedSpend,
    color: '#2563eb',
    fill: true,
  },
])

const trendsDataset = computed<LineDs[]>(() => [
  {
    label: 'Behavior score',
    data: props.behavior.trends.scores,
    color: '#0d8147',
    fill: true,
  },
])

function pct(n: number) {
  return `${Math.round(Math.min(1, Math.max(0, n)) * 100)}%`
}

const spendingGuard = ref(props.behavior.controlDefaults.spendingGuard)
const impulseDelay = ref(props.behavior.controlDefaults.impulseDelay)
const categoryLimits = ref<BehaviorCategoryLimit[]>(
  props.behavior.controlDefaults.categoryLimits.map((c) => ({ ...c })),
)
const dailyAlertThreshold = ref(props.behavior.controlDefaults.dailyAlertThreshold)

function onAgentAction(actionId: string, actionLabel: string) {
  emit('agent-action', { actionId, actionLabel })
}
</script>

<style scoped>
.behavior {
  display: flex;
  flex-direction: column;
  gap: 1.35rem;
}

.behavior__snapshot {
  display: grid;
  grid-template-columns: minmax(200px, 240px) 1fr;
  gap: 1.5rem;
  align-items: start;
  padding: 1.35rem;
  border-radius: 1rem;
  border: 1px solid var(--color-border);
  background: linear-gradient(145deg, var(--color-surface) 0%, var(--color-surface-raised) 100%);
  box-shadow: var(--shadow-card);
}

.behavior__score-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.65rem;
}

.behavior__dial {
  position: relative;
  width: 7.5rem;
  height: 7.5rem;
}

.behavior__kicker {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-faint);
  margin: 0;
}

.behavior__ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: conic-gradient(
    from -90deg,
    var(--score-color) calc(var(--score-pct) * 1%),
    var(--color-surface-raised) 0
  );
  box-shadow: inset 0 0 0 10px var(--color-surface);
}

.behavior__score-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: row;
  align-items: baseline;
  justify-content: center;
  gap: 0.15rem;
  pointer-events: none;
}

.behavior__score-num {
  font-size: 1.85rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--color-text);
}

.behavior__score-cap {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  font-weight: 600;
}

.behavior__badge {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.3rem 0.65rem;
  border-radius: 9999px;
}
.behavior__badge--disciplined {
  background: rgba(22, 163, 74, 0.14);
  color: #15803d;
}
.behavior__badge--unstable {
  background: rgba(202, 138, 4, 0.16);
  color: #a16207;
}
.behavior__badge--risky {
  background: rgba(220, 38, 38, 0.14);
  color: #b91c1c;
}

.behavior__snapshot-main {
  min-width: 0;
}

.behavior__trend {
  font-size: 0.9rem;
  font-weight: 650;
  margin: 0 0 1rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.behavior__trend--up {
  color: #15803d;
}
.behavior__trend--down {
  color: #b45309;
}
.behavior__trend--steady {
  color: var(--color-text-muted);
}

.behavior__ai-card {
  padding: 1rem 1.1rem;
  border-radius: 0.85rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}
.behavior__ai-card--tint {
  margin-top: 1rem;
  background: color-mix(in srgb, var(--color-info) 6%, var(--color-surface));
  border-color: color-mix(in srgb, var(--color-info) 18%, var(--color-border));
}

.behavior__ai-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-faint);
  margin: 0 0 0.45rem;
}

.behavior__ai-text {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text);
}
.behavior__ai-text--compact {
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}

.behavior__section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.behavior__section--last {
  padding-bottom: 0.25rem;
}

.behavior__h3 {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-text-faint);
  margin: 0;
}
.behavior__h3--risk {
  color: #b91c1c;
}

.behavior__lead {
  margin: 0;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  max-width: 44rem;
}
.behavior__lead--inline {
  font-size: 0.78rem;
  margin-bottom: 0.35rem;
}

.behavior__grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}
@media (max-width: 800px) {
  .behavior__grid-2 {
    grid-template-columns: 1fr;
  }
  .behavior__snapshot {
    grid-template-columns: 1fr;
  }
}

.behavior__card {
  padding: 1.1rem 1.15rem;
  border-radius: 0.95rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}
.behavior__card--wide {
  grid-column: 1 / -1;
}

.behavior__card-head {
  display: flex;
  gap: 0.65rem;
  margin-bottom: 0.5rem;
}

.behavior__icon {
  font-size: 1.25rem;
  line-height: 1;
}

.behavior__h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 650;
  color: var(--color-text);
}

.behavior__card-sub {
  margin: 0.2rem 0 0;
  font-size: 0.78rem;
  color: var(--color-text-muted);
  line-height: 1.4;
}

.behavior__p {
  margin: 0;
  font-size: 0.84rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.behavior__p--compact {
  font-size: 0.8rem;
  line-height: 1.4;
}

.behavior__bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.35rem;
  height: 120px;
  padding-top: 0.35rem;
}

.behavior__bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
}

.behavior__bar-track {
  width: 100%;
  max-width: 2.25rem;
  height: 92px;
  background: var(--color-surface-raised);
  border-radius: 9999px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
}

.behavior__bar-fill {
  width: 100%;
  background: linear-gradient(180deg, #3b82f6, #1d4ed8);
  border-radius: 9999px;
  min-height: 4px;
  transition: height 0.5s ease;
}

.behavior__bar-lbl {
  font-size: 0.62rem;
  font-weight: 600;
  color: var(--color-text-faint);
}

.behavior__bullets {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.84rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.behavior__bullets li {
  margin-bottom: 0.4rem;
}
.behavior__bullets--tight li {
  margin-bottom: 0.25rem;
}
.behavior__bullets--tight {
  font-size: 0.8rem;
  line-height: 1.45;
}

.behavior__risk-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

.behavior__risk-card {
  padding: 1.1rem;
  border-radius: 0.95rem;
  border: 2px solid transparent;
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}
.behavior__risk-card--high {
  border-color: rgba(220, 38, 38, 0.45);
  background: linear-gradient(160deg, #fff5f5 0%, var(--color-surface) 55%);
}
.behavior__risk-card--medium {
  border-color: rgba(234, 88, 12, 0.4);
  background: linear-gradient(160deg, #fff7ed 0%, var(--color-surface) 55%);
}
.behavior__risk-card--low {
  border-color: var(--color-border);
}

.behavior__risk-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.65rem;
}

.behavior__risk-emoji {
  font-size: 1.25rem;
}

.behavior__risk-meta {
  text-align: right;
}

.behavior__risk-badge {
  display: inline-block;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  margin-bottom: 0.25rem;
}
.behavior__risk-badge--high {
  background: rgba(220, 38, 38, 0.15);
  color: #b91c1c;
}
.behavior__risk-badge--medium {
  background: rgba(234, 88, 12, 0.15);
  color: #c2410c;
}
.behavior__risk-badge--low {
  background: var(--color-surface-raised);
  color: var(--color-text-muted);
}

.behavior__risk-prob {
  display: block;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.behavior__risk-title {
  margin: 0 0 0.4rem;
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.3;
}

.behavior__risk-body {
  margin: 0;
  font-size: 0.78rem;
  line-height: 1.4;
  color: var(--color-text-muted);
}

.behavior__forecast-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 1rem;
}
@media (max-width: 900px) {
  .behavior__forecast-grid {
    grid-template-columns: 1fr;
  }
}

.behavior__forecast-stat .behavior__forecast-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--color-text-faint);
  margin: 0 0 0.5rem;
}

.behavior__forecast-big {
  margin: 0 0 1rem;
  font-size: 1.65rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--color-text);
}

.behavior__forecast-delta {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-muted);
}
.behavior__forecast-delta--up {
  color: #c2410c;
}

.behavior__alerts {
  margin: 0;
  padding-left: 1rem;
  font-size: 0.82rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.behavior__alerts--tight {
  font-size: 0.78rem;
  line-height: 1.4;
}

.behavior__chart-card .behavior__h4 {
  margin-bottom: 0.5rem;
}

.behavior__line-h {
  height: 180px;
  margin-top: 0.35rem;
}
.behavior__line-h--tall {
  height: 220px;
}

.behavior__rec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.behavior__rec-card {
  padding: 0.9rem 1rem;
  border-radius: 0.95rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  box-shadow: var(--shadow-card);
}

.behavior__rec-title {
  margin: 0;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.35;
}

.behavior__rec-detail {
  margin: 0;
  flex: 1;
  font-size: 0.76rem;
  line-height: 1.4;
  color: var(--color-text-muted);
}

.behavior__btn {
  align-self: flex-start;
  margin-top: 0.25rem;
  padding: 0.5rem 0.9rem;
  border-radius: 0.55rem;
  border: 1px solid color-mix(in srgb, var(--color-primary) 35%, var(--color-border));
  background: var(--color-primary-glow);
  color: var(--color-primary-dim);
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
}
.behavior__btn:hover {
  background: color-mix(in srgb, var(--color-primary) 18%, transparent);
  transform: translateY(-1px);
}

.behavior__controls {
  padding: 1.15rem;
  border-radius: 0.95rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface-raised);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.behavior__toggle {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text);
  cursor: pointer;
}
.behavior__toggle input {
  width: 1.05rem;
  height: 1.05rem;
  accent-color: var(--color-primary);
}

.behavior__limits-title {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-faint);
  margin: 0 0 0.5rem;
}

.behavior__limit-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.behavior__limit-name {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--color-text);
}

.behavior__limit-input-wrap {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background: var(--color-surface);
  padding: 0.2rem 0.5rem;
}
.behavior__limit-input-wrap--sm {
  max-width: 6rem;
}

.behavior__limit-prefix {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  font-weight: 600;
}

.behavior__limit-input {
  width: 5rem;
  border: none;
  background: transparent;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text);
  outline: none;
}

.behavior__alert-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.84rem;
  font-weight: 500;
  color: var(--color-text);
}

.behavior__goal-list {
  list-style: none;
  margin: 0 0 1rem;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.behavior__goal-row {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.84rem;
  line-height: 1.5;
  color: var(--color-text-muted);
}

.behavior__goal-icon {
  flex-shrink: 0;
}

.behavior__progress-block {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.behavior__progress-row {
  display: grid;
  grid-template-columns: 8.5rem 1fr 2.5rem;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
@media (max-width: 520px) {
  .behavior__progress-row {
    grid-template-columns: 1fr;
  }
}

.behavior__progress-track {
  height: 8px;
  background: var(--color-surface-raised);
  border-radius: 9999px;
  overflow: hidden;
}

.behavior__progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.6s ease;
}
.behavior__progress-fill--debt {
  background: linear-gradient(90deg, #ef4444, #f97316);
}
.behavior__progress-fill--save {
  background: linear-gradient(90deg, #0d8147, #22c55e);
}
.behavior__progress-fill--inv {
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
}

.behavior__progress-pct {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text);
  text-align: right;
}

.behavior__profile {
  display: flex;
  gap: 1.25rem;
  padding: 1.25rem;
  border-radius: 1rem;
  border: 1px solid color-mix(in srgb, #6d28d9 22%, var(--color-border));
  background: linear-gradient(125deg, color-mix(in srgb, #6d28d9 8%, var(--color-surface)) 0%, var(--color-surface) 55%);
  box-shadow: var(--shadow-card);
}
@media (max-width: 600px) {
  .behavior__profile {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .behavior__profile-cols {
    text-align: left;
  }
}

.behavior__profile-avatar {
  width: 4.5rem;
  height: 4.5rem;
  border-radius: 1.1rem;
  background: var(--color-surface-raised);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  flex-shrink: 0;
  border: 1px solid var(--color-border);
}

.behavior__profile-body {
  min-width: 0;
}

.behavior__profile-id {
  margin: 0;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6d28d9;
}

.behavior__profile-title {
  margin: 0.25rem 0 0.5rem;
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

.behavior__profile-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
}
@media (max-width: 520px) {
  .behavior__profile-cols {
    grid-template-columns: 1fr;
  }
}

.behavior__mini-h {
  margin: 0 0 0.35rem;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-faint);
}

.behavior__mini-list {
  margin: 0;
  padding-left: 1rem;
  font-size: 0.8rem;
  line-height: 1.5;
  color: var(--color-text-muted);
}
</style>
