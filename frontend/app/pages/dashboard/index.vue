<template>
  <div class="dash-page dash-page--cash">
    <header class="dash-hero">
      <p class="dash-hero__eyebrow">
        <span class="dash-hero__eyebrow-dot" aria-hidden="true" />
        Checking &amp; spending
      </p>
      <h1 class="dash-hero__title">
        Good morning<template v-if="displayName">, {{ displayName }}</template>
      </h1>
      <p class="dash-hero__sub">
        <span v-if="today">{{ today }} · </span>
        Checking, spending mix, and recent moves—built to surface patterns before they become problems.
      </p>
    </header>

    <!-- AI status bar -->
    <div class="dash-ai-bar">
      <span v-if="isLoading" class="dash-ai-bar__status dash-ai-bar__status--loading">
        <span class="dash-ai-bar__dot" />
        ARIA is computing your dashboard…
      </span>
      <span v-else-if="!isUsingDummyData && data" class="dash-ai-bar__status dash-ai-bar__status--live">
        <span class="dash-ai-bar__dot dash-ai-bar__dot--live" />
        AI-powered · live calculations
      </span>
      <span v-else-if="isUsingDummyData" class="dash-ai-bar__status dash-ai-bar__status--demo">
        <span class="dash-ai-bar__dot dash-ai-bar__dot--demo" />
        Demo data · start the Python agent for live AI
      </span>
      <button
        class="dash-ai-bar__refresh"
        :disabled="isLoading"
        @click="refreshAI()"
        title="Re-run AI analysis"
      >
        {{ isLoading ? 'Computing…' : '⟳ Refresh AI' }}
      </button>
    </div>

    <p v-if="!data && isLoading" class="dash-page__hint">ARIA is running your financial analysis…</p>
    <p v-else-if="!data && aiError" class="dash-page__hint">
      AI agent unreachable. Start the Python server:
      <code>cd Hackathon &amp;&amp; uvicorn app.main:app --port 8000</code>
    </p>

    <template v-if="data">

      <!-- ── AI Risk chips ──────────────────────────────────────────────────── -->
      <div v-if="data.risks" class="dash-risk-row">
        <div
          v-for="(risk, key) in data.risks"
          :key="key"
          class="dash-risk-chip"
          :class="`dash-risk-chip--${risk.level}`"
          :title="risk.factors?.join(' · ')"
        >
          <span class="dash-risk-icon">{{ risk.level === 'high' ? '🔴' : risk.level === 'moderate' ? '🟡' : '🟢' }}</span>
          <span class="dash-risk-label">{{ risk.label }}</span>
          <span class="dash-risk-prob">{{ Math.round((risk.probability ?? 0) * 100) }}%</span>
        </div>
      </div>

      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Overview</h2>
        </div>
        <p class="dash-section-lead">Balances and income snapshot tied to your profile.</p>
        <div class="dash-grid-4">
          <StatCard
            variant="dash"
            label="Monthly income"
            :value="`$${data.user.monthlyIncome.toLocaleString('en-US')}`"
            sub="Estimated cash inflow"
            icon-bg="var(--color-info-dim)"
            value-color="var(--color-info)"
          >
            <template #icon><span style="font-size:1.1rem">💵</span></template>
          </StatCard>
          <StatCard
            variant="dash"
            label="Checking"
            :value="`$${data.accounts.checking.toLocaleString('en-US', { minimumFractionDigits: 2 })}`"
            sub="Primary spending"
            sub-class="text-warn"
            icon-bg="var(--color-warning-dim)"
            value-color="var(--color-warning)"
          >
            <template #icon><span style="font-size:1.1rem">🏦</span></template>
          </StatCard>
          <StatCard
            variant="dash"
            label="Savings"
            :value="`$${data.accounts.savings.toLocaleString('en-US', { minimumFractionDigits: 2 })}`"
            sub="Buffer & goals"
            icon-bg="var(--color-primary-glow)"
            value-color="var(--color-primary)"
          >
            <template #icon><span style="font-size:1.1rem">🛡️</span></template>
          </StatCard>
          <StatCard
            variant="dash"
            label="Credit score"
            :value="data.accounts.creditScore != null ? `${data.accounts.creditScore}` : '—'"
            sub="From your profile"
            icon-bg="var(--color-surface-raised)"
            value-color="var(--color-text)"
          >
            <template #icon><span style="font-size:1.1rem">⭐</span></template>
          </StatCard>
        </div>
      </section>

      <section class="dash-mb dash-checking-spend" aria-labelledby="checking-spend-heading">
        <div class="dash-section">
          <h2 id="checking-spend-heading" class="dash-section-title">Checking &amp; spending</h2>
        </div>
        <p class="dash-section-lead">Spending mix, behavior snapshot, and recent activity.</p>

        <div class="dash-checking-spend__block">
          <h3 class="dash-subsection">Spending mix</h3>
          <div class="dash-grid-2">
            <div class="dash-card dash-card--chart">
              <h3 class="dash-card__title">Category mix</h3>
              <p class="dash-card__sub">Total tracked: ${{ spendingTotal.toLocaleString('en-US') }}</p>
              <div class="dash-chart-wrap">
                <ClientOnly v-if="spendingChartReady">
                  <DonutChart
                    :labels="data.spending.labels"
                    :amounts="data.spending.amounts"
                    :colors="data.spending.colors"
                  />
                  <template #fallback>
                    <div class="dash-chart-fallback" aria-hidden="true" />
                  </template>
                </ClientOnly>
                <p v-else class="dash-page__hint" style="margin: 0; border: none; background: transparent; padding: 1rem 0">
                  Add transactions or a spending series to see the breakdown.
                </p>
              </div>
            </div>
            <div class="dash-card dash-card--muted">
              <h3 class="dash-card__title">Quick category signal</h3>
              <p class="dash-card__sub">From your current spending mix</p>
              <ul class="dash-insight">
                <li>
                  <strong>{{ topSpendCategory.label }}</strong>
                  leads at
                  <strong>${{ topSpendCategory.amount.toLocaleString('en-US') }}</strong>
                  ({{ topSpendCategory.pct }}% of spend).
                </li>
                <li v-if="data.accounts.checking < spendingTotal">
                  Category totals exceed displayed checking—timing of bills vs. deposits may explain the gap.
                </li>
                <li v-else>
                  Behavior analysis in this same tab feeds your AI advisor context.
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="dash-checking-spend__block dash-checking-spend__block--behavior">
          <h3 class="dash-subsection">Behavior &amp; AI insights</h3>
          <p class="dash-checking-spend__behavior-lead">
            Quick read on habits, risks, and next steps.
          </p>
          <BehaviorInsightsPanel
            :behavior="behaviorPayload"
            @agent-action="onBehaviorAgentAction"
          />
        </div>

      <!-- ── Financial Momentum ─────────────────────────────────────────────── -->
      <div class="dash-checking-spend__block dash-checking-spend__block--momentum">
        <h3 class="dash-subsection">Financial momentum</h3>
        <p class="dash-checking-spend__behavior-lead">AI-computed trends: net gains over time and your debt paydown trajectory.</p>
        <div class="dash-grid-2">
          <!-- Financial Gains -->
          <div class="dash-card dash-card--chart">
            <h3 class="dash-card__title">Net financial gains</h3>
            <p class="dash-card__sub">Monthly cash gain &amp; savings balance (AI)</p>
            <div class="dash-chart-wrap dash-chart-wrap--line" v-if="financialGainsReady">
              <svg class="dash-sparkline" viewBox="0 0 300 80" preserveAspectRatio="none" aria-hidden="true">
                <defs>
                  <linearGradient id="gainGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#22c55e" stop-opacity="0.25" />
                    <stop offset="100%" stop-color="#22c55e" stop-opacity="0" />
                  </linearGradient>
                </defs>
                <polygon
                  v-if="(data as any).financialGains?.datasets?.[0]"
                  :points="svgFillPoints((data as any).financialGains.datasets[0].data, 300, 80)"
                  fill="url(#gainGrad)"
                />
                <polyline
                  v-if="(data as any).financialGains?.datasets?.[0]"
                  :points="svgLinePoints((data as any).financialGains.datasets[0].data, 300, 80)"
                  fill="none" stroke="#22c55e" stroke-width="2" stroke-linejoin="round"
                />
                <polyline
                  v-if="(data as any).financialGains?.datasets?.[1]"
                  :points="svgLinePoints((data as any).financialGains.datasets[1].data, 300, 80)"
                  fill="none" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="4 3" stroke-linejoin="round"
                />
              </svg>
              <div class="dash-sparkline-legend">
                <span v-for="ds in (data as any).financialGains.datasets" :key="ds.label" class="dash-sparkline-legend__item">
                  <span class="dash-sparkline-legend__dot" :style="{ background: ds.color }" />
                  {{ ds.label }}
                </span>
              </div>
              <div class="dash-sparkline-labels">
                <span>{{ (data as any).financialGains.labels[0] }}</span>
                <span>{{ (data as any).financialGains.labels[Math.floor((data as any).financialGains.labels.length / 2)] }}</span>
                <span>{{ (data as any).financialGains.labels[(data as any).financialGains.labels.length - 1] }}</span>
              </div>
            </div>
            <p v-else class="dash-page__hint" style="margin:0;border:none;background:transparent;padding:1rem 0">
              Gain data generated after AI analysis runs.
            </p>
          </div>
          <!-- Debt Timeline -->
          <div class="dash-card dash-card--chart">
            <h3 class="dash-card__title">Debt paydown trajectory</h3>
            <p class="dash-card__sub">AI-projected total balance over time</p>
            <div class="dash-chart-wrap dash-chart-wrap--line" v-if="debtTimelineReady">
              <svg class="dash-sparkline" viewBox="0 0 300 80" preserveAspectRatio="none" aria-hidden="true">
                <defs>
                  <linearGradient id="debtGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#ef4444" stop-opacity="0.2" />
                    <stop offset="100%" stop-color="#ef4444" stop-opacity="0" />
                  </linearGradient>
                </defs>
                <polygon
                  v-if="(data as any).debtTimeline?.datasets?.[0]"
                  :points="svgFillPoints((data as any).debtTimeline.datasets[0].data, 300, 80)"
                  fill="url(#debtGrad)"
                />
                <polyline
                  v-if="(data as any).debtTimeline?.datasets?.[0]"
                  :points="svgLinePoints((data as any).debtTimeline.datasets[0].data, 300, 80)"
                  fill="none" stroke="#ef4444" stroke-width="2" stroke-linejoin="round"
                />
              </svg>
              <div class="dash-sparkline-labels">
                <span>{{ (data as any).debtTimeline.labels[0] }}</span>
                <span>{{ (data as any).debtTimeline.labels[Math.floor((data as any).debtTimeline.labels.length / 2)] }}</span>
                <span>{{ (data as any).debtTimeline.labels[(data as any).debtTimeline.labels.length - 1] }}</span>
              </div>
            </div>
            <p v-else class="dash-page__hint" style="margin:0;border:none;background:transparent;padding:1rem 0">
              Debt timeline generated after AI analysis runs.
            </p>
          </div>
        </div>
      </div>

        <div class="dash-checking-spend__block">
          <h3 class="dash-subsection">Recent activity</h3>
          <p class="dash-checking-spend__behavior-lead" style="margin-top: -0.35rem">
            Latest lines we use to infer rhythm and recurring costs.
          </p>
          <div class="dash-card" style="padding: 0">
            <div class="dash-activity">
              <div
                v-for="tx in data.recentActivity"
                :key="tx.description + tx.date"
                class="dash-activity__row"
              >
                <div>
                  <p class="dash-activity__desc">{{ tx.description }}</p>
                  <p class="dash-activity__meta">{{ tx.date }} · {{ tx.category }}</p>
                </div>
                <p
                  class="dash-activity__amt"
                  :style="{ color: tx.amount > 0 ? 'var(--color-success)' : 'var(--color-text)' }"
                >
                  {{ tx.amount > 0 ? '+' : '' }}${{ Math.abs(tx.amount).toFixed(2) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { defaultBehaviorInsights } from '~/data/behaviorMock'
import type { BehaviorInsightsPayload } from '~/types/behaviorInsights'

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
  ssr: false,
})

const { data, isLoading, isUsingDummyData, aiError, refreshAI } = useFinancialData()
const { user } = useAuth()

const displayName = computed(() => {
  const meta = user.value?.user_metadata as Record<string, unknown> | undefined
  if (meta?.legal_first_name) return String(meta.legal_first_name).trim().split(/\s+/)[0] || ''
  const fullName = meta?.full_name ?? meta?.name
  if (typeof fullName === 'string' && fullName) return fullName.split(' ')[0] || ''
  const email = user.value?.email
  if (email) return email.split('@')[0] || ''
  return ''
})

const today = ref('')
onMounted(() => {
  today.value = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
})

const spendingTotal = computed(
  () => data.value?.spending?.amounts?.reduce((s, a) => s + a, 0) ?? 0,
)

const spendingChartReady = computed(() => {
  const s = data.value?.spending
  return Boolean(s?.labels?.length && s.amounts?.length && spendingTotal.value > 0)
})

const topSpendCategory = computed(() => {
  const d = data.value
  if (!d?.spending?.labels?.length) {
    return { label: '—', amount: 0, pct: 0 }
  }
  let maxI = 0
  let maxAmt = 0
  d.spending.amounts.forEach((amt, i) => {
    if (amt > maxAmt) {
      maxAmt = amt
      maxI = i
    }
  })
  const total = spendingTotal.value || 1
  return {
    label: d.spending.labels[maxI] || 'Other',
    amount: maxAmt,
    pct: Math.round((maxAmt / total) * 100),
  }
})

const financialGainsReady = computed(() => {
  const fg = (data.value as any)?.financialGains
  return Boolean(fg?.labels?.length && fg?.datasets?.[0]?.data?.length > 0)
})

const debtTimelineReady = computed(() => {
  const dt = (data.value as any)?.debtTimeline
  return Boolean(dt?.labels?.length && dt?.datasets?.[0]?.data?.length > 0)
})

function svgLinePoints(values: number[], w: number, h: number): string {
  if (!values?.length) return ''
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const pad = 4
  return values.map((v, i) => {
    const x = (i / (values.length - 1)) * w
    const y = h - pad - ((v - min) / range) * (h - pad * 2)
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
}

function svgFillPoints(values: number[], w: number, h: number): string {
  if (!values?.length) return ''
  const line = svgLinePoints(values, w, h)
  return `0,${h} ${line} ${w},${h}`
}

function isUsableBehavior(b: unknown): b is BehaviorInsightsPayload {
  if (!b || typeof b !== 'object') return false
  const o = b as Record<string, unknown>
  return typeof o.score === 'number' && typeof o.aiSummary === 'string'
}

const behaviorPayload = computed<BehaviorInsightsPayload>(() => {
  const raw = data.value as { behavior?: unknown } | null | undefined
  const b = raw?.behavior
  if (isUsableBehavior(b)) return b
  return defaultBehaviorInsights
})

function onBehaviorAgentAction(payload: { actionId: string; actionLabel: string }) {
  // Wire to FastAPI agent / rules engine (e.g. POST agentBase + /api/agent/actions)
  console.info('[behavior → agent]', payload.actionId, payload.actionLabel)
}

useHead({ title: 'Checking & spending — AI Financial' })
</script>

<style scoped>
.text-warn {
  color: var(--color-warning) !important;
}

/* ── AI status bar ─────────────────────────────────────────────────────────── */
.dash-ai-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  padding: 0.5rem 0.875rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  font-size: 0.8rem;
}

.dash-ai-bar__status {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex: 1;
  color: var(--color-text-muted);
}

.dash-ai-bar__dot {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: var(--color-text-faint);
  flex-shrink: 0;
}

.dash-ai-bar__status--loading .dash-ai-bar__dot {
  background: var(--color-primary);
  animation: ai-pulse 1.2s ease-in-out infinite;
}

.dash-ai-bar__dot--live { background: var(--color-success, #22c55e); }
.dash-ai-bar__dot--demo { background: var(--color-warning, #f59e0b); }

.dash-ai-bar__refresh {
  padding: 0.25rem 0.75rem;
  font-size: 0.775rem;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-primary-glow, rgba(99,102,241,0.08));
  border: 1px solid var(--color-primary-glow, rgba(99,102,241,0.2));
  border-radius: 999px;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}

.dash-ai-bar__refresh:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

@keyframes ai-pulse { 0%, 100% { opacity: 1 } 50% { opacity: 0.3 } }

/* ── AI Risk chips ──────────────────────────────────────────────────────────── */
.dash-risk-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.dash-risk-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-size: 0.775rem;
  font-weight: 600;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  cursor: default;
}

.dash-risk-chip--high {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.dash-risk-chip--moderate {
  background: rgba(245, 158, 11, 0.08);
  border-color: rgba(245, 158, 11, 0.3);
  color: #d97706;
}

.dash-risk-chip--low {
  background: rgba(34, 197, 94, 0.08);
  border-color: rgba(34, 197, 94, 0.25);
  color: #16a34a;
}

.dash-risk-label { font-weight: 600; }
.dash-risk-prob  { opacity: 0.75; font-weight: 500; }

/* ── Sparkline charts ──────────────────────────────────────────────────────── */
.dash-chart-wrap--line {
  padding: 0.5rem 0 0;
}

.dash-sparkline {
  width: 100%;
  height: 80px;
  display: block;
  border-radius: 6px;
  overflow: hidden;
}

.dash-sparkline-legend {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.dash-sparkline-legend__item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.dash-sparkline-legend__dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.dash-sparkline-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--color-text-faint);
  margin-top: 0.3rem;
}
</style>
