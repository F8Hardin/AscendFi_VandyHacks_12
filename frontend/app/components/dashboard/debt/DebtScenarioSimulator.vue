<template>
  <div v-if="scenarioMods && risk" class="debt-scenario debt-eng-card">
    <div class="debt-scenario__head">
      <h4 class="debt-scenario__title">Scenario simulator</h4>
      <p class="debt-scenario__stress">{{ stressLabel }}</p>
    </div>
    <div class="debt-scenario__sliders">
      <label class="debt-scenario__row">
        <span>Income −10% steps</span>
        <input v-model.number="scenarioMods.incomeDownPct" type="range" min="0" max="20" step="5" />
        <em>{{ scenarioMods.incomeDownPct }}%</em>
      </label>
      <label class="debt-scenario__row">
        <span>Rent / housing +$</span>
        <input v-model.number="scenarioMods.rentUp" type="range" min="0" max="400" step="25" />
        <em>${{ scenarioMods.rentUp }}</em>
      </label>
      <label class="debt-scenario__row">
        <span>Extra to debt / mo</span>
        <input v-model.number="scenarioMods.debtExtra" type="range" min="0" max="400" step="25" />
        <em>${{ scenarioMods.debtExtra }}</em>
      </label>
      <label class="debt-scenario__row">
        <span>Discretionary cut</span>
        <input v-model.number="scenarioMods.discretionaryCutPct" type="range" min="0" max="40" step="5" />
        <em>{{ scenarioMods.discretionaryCutPct }}%</em>
      </label>
      <label class="debt-scenario__row">
        <span>One-time lump → debt</span>
        <input v-model.number="scenarioMods.lumpToDebt" type="range" min="0" max="2000" step="100" />
        <em>${{ scenarioMods.lumpToDebt }}</em>
      </label>
    </div>
    <div class="debt-scenario__out">
      <div>
        <span class="debt-scenario__out-label">Adjusted risk score</span>
        <strong class="debt-scenario__out-val">{{ risk.hero.score }}</strong>
      </div>
      <div>
        <span class="debt-scenario__out-label">Status</span>
        <strong class="debt-scenario__out-val debt-scenario__out-val--sm">{{ risk.hero.bandLabel }}</strong>
      </div>
      <div>
        <span class="debt-scenario__out-label">Debt load (category)</span>
        <strong class="debt-scenario__out-val debt-scenario__out-val--sm">
          {{ debtCat?.score ?? '—' }}
        </strong>
      </div>
    </div>
    <button type="button" class="debt-scenario__reset" @click="reset">Reset scenarios</button>
  </div>
</template>

<script setup lang="ts">
import type { ScenarioMods } from '~/utils/debtEnginesCore'
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const scenarioMods = inject<Ref<ScenarioMods> | null>('debtScenarioMods', null)
const risk = computed(() => engines?.riskEngine.value)
const stressLabel = computed(() => engines?.scenarioStressLabel.value ?? '')

const debtCat = computed(() => risk.value?.categories.find((c) => c.id === 'debt'))

function reset() {
  if (!scenarioMods) return
  scenarioMods.value.incomeDownPct = 0
  scenarioMods.value.rentUp = 0
  scenarioMods.value.debtExtra = 0
  scenarioMods.value.discretionaryCutPct = 0
  scenarioMods.value.lumpToDebt = 0
}
</script>

<style scoped>
.debt-scenario {
  padding: 1.15rem 1.2rem 1.2rem;
}
.debt-scenario__head {
  margin-bottom: 1rem;
}
.debt-scenario__title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-scenario__stress {
  margin: 0.35rem 0 0;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
.debt-scenario__sliders {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.debt-scenario__row {
  display: grid;
  grid-template-columns: 1fr minmax(0, 9rem) 2.5rem;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.78rem;
  color: var(--color-text-muted);
}
.debt-scenario__row input[type='range'] {
  width: 100%;
  accent-color: var(--eng-blue);
}
.debt-scenario__row em {
  font-style: normal;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
  text-align: right;
}
.debt-scenario__out {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-top: 1.15rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}
@media (max-width: 640px) {
  .debt-scenario__out {
    grid-template-columns: 1fr;
  }
}
.debt-scenario__out-label {
  display: block;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-faint);
}
.debt-scenario__out-val {
  display: block;
  margin-top: 0.2rem;
  font-size: 1.35rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}
.debt-scenario__out-val--sm {
  font-size: 1rem;
}
.debt-scenario__reset {
  margin-top: 1rem;
  padding: 0.45rem 0.85rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface-raised);
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-text-muted);
  cursor: pointer;
}
.debt-scenario__reset:hover {
  color: var(--color-text);
}
</style>
