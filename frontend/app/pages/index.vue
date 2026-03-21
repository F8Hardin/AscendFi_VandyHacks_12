<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dashboard__header">
      <div>
        <h1 class="dashboard__title">Good morning, {{ data?.user.name.split(' ')[0] }} 👋</h1>
        <p class="dashboard__date">{{ today }} · Financial Recovery Dashboard</p>
      </div>
    </div>

    <template v-if="data">
      <!-- ── KPI Row ──────────────────────────────────────────────── -->
      <section class="grid-4 mb-section">
        <StatCard
          label="Monthly Income"
          :value="`$${data.user.monthlyIncome.toLocaleString()}`"
          sub="Bi-weekly deposits"
          icon-bg="var(--color-info-dim)"
          value-color="var(--color-info)"
        >
          <template #icon><span style="font-size:1.1rem">💵</span></template>
        </StatCard>

        <StatCard
          label="Checking Balance"
          :value="`$${data.accounts.checking.toLocaleString('en-US', { minimumFractionDigits: 2 })}`"
          sub="⚠ Low — bills incoming"
          sub-class="text-warning"
          icon-bg="var(--color-warning-dim)"
          value-color="var(--color-warning)"
        >
          <template #icon><span style="font-size:1.1rem">🏦</span></template>
        </StatCard>

        <StatCard
          label="Total Debt"
          :value="`$${totalDebt.toLocaleString()}`"
          :sub="`${data.debts.length} accounts`"
          icon-bg="var(--color-danger-dim)"
          value-color="var(--color-danger)"
        >
          <template #icon><span style="font-size:1.1rem">📉</span></template>
        </StatCard>

        <StatCard
          label="Credit Score"
          :value="`${data.accounts.creditScore}`"
          sub="Fair — improving path available"
          icon-bg="var(--color-primary-glow)"
          value-color="var(--color-primary)"
        >
          <template #icon><span style="font-size:1.1rem">⭐</span></template>
        </StatCard>
      </section>

      <!-- ── Risk Gauges ──────────────────────────────────────────── -->
      <section class="mb-section">
        <h2 class="section-title">Risk Indicators</h2>
        <div class="grid-3">
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

      <!-- ── Charts Row ───────────────────────────────────────────── -->
      <section class="grid-2 mb-section">
        <!-- Spending Breakdown -->
        <div class="card">
          <h3 class="card__title">Monthly Spending Breakdown</h3>
          <p class="card__sub">Total: ${{ spendingTotal.toLocaleString() }}</p>
          <ClientOnly>
            <DonutChart
              :labels="data.spending.labels"
              :amounts="data.spending.amounts"
              :colors="data.spending.colors"
            />
          </ClientOnly>
        </div>

        <!-- Debt Payoff Timeline -->
        <div class="card">
          <h3 class="card__title">Debt Payoff Projection</h3>
          <p class="card__sub">
            Est. payoff: <span style="color:var(--color-primary)">~12 months</span> with optimized plan
          </p>
          <div style="height: 260px; margin-top: 1rem;">
            <ClientOnly>
              <LineChart
                :labels="data.debtTimeline.labels"
                :balances="data.debtTimeline.balances"
              />
            </ClientOnly>
          </div>
        </div>
      </section>

      <!-- ── Bottom Row ───────────────────────────────────────────── -->
      <section class="grid-2 mb-section">
        <!-- Paycheck Split -->
        <div class="card">
          <h3 class="card__title">Recommended Paycheck Split</h3>
          <p class="card__sub">Based on ${{ data.user.monthlyIncome.toLocaleString() }}/mo income</p>
          <ClientOnly>
            <DonutChart
              :labels="data.paycheckSplit.labels"
              :amounts="data.paycheckSplit.amounts"
              :colors="data.paycheckSplit.colors"
              cutout="60%"
            />
          </ClientOnly>
        </div>

        <!-- Debt Table + Activity -->
        <div class="card">
          <h3 class="card__title">Active Debts</h3>
          <div class="debt-list">
            <div v-for="debt in data.debts" :key="debt.name" class="debt-row">
              <div>
                <p class="debt-row__name">{{ debt.name }}</p>
                <p class="debt-row__type">{{ debt.type }} · {{ debt.rate }}% APR</p>
              </div>
              <div class="debt-row__right">
                <p class="debt-row__balance">${{ debt.balance.toLocaleString() }}</p>
                <p class="debt-row__min">min ${{ debt.min }}/mo</p>
              </div>
              <div class="debt-row__bar-wrap">
                <div
                  class="debt-row__bar"
                  :style="{ width: `${(debt.balance / totalDebt) * 100}%`, background: debtColor(debt.type) }"
                />
              </div>
            </div>
          </div>

          <h3 class="card__title" style="margin-top: 1.5rem">Recent Activity</h3>
          <div class="activity-list">
            <div v-for="tx in data.recentActivity" :key="tx.description + tx.date" class="activity-row">
              <div>
                <p class="activity-row__desc">{{ tx.description }}</p>
                <p class="activity-row__date">{{ tx.date }} · {{ tx.category }}</p>
              </div>
              <p
                class="activity-row__amount"
                :style="{ color: tx.amount > 0 ? 'var(--color-success)' : 'var(--color-text)' }"
              >
                {{ tx.amount > 0 ? '+' : '' }}${{ Math.abs(tx.amount).toFixed(2) }}
              </p>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
const { data } = useFinancialData()

const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })

const totalDebt = computed(() =>
  data.value?.debts.reduce((s, d) => s + d.balance, 0) ?? 0
)

const spendingTotal = computed(() =>
  data.value?.spending.amounts.reduce((s, a) => s + a, 0) ?? 0
)

function debtColor(type: string) {
  const map: Record<string, string> = {
    'Credit Card': '#ef4444',
    'Auto': '#3b82f6',
    'Medical': '#f59e0b',
  }
  return map[type] ?? '#6b7280'
}
</script>

<style scoped>
.dashboard { max-width: 1200px; margin: 0 auto; }
.dashboard__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.dashboard__title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
}
.dashboard__date {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}
.mb-section { margin-bottom: 2rem; }
.section-title {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--color-text-muted);
  margin-bottom: 1rem;
}
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  padding: 1.25rem;
}
.card__title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.2rem;
}
.card__sub {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: 0.5rem;
}

/* Debt list */
.debt-list { display: flex; flex-direction: column; gap: 1rem; margin-top: 0.75rem; }
.debt-row { position: relative; padding-bottom: 0.75rem; border-bottom: 1px solid var(--color-border); }
.debt-row:last-child { border-bottom: none; }
.debt-row { display: grid; grid-template-columns: 1fr auto; gap: 0.25rem; }
.debt-row__bar-wrap { grid-column: 1 / -1; height: 3px; background: var(--color-surface-raised); border-radius: 9999px; overflow: hidden; }
.debt-row__bar { height: 100%; border-radius: 9999px; transition: width 1s ease; }
.debt-row__name { font-size: 0.875rem; font-weight: 600; color: var(--color-text); }
.debt-row__type { font-size: 0.72rem; color: var(--color-text-muted); margin-top: 0.1rem; }
.debt-row__balance { font-size: 0.9rem; font-weight: 700; color: var(--color-danger); text-align: right; }
.debt-row__min { font-size: 0.7rem; color: var(--color-text-muted); text-align: right; }

/* Activity */
.activity-list { display: flex; flex-direction: column; gap: 0.625rem; margin-top: 0.75rem; }
.activity-row { display: flex; justify-content: space-between; align-items: center; }
.activity-row__desc { font-size: 0.8rem; color: var(--color-text); }
.activity-row__date { font-size: 0.7rem; color: var(--color-text-muted); margin-top: 0.1rem; }
.activity-row__amount { font-size: 0.875rem; font-weight: 600; }

.text-warning { color: var(--color-warning) !important; }
</style>
