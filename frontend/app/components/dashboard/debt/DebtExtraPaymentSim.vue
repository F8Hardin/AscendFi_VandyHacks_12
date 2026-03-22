<template>
  <div v-if="impact" id="debt-extra-pay-sim" class="debt-extra debt-eng-card">
    <h4 class="debt-extra__title">Extra payment lab</h4>
    <p class="debt-extra__sub">See how steady extra dollars toward the hybrid path change the modeled outcome.</p>
    <div class="debt-extra__presets">
      <button
        v-for="n in presets"
        :key="n"
        type="button"
        class="debt-extra__chip"
        :class="{ 'debt-extra__chip--on': extra === n && !customOn }"
        @click="
          customOn = false;
          extra = n;
        "
      >
        +${{ n }}/mo
      </button>
      <button type="button" class="debt-extra__chip" :class="{ 'debt-extra__chip--on': customOn }" @click="enableCustom">Custom</button>
    </div>
    <label v-if="customOn" class="debt-extra__custom">
      <span>Custom monthly extra</span>
      <input v-model.number="extra" type="number" min="0" max="2000" step="25" />
    </label>
    <div class="debt-extra__out">
      <div>
        <span class="debt-extra__lbl">Months saved</span>
        <strong>{{ impact.monthsSaved }}</strong>
      </div>
      <div>
        <span class="debt-extra__lbl">Interest saved (modeled)</span>
        <strong>${{ impact.interestSaved.toLocaleString('en-US') }}</strong>
      </div>
      <div>
        <span class="debt-extra__lbl">New payoff horizon</span>
        <strong>{{ impact.newMonths }} mo</strong>
      </div>
    </div>
    <p class="debt-extra__fine">
      Paying an extra ${{ extra }}/mo could save roughly ${{ Math.max(0, Math.round(extra * 7)) }} in interest over the first year on high-rate revolving balances (illustrative).
    </p>
  </div>
</template>

<script setup lang="ts">
import type { useDebtPageEngines } from '~/composables/useDebtPageEngines'

const engines = inject('debtEngines') as ReturnType<typeof useDebtPageEngines>
const extraRef = inject<Ref<number> | null>('debtExtraPayment', null)

const presets = [25, 50, 100] as const
const customOn = ref(false)

const extra = computed({
  get: () => extraRef?.value ?? 0,
  set: (v: number) => {
    if (extraRef) extraRef.value = Number.isFinite(v) ? Math.max(0, v) : 0
  },
})

const impact = computed(() => engines?.extraPaymentImpact.value)

function enableCustom() {
  customOn.value = true
  if (extra.value === 0) extra.value = 75
}
</script>

<style scoped>
.debt-extra {
  padding: 1.15rem 1.2rem 1.2rem;
  scroll-margin-top: 5rem;
}
.debt-extra__title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 750;
  color: var(--color-text);
}
.debt-extra__sub {
  margin: 0.35rem 0 0.85rem;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}
.debt-extra__presets {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}
.debt-extra__chip {
  padding: 0.45rem 0.85rem;
  border-radius: 9999px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-raised);
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text-muted);
  cursor: pointer;
}
.debt-extra__chip--on {
  border-color: color-mix(in srgb, var(--eng-green) 45%, var(--color-border));
  background: rgba(34, 197, 94, 0.1);
  color: var(--eng-green);
}
.debt-extra__custom {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.85rem;
  font-size: 0.78rem;
  color: var(--color-text-muted);
}
.debt-extra__custom input {
  width: 6rem;
  padding: 0.4rem 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  font-weight: 700;
}
.debt-extra__out {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}
@media (max-width: 600px) {
  .debt-extra__out {
    grid-template-columns: 1fr;
  }
}
.debt-extra__lbl {
  display: block;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-faint);
}
.debt-extra__out strong {
  display: block;
  margin-top: 0.2rem;
  font-size: 1.2rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}
.debt-extra__fine {
  margin: 0.85rem 0 0;
  font-size: 0.7rem;
  line-height: 1.45;
  color: var(--color-text-faint);
}
</style>
