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

      <!-- Paycheck Split Overview -->
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Paycheck split</h2>
        </div>
        <p class="dash-section-lead">
          Suggested buckets from ${{ data.user.monthlyIncome.toLocaleString('en-US') }}/mo take-home.
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
          </div>
        </div>
      </section>

      <!-- Needs Budget Tracker -->
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">🏠 Needs Budget Tracker</h2>
        </div>
        <p class="dash-section-lead">Track your essential spending and see how much is safe to spend.</p>
        
        <div class="dash-grid-3">
          <div class="dash-card dash-card--needs">
            <h3 class="dash-card__title">Monthly Needs Budget</h3>
            <div class="needs-summary">
              <div class="needs-summary__item">
                <span class="needs-summary__label">Total Budget</span>
                <span class="needs-summary__value">${{ needsBudget.toLocaleString() }}</span>
              </div>
              <div class="needs-summary__item">
                <span class="needs-summary__label">Spent So Far</span>
                <span class="needs-summary__value spent">${{ needsSpent.toLocaleString() }}</span>
              </div>
              <div class="needs-summary__item">
                <span class="needs-summary__label">Safe to Spend</span>
                <span class="needs-summary__value safe">${{ safeToSpend.toLocaleString() }}</span>
              </div>
            </div>
            <div class="needs-progress">
              <div class="needs-progress__bar">
                <div 
                  class="needs-progress__fill" 
                  :class="getNeedsProgressClass(needsUsagePercent)"
                  :style="{ width: `${Math.min(needsUsagePercent, 100)}%` }"
                />
              </div>
              <p class="needs-progress__label">
                {{ needsUsagePercent.toFixed(0) }}% used · {{ daysRemaining }} days left in month
              </p>
            </div>
            <div v-if="needsUsagePercent > 70" class="needs-alert">
              <span class="needs-alert__icon">⚠️</span>
              <span>{{ needsAlertMessage }}</span>
            </div>
          </div>

          <div class="dash-card dash-card--needs-detail">
            <h3 class="dash-card__title">By Category</h3>
            <ul class="needs-categories">
              <li v-for="cat in needsCategories" :key="cat.name" class="needs-category">
                <div class="needs-category__header">
                  <span class="needs-category__name">{{ cat.name }}</span>
                  <span class="needs-category__value">${{ cat.spent }} / ${{ cat.budget }}</span>
                </div>
                <div class="needs-category__bar">
                  <div 
                    class="needs-category__fill" 
                    :style="{ width: `${Math.min((cat.spent / cat.budget) * 100, 100)}%` }"
                    :class="{ 'needs-category__fill--over': cat.spent > cat.budget }"
                  />
                </div>
              </li>
            </ul>
          </div>

          <div class="dash-card dash-card--needs-tips">
            <h3 class="dash-card__title">💡 Smart Tips</h3>
            <ul class="needs-tips">
              <li v-if="needsUsagePercent < 50">
                <span class="needs-tips__icon">✅</span>
                <span>You're under budget! Consider moving extra to savings.</span>
              </li>
              <li v-else-if="needsUsagePercent < 80">
                <span class="needs-tips__icon">👍</span>
                <span>On track! Keep monitoring for the rest of the month.</span>
              </li>
              <li v-else>
                <span class="needs-tips__icon">📉</span>
                <span>Review discretionary spending to cover essential needs.</span>
              </li>
              <li>
                <span class="needs-tips__icon">📊</span>
                <span>Per day remaining: ${{ perDayRemaining.toLocaleString() }}</span>
              </li>
              <li>
                <span class="needs-tips__icon">🎯</span>
                <span>Weekly equivalent: ${{ perWeekRemaining.toLocaleString() }}/week</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Emergency Fund Tracker -->
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">🛡️ Emergency Fund Tracker</h2>
        </div>
        <p class="dash-section-lead">See how many months of expenses you have covered and when you'll reach your goals.</p>
        
        <div class="dash-grid-2">
          <div class="dash-card dash-card--emergency">
            <h3 class="dash-card__title">Months of Expenses Covered</h3>
            <div class="emergency-main">
              <div class="emergency-main__value">
                {{ monthsCovered.toFixed(1) }}
                <span class="emergency-main__unit">months</span>
              </div>
              <div class="emergency-main__detail">
                <p><strong>Current savings:</strong> ${{ data.accounts.savings.toLocaleString() }}</p>
                <p><strong>Monthly expenses:</strong> ${{ monthlyExpenses.toLocaleString() }}</p>
              </div>
            </div>
            <div class="emergency-tiers">
              <div 
                v-for="tier in emergencyTiers" 
                :key="tier.label"
                class="emergency-tier"
                :class="{ 'emergency-tier--achieved': tier.achieved, 'emergency-tier--current': tier.current }"
              >
                <div class="emergency-tier__icon">{{ tier.achieved ? '✅' : tier.current ? '🎯' : '🔒' }}</div>
                <div class="emergency-tier__content">
                  <p class="emergency-tier__label">{{ tier.label }}</p>
                  <p class="emergency-tier__target">${{ tier.target.toLocaleString() }}</p>
                  <p class="emergency-tier__progress">
                    {{ tier.percent.toFixed(0) }}% · 
                    <span v-if="!tier.achieved">${{ (tier.target - data.accounts.savings).toLocaleString() }} more needed</span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div class="dash-card dash-card--emergency-projection">
            <h3 class="dash-card__title">Funding Projection</h3>
            <p class="dash-card__sub">At ${{ emergencyMonthlyContribution }}/mo, you'll reach:</p>
            <div class="projection-timeline">
              <div 
                v-for="milestone in emergencyMilestones" 
                :key="milestone.label"
                class="projection-milestone"
                :class="{ 'projection-milestone--achieved': milestone.achieved }"
              >
                <div class="projection-milestone__date">
                  {{ milestone.achieved ? 'Achieved!' : milestone.date }}
                </div>
                <div class="projection-milestone__label">{{ milestone.label }}</div>
              </div>
            </div>
            <div class="emergency-adjust">
              <label class="emergency-adjust__label">
                Monthly contribution:
                <input 
                  v-model.number="emergencyMonthlyContribution" 
                  type="number" 
                  min="50" 
                  step="50"
                  class="emergency-adjust__input"
                />
              </label>
            </div>
          </div>
        </div>
      </section>

      <!-- Debt Payoff Accelerator -->
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">💳 Debt Payoff Accelerator</h2>
        </div>
        <p class="dash-section-lead">See how extra payments can save you interest and get you debt-free faster.</p>
        
        <div class="dash-grid-2">
          <div class="dash-card dash-card--debt-accel">
            <h3 class="dash-card__title">Current Plan vs Accelerated</h3>
            
            <div class="debt-comparison">
              <div class="debt-comparison__plan">
                <h4>Minimum Payments Only</h4>
                <div class="debt-stat">
                  <span class="debt-stat__label">Monthly payment</span>
                  <span class="debt-stat__value">${{ totalMinPayments.toLocaleString() }}</span>
                </div>
                <div class="debt-stat">
                  <span class="debt-stat__label">Debt-free date</span>
                  <span class="debt-stat__value debt-stat__value--warning">{{ minPaymentPayoffDate }}</span>
                </div>
                <div class="debt-stat">
                  <span class="debt-stat__label">Total interest</span>
                  <span class="debt-stat__value debt-stat__value--danger">${{ minPaymentInterest.toLocaleString() }}</span>
                </div>
                <div class="debt-stat">
                  <span class="debt-stat__label">Total paid</span>
                  <span class="debt-stat__value">${{ (totalDebtOriginal + minPaymentInterest).toLocaleString() }}</span>
                </div>
              </div>

              <div class="debt-comparison__plan debt-comparison__plan--accelerated">
                <h4>With Extra Payment</h4>
                <div class="extra-payment-control">
                  <label>
                    Extra per month:
                    <input 
                      v-model.number="extraDebtPayment" 
                      type="number" 
                      min="50" 
                      step="50"
                      class="extra-payment-control__input"
                    />
                  </label>
                  <div class="extra-presets">
                    <button 
                      v-for="preset in [50, 100, 200, 500]" 
                      :key="preset"
                      @click="extraDebtPayment = preset"
                      :class="{ 'extra-preset--active': extraDebtPayment === preset }"
                    >
                      +${{ preset }}
                    </button>
                  </div>
                </div>
                <div class="debt-stat">
                  <span class="debt-stat__label">Monthly payment</span>
                  <span class="debt-stat__value">${{ (totalMinPayments + extraDebtPayment).toLocaleString() }}</span>
                </div>
                <div class="debt-stat">
                  <span class="debt-stat__label">Debt-free date</span>
                  <span class="debt-stat__value debt-stat__value--success">{{ acceleratedPayoffDate }}</span>
                </div>
                <div class="debt-stat">
                  <span class="debt-stat__label">Interest saved</span>
                  <span class="debt-stat__value debt-stat__value--success">${{ interestSaved.toLocaleString() }}</span>
                </div>
                <div class="debt-stat">
                  <span class="debt-stat__label">Time saved</span>
                  <span class="debt-stat__value debt-stat__value--success">{{ monthsSaved }} months</span>
                </div>
              </div>
            </div>
          </div>

          <div class="dash-card dash-card--debt-details">
            <h3 class="dash-card__title">Your Debts (Avalanche Order)</h3>
            <div class="table-responsive">
              <table class="dash-table dash-table--compact">
                <thead>
                  <tr>
                    <th>Debt</th>
                    <th>Balance</th>
                    <th>APR</th>
                    <th>Min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="debt in sortedDebts" :key="debt.name">
                    <td>
                      <strong>{{ debt.name }}</strong>
                      <span v-if="debt.avalancheRank === 1" class="badge badge--priority">Pay First</span>
                    </td>
                    <td class="tabular-num">${{ debt.balance.toLocaleString() }}</td>
                    <td :class="getAprClass(debt.rate)">{{ debt.rate.toFixed(2) }}%</td>
                    <td class="tabular-num">${{ debt.min.toLocaleString() }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="debt-summary-footer">
              <p><strong>Total Balance:</strong> ${{ totalDebtOriginal.toLocaleString() }}</p>
              <p><strong>Weighted APR:</strong> {{ weightedApr.toFixed(2) }}%</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Sinking Funds / Savings Goals -->
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">🎯 Savings Goals (Sinking Funds)</h2>
        </div>
        <p class="dash-section-lead">Set aside money each month for irregular expenses so they don't derail your budget.</p>
        
        <div class="dash-card dash-card--goals">
          <div class="goals-header">
            <h3 class="goals-header__title">Your Savings Buckets</h3>
            <button class="btn btn--primary btn--sm" @click="showAddGoal = !showAddGoal">
              {{ showAddGoal ? 'Cancel' : '+ Add Goal' }}
            </button>
          </div>

          <!-- Add Goal Form -->
          <div v-if="showAddGoal" class="add-goal-form">
            <div class="add-goal-form__row">
              <input 
                v-model="newGoal.name" 
                type="text" 
                placeholder="Goal name (e.g., Car Maintenance)" 
                class="add-goal-form__input"
              />
              <input 
                v-model.number="newGoal.target" 
                type="number" 
                placeholder="Target amount" 
                class="add-goal-form__input"
              />
              <input 
                v-model.number="newGoal.monthly" 
                type="number" 
                placeholder="Monthly contribution" 
                class="add-goal-form__input"
              />
              <button class="btn btn--success btn--sm" @click="addGoal">Save Goal</button>
            </div>
          </div>

          <!-- Goals Grid -->
          <div class="goals-grid">
            <div 
              v-for="(goal, idx) in savingsGoals" 
              :key="goal.name"
              class="goal-card"
              :class="{ 'goal-card--complete': goal.current >= goal.target }"
            >
              <div class="goal-card__header">
                <div class="goal-card__icon">{{ goal.icon }}</div>
                <div class="goal-card__title">
                  <h4>{{ goal.name }}</h4>
                  <p>Target: ${{ goal.target.toLocaleString() }}</p>
                </div>
                <button class="goal-card__delete" @click="removeGoal(idx)">×</button>
              </div>
              <div class="goal-card__progress">
                <div class="goal-card__bar">
                  <div 
                    class="goal-card__fill" 
                    :style="{ width: `${Math.min((goal.current / goal.target) * 100, 100)}%` }"
                  />
                </div>
                <div class="goal-card__stats">
                  <span>${{ goal.current.toLocaleString() }} saved</span>
                  <span>${{ (goal.target - goal.current).toLocaleString() }} to go</span>
                </div>
              </div>
              <div class="goal-card__footer">
                <span class="goal-card__monthly">${{ goal.monthly }}/mo</span>
                <span class="goal-card__percent">{{ ((goal.current / goal.target) * 100).toFixed(0) }}%</span>
              </div>
            </div>

            <!-- Default goals if none added -->
            <div 
              v-for="goal in defaultSinkingFunds" 
              :key="goal.name"
              class="goal-card"
            >
              <div class="goal-card__header">
                <div class="goal-card__icon">{{ goal.icon }}</div>
                <div class="goal-card__title">
                  <h4>{{ goal.name }}</h4>
                  <p>Target: ${{ goal.target.toLocaleString() }}</p>
                </div>
              </div>
              <div class="goal-card__progress">
                <div class="goal-card__bar">
                  <div 
                    class="goal-card__fill" 
                    :style="{ width: `${Math.min((goal.current / goal.target) * 100, 100)}%` }"
                  />
                </div>
                <div class="goal-card__stats">
                  <span>${{ goal.current.toLocaleString() }} saved</span>
                  <span>${{ (goal.target - goal.current).toLocaleString() }} to go</span>
                </div>
              </div>
              <div class="goal-card__footer">
                <span class="goal-card__monthly">${{ goal.monthly }}/mo</span>
                <span class="goal-card__percent">{{ ((goal.current / goal.target) * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </div>

          <!-- Goals Summary -->
          <div class="goals-summary">
            <div class="goals-summary__item">
              <span class="goals-summary__label">Total Goals</span>
              <span class="goals-summary__value">{{ allGoals.length }}</span>
            </div>
            <div class="goals-summary__item">
              <span class="goals-summary__label">Total Saved</span>
              <span class="goals-summary__value">${{ totalGoalsSaved.toLocaleString() }}</span>
            </div>
            <div class="goals-summary__item">
              <span class="goals-summary__label">Total Target</span>
              <span class="goals-summary__value">${{ totalGoalsTarget.toLocaleString() }}</span>
            </div>
            <div class="goals-summary__item">
              <span class="goals-summary__label">Monthly Contribution</span>
              <span class="goals-summary__value">${{ totalGoalsMonthly.toLocaleString() }}/mo</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Investment Growth Simulator -->
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">📈 Investment Growth Simulator</h2>
        </div>
        <p class="dash-section-lead">
          See how regular investing grows over time through compound returns.
        </p>

        <div class="dash-grid-2">
          <div class="dash-card dash-card--simulator">
            <h3 class="dash-card__title">Configure Your Investment</h3>
            
            <div class="simulator-controls">
              <div class="simulator-control">
                <label class="simulator-label">
                  Monthly Contribution
                  <span class="simulator-value">${{ monthlyContribution }}</span>
                </label>
                <input
                  v-model.number="monthlyContribution"
                  type="range"
                  min="50"
                  max="5000"
                  step="50"
                  class="simulator-slider"
                />
                <div class="simulator-presets">
                  <button
                    v-for="preset in [100, 250, 500, 750, 1000, 1500, 2000]"
                    :key="preset"
                    :class="['simulator-preset', { 'simulator-preset--active': monthlyContribution === preset }]"
                    @click="monthlyContribution = preset"
                  >
                    ${{ preset }}
                  </button>
                </div>
              </div>

              <div class="simulator-control">
                <label class="simulator-label">
                  Investment Period
                  <span class="simulator-value">{{ investmentYears }} years</span>
                </label>
                <input
                  v-model.number="investmentYears"
                  type="range"
                  min="5"
                  max="40"
                  step="5"
                  class="simulator-slider"
                />
                <div class="simulator-presets">
                  <button
                    v-for="preset in [5, 10, 20, 30, 40]"
                    :key="preset"
                    :class="['simulator-preset', { 'simulator-preset--active': investmentYears === preset }]"
                    @click="investmentYears = preset"
                  >
                    {{ preset }}y
                  </button>
                </div>
              </div>

              <div class="simulator-control">
                <label class="simulator-label">
                  Expected Annual Return
                  <span class="simulator-value" :style="{ color: scenarioColor }">{{ selectedScenario.name }} ({{ selectedScenario.return }}%)</span>
                </label>
                <div class="scenario-selector">
                  <button
                    v-for="scenario in scenarios"
                    :key="scenario.id"
                    :class="['scenario-btn', `scenario-btn--${scenario.id}`, { 'scenario-btn--active': selectedScenario.id === scenario.id }]"
                    @click="selectedScenario = scenario"
                  >
                    <span class="scenario-btn__name">{{ scenario.name }}</span>
                    <span class="scenario-btn__return">{{ scenario.return }}%</span>
                    <span class="scenario-btn__desc">{{ scenario.description }}</span>
                  </button>
                </div>
              </div>
            </div>

            <div class="simulator-summary">
              <div class="simulator-summary__item">
                <span class="simulator-summary__label">Total Invested</span>
                <span class="simulator-summary__value">${{ totalInvested.toLocaleString() }}</span>
              </div>
              <div class="simulator-summary__item">
                <span class="simulator-summary__label">Interest Earned</span>
                <span class="simulator-summary__value interest">${{ interestEarned.toLocaleString() }}</span>
              </div>
              <div class="simulator-summary__item simulator-summary__item--total">
                <span class="simulator-summary__label">Future Value</span>
                <span class="simulator-summary__value total">${{ futureValue.toLocaleString() }}</span>
              </div>
            </div>
          </div>

          <div class="dash-card dash-card--chart">
            <h3 class="dash-card__title">Growth Projection</h3>
            <p class="dash-card__sub">Over {{ investmentYears }} years at {{ selectedScenario.return }}%</p>
            <div class="dash-chart-wrap" style="height: 320px">
              <ClientOnly>
                <Line
                  :data="chartData"
                  :options="chartOptions"
                />
                <template #fallback>
                  <div class="projection-fallback"><p>Chart loading...</p></div>
                </template>
              </ClientOnly>
            </div>
          </div>
        </div>

        <div class="dash-card dash-card--comparison" style="margin-top: 1rem">
          <h3 class="dash-card__title">Compare All Scenarios</h3>
          <div class="comparison-table-wrap">
            <table class="comparison-table">
              <thead>
                <tr>
                  <th>Scenario</th>
                  <th>Return</th>
                  <th>Invested</th>
                  <th>Interest</th>
                  <th>Future Value</th>
                  <th>Today's Value*</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="scenario in scenarios"
                  :key="scenario.id"
                  :class="{ 'comparison-table__row--highlighted': selectedScenario.id === scenario.id }"
                >
                  <td>
                    <strong>{{ scenario.name }}</strong>
                    <span class="comparison-table__desc">{{ scenario.description }}</span>
                  </td>
                  <td class="tabular-num" :style="{ color: getScenarioColor(scenario.return) }">{{ scenario.return }}%</td>
                  <td class="tabular-num">${{ calcTotalInvested(monthlyContribution, investmentYears).toLocaleString() }}</td>
                  <td class="tabular-num" style="color: #22c55e">${{ calcInterest(monthlyContribution, investmentYears, scenario.return).toLocaleString() }}</td>
                  <td class="tabular-num">${{ calcFutureValue(monthlyContribution, investmentYears, scenario.return).toLocaleString() }}</td>
                  <td class="tabular-num comparison-table__value--muted">${{ calcInflationAdjusted(calcFutureValue(monthlyContribution, investmentYears, scenario.return), investmentYears).toLocaleString() }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="comparison-table__footnote">* Inflation-adjusted (3% assumed)</p>
        </div>

        <div class="dash-disclaimer">
          <span class="dash-disclaimer__icon">⚠️</span>
          <div class="dash-disclaimer__content">
            <p class="dash-disclaimer__title">This is a projection, not a guarantee</p>
            <ul class="dash-disclaimer__list">
              <li>Actual returns vary — markets go up AND down</li>
              <li>Past performance doesn't guarantee future results</li>
              <li>Inflation reduces purchasing power over time</li>
              <li>Consult a licensed financial advisor for personalized advice</li>
            </ul>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
  ssr: false,
})

const { data, isLoading, isUsingDummyData } = useFinancialData()

const splitReady = computed(() => {
  const p = data.value?.paycheckSplit
  return Boolean(p?.labels?.length && p.amounts?.length)
})

// Monthly expenses
const monthlyExpenses = computed(() => {
  if (!data.value?.spending?.amounts) return 0
  return data.value.spending.amounts.reduce((sum, amt) => sum + amt, 0)
})

// Current investing amount
const currentMonthlyInvesting = computed(() => {
  if (!data.value?.paycheckSplit?.amounts) return 0
  const idx = data.value.paycheckSplit.labels.findIndex(l => l.toLowerCase().includes('invest'))
  return idx >= 0 ? data.value.paycheckSplit.amounts[idx] : 0
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

const weightedApr = computed(() => {
  if (!data.value?.debts || totalDebtOriginal.value === 0) return 0
  const total = data.value.debts.reduce((sum, d) => sum + (d.balance * d.rate), 0)
  return total / totalDebtOriginal.value
})

const sortedDebts = computed(() => {
  if (!data.value?.debts) return []
  const debts = data.value.debts.map((d, i) => ({ ...d, idx: i }))
  const byApr = [...debts].sort((a, b) => b.rate - a.rate)
  byApr.forEach((d, rank) => { d.avalancheRank = rank + 1 })
  return byApr
})

// ============ NEEDS BUDGET TRACKER ============
const needsBudget = computed(() => {
  if (!data.value?.paycheckSplit?.amounts) return 0
  const idx = data.value.paycheckSplit.labels.findIndex(l => l.toLowerCase().includes('needs'))
  return idx >= 0 ? data.value.paycheckSplit.amounts[idx] : Math.round(monthlyExpenses.value)
})

const daysInMonth = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).getDate()
const dayOfMonth = new Date().getDate()
const daysRemaining = daysInMonth - dayOfMonth
const monthProgress = dayOfMonth / daysInMonth

const needsSpent = computed(() => {
  // Simulate spending based on month progress + some variance
  if (!data.value?.spending?.amounts) return 0
  const essentialCategories = data.value.spending.amounts.slice(0, 4) // First 4 categories
  return Math.round(essentialCategories.reduce((sum, amt) => sum + amt, 0) * monthProgress * 1.05)
})

const safeToSpend = computed(() => needsBudget.value - needsSpent.value)
const needsUsagePercent = computed(() => (needsSpent.value / needsBudget.value) * 100)
const perDayRemaining = computed(() => daysRemaining > 0 ? safeToSpend.value / daysRemaining : 0)
const perWeekRemaining = computed(() => Math.ceil(perDayRemaining.value * 7))

const needsAlertMessage = computed(() => {
  if (needsUsagePercent.value > 90) return 'Critical! Only a few days left—review spending immediately.'
  if (needsUsagePercent.value > 80) return 'High usage—consider reducing discretionary spending.'
  return 'Moderate usage—stay mindful for the rest of the month.'
})

const needsCategories = computed(() => {
  if (!data.value?.spending) return []
  const names = ['Housing', 'Food', 'Transport', 'Utilities']
  const budgets = [1350, 680, 290, 165]
  return names.map((name, i) => ({
    name,
    budget: budgets[i],
    spent: Math.round((data.value!.spending.amounts[i] || 0) * monthProgress),
  }))
})

function getNeedsProgressClass(percent: number) {
  if (percent > 90) return 'needs-progress__fill--danger'
  if (percent > 70) return 'needs-progress__fill--warning'
  return 'needs-progress__fill--good'
}

// ============ EMERGENCY FUND TRACKER ============
const monthsCovered = computed(() => {
  if (!data.value || monthlyExpenses.value === 0) return 0
  return data.value.accounts.savings / monthlyExpenses.value
})

const emergencyTiers = computed(() => {
  const savings = data.value?.accounts.savings || 0
  const targets = [
    { label: 'Starter Fund', months: 1 },
    { label: '3-Month Safety Net', months: 3 },
    { label: '6-Month Security', months: 6 },
  ]
  return targets.map(t => {
    const target = monthlyExpenses.value * t.months
    return {
      ...t,
      target,
      achieved: savings >= target,
      current: savings >= target * 0.5 && savings < target,
      percent: Math.min((savings / target) * 100, 100),
    }
  })
})

const emergencyMonthlyContribution = ref(450)

const emergencyMilestones = computed(() => {
  const savings = data.value?.accounts.savings || 0
  const contribution = emergencyMonthlyContribution.value
  const targets = [
    { label: '1 Month Expenses', target: monthlyExpenses.value },
    { label: '3 Months Expenses', target: monthlyExpenses.value * 3 },
    { label: '6 Months Expenses', target: monthlyExpenses.value * 6 },
  ]
  
  return targets.map(t => {
    if (savings >= t.target) {
      return { ...t, achieved: true, date: 'Achieved!' }
    }
    const remaining = t.target - savings
    const months = Math.ceil(remaining / contribution)
    const date = new Date()
    date.setMonth(date.getMonth() + months)
    return {
      ...t,
      achieved: false,
      date: date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
    }
  })
})

// ============ DEBT PAYOFF ACCELERATOR ============
const extraDebtPayment = ref(100)

function calculatePayoff(debts: any[], extraPayment: number) {
  let totalMonths = 0
  let totalInterest = 0
  const debtsCopy = debts.map(d => ({ ...d }))
  
  while (debtsCopy.some(d => d.balance > 0) && totalMonths < 600) {
    const availablePayment = debtsCopy.reduce((sum, d) => sum + d.min, 0) + extraPayment
    let remaining = availablePayment
    
    // Minimum payments first
    for (const debt of debtsCopy) {
      if (debt.balance > 0) {
        const interest = debt.balance * (debt.rate / 100 / 12)
        totalInterest += interest
        const payment = Math.min(debt.min + interest, debt.balance)
        debt.balance -= (payment - interest)
        remaining -= payment
      }
    }
    
    // Extra to highest APR debt
    const byApr = [...debtsCopy].sort((a, b) => b.rate - a.rate)
    for (const debt of byApr) {
      if (debt.balance > 0 && remaining > 0) {
        const interest = debt.balance * (debt.rate / 100 / 12)
        const payment = Math.min(remaining + interest, debt.balance)
        debt.balance -= (payment - interest)
        remaining -= payment
      }
    }
    
    totalMonths++
  }
  
  return { months: totalMonths, interest: Math.round(totalInterest) }
}

const minPayoff = computed(() => calculatePayoff(data.value?.debts || [], 0))
const acceleratedPayoff = computed(() => calculatePayoff(data.value?.debts || [], extraDebtPayment.value))

const minPaymentPayoffDate = computed(() => {
  const date = new Date()
  date.setMonth(date.getMonth() + minPayoff.value.months)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
})

const acceleratedPayoffDate = computed(() => {
  const date = new Date()
  date.setMonth(date.getMonth() + acceleratedPayoff.value.months)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
})

const minPaymentInterest = computed(() => minPayoff.value.interest)
const interestSaved = computed(() => minPayoff.value.interest - acceleratedPayoff.value.interest)
const monthsSaved = computed(() => minPayoff.value.months - acceleratedPayoff.value.months)

// ============ SINKING FUNDS / SAVINGS GOALS ============
const showAddGoal = ref(false)
const newGoal = ref({ name: '', target: 0, monthly: 0 })

const defaultSinkingFunds = [
  { name: 'Car Maintenance', icon: '🚗', target: 600, current: 150, monthly: 50 },
  { name: 'Holiday Gifts', icon: '🎁', target: 900, current: 200, monthly: 75 },
  { name: 'Medical Co-pays', icon: '🏥', target: 300, current: 75, monthly: 25 },
  { name: 'Vacation', icon: '✈️', target: 2000, current: 400, monthly: 100 },
]

const savingsGoals = ref<any[]>([])

const allGoals = computed(() => [...savingsGoals.value, ...defaultSinkingFunds])
const totalGoalsSaved = computed(() => allGoals.value.reduce((sum, g) => sum + g.current, 0))
const totalGoalsTarget = computed(() => allGoals.value.reduce((sum, g) => sum + g.target, 0))
const totalGoalsMonthly = computed(() => allGoals.value.reduce((sum, g) => sum + g.monthly, 0))

function addGoal() {
  if (newGoal.value.name && newGoal.value.target && newGoal.value.monthly) {
    savingsGoals.value.push({
      ...newGoal.value,
      icon: '🎯',
      current: 0,
    })
    newGoal.value = { name: '', target: 0, monthly: 0 }
    showAddGoal.value = false
  }
}

function removeGoal(idx: number) {
  savingsGoals.value.splice(idx, 1)
}

// ============ INVESTMENT SIMULATOR ============
const monthlyContribution = ref(500)
const investmentYears = ref(30)

const scenarios = [
  { id: 'conservative', name: 'Conservative', return: 6, description: 'Bonds & stable' },
  { id: 'moderate', name: 'Moderate', return: 8, description: 'Balanced' },
  { id: 'aggressive', name: 'Aggressive', return: 10, description: 'S&P 500 avg' },
  { id: 'bull', name: 'Bull Market', return: 12, description: 'Tech-heavy' },
]

const selectedScenario = ref(scenarios[2])
const scenarioColor = computed(() => getScenarioColor(selectedScenario.value.return))

function getScenarioColor(rate: number): string {
  if (rate <= 6) return '#22c55e'
  if (rate <= 8) return '#3b82f6'
  if (rate <= 10) return '#f59e0b'
  return '#8b5cf6'
}

function calcFutureValue(monthly: number, years: number, rate: number): number {
  const r = rate / 100 / 12
  const n = years * 12
  if (r === 0) return monthly * n
  return monthly * ((Math.pow(1 + r, n) - 1) / r)
}

function calcTotalInvested(monthly: number, years: number): number {
  return monthly * years * 12
}

function calcInterest(monthly: number, years: number, rate: number): number {
  return calcFutureValue(monthly, years, rate) - calcTotalInvested(monthly, years)
}

function calcInflationAdjusted(fv: number, years: number): number {
  return fv / Math.pow(1.03, years)
}

const totalInvested = computed(() => calcTotalInvested(monthlyContribution.value, investmentYears.value))
const interestEarned = computed(() => calcInterest(monthlyContribution.value, investmentYears.value, selectedScenario.value.return))
const futureValue = computed(() => calcFutureValue(monthlyContribution.value, investmentYears.value, selectedScenario.value.return))

const chartData = computed(() => {
  const labels: string[] = []
  const valueData: number[] = []
  const investedData: number[] = []
  const r = selectedScenario.value.return / 100 / 12
  let totalValue = 0
  let totalInv = 0
  
  for (let year = 0; year <= investmentYears.value; year++) {
    labels.push(`Year ${year}`)
    investedData.push(totalInv)
    valueData.push(totalValue)
    for (let month = 0; month < 12; month++) {
      totalInv += monthlyContribution.value
      totalValue = (totalValue + monthlyContribution.value) * (1 + r)
    }
  }
  
  return {
    labels,
    datasets: [
      {
        label: 'Portfolio Value',
        data: valueData,
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 2,
      },
      {
        label: 'Total Invested',
        data: investedData,
        borderColor: '#3b82f6',
        borderDash: [5, 5],
        fill: false,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 2,
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' as const, labels: { usePointStyle: true, padding: 15 } },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      titleColor: '#f8fafc',
      bodyColor: '#f8fafc',
      padding: 12,
      callbacks: { label: (ctx: any) => `${ctx.dataset.label}: $${ctx.parsed.y.toLocaleString()}` },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 8, color: '#64748b' } },
    y: {
      grid: { color: 'rgba(226, 232, 240, 0.5)' },
      ticks: {
        callback: (v: any) => v >= 1e6 ? `$${(v/1e6).toFixed(1)}M` : v >= 1000 ? `$${(v/1000).toFixed(0)}K` : `$${v}`,
        color: '#64748b',
      },
    },
  },
}

// Next Steps
const nextSteps = computed(() => {
  if (!data.value) return []
  const steps: any[] = []
  
  if (data.value.accounts.savings < 500) {
    steps.push({
      priority: 'high',
      title: 'Build $500 starter emergency fund',
      description: `You have $${data.value.accounts.savings.toFixed(0)}, need $${500 - data.value.accounts.savings.toFixed(0)} more`,
    })
  } else if (monthsCovered.value < 3) {
    steps.push({
      priority: 'medium',
      title: 'Continue building emergency fund',
      description: `${(3 - monthsCovered.value).toFixed(1)} months to reach 3-month target`,
    })
  }
  
  const highInterestDebts = data.value.debts.filter(d => d.rate >= 15)
  if (highInterestDebts.length > 0) {
    const d = highInterestDebts[0]
    steps.push({
      priority: 'high',
      title: `Pay extra toward ${d.name} (${d.rate.toFixed(1)}% APR)`,
      description: 'Add $100/mo to save on interest',
    })
  }
  
  if (steps.length === 0) {
    steps.push({ priority: 'low', title: "You're on track!", description: 'Keep following your current plan' })
  }
  
  return steps
})

function getAprClass(rate: number) {
  if (rate >= 20) return 'tabular-num--high'
  if (rate >= 10) return 'tabular-num--warning'
  return ''
}

useHead({ title: 'Autonomous finance — AI Financial' })
</script>

<style scoped>
/* Progress Bar */
.progress-bar {
  background: #f1f5f9;
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
.progress-bar__fill--good { background: linear-gradient(90deg, #22c55e, #4ade80); }
.progress-bar__fill--warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.progress-bar__fill--danger { background: linear-gradient(90deg, #ef4444, #f87171); }
.progress-bar__label { font-size: 0.8125rem; color: #64748b; margin: 0; }

/* Next Steps */
.dash-card--next-steps { border-left: 4px solid #3b82f6; }
.next-steps__list { display: flex; flex-direction: column; gap: 1rem; }
.next-steps__item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  background: #f8fafc;
  border-left: 3px solid #94a3b8;
}
.next-steps__item--priority-high { border-left-color: #ef4444; background: rgba(239, 68, 68, 0.05); }
.next-steps__item--priority-medium { border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.05); }
.next-steps__item--priority-low { border-left-color: #22c55e; background: rgba(34, 197, 94, 0.05); }
.next-steps__num {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
}
.next-steps__content { flex: 1; }
.next-steps__title { font-weight: 600; font-size: 1rem; margin: 0 0 0.25rem 0; }
.next-steps__desc { font-size: 0.875rem; color: #64748b; margin: 0 0 0.5rem 0; }
.next-steps__impact { font-size: 0.8125rem; color: #3b82f6; font-weight: 500; margin: 0; }

/* Needs Budget */
.dash-card--needs { border-left: 4px solid #3b82f6; }
.dash-card--needs-detail { border-left: 4px solid #22c55e; }
.dash-card--needs-tips { border-left: 4px solid #f59e0b; }
.needs-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
}
.needs-summary__item { display: flex; flex-direction: column; gap: 0.25rem; }
.needs-summary__label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 600; }
.needs-summary__value { font-size: 1.25rem; font-weight: 700; }
.needs-summary__value.spent { color: #f59e0b; }
.needs-summary__value.safe { color: #22c55e; }
.needs-progress__bar {
  background: #e2e8f0;
  border-radius: 999px;
  height: 10px;
  overflow: hidden;
}
.needs-progress__fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s ease;
}
.needs-progress__fill--good { background: #22c55e; }
.needs-progress__fill--warning { background: #f59e0b; }
.needs-progress__fill--danger { background: #ef4444; }
.needs-progress__label { font-size: 0.8125rem; color: #64748b; margin: 0.5rem 0 0; }
.needs-alert {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 0.5rem;
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #ef4444;
}
.needs-categories { list-style: none; padding: 0; margin: 0; }
.needs-category { margin-bottom: 1rem; }
.needs-category__header {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}
.needs-category__name { font-weight: 500; }
.needs-category__value { color: #64748b; }
.needs-category__bar {
  background: #e2e8f0;
  border-radius: 999px;
  height: 6px;
  overflow: hidden;
}
.needs-category__fill {
  height: 100%;
  border-radius: 999px;
  background: #3b82f6;
  transition: width 0.3s ease;
}
.needs-category__fill--over { background: #ef4444; }
.needs-tips { list-style: none; padding: 0; margin: 0; }
.needs-tips li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: #475569;
}
.needs-tips__icon { font-size: 1rem; }

/* Emergency Fund */
.dash-card--emergency { border-left: 4px solid #22c55e; }
.dash-card--emergency-projection { border-left: 4px solid #3b82f6; }
.emergency-main {
  text-align: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.05), rgba(59, 130, 246, 0.05));
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
}
.emergency-main__value {
  font-size: 3rem;
  font-weight: 800;
  color: #22c55e;
  line-height: 1;
}
.emergency-main__unit { font-size: 1.25rem; color: #64748b; }
.emergency-main__detail { margin-top: 0.75rem; font-size: 0.875rem; color: #64748b; }
.emergency-main__detail p { margin: 0.25rem 0; }
.emergency-tiers { display: flex; flex-direction: column; gap: 0.75rem; }
.emergency-tier {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  opacity: 0.6;
}
.emergency-tier--achieved {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(59, 130, 246, 0.1));
  border-color: #22c55e;
  opacity: 1;
}
.emergency-tier--current { border-color: #3b82f6; opacity: 0.8; }
.emergency-tier__icon { font-size: 1.5rem; }
.emergency-tier__content { flex: 1; }
.emergency-tier__label { font-weight: 600; font-size: 0.9375rem; margin: 0 0 0.25rem 0; }
.emergency-tier__target { font-size: 0.875rem; color: #64748b; margin: 0 0 0.25rem 0; }
.emergency-tier__progress { font-size: 0.8125rem; color: #22c55e; margin: 0; }
.projection-timeline { display: flex; flex-direction: column; gap: 1rem; padding: 1rem; }
.projection-milestone {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border-left: 3px solid #e2e8f0;
}
.projection-milestone--achieved {
  background: rgba(34, 197, 94, 0.05);
  border-left-color: #22c55e;
}
.projection-milestone__date { font-weight: 600; color: #0f172a; }
.projection-milestone__label { font-size: 0.875rem; color: #64748b; }
.emergency-adjust { margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; }
.emergency-adjust__label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #475569;
}
.emergency-adjust__input {
  width: 100px;
  padding: 0.375rem 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

/* Debt Accelerator */
.dash-card--debt-accel { border-left: 4px solid #ef4444; }
.dash-card--debt-details { border-left: 4px solid #f59e0b; }
.debt-comparison {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}
.debt-comparison__plan {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}
.debt-comparison__plan h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}
.debt-comparison__plan--accelerated {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.05), rgba(59, 130, 246, 0.05));
  border-color: #22c55e;
}
.debt-stat {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
}
.debt-stat:last-child { border-bottom: none; }
.debt-stat__label { color: #64748b; }
.debt-stat__value { font-weight: 600; }
.debt-stat__value--success { color: #22c55e; }
.debt-stat__value--warning { color: #f59e0b; }
.debt-stat__value--danger { color: #ef4444; }
.extra-payment-control { margin-bottom: 1rem; }
.extra-payment-control label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #475569;
  margin-bottom: 0.5rem;
}
.extra-payment-control__input {
  width: 100px;
  padding: 0.375rem 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
}
.extra-presets { display: flex; gap: 0.5rem; }
.extra-preset {
  padding: 0.375rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: white;
  font-size: 0.8125rem;
  cursor: pointer;
}
.extra-preset--active {
  background: #22c55e;
  border-color: #22c55e;
  color: white;
}
.dash-table--compact { font-size: 0.8125rem; }
.dash-table--compact th, .dash-table--compact td { padding: 0.5rem 0.75rem; }
.debt-summary-footer {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  font-size: 0.875rem;
}
.debt-summary-footer p { margin: 0; }

/* Savings Goals */
.dash-card--goals { border-left: 4px solid #8b5cf6; }
.goals-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.goals-header__title { margin: 0; font-size: 1.125rem; }
.add-goal-form {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}
.add-goal-form__row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.add-goal-form__input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}
.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}
.goal-card {
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  transition: all 0.2s ease;
}
.goal-card--complete {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(59, 130, 246, 0.1));
  border-color: #22c55e;
}
.goal-card__header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
.goal-card__icon { font-size: 1.5rem; }
.goal-card__title { flex: 1; }
.goal-card__title h4 { margin: 0 0 0.25rem 0; font-size: 1rem; }
.goal-card__title p { margin: 0; font-size: 0.75rem; color: #64748b; }
.goal-card__delete {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
.goal-card__delete:hover { color: #ef4444; }
.goal-card__bar {
  background: #e2e8f0;
  border-radius: 999px;
  height: 8px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}
.goal-card__fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #8b5cf6, #3b82f6);
  transition: width 0.3s ease;
}
.goal-card__stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0.75rem;
}
.goal-card__footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}
.goal-card__monthly { font-weight: 600; color: #475569; }
.goal-card__percent { font-weight: 700; color: #8b5cf6; }
.goals-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.75rem;
  border-top: 1px solid #e2e8f0;
}
.goals-summary__item { display: flex; flex-direction: column; gap: 0.25rem; text-align: center; }
.goals-summary__label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 600; }
.goals-summary__value { font-size: 1.25rem; font-weight: 700; color: #8b5cf6; }

/* Simulator */
.dash-card--simulator { border-left: 4px solid #22c55e; }
.simulator-controls { display: flex; flex-direction: column; gap: 1.5rem; margin-bottom: 1.5rem; }
.simulator-control { display: flex; flex-direction: column; gap: 0.75rem; }
.simulator-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 0.9375rem;
}
.simulator-value { font-weight: 700; color: #3b82f6; }
.simulator-slider {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(90deg, #3b82f6, #22c55e);
  -webkit-appearance: none;
  appearance: none;
}
.simulator-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: white;
  border: 3px solid #3b82f6;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.simulator-presets { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.simulator-preset {
  padding: 0.375rem 0.75rem;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: white;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
}
.simulator-preset:hover { border-color: #3b82f6; color: #3b82f6; }
.simulator-preset--active { background: #3b82f6; border-color: #3b82f6; color: white; }
.scenario-selector { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; }
.scenario-btn {
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 2px solid #e2e8f0;
  background: white;
  cursor: pointer;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.scenario-btn:hover { border-color: #3b82f6; }
.scenario-btn--active { border-color: #3b82f6; background: rgba(59, 130, 246, 0.05); }
.scenario-btn__name { font-weight: 600; font-size: 0.875rem; }
.scenario-btn__return { font-size: 1.125rem; font-weight: 700; }
.scenario-btn--conservative .scenario-btn__return { color: #22c55e; }
.scenario-btn--moderate .scenario-btn__return { color: #3b82f6; }
.scenario-btn--aggressive .scenario-btn__return { color: #f59e0b; }
.scenario-btn--bull .scenario-btn__return { color: #8b5cf6; }
.scenario-btn__desc { font-size: 0.75rem; color: #94a3b8; }
.simulator-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
}
.simulator-summary__item { display: flex; flex-direction: column; gap: 0.25rem; }
.simulator-summary__item--total {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(34, 197, 94, 0.1));
  border: 1px solid rgba(59, 130, 246, 0.2);
}
.simulator-summary__label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
.simulator-summary__value { font-size: 1.25rem; font-weight: 700; }
.simulator-summary__value.interest { color: #22c55e; }
.simulator-summary__value.total {
  font-size: 1.5rem;
  background: linear-gradient(90deg, #3b82f6, #22c55e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Comparison Table */
.dash-card--comparison { border-left: 4px solid #3b82f6; }
.comparison-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.comparison-table th {
  background: #f8fafc;
  font-weight: 600;
  text-align: left;
  padding: 0.75rem 1rem;
  border-bottom: 2px solid #e2e8f0;
}
.comparison-table td { padding: 0.75rem 1rem; border-bottom: 1px solid #e2e8f0; color: #475569; }
.comparison-table__desc { display: block; font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem; }
.comparison-table__value--muted { font-weight: 400; color: #94a3b8; }
.comparison-table__row--highlighted { background: rgba(59, 130, 246, 0.05); }
.comparison-table__footnote { font-size: 0.75rem; color: #94a3b8; margin: 0.75rem 0 0; padding: 0 1rem 1rem; }

/* Disclaimer */
.dash-disclaimer {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  margin-top: 1rem;
  background: rgba(245, 158, 11, 0.05);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 0.75rem;
  border-left: 4px solid #f59e0b;
}
.dash-disclaimer__icon { font-size: 1.5rem; }
.dash-disclaimer__content { flex: 1; }
.dash-disclaimer__title { font-weight: 600; font-size: 0.9375rem; margin: 0 0 0.5rem 0; }
.dash-disclaimer__list { margin: 0; padding-left: 1.25rem; font-size: 0.8125rem; color: #64748b; }
.dash-disclaimer__list li { margin-bottom: 0.25rem; }

/* Projection Fallback */
.projection-fallback { display: flex; align-items: center; justify-content: center; min-height: 200px; color: #64748b; }

/* Buttons */
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
}
.btn--primary { background: #3b82f6; color: white; }
.btn--primary:hover { background: #2563eb; }
.btn--success { background: #22c55e; color: white; }
.btn--success:hover { background: #16a34a; }
.btn--sm { padding: 0.375rem 0.75rem; font-size: 0.8125rem; }

/* Badge */
.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
}
.badge--priority { background: rgba(239, 68, 68, 0.1); color: #ef4444; }

/* Table */
.tabular-num { font-family: 'SF Mono', Consolas, monospace; text-align: right; }
.tabular-num--high { color: #ef4444; font-weight: 600; }
.tabular-num--warning { color: #f59e0b; font-weight: 500; }
</style>
