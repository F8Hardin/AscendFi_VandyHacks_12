<template>
  <div class="dash-page dash-page--auto">
    <header class="dash-hero">
      <p class="dash-hero__eyebrow">
        <span class="dash-hero__eyebrow-dot" aria-hidden="true" />
        Tab 3 · Automation
      </p>
      <h1 class="dash-hero__title">Autonomous finance</h1>
      <p class="dash-hero__sub">
        A rules-of-thumb split for paychecks, plus guardrails for savings, debt, and investing—adjust with a planner.
      </p>
    </header>

    <p v-if="!data && isLoading" class="dash-page__hint">Loading…</p>
    <p v-else-if="!data && !isUsingDummyData" class="dash-page__hint">
      Connect Supabase or enable demo data to see this tab.
    </p>

    <template v-if="data">
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Paycheck split</h2>
        </div>
        <p class="dash-section-lead">
          Suggested buckets from ${{ data.user.monthlyIncome.toLocaleString('en-US') }}/mo take-home (model output).
        </p>
        <div class="dash-grid-2">
          <div class="dash-card dash-card--chart">
            <h3 class="dash-card__title">Allocation</h3>
            <p class="dash-card__sub">Needs, debt, buffer, growth, and flex</p>
            <div class="dash-chart-wrap">
              <ClientOnly v-if="splitReady">
                <DonutChart
                  :labels="data.paycheckSplit.labels"
                  :amounts="data.paycheckSplit.amounts"
                  :colors="data.paycheckSplit.colors"
                  cutout="60%"
                />
                <template #fallback>
                  <div class="dash-chart-fallback" aria-hidden="true" />
                </template>
              </ClientOnly>
              <p v-else class="dash-page__hint" style="margin: 0; border: none; background: transparent">
                Configure <code>paycheck_split</code> in chart series or use demo data.
              </p>
            </div>
          </div>
          <div class="dash-card dash-card--muted">
            <h3 class="dash-card__title">Bucket detail</h3>
            <p class="dash-card__sub">Amounts per slice</p>
            <ul v-if="splitReady" class="dash-split-legend">
              <li v-for="(label, i) in data.paycheckSplit.labels" :key="label" class="dash-split-legend__row">
                <span
                  class="dash-split-legend__dot"
                  :style="{ background: data.paycheckSplit.colors[i] || 'var(--color-primary)' }"
                />
                <span class="dash-split-legend__label">{{ label }}</span>
                <span class="dash-split-legend__amt">
                  ${{ (data.paycheckSplit.amounts[i] ?? 0).toLocaleString('en-US') }}
                </span>
              </li>
            </ul>
            <p v-else class="dash-page__hint" style="margin-top: 0.5rem; margin-bottom: 0">
              Legend appears when split data exists.
            </p>
          </div>
        </div>
      </section>

      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Save · Pay down · Invest</h2>
        </div>
        <p class="dash-section-lead">Three pillars that usually come after you know your cash-flow baseline.</p>
        <div class="dash-grid-3">
          <div class="dash-card dash-pillar">
            <span class="dash-pillar__icon" aria-hidden="true">🏦</span>
            <h3 class="dash-card__title">Emergency fund</h3>
            <p class="dash-pillar__copy">
              Aim for 3–6 months of must-pay expenses in cash before taking meaningful market risk.
            </p>
            <p class="dash-pillar__meta">
              Savings balance: <strong>${{ data.accounts.savings.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</strong>
            </p>
          </div>
          <div class="dash-card dash-pillar">
            <span class="dash-pillar__icon" aria-hidden="true">📉</span>
            <h3 class="dash-card__title">Debt payoff</h3>
            <p class="dash-pillar__copy">
              Route extra payments via avalanche (APR) or snowball (balance)—see the
              <NuxtLink to="/dashboard/debt" class="dash-pillar__link">Debt tab</NuxtLink>.
            </p>
            <p class="dash-pillar__meta">{{ data.debts.length }} debts on file</p>
          </div>
          <div class="dash-card dash-pillar">
            <span class="dash-pillar__icon" aria-hidden="true">📈</span>
            <h3 class="dash-card__title">Investing</h3>
            <p class="dash-pillar__copy">
              After expensive debt and a starter buffer, consider broad index funds or an employer match. This app is not personalized investment advice.
            </p>
            <p class="dash-pillar__meta">Consult a licensed professional for your situation.</p>
          </div>
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

const splitReady = computed(() => {
  const p = data.value?.paycheckSplit
  return Boolean(p?.labels?.length && p.amounts?.length && p.labels.length === p.amounts.length)
})

useHead({ title: 'Autonomous finance — AI Financial' })
</script>
