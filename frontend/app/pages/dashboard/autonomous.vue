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
            <button class="btn btn--secondary btn--sm" style="margin-top: 0.75rem; width: 100%" @click="showEmergencyPlanner = !showEmergencyPlanner">
              {{ showEmergencyPlanner ? 'Hide' : 'View' }} Projection Plan
            </button>
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
            <button class="btn btn--secondary btn--sm" style="margin-top: 0.75rem; width: 100%" @click="showDebtPlanner = !showDebtPlanner">
              {{ showDebtPlanner ? 'Hide' : 'View' }} Payoff Simulator
            </button>
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
            <button class="btn btn--secondary btn--sm" style="margin-top: 0.75rem; width: 100%" @click="showInvestmentPlanner = !showInvestmentPlanner">
              {{ showInvestmentPlanner ? 'Hide' : 'View' }} Market Simulator
            </button>
          </div>
        </div>
      </section>

      <!-- Emergency Fund Planner -->
      <section v-if="showEmergencyPlanner" class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Emergency Fund Projection</h2>
        </div>
        <div class="dash-card dash-card--planner">
          <div class="planner-grid">
            <div class="planner-inputs">
              <h3 class="planner-title">Adjust Your Savings Rate</h3>
              <div class="input-group">
                <label class="input-label">Monthly contribution</label>
                <div class="input-with-prefix">
                  <span class="input-prefix">$</span>
                  <input
                    v-model.number="emergencyMonthlyContribution"
                    type="number"
                    class="form-input"
                    min="0"
                    step="50"
                  />
                </div>
              </div>
              <div class="input-group">
                <label class="input-label">Current savings</label>
                <div class="input-with-prefix">
                  <span class="input-prefix">$</span>
                  <input
                    v-model.number="emergencyCurrentSavings"
                    type="number"
                    class="form-input"
                    min="0"
                    step="100"
                  />
                </div>
              </div>
              <div class="input-group">
                <label class="input-label">Target months</label>
                <select v-model="emergencyTargetMonths" class="form-select">
                  <option :value="3">3 months</option>
                  <option :value="4">4 months</option>
                  <option :value="6">6 months</option>
                  <option :value="12">12 months</option>
                </select>
              </div>
            </div>
            <div class="planner-results">
              <h3 class="planner-title">Your Timeline</h3>
              <div class="result-cards">
                <div class="result-card">
                  <span class="result-label">Time to goal</span>
                  <span class="result-value" :class="emergencyMonthsToGoal > 24 ? 'result-value--warning' : 'result-value--success'">
                    {{ emergencyMonthsToGoal }} months
                  </span>
                </div>
                <div class="result-card">
                  <span class="result-label">Target amount</span>
                  <span class="result-value">${{ emergencyFundTargetFormatted }}</span>
                </div>
                <div class="result-card">
                  <span class="result-label">Interest earned (HYSA)</span>
                  <span class="result-value result-value--success">+${{ emergencyInterestEarned }}</span>
                </div>
              </div>
              <div class="milestone-timeline">
                <div
                  v-for="(milestone, idx) in emergencyMilestones"
                  :key="idx"
                  class="milestone-item"
                  :class="{ 'milestone-item--achieved': milestone.achieved }"
                >
                  <span class="milestone-dot" :class="{ 'milestone-dot--achieved': milestone.achieved }" />
                  <div class="milestone-content">
                    <span class="milestone-label">{{ milestone.label }}</span>
                    <span class="milestone-date">{{ milestone.date }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Debt Payoff Simulator -->
      <section v-if="showDebtPlanner" class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Debt Payoff Simulator</h2>
        </div>
        <div class="dash-card dash-card--planner">
          <div class="planner-grid">
            <div class="planner-inputs">
              <h3 class="planner-title">Extra Payment Strategy</h3>
              <div class="input-group">
                <label class="input-label">Extra monthly payment</label>
                <div class="input-with-prefix">
                  <span class="input-prefix">$</span>
                  <input
                    v-model.number="debtExtraPayment"
                    type="number"
                    class="form-input"
                    min="0"
                    step="25"
                  />
                </div>
              </div>
              <div class="input-group">
                <label class="input-label">Payoff method</label>
                <select v-model="debtMethod" class="form-select">
                  <option value="avalanche">Avalanche (highest APR first)</option>
                  <option value="snowball">Snowball (lowest balance first)</option>
                </select>
              </div>
              <div class="strategy-info">
                <p v-if="debtMethod === 'avalanche'" class="info-text info-text--primary">
                  💡 Avalanche saves more money on interest over time
                </p>
                <p v-else class="info-text info-text--secondary">
                  🎯 Snowball provides quick wins for motivation
                </p>
              </div>
            </div>
            <div class="planner-results">
              <h3 class="planner-title">Payoff Projection</h3>
              <div class="result-cards">
                <div class="result-card">
                  <span class="result-label">Debt-free date</span>
                  <span class="result-value">{{ debtFreeDate }}</span>
                </div>
                <div class="result-card">
                  <span class="result-label">Total interest paid</span>
                  <span class="result-value" :class="debtInterestSaved > 0 ? 'result-value--success' : ''">
                    ${{ totalDebtInterestWithStrategy.toLocaleString() }}
                  </span>
                </div>
                <div class="result-card">
                  <span class="result-label">Interest saved</span>
                  <span class="result-value result-value--success">+${{ debtInterestSaved.toLocaleString() }}</span>
                </div>
              </div>
              <div class="debt-breakdown">
                <h4 class="breakdown-title">Payoff Order ({{ debtMethod }})</h4>
                <div class="debt-list">
                  <div
                    v-for="(debt, idx) in simulatedDebtPayoff"
                    :key="debt.name"
                    class="debt-item"
                  >
                    <span class="debt-rank">#{{ idx + 1 }}</span>
                    <div class="debt-info">
                      <span class="debt-name">{{ debt.name }}</span>
                      <span class="debt-details">{{ debt.rate.toFixed(1) }}% APR · ${{ debt.balance.toLocaleString() }}</span>
                    </div>
                    <span class="debt-months">{{ debt.monthsToPayoff }} mo</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Investment Market Simulator -->
      <section v-if="showInvestmentPlanner" class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Investment Growth Simulator</h2>
        </div>
        <div class="dash-card dash-card--planner">
          <div class="planner-grid planner-grid--wide">
            <div class="planner-inputs">
              <h3 class="planner-title">Investment Parameters</h3>
              <div class="input-group">
                <label class="input-label">Monthly contribution</label>
                <div class="input-with-prefix">
                  <span class="input-prefix">$</span>
                  <input
                    v-model.number="investMonthlyContribution"
                    type="number"
                    class="form-input"
                    min="0"
                    step="50"
                  />
                </div>
              </div>
              <div class="input-group">
                <label class="input-label">Current portfolio</label>
                <div class="input-with-prefix">
                  <span class="input-prefix">$</span>
                  <input
                    v-model.number="investCurrentPortfolio"
                    type="number"
                    class="form-input"
                    min="0"
                    step="100"
                  />
                </div>
              </div>
              <div class="input-group">
                <label class="input-label">Investment horizon</label>
                <select v-model="investYears" class="form-select">
                  <option :value="5">5 years</option>
                  <option :value="10">10 years</option>
                  <option :value="20">20 years</option>
                  <option :value="30">30 years</option>
                </select>
              </div>
              <div class="input-group">
                <label class="input-label">Market scenario</label>
                <select v-model="investScenario" class="form-select" @change="updateInvestmentAllocation">
                  <option value="conservative">Conservative (4-6% avg)</option>
                  <option value="moderate">Moderate (7-9% avg)</option>
                  <option value="aggressive">Aggressive (10-12% avg)</option>
                </select>
              </div>
              <div class="scenario-details">
                <p class="scenario-label">Selected scenario breakdown:</p>
                <div class="scenario-stats">
                  <span class="stat-item">
                    <span class="stat-label">Expected</span>
                    <span class="stat-value">{{ scenarioStats.expected }}%</span>
                  </span>
                  <span class="stat-item">
                    <span class="stat-label">Best case</span>
                    <span class="stat-value stat-value--positive">+{{ scenarioStats.best }}%</span>
                  </span>
                  <span class="stat-item">
                    <span class="stat-label">Worst case</span>
                    <span class="stat-value stat-value--negative">{{ scenarioStats.worst }}%</span>
                  </span>
                </div>
              </div>
            </div>
            <div class="planner-results">
              <h3 class="planner-title">Projected Growth</h3>
              <div class="result-cards result-cards--horizontal">
                <div class="result-card result-card--highlight">
                  <span class="result-label">Future value (avg)</span>
                  <span class="result-value result-value--large">${{ projectedFutureValue.toLocaleString() }}</span>
                  <span class="result-sub">+${{ projectedGains.toLocaleString() }} gains</span>
                </div>
                <div class="result-card">
                  <span class="result-label">Best case</span>
                  <span class="result-value result-value--positive">${{ projectedBestCase.toLocaleString() }}</span>
                </div>
                <div class="result-card">
                  <span class="result-label">Worst case</span>
                  <span class="result-value result-value--negative">${{ projectedWorstCase.toLocaleString() }}</span>
                </div>
              </div>
              <div class="growth-breakdown">
                <h4 class="breakdown-title">Growth Projection by Year</h4>
                <div class="growth-chart">
                  <div
                    v-for="(year, idx) in growthProjection"
                    :key="year.year"
                    class="growth-bar"
                    :style="{ '--growth-pct': Math.min((year.value / growthProjection[growthProjection.length - 1].value) * 100, 100) }"
                  >
                    <span class="growth-year">{{ year.year }}y</span>
                    <div class="growth-bar-fill" />
                    <span class="growth-value">${{ (year.value / 1000).toFixed(0) }}k</span>
                  </div>
                </div>
              </div>
              <div class="investment-mix">
                <h4 class="breakdown-title">Suggested Asset Allocation</h4>
                <div class="allocation-pie">
                  <div class="allocation-segment" :style="{ width: `${assetAllocation.stocks}%`, background: 'var(--color-primary)' }">
                    <span>Stocks {{ assetAllocation.stocks }}%</span>
                  </div>
                  <div class="allocation-segment" :style="{ width: `${assetAllocation.bonds}%`, background: '#f59e0b' }">
                    <span>Bonds {{ assetAllocation.bonds }}%</span>
                  </div>
                  <div class="allocation-segment" :style="{ width: `${assetAllocation.cash}%`, background: '#22c55e' }">
                    <span>Cash {{ assetAllocation.cash }}%</span>
                  </div>
                </div>
                <p class="allocation-note">Based on {{ investScenario }} scenario and {{ investYears }}-year horizon</p>
              </div>
            </div>
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

// Planner visibility state
const showEmergencyPlanner = ref(false)
const showDebtPlanner = ref(false)
const showInvestmentPlanner = ref(false)

// Emergency Fund Planner state
const emergencyMonthlyContribution = ref(500)
const emergencyCurrentSavings = ref(0)
const emergencyTargetMonths = ref(6)

// Debt Payoff Simulator state
const debtExtraPayment = ref(200)
const debtMethod = ref<'avalanche' | 'snowball'>('avalanche')

// Investment Simulator state
const investMonthlyContribution = ref(500)
const investCurrentPortfolio = ref(0)
const investYears = ref(30)
const investScenario = ref<'conservative' | 'moderate' | 'aggressive'>('moderate')
const assetAllocation = ref({ stocks: 70, bonds: 25, cash: 5 })

// Investment scenario definitions
const investmentScenarios = {
  conservative: { expected: 5, best: 6, worst: 4 },
  moderate: { expected: 8, best: 9, worst: 7 },
  aggressive: { expected: 11, best: 12, worst: 10 },
}

// Initialize slider values from current allocation
watch(
  () => data.value?.paycheckSplit,
  (split) => {
    if (split?.amounts && split.labels) {
      const total = split.amounts.reduce((sum, amt) => sum + amt, 0)
      userAllocations.value = split.amounts.map(amt => Math.round((amt / total) * 100))
      allocationValues.value = split.amounts.map(amt => amt)
      allocationDiffs.value = split.amounts.map(() => 0)
      
      // Initialize planner values from data
      const savingsIdx = split.labels.findIndex(l => l.toLowerCase().includes('save') || l.toLowerCase().includes('emergency'))
      if (savingsIdx !== -1) {
        emergencyMonthlyContribution.value = split.amounts[savingsIdx]
        emergencyCurrentSavings.value = data.value?.accounts.savings || 0
      }
      
      const investingIdx = split.labels.findIndex(l => l.toLowerCase().includes('invest'))
      if (investingIdx !== -1) {
        investMonthlyContribution.value = split.amounts[investingIdx]
      }
    }
  },
  { immediate: true }
)

// Emergency Fund Planner computed properties
const emergencyFundTargetFormatted = computed(() => {
  const target = monthlyExpenses.value * emergencyTargetMonths.value
  return target.toLocaleString('en-US', { maximumFractionDigits: 0 })
})

const emergencyMonthsToGoal = computed(() => {
  const target = monthlyExpenses.value * emergencyTargetMonths.value
  const remaining = target - emergencyCurrentSavings.value
  if (remaining <= 0) return 0
  if (emergencyMonthlyContribution.value <= 0) return Infinity
  // Account for 4.5% APY from HYSA (compounded monthly)
  const monthlyRate = 0.045 / 12
  let months = 0
  let balance = emergencyCurrentSavings.value
  while (balance < target && months < 600) {
    balance = balance * (1 + monthlyRate) + emergencyMonthlyContribution.value
    months++
  }
  return months
})

const emergencyInterestEarned = computed(() => {
  const target = monthlyExpenses.value * emergencyTargetMonths.value
  const months = emergencyMonthsToGoal.value
  if (months <= 0 || months === Infinity) return '0'
  const monthlyRate = 0.045 / 12
  let balance = emergencyCurrentSavings.value
  let totalContributed = 0
  for (let i = 0; i < months; i++) {
    const interest = balance * monthlyRate
    balance += interest + emergencyMonthlyContribution.value
    totalContributed += emergencyMonthlyContribution.value
  }
  const interestEarned = balance - emergencyCurrentSavings.value - totalContributed
  return Math.round(interestEarned).toLocaleString()
})

const emergencyMilestones = computed(() => {
  const target = monthlyExpenses.value * emergencyTargetMonths.value
  const milestones = [
    { pct: 0.25, label: '25% of goal' },
    { pct: 0.5, label: '50% of goal' },
    { pct: 0.75, label: '75% of goal' },
    { pct: 1, label: 'Fully funded!' },
  ]
  
  const monthlyRate = 0.045 / 12
  let balance = emergencyCurrentSavings.value
  let month = 0
  
  return milestones.map(m => {
    const milestoneAmount = target * m.pct
    let achievedDate = 'Already achieved!'
    let achieved = balance >= milestoneAmount
    
    if (!achieved && emergencyMonthlyContribution.value > 0) {
      while (balance < milestoneAmount && month < 600) {
        balance = balance * (1 + monthlyRate) + emergencyMonthlyContribution.value
        month++
      }
      const futureDate = new Date()
      futureDate.setMonth(futureDate.getMonth() + month)
      achievedDate = futureDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    }
    
    return {
      label: m.label,
      date: achievedDate,
      achieved,
    }
  })
})

// Debt Payoff Simulator computed properties
const simulatedDebtPayoff = computed(() => {
  if (!data.value?.debts || data.value.debts.length === 0) return []
  
  const debts = data.value.debts.map(d => ({
    ...d,
    remainingBalance: d.balance,
    monthsToPayoff: 0,
  }))
  
  // Sort based on method
  if (debtMethod.value === 'avalanche') {
    debts.sort((a, b) => b.rate - a.rate)
  } else {
    debts.sort((a, b) => a.remainingBalance - b.remainingBalance)
  }
  
  let extraPayment = debtExtraPayment.value
  const monthlyRate = 0.05 / 12 // Average rate for simulation
  
  // Simulate payoff
  debts.forEach((debt, idx) => {
    let balance = debt.remainingBalance
    let months = 0
    const minPayment = debt.min
    const totalPayment = minPayment + (idx === 0 ? extraPayment : 0)
    
    while (balance > 0 && months < 360) {
      const interest = balance * (debt.rate / 100 / 12)
      const principal = Math.min(totalPayment - interest, balance)
      balance -= principal
      balance += interest
      months++
    }
    debt.monthsToPayoff = months
  })
  
  return debts
})

const debtFreeDate = computed(() => {
  if (simulatedDebtPayoff.value.length === 0) return 'N/A'
  const maxMonths = Math.max(...simulatedDebtPayoff.value.map(d => d.monthsToPayoff))
  if (maxMonths === 0) return 'Already debt-free!'
  const futureDate = new Date()
  futureDate.setMonth(futureDate.getMonth() + maxMonths)
  return futureDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const totalDebtInterestWithStrategy = computed(() => {
  let totalInterest = 0
  simulatedDebtPayoff.value.forEach(debt => {
    const monthlyRate = debt.rate / 100 / 12
    let balance = debt.balance
    const payment = debt.min + (simulatedDebtPayoff.value.indexOf(debt) === 0 ? debtExtraPayment.value : 0)
    
    for (let i = 0; i < debt.monthsToPayoff && balance > 0; i++) {
      const interest = balance * monthlyRate
      totalInterest += interest
      balance = balance - payment + interest
    }
  })
  return Math.round(totalInterest)
})

const debtInterestSaved = computed(() => {
  // Calculate interest without extra payments
  let baselineInterest = 0
  let strategyInterest = totalDebtInterestWithStrategy.value
  
  data.value?.debts.forEach(debt => {
    const monthlyRate = debt.rate / 100 / 12
    let balance = debt.balance
    let months = 0
    
    // Baseline: minimum payments only
    while (balance > 0 && months < 600) {
      const interest = balance * monthlyRate
      baselineInterest += interest
      balance = balance - debt.min + interest
      months++
    }
  })
  
  return Math.round(baselineInterest - strategyInterest)
})

// Investment Simulator computed properties
const scenarioStats = computed(() => {
  return investmentScenarios[investScenario.value]
})

const projectedFutureValue = computed(() => {
  const rate = investmentScenarios[investScenario.value].expected / 100 / 12
  const months = investYears.value * 12
  let fv = investCurrentPortfolio.value
  
  for (let i = 0; i < months; i++) {
    fv = fv * (1 + rate) + investMonthlyContribution.value
  }
  
  return Math.round(fv)
})

const projectedGains = computed(() => {
  const totalContributed = investCurrentPortfolio.value + (investMonthlyContribution.value * investYears.value * 12)
  return projectedFutureValue.value - totalContributed
})

const projectedBestCase = computed(() => {
  const rate = investmentScenarios[investScenario.value].best / 100 / 12
  const months = investYears.value * 12
  let fv = investCurrentPortfolio.value
  
  for (let i = 0; i < months; i++) {
    fv = fv * (1 + rate) + investMonthlyContribution.value
  }
  
  return Math.round(fv)
})

const projectedWorstCase = computed(() => {
  const rate = investmentScenarios[investScenario.value].worst / 100 / 12
  const months = investYears.value * 12
  let fv = investCurrentPortfolio.value
  
  for (let i = 0; i < months; i++) {
    fv = fv * (1 + rate) + investMonthlyContribution.value
  }
  
  return Math.round(fv)
})

const growthProjection = computed(() => {
  const rate = investmentScenarios[investScenario.value].expected / 100 / 12
  const months = investYears.value * 12
  let fv = investCurrentPortfolio.value
  const projections = []
  
  for (let year = 1; year <= investYears.value; year++) {
    for (let m = 0; m < 12; m++) {
      fv = fv * (1 + rate) + investMonthlyContribution.value
    }
    projections.push({
      year,
      value: Math.round(fv),
    })
  }
  
  return projections
})

function updateInvestmentAllocation() {
  const scenario = investScenario.value
  const years = investYears.value
  
  // Adjust allocation based on scenario and time horizon
  if (scenario === 'conservative') {
    assetAllocation.value = { stocks: 40, bonds: 45, cash: 15 }
  } else if (scenario === 'moderate') {
    if (years >= 20) {
      assetAllocation.value = { stocks: 70, bonds: 25, cash: 5 }
    } else if (years >= 10) {
      assetAllocation.value = { stocks: 60, bonds: 35, cash: 5 }
    } else {
      assetAllocation.value = { stocks: 50, bonds: 40, cash: 10 }
    }
  } else if (scenario === 'aggressive') {
    if (years >= 20) {
      assetAllocation.value = { stocks: 90, bonds: 8, cash: 2 }
    } else {
      assetAllocation.value = { stocks: 80, bonds: 15, cash: 5 }
    }
  }
}

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

/* Secondary button */
.btn--secondary {
  background: var(--color-bg-subtle, #e2e8f0);
  color: var(--color-text, #0f172a);
}

.btn--secondary:hover {
  background: #cbd5e1;
}

.btn--sm {
  padding: 0.5rem 0.875rem;
  font-size: 0.8125rem;
}

/* Planner Card Styles */
.dash-card--planner {
  background: linear-gradient(135deg, var(--color-bg, #ffffff) 0%, var(--color-bg-subtle, #f8fafc) 100%);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 1rem;
  padding: 1.5rem;
}

.planner-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.planner-grid--wide {
  grid-template-columns: 1fr 1.5fr;
}

@media (max-width: 900px) {
  .planner-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

.planner-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  margin: 0 0 1rem 0;
}

/* Planner Inputs */
.planner-inputs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-right: 1rem;
  border-right: 1px solid var(--color-border, #e2e8f0);
}

@media (max-width: 900px) {
  .planner-inputs {
    border-right: none;
    border-bottom: 1px solid var(--color-border, #e2e8f0);
    padding-right: 0;
    padding-bottom: 1rem;
  }
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.input-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted, #64748b);
}

.input-with-prefix {
  display: flex;
  align-items: center;
  background: var(--color-bg, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 0.5rem;
  padding: 0 0.75rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-with-prefix:focus-within {
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-prefix {
  color: var(--color-text-muted, #94a3b8);
  font-weight: 500;
  margin-right: 0.25rem;
}

.form-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 0.625rem 0;
  font-size: 0.9375rem;
  color: var(--color-text, #0f172a);
  outline: none;
}

.form-input[type="number"]::-webkit-inner-spin-button,
.form-input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-select {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 0.5rem;
  background: var(--color-bg, #ffffff);
  font-size: 0.9375rem;
  color: var(--color-text, #0f172a);
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-select:focus {
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.strategy-info {
  margin-top: 0.5rem;
}

.info-text {
  font-size: 0.8125rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  margin: 0;
}

.info-text--primary {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-primary, #3b82f6);
}

.info-text--secondary {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning, #f59e0b);
}

/* Scenario Details */
.scenario-details {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: var(--color-bg-subtle, #f1f5f9);
  border-radius: 0.5rem;
}

.scenario-label {
  font-size: 0.75rem;
  color: var(--color-text-muted, #64748b);
  margin: 0 0 0.5rem 0;
}

.scenario-stats {
  display: flex;
  gap: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.stat-label {
  font-size: 0.6875rem;
  color: var(--color-text-muted, #94a3b8);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.stat-value {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
}

.stat-value--positive {
  color: var(--color-success, #22c55e);
}

.stat-value--negative {
  color: var(--color-danger, #ef4444);
}

/* Planner Results */
.planner-results {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.result-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.result-cards--horizontal {
  grid-template-columns: 1.5fr 1fr 1fr;
}

@media (max-width: 700px) {
  .result-cards,
  .result-cards--horizontal {
    grid-template-columns: 1fr;
  }
}

.result-card {
  padding: 1rem;
  background: var(--color-bg-subtle, #f8fafc);
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.result-card--highlight {
  background: linear-gradient(135deg, var(--color-primary, #3b82f6) 0%, #2563eb 100%);
  color: white;
}

.result-label {
  font-size: 0.75rem;
  color: var(--color-text-muted, #64748b);
  font-weight: 500;
}

.result-card--highlight .result-label {
  color: rgba(255, 255, 255, 0.8);
}

.result-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text, #0f172a);
}

.result-value--large {
  font-size: 1.5rem;
}

.result-value--success {
  color: var(--color-success, #22c55e);
}

.result-value--warning {
  color: var(--color-warning, #f59e0b);
}

.result-value--negative {
  color: var(--color-danger, #ef4444);
}

.result-card--highlight .result-value {
  color: white;
}

.result-sub {
  font-size: 0.75rem;
  color: var(--color-text-muted, #64748b);
}

.result-card--highlight .result-sub {
  color: rgba(255, 255, 255, 0.7);
}

/* Milestone Timeline */
.milestone-timeline {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--color-bg-subtle, #f8fafc);
  border-radius: 0.75rem;
}

.milestone-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  opacity: 0.5;
  transition: opacity 0.2s ease;
}

.milestone-item--achieved {
  opacity: 1;
}

.milestone-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--color-border, #e2e8f0);
  flex-shrink: 0;
  transition: background 0.2s ease;
}

.milestone-dot--achieved {
  background: var(--color-success, #22c55e);
}

.milestone-content {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.milestone-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text, #0f172a);
}

.milestone-date {
  font-size: 0.75rem;
  color: var(--color-text-muted, #64748b);
}

/* Debt Breakdown */
.debt-breakdown {
  padding: 0.75rem;
  background: var(--color-bg-subtle, #f8fafc);
  border-radius: 0.75rem;
}

.breakdown-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  margin: 0 0 0.75rem 0;
}

.debt-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.debt-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  background: var(--color-bg, #ffffff);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border, #e2e8f0);
}

.debt-rank {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-primary, #3b82f6);
  width: 2rem;
}

.debt-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.debt-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text, #0f172a);
}

.debt-details {
  font-size: 0.75rem;
  color: var(--color-text-muted, #64748b);
}

.debt-months {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-muted, #94a3b8);
}

/* Growth Chart */
.growth-breakdown {
  padding: 0.75rem;
  background: var(--color-bg-subtle, #f8fafc);
  border-radius: 0.75rem;
}

.growth-chart {
  display: flex;
  align-items: flex-end;
  gap: 0.375rem;
  height: 120px;
  padding: 0.5rem;
}

.growth-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  position: relative;
}

.growth-year {
  font-size: 0.625rem;
  color: var(--color-text-muted, #94a3b8);
  position: absolute;
  bottom: -18px;
}

.growth-bar-fill {
  width: 100%;
  height: calc(var(--growth-pct) * 1%);
  min-height: 4px;
  background: linear-gradient(180deg, var(--color-primary, #3b82f6) 0%, #60a5fa 100%);
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
}

.growth-value {
  font-size: 0.625rem;
  color: var(--color-text-muted, #94a3b8);
  position: absolute;
  top: -14px;
  white-space: nowrap;
}

/* Investment Mix */
.investment-mix {
  padding: 0.75rem;
  background: var(--color-bg-subtle, #f8fafc);
  border-radius: 0.75rem;
}

.allocation-pie {
  display: flex;
  height: 32px;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.allocation-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: width 0.3s ease;
  overflow: hidden;
}

.allocation-segment span {
  font-size: 0.6875rem;
  font-weight: 600;
  color: white;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.allocation-note {
  font-size: 0.75rem;
  color: var(--color-text-muted, #64748b);
  margin: 0;
  text-align: center;
}
</style>
