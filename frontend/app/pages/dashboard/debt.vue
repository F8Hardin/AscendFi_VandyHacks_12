<template>
  <div class="dash-page dash-page--debt">
    <header class="dash-hero">
      <p class="dash-hero__eyebrow">
        <span class="dash-hero__eyebrow-dot" aria-hidden="true" />
        Tab 2 · Risk &amp; debt
      </p>
      <h1 class="dash-hero__title">Debt &amp; predictions</h1>
      <p class="dash-hero__sub">
        Stress tests and payoff curves—not advice. Use them to decide where extra dollars go first.
      </p>
    </header>

    <p v-if="!data && isLoading" class="dash-page__hint">Loading…</p>
    <p v-else-if="!data && !isUsingDummyData" class="dash-page__hint">
      Connect Supabase or enable demo data to see this tab.
    </p>

    <template v-if="data">
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Predictive signals</h2>
        </div>
        <p class="dash-section-lead">
          Probability-style gauges for overdraft, missed payments, and credit pressure. Outcomes are not guaranteed.
        </p>
        <div class="dash-grid-3">
          <RiskGauge
            :probability="data.risks.overdraft.probability"
            :level="data.risks.overdraft.level"
            :label="data.risks.overdraft.label"
          />
          <RiskGauge
            :probability="data.risks.missingPayments.probability"
            :level="data.risks.missingPayments.level"
            :label="data.risks.missingPayments.label"
          />
          <RiskGauge
            :probability="data.risks.creditShift.probability"
            :level="data.risks.creditShift.level"
            :label="data.risks.creditShift.label"
          />
        </div>
      </section>

      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Optimization</h2>
        </div>
        <p class="dash-section-lead">Projected balance decline vs. who you owe today.</p>
        <div class="dash-grid-2">
          <div class="dash-card dash-card--chart">
            <h3 class="dash-card__title">Payoff projection</h3>
            <p class="dash-card__sub">Illustrative path on an accelerated plan (demo uses ~12 months).</p>
            <ClientOnly v-if="debtTimelineReady">
              <div class="dash-chart-block">
                <LineChart
                  :labels="data.debtTimeline.labels"
                  :datasets="debtTimelineDatasets"
                  y-prefix="$"
                />
              </div>
              <template #fallback>
                <div class="dash-chart-fallback dash-chart-fallback--line" aria-hidden="true" />
              </template>
            </ClientOnly>
            <p v-else class="dash-page__hint" style="margin-top: 1rem; margin-bottom: 0">
              Add a <code>debt_timeline</code> series in Supabase or use demo data.
            </p>
          </div>
          <div class="dash-card dash-card--muted">
            <h3 class="dash-card__title">Active debts</h3>
            <p class="dash-card__sub">{{ data.debts.length }} accounts · ${{ totalDebt.toLocaleString('en-US') }} total</p>
            <div class="dash-debt-list">
              <div v-for="debt in data.debts" :key="debt.name" class="dash-debt-row">
                <div>
                  <p class="dash-debt-row__name">{{ debt.name }}</p>
                  <p class="dash-debt-row__type">{{ debt.type }} · {{ debt.rate }}% APR</p>
                </div>
                <div>
                  <p class="dash-debt-row__bal">${{ debt.balance.toLocaleString('en-US') }}</p>
                  <p class="dash-debt-row__min">min ${{ debt.min }}/mo</p>
                </div>
                <div class="dash-debt-row__bar">
                  <div
                    class="dash-debt-row__bar-fill"
                    :style="{ width: `${totalDebt ? (debt.balance / totalDebt) * 100 : 0}%`, background: debtColor(debt.type) }"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Financial trajectory</h2>
        </div>
        <p class="dash-section-lead">Net monthly movement vs. savings balance (when series exist).</p>
        <div class="dash-card">
          <div class="dash-gains-head">
            <div>
              <h3 class="dash-card__title" style="margin-bottom: 0.15rem">Net &amp; savings</h3>
              <p class="dash-card__sub" style="margin-bottom: 0">Last point on the net series</p>
            </div>
            <div class="dash-gains-stat">
              <span class="dash-gains-stat__label">Latest net</span>
              <span class="dash-gains-stat__value">{{ lastNetFormatted }}</span>
            </div>
          </div>
          <ClientOnly v-if="financialGainsReady">
            <div class="dash-chart-block dash-chart-block--tall">
              <LineChart
                :labels="data.financialGains.labels"
                :datasets="financialGainsDatasets"
                y-prefix="$"
                :show-legend="true"
                :show-zero-line="true"
              />
            </div>
            <template #fallback>
              <div class="dash-chart-fallback dash-chart-fallback--line-tall" aria-hidden="true" />
            </template>
          </ClientOnly>
          <p v-else class="dash-page__hint" style="margin: 1rem 0 0">
            Seed <code>financial_gains</code> in <code>financial_chart_series</code> or enable demo data.
          </p>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
  ssr: false,
})

const { data, isLoading, isUsingDummyData } = useFinancialData()

const totalDebt = computed(() => data.value?.debts.reduce((s, d) => s + d.balance, 0) ?? 0)

type LineDs = { label: string; data: number[]; color: string; fill?: boolean; dashed?: boolean }

function normalizeLineDatasets(raw: unknown): LineDs[] {
  if (!Array.isArray(raw)) return []
  return raw
    .map((x) => {
      const o = x as Record<string, unknown>
      const label = typeof o.label === 'string' ? o.label : 'Series'
      const dataArr = Array.isArray(o.data) ? o.data.map((n) => Number(n)) : []
      const color = typeof o.color === 'string' ? o.color : '#64748b'
      return {
        label,
        data: dataArr,
        color,
        fill: o.fill !== false,
        dashed: Boolean(o.dashed),
      }
    })
    .filter((ds) => ds.data.length > 0)
}

const debtTimelineReady = computed(() => {
  const d = data.value?.debtTimeline
  return Boolean(d?.labels?.length && normalizeLineDatasets(d.datasets).length)
})

const debtTimelineDatasets = computed(() =>
  normalizeLineDatasets(data.value?.debtTimeline?.datasets),
)

const financialGainsReady = computed(() => {
  const d = data.value?.financialGains
  return Boolean(d?.labels?.length && normalizeLineDatasets(d.datasets).length)
})

const financialGainsDatasets = computed(() =>
  normalizeLineDatasets(data.value?.financialGains?.datasets),
)

const lastNetGain = computed(() => {
  const list = financialGainsDatasets.value
  const net =
    list.find((d) => /net/i.test(d.label)) ??
    list.find((d) => !/savings/i.test(d.label)) ??
    list[0]
  if (!net?.data?.length) return null
  return net.data[net.data.length - 1]
})

const lastNetFormatted = computed(() => {
  const v = lastNetGain.value
  if (v == null) return '—'
  const sign = v < 0 ? '−' : '+'
  return `${sign}$${Math.abs(v).toLocaleString('en-US')}`
})

function debtColor(type: string) {
  const map: Record<string, string> = {
    'Credit Card': '#ef4444',
    Auto: '#3b82f6',
    Medical: '#f59e0b',
  }
  return map[type] ?? '#6b7280'
}

useHead({ title: 'Debt & predictions — AI Financial' })
</script>
