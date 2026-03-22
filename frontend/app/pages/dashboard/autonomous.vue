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
      <!-- Next Steps Card -->
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Your Next Steps</h2>
        </div>
        <div class="dash-card dash-card--next-steps">
          <div class="next-steps__list">
            <div
              v-for="(step, idx) in nextSteps"
              :key="idx"
              class="next-steps__item"
              :class="`next-steps__item--priority-${step.priority}`"
            >
              <span class="next-steps__num">{{ idx + 1 }}</span>
              <div class="next-steps__content">
                <p class="next-steps__title">{{ step.title }}</p>
                <p class="next-steps__desc">{{ step.description }}</p>
                <p v-if="step.impact" class="next-steps__impact">{{ step.impact }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

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

        <!-- Interactive Paycheck Slider -->
        <div class="dash-card dash-card--slider" style="margin-top: 1rem">
          <h3 class="dash-card__title">Adjust your allocation</h3>
          <p class="dash-card__sub">Drag sliders to customize. Total must equal 100%.</p>
          <div v-if="splitReady" class="slider-group">
            <div v-for="(label, i) in data.paycheckSplit.labels" :key="label" class="slider-row">
              <div class="slider-row__header">
                <span class="slider-row__label">{{ label }}</span>
                <span class="slider-row__value">${{ allocationValues[i] }}</span>
              </div>
              <input
                v-model.number="userAllocations[i]"
                type="range"
                :min="0"
                :max="100"
                :step="1"
                class="slider-row__input"
                @input="onAllocationChange"
              />
              <div class="slider-row__meta">
                <span class="slider-row__pct">{{ userAllocations[i] }}%</span>
                <span class="slider-row__diff" :class="{ 'slider-row__diff--pos': allocationDiffs[i] > 0, 'slider-row__diff--neg': allocationDiffs[i] < 0 }">
                  {{ allocationDiffs[i] > 0 ? '+' : '' }}{{ allocationDiffs[i] }}%
                </span>
              </div>
            </div>
            <div class="slider-row slider-row__total" :class="{ 'slider-row__total--invalid': totalAllocation !== 100 }">
              <span>Total</span>
              <span>{{ totalAllocation }}%</span>
            </div>
            <p v-if="totalAllocation !== 100" class="slider-row__warning">
              Adjust sliders so total equals 100% (currently {{ totalAllocation }}%)
            </p>
            <button
              v-else
              class="btn btn--primary"
              style="margin-top: 0.75rem; width: 100%"
              @click="saveAllocation"
            >
              Save Allocation Plan
            </button>
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
            <div class="dash-pillar__progress">
              <div class="progress-bar">
                <div
                  class="progress-bar__fill"
                  :class="getProgressClass(emergencyFundProgress)"
                  :style="{ width: `${Math.min(emergencyFundProgress, 100)}%` }"
                />
              </div>
              <p class="progress-bar__label">
                <strong>${{ data.accounts.savings.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</strong>
                of ${{ emergencyFundTarget.toLocaleString('en-US', { minimumFractionDigits: 0 }) }}
                ({{ Math.min(emergencyFundProgress, 100).toFixed(0) }}%)
              </p>
            </div>
            <p class="dash-pillar__meta">
              Target: {{ emergencyFundMonths }} months of expenses
            </p>
          </div>
          <div class="dash-card dash-pillar">
            <span class="dash-pillar__icon" aria-hidden="true">📉</span>
            <h3 class="dash-card__title">Debt payoff</h3>
            <p class="dash-pillar__copy">
              Route extra payments via avalanche (APR) or snowball (balance)—see the
              <NuxtLink to="/dashboard/debt" class="dash-pillar__link">Debt tab</NuxtLink>.
            </p>
            <div class="dash-pillar__progress">
              <div class="progress-bar">
                <div
                  class="progress-bar__fill"
                  :class="getProgressClass(debtPayoffProgress)"
                  :style="{ width: `${debtPayoffProgress}%` }"
                />
              </div>
              <p class="progress-bar__label">
                <strong>${{ totalDebtPaid.toLocaleString('en-US', { minimumFractionDigits: 0 }) }}</strong>
                paid of ${{ totalDebtOriginal.toLocaleString('en-US', { minimumFractionDigits: 0 }) }}
                ({{ debtPayoffProgress.toFixed(0) }}%)
              </p>
            </div>
            <p class="dash-pillar__meta">{{ data.debts.length }} debts on file</p>
          </div>
          <div class="dash-card dash-pillar">
            <span class="dash-pillar__icon" aria-hidden="true">📈</span>
            <h3 class="dash-card__title">Investing</h3>
            <p class="dash-pillar__copy">
              After expensive debt and a starter buffer, consider broad index funds or an employer match. This app is not personalized investment advice.
            </p>
            <div class="dash-pillar__progress">
              <div class="progress-bar">
                <div
                  class="progress-bar__fill"
                  :class="getProgressClass(investingProgress)"
                  :style="{ width: `${investingProgress}%` }"
                />
              </div>
              <p class="progress-bar__label">
                <strong>${{ (data.paycheckSplit.amounts[3] ?? 0).toLocaleString('en-US') }}/mo</strong>
                allocated
              </p>
            </div>
            <p class="dash-pillar__meta">Consult a licensed professional for your situation.</p>
          </div>
        </div>
      </section>

      <!-- Debt Details Section -->
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Your Debts</h2>
        </div>
        <div class="dash-card dash-card--table">
          <div class="table-responsive">
            <table class="dash-table">
              <thead>
                <tr>
                  <th>Debt</th>
                  <th>Type</th>
                  <th>Balance</th>
                  <th>APR</th>
                  <th>Min Payment</th>
                  <th>Payoff Strategy</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="debt in sortedDebts" :key="debt.name">
                  <td><strong>{{ debt.name }}</strong></td>
                  <td>{{ debt.type }}</td>
                  <td class="tabular-num">${{ debt.balance.toLocaleString('en-US', { minimumFractionDigits: 0 }) }}</td>
                  <td :class="getAprClass(debt.rate)">{{ debt.rate.toFixed(2) }}%</td>
                  <td class="tabular-num">${{ debt.min.toLocaleString('en-US', { minimumFractionDigits: 0 }) }}</td>
                  <td>
                    <span v-if="debt.avalancheRank === 1" class="badge badge--priority">
                      Pay first (avalanche)
                    </span>
                    <span v-else-if="debt.snowballRank === 1" class="badge badge--secondary">
                      Pay first (snowball)
                    </span>
                    <span v-else class="badge badge--muted">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="dash-table__footer">
            <p><strong>Total Balance:</strong> ${{ totalDebtOriginal.toLocaleString('en-US', { minimumFractionDigits: 0 }) }}</p>
            <p><strong>Total Min Payments:</strong> ${{ totalMinPayments.toLocaleString('en-US', { minimumFractionDigits: 0 }) }}/mo</p>
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

// Calculate monthly expenses from spending data
const monthlyExpenses = computed(() => {
  if (!data.value?.spending?.amounts) return 0
  return data.value.spending.amounts.reduce((sum, amt) => sum + amt, 0)
})

// Emergency fund calculations (3-6 months target)
const emergencyFundMonths = 4 // Default to 4 months
const emergencyFundTarget = computed(() => monthlyExpenses.value * emergencyFundMonths)
const emergencyFundProgress = computed(() => {
  if (!data.value || emergencyFundTarget.value === 0) return 0
  return (data.value.accounts.savings / emergencyFundTarget.value) * 100
})

// Debt calculations
const totalDebtOriginal = computed(() => {
  if (!data.value?.debts) return 0
  return data.value.debts.reduce((sum, debt) => sum + debt.balance, 0)
})

const totalMinPayments = computed(() => {
  if (!data.value?.debts) return 0
  return data.value.debts.reduce((sum, debt) => sum + debt.min, 0)
})

// Assume 15% of income goes to debt from paycheck split
const totalDebtPaid = computed(() => {
  if (!data.value?.paycheckSplit?.amounts) return 0
  // Find "Debt Payoff" category
  const debtIdx = data.value.paycheckSplit.labels.findIndex(l => l.toLowerCase().includes('debt'))
  if (debtIdx === -1) return 0
  return data.value.paycheckSplit.amounts[debtIdx]
})

const debtPayoffProgress = computed(() => {
  if (totalDebtOriginal.value === 0) return 100
  // This is a simplified estimate - in reality you'd track historical debt
  return Math.min((totalDebtPaid.value / (totalDebtPaid.value + totalDebtOriginal.value)) * 100, 100)
})

// Investing progress (based on allocation vs recommended 15-20% of income)
const investingProgress = computed(() => {
  if (!data.value?.paycheckSplit?.amounts || data.value.user.monthlyIncome === 0) return 0
  const investingIdx = data.value.paycheckSplit.labels.findIndex(l => l.toLowerCase().includes('invest'))
  if (investingIdx === -1) return 0
  const investingAmount = data.value.paycheckSplit.amounts[investingIdx]
  const recommendedInvesting = data.value.user.monthlyIncome * 0.15 // 15% recommended
  return Math.min((investingAmount / recommendedInvesting) * 100, 100)
})

// Sorted debts for display (avalanche = by APR desc, snowball = by balance asc)
const sortedDebts = computed(() => {
  if (!data.value?.debts) return []
  const debtsWithRank = data.value.debts.map((debt, idx) => ({ ...debt, idx }))
  
  // Sort by APR descending for avalanche
  const byApr = [...debtsWithRank].sort((a, b) => b.rate - a.rate)
  byApr.forEach((debt, rank) => { debt.avalancheRank = rank + 1 })
  
  // Sort by balance ascending for snowball
  const byBalance = [...debtsWithRank].sort((a, b) => a.balance - b.balance)
  byBalance.forEach((debt, rank) => { debt.snowballRank = rank + 1 })
  
  // Return sorted by APR (avalanche is mathematically optimal)
  return byApr
})

// Next Steps logic
const nextSteps = computed(() => {
  if (!data.value) return []
  
  const steps: Array<{
    priority: 'high' | 'medium' | 'low'
    title: string
    description: string
    impact?: string
  }> = []
  
  // Step 1: Emergency fund if below $500
  if (data.value.accounts.savings < 500) {
    const needed = 500 - data.value.accounts.savings
    steps.push({
      priority: 'high',
      title: 'Build $500 starter emergency fund',
      description: `You have $${data.value.accounts.savings.toLocaleString('en-US', { minimumFractionDigits: 2 })}, need $${needed.toLocaleString('en-US', { minimumFractionDigits: 0 })} more`,
      impact: 'Protects you from unexpected expenses',
    })
  } else if (emergencyFundProgress.value < 100) {
    const remaining = emergencyFundTarget.value - data.value.accounts.savings
    steps.push({
      priority: 'medium',
      title: 'Continue building emergency fund',
      description: `You have $${data.value.accounts.savings.toLocaleString('en-US', { minimumFractionDigits: 2 })} of $${emergencyFundTarget.value.toLocaleString('en-US', { minimumFractionDigits: 0 })} goal`,
      impact: `${(100 - emergencyFundProgress.value).toFixed(0)}% remaining to reach ${emergencyFundMonths}-month target`,
    })
  }
  
  // Step 2: High-interest debt payoff
  const highInterestDebts = data.value.debts.filter(d => d.rate >= 15)
  if (highInterestDebts.length > 0) {
    const topDebt = highInterestDebts[0]
    const extraPayment = Math.round(data.value.user.monthlyIncome * 0.05) // Suggest 5% extra
    const interestSaved = Math.round(topDebt.balance * (topDebt.rate / 100) * 0.5) // Rough estimate
    const monthsSaved = Math.round(topDebt.balance / (topDebt.min + extraPayment) * 0.3)
    
    steps.push({
      priority: 'high',
      title: `Pay extra toward ${topDebt.name} (${topDebt.rate.toFixed(1)}% APR)`,
      description: `Add $${extraPayment}/mo to your $${topDebt.min} minimum payment`,
      impact: `Save ~$${interestSaved} in interest, pay off ~${monthsSaved} months faster`,
    })
  }
  
  // Step 3: Investing if emergency fund is adequate and no high-interest debt
  if (emergencyFundProgress.value >= 50 && highInterestDebts.length === 0) {
    const investingIdx = data.value.paycheckSplit.labels.findIndex(l => l.toLowerCase().includes('invest'))
    const currentInvesting = investingIdx >= 0 ? data.value.paycheckSplit.amounts[investingIdx] : 0
    const recommendedInvesting = data.value.user.monthlyIncome * 0.15
    
    if (currentInvesting < recommendedInvesting) {
      steps.push({
        priority: 'medium',
        title: 'Increase retirement contributions',
        description: `Currently allocating $${currentInvesting.toLocaleString('en-US')}/mo, consider $${recommendedInvesting.toLocaleString('en-US')}/mo (15%)`,
        impact: 'Long-term wealth building through compound growth',
      })
    }
  }
  
  // Fallback if no specific steps
  if (steps.length === 0) {
    steps.push({
      priority: 'low',
      title: 'You\'re on track!',
      description: 'Keep following your current allocation plan',
      impact: 'Consistency is key to financial health',
    })
  }
  
  return steps
})

// Interactive slider state
const userAllocations = ref<number[]>([])
const allocationValues = ref<number[]>([])
const allocationDiffs = ref<number[]>([])

// Initialize slider values from current allocation
watch(
  () => data.value?.paycheckSplit,
  (split) => {
    if (split?.amounts && split.labels) {
      const total = split.amounts.reduce((sum, amt) => sum + amt, 0)
      userAllocations.value = split.amounts.map(amt => Math.round((amt / total) * 100))
      allocationValues.value = split.amounts.map(amt => amt)
      allocationDiffs.value = split.amounts.map(() => 0)
    }
  },
  { immediate: true }
)

const totalAllocation = computed(() => {
  return userAllocations.value.reduce((sum, pct) => sum + pct, 0)
})

function onAllocationChange() {
  const total = data.value?.paycheckSplit.amounts.reduce((sum, amt) => sum + amt, 0) || 0
  allocationValues.value = userAllocations.value.map(pct => Math.round((pct / 100) * total))
  allocationDiffs.value = userAllocations.value.map((pct, i) => {
    const originalPct = data.value?.paycheckSplit.amounts[i] 
      ? Math.round((data.value.paycheckSplit.amounts[i] / total) * 100)
      : 0
    return pct - originalPct
  })
}

function saveAllocation() {
  // TODO: Save to backend/user preferences
  alert('Allocation plan saved! (Backend integration pending)')
}

// Helper functions
function getProgressClass(progress: number) {
  if (progress >= 80) return 'progress-bar__fill--good'
  if (progress >= 50) return 'progress-bar__fill--warning'
  return 'progress-bar__fill--danger'
}

function getAprClass(rate: number) {
  if (rate >= 20) return 'tabular-num--high'
  if (rate >= 10) return 'tabular-num--warning'
  return 'tabular-num--low'
}

useHead({ title: 'Autonomous finance — AI Financial' })
</script>

<style scoped>
/* Progress Bar Styles */
.progress-bar {
  background: var(--color-bg-subtle, #f1f5f9);
  border-radius: 999px;
  height: 8px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-bar__fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s ease;
}

.progress-bar__fill--good {
  background: linear-gradient(90deg, var(--color-success, #22c55e), #4ade80);
}

.progress-bar__fill--warning {
  background: linear-gradient(90deg, var(--color-warning, #f59e0b), #fbbf24);
}

.progress-bar__fill--danger {
  background: linear-gradient(90deg, var(--color-danger, #ef4444), #f87171);
}

.progress-bar__label {
  font-size: 0.8125rem;
  color: var(--color-text-muted, #64748b);
  margin: 0;
}

/* Next Steps Card */
.dash-card--next-steps {
  border-left: 4px solid var(--color-primary, #3b82f6);
}

.next-steps__list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.next-steps__item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  background: var(--color-bg-subtle, #f8fafc);
  border-left: 3px solid var(--color-muted, #94a3b8);
}

.next-steps__item--priority-high {
  border-left-color: var(--color-danger, #ef4444);
  background: rgba(239, 68, 68, 0.05);
}

.next-steps__item--priority-medium {
  border-left-color: var(--color-warning, #f59e0b);
  background: rgba(245, 158, 11, 0.05);
}

.next-steps__item--priority-low {
  border-left-color: var(--color-success, #22c55e);
  background: rgba(34, 197, 94, 0.05);
}

.next-steps__num {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: var(--color-primary, #3b82f6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
}

.next-steps__content {
  flex: 1;
}

.next-steps__title {
  font-weight: 600;
  font-size: 1rem;
  margin: 0 0 0.25rem 0;
  color: var(--color-text, #0f172a);
}

.next-steps__desc {
  font-size: 0.875rem;
  color: var(--color-text-muted, #64748b);
  margin: 0 0 0.5rem 0;
}

.next-steps__impact {
  font-size: 0.8125rem;
  color: var(--color-primary, #3b82f6);
  font-weight: 500;
  margin: 0;
}

/* Slider Styles */
.slider-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.slider-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.slider-row__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-row__label {
  font-weight: 500;
  font-size: 0.9375rem;
}

.slider-row__value {
  font-weight: 600;
  color: var(--color-primary, #3b82f6);
}

.slider-row__input {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: var(--color-bg-subtle, #e2e8f0);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.slider-row__input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary, #3b82f6);
  cursor: pointer;
  transition: transform 0.1s ease;
}

.slider-row__input::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.slider-row__input::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary, #3b82f6);
  cursor: pointer;
  border: none;
}

.slider-row__meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8125rem;
}

.slider-row__pct {
  font-weight: 600;
  color: var(--color-text, #0f172a);
}

.slider-row__diff {
  color: var(--color-text-muted, #94a3b8);
}

.slider-row__diff--pos {
  color: var(--color-success, #22c55e);
}

.slider-row__diff--neg {
  color: var(--color-danger, #ef4444);
}

.slider-row__total {
  flex-direction: row;
  justify-content: space-between;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border, #e2e8f0);
  font-weight: 700;
  font-size: 1rem;
}

.slider-row__total--invalid {
  color: var(--color-danger, #ef4444);
}

.slider-row__warning {
  font-size: 0.8125rem;
  color: var(--color-danger, #ef4444);
  margin: 0.5rem 0 0 0;
}

/* Table Styles */
.dash-card--table {
  padding: 0;
  overflow: hidden;
}

.table-responsive {
  overflow-x: auto;
}

.dash-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9375rem;
}

.dash-table th {
  background: var(--color-bg-subtle, #f8fafc);
  font-weight: 600;
  text-align: left;
  padding: 0.75rem 1rem;
  border-bottom: 2px solid var(--color-border, #e2e8f0);
  color: var(--color-text, #0f172a);
  white-space: nowrap;
}

.dash-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border, #e2e8f0);
  color: var(--color-text-muted, #475569);
}

.dash-table tbody tr:hover {
  background: var(--color-bg-subtle, #f8fafc);
}

.tabular-num {
  font-family: var(--font-mono, 'SF Mono', Consolas, monospace);
  text-align: right;
}

.tabular-num--high {
  color: var(--color-danger, #ef4444);
  font-weight: 600;
}

.tabular-num--warning {
  color: var(--color-warning, #f59e0b);
  font-weight: 500;
}

.tabular-num--low {
  color: var(--color-success, #22c55e);
  font-weight: 500;
}

.dash-table__footer {
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  background: var(--color-bg-subtle, #f8fafc);
  border-top: 1px solid var(--color-border, #e2e8f0);
  font-size: 0.9375rem;
}

.dash-table__footer p {
  margin: 0;
}

/* Badge Styles */
.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge--priority {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger, #ef4444);
}

.badge--secondary {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-primary, #3b82f6);
}

.badge--muted {
  background: var(--color-bg-subtle, #e2e8f0);
  color: var(--color-text-muted, #94a3b8);
}

/* Button */
.btn {
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.9375rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn--primary {
  background: var(--color-primary, #3b82f6);
  color: white;
}

.btn--primary:hover {
  background: #2563eb;
}
</style>
