<template>
  <div class="dash-page dash-page--debt debt-engines">
    <header class="dash-hero dash-hero--compact">
      <p class="dash-hero__eyebrow">
        <span class="dash-hero__eyebrow-dot" aria-hidden="true" />
        Command center · Debt &amp; predictions
      </p>
      <h1 class="dash-hero__title">Risk detection &amp; debt strategy</h1>
      <p class="dash-hero__sub">
        Early-warning risk scoring plus payoff optimization — modeled from your dashboard data, not personalized investment advice.
      </p>
    </header>

    <p v-if="!data && isLoading" class="dash-page__hint">Loading…</p>
    <p v-else-if="!data && !isUsingDummyData" class="dash-page__hint">
      Connect Supabase or enable demo data to see this tab.
    </p>

    <template v-if="data">
      <!-- Financial Risk Engine -->
      <section class="debt-eng-section" aria-labelledby="risk-engine-title">
        <div class="debt-eng-section__head">
          <div>
            <span class="debt-eng-pill">Engine 1</span>
            <h2 id="risk-engine-title" class="debt-eng-section__title">Financial Risk Engine</h2>
            <p class="debt-eng-section__sub">
              Understand stability, emerging risks, and what to do before you slip deeper — like a personal early-warning system.
            </p>
          </div>
        </div>

        <div class="debt-eng-stack">
          <DebtRiskHero />
          <DebtRiskCategoryGrid />
          <div class="debt-eng-split">
            <div>
              <h3 class="debt-eng-h3">AI insight feed</h3>
              <DebtInsightFeed />
            </div>
            <div>
              <DebtBehavioralStrip />
            </div>
          </div>
          <DebtForecastPanel />
          <div class="debt-eng-split">
            <DebtScenarioSimulator />
            <DebtActionPlan />
          </div>
        </div>
      </section>

      <!-- Debt Optimization Engine -->
      <section class="debt-eng-section" aria-labelledby="debt-opt-title">
        <div class="debt-eng-section__head">
          <div>
            <span class="debt-eng-pill">Engine 2</span>
            <h2 id="debt-opt-title" class="debt-eng-section__title">Debt Optimization Engine</h2>
            <p class="debt-eng-section__sub">
              One place for balances, strategies, and allocation ideas — built to answer “what’s the smartest way to pay this down?”
            </p>
          </div>
        </div>

        <div class="debt-eng-stack">
          <DebtOptimizationHero />
          <DebtStackCards />
          <DebtStrategyCompare />
          <div class="debt-eng-split debt-eng-split--wide">
            <DebtOptimizationTimeline />
            <div class="debt-eng-col">
              <DebtExtraPaymentSim />
              <DebtRecommendationFeed />
            </div>
          </div>
          <DebtMilestonesRow />
          <DebtActionChecklist />
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
const engines = useDebtPageEngines()

provide('debtEngines', engines)
provide('debtScenarioMods', engines.scenarioMods)
provide('debtPayoffMode', engines.payoffStressMode)
provide('debtExtraPayment', engines.extraPaymentMonthly)

useHead({ title: 'Debt & predictions — AI Financial' })
</script>

<style scoped>
.dash-hero--compact {
  margin-bottom: 1.75rem;
}
.debt-eng-stack {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.debt-eng-split {
  display: grid;
  gap: 1.25rem;
}
@media (min-width: 900px) {
  .debt-eng-split {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }
  .debt-eng-split--wide {
    grid-template-columns: 1fr 1.15fr;
  }
}
.debt-eng-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.debt-eng-h3 {
  margin: 0 0 0.5rem;
  font-size: 0.82rem;
  font-weight: 750;
  color: var(--color-text);
}
</style>
