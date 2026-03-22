<template>
  <div v-if="plan" id="debt-action-plan" class="debt-plan debt-eng-card">
    <h4 class="debt-plan__title">Personalized mitigation plan</h4>
    <p class="debt-plan__sub">Mapped from your highest risk categories and debt stack — not a legal promise of outcomes.</p>
    <div class="debt-plan__cols">
      <div class="debt-plan__col">
        <h5 class="debt-plan__tier">Immediate</h5>
        <ul>
          <li v-for="(x, i) in plan.immediate" :key="'i' + i">{{ x }}</li>
        </ul>
      </div>
      <div class="debt-plan__col">
        <h5 class="debt-plan__tier">This month</h5>
        <ul>
          <li v-for="(x, i) in plan.monthly" :key="'m' + i">{{ x }}</li>
        </ul>
      </div>
      <div class="debt-plan__col">
        <h5 class="debt-plan__tier">Long-term</h5>
        <ul>
          <li v-for="(x, i) in plan.longTerm" :key="'l' + i">{{ x }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const plan = computed(() => engines?.mitigationPlan.value)
</script>

<style scoped>
.debt-plan {
  padding: 1.15rem 1.2rem 1.25rem;
  scroll-margin-top: 5rem;
}
.debt-plan__title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-plan__sub {
  margin: 0.35rem 0 1rem;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}
.debt-plan__cols {
  display: grid;
  gap: 1.15rem;
}
@media (min-width: 768px) {
  .debt-plan__cols {
    grid-template-columns: repeat(3, 1fr);
  }
}
.debt-plan__tier {
  margin: 0 0 0.5rem;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--dash-accent-text);
}
.debt-plan__col ul {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.debt-plan__col li + li {
  margin-top: 0.4rem;
}
</style>
