<template>
  <div class="dash-page dash-page--cash">
    <header class="dash-hero">
      <p class="dash-hero__eyebrow">
        <span class="dash-hero__eyebrow-dot" aria-hidden="true" />
        Checking &amp; spending
      </p>
      <h1 class="dash-hero__title">
        Good morning<template v-if="displayName">, {{ displayName }}</template>
      </h1>
      <p class="dash-hero__sub">
        <span v-if="today">{{ today }} · </span>
        Checking, spending mix, and recent moves—built to surface patterns before they become problems.
      </p>
    </header>

    <p v-if="!data && isLoading" class="dash-page__hint">Loading your dashboard…</p>
    <p v-else-if="!data && !isUsingDummyData" class="dash-page__hint">
      No data loaded. Check that the Node backend has <code>SUPABASE_URL</code> / <code>SUPABASE_ANON_KEY</code> and your Supabase tables exist.
    </p>

    <template v-if="data">
      <section class="dash-mb">
        <div class="dash-section">
          <h2 class="dash-section-title">Overview</h2>
        </div>
        <p class="dash-section-lead">Balances and income snapshot tied to your profile.</p>
        <div class="dash-grid-4">
          <StatCard
            variant="dash"
            label="Monthly income"
            :value="`$${data.user.monthlyIncome.toLocaleString('en-US')}`"
            sub="Estimated cash inflow"
            icon-bg="var(--color-info-dim)"
            value-color="var(--color-info)"
          >
            <template #icon><span style="font-size:1.1rem">💵</span></template>
          </StatCard>
          <StatCard
            variant="dash"
            label="Checking"
            :value="`$${data.accounts.checking.toLocaleString('en-US', { minimumFractionDigits: 2 })}`"
            sub="Primary spending"
            sub-class="text-warn"
            icon-bg="var(--color-warning-dim)"
            value-color="var(--color-warning)"
          >
            <template #icon><span style="font-size:1.1rem">🏦</span></template>
          </StatCard>
          <StatCard
            variant="dash"
            label="Savings"
            :value="`$${data.accounts.savings.toLocaleString('en-US', { minimumFractionDigits: 2 })}`"
            sub="Buffer & goals"
            icon-bg="var(--color-primary-glow)"
            value-color="var(--color-primary)"
          >
            <template #icon><span style="font-size:1.1rem">🛡️</span></template>
          </StatCard>
          <StatCard
            variant="dash"
            label="Credit score"
            :value="data.accounts.creditScore != null ? `${data.accounts.creditScore}` : '—'"
            sub="From your profile"
            icon-bg="var(--color-surface-raised)"
            value-color="var(--color-text)"
          >
            <template #icon><span style="font-size:1.1rem">⭐</span></template>
          </StatCard>
        </div>
      </section>

      <section class="dash-mb dash-checking-spend" aria-labelledby="checking-spend-heading">
        <div class="dash-section">
          <h2 id="checking-spend-heading" class="dash-section-title">Checking &amp; spending</h2>
        </div>
        <p class="dash-section-lead">Spending mix, behavior snapshot, and recent activity.</p>

        <div class="dash-checking-spend__block">
          <h3 class="dash-subsection">Spending mix</h3>
          <div class="dash-grid-2">
            <div class="dash-card dash-card--chart">
              <h3 class="dash-card__title">Category mix</h3>
              <p class="dash-card__sub">Total tracked: ${{ spendingTotal.toLocaleString('en-US') }}</p>
              <div class="dash-chart-wrap">
                <ClientOnly v-if="spendingChartReady">
                  <DonutChart
                    :labels="data.spending.labels"
                    :amounts="data.spending.amounts"
                    :colors="data.spending.colors"
                  />
                  <template #fallback>
                    <div class="dash-chart-fallback" aria-hidden="true" />
                  </template>
                </ClientOnly>
                <p v-else class="dash-page__hint" style="margin: 0; border: none; background: transparent; padding: 1rem 0">
                  Add transactions or a spending series to see the breakdown.
                </p>
              </div>
            </div>
            <div class="dash-card dash-card--muted">
              <h3 class="dash-card__title">Quick category signal</h3>
              <p class="dash-card__sub">From your current spending mix</p>
              <ul class="dash-insight">
                <li>
                  <strong>{{ topSpendCategory.label }}</strong>
                  leads at
                  <strong>${{ topSpendCategory.amount.toLocaleString('en-US') }}</strong>
                  ({{ topSpendCategory.pct }}% of spend).
                </li>
                <li v-if="data.accounts.checking < spendingTotal">
                  Category totals exceed displayed checking—timing of bills vs. deposits may explain the gap.
                </li>
                <li v-else>
                  Behavior analysis in this same tab feeds your AI advisor context.
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="dash-checking-spend__block dash-checking-spend__block--behavior">
          <h3 class="dash-subsection">Behavior &amp; AI insights</h3>
          <p class="dash-checking-spend__behavior-lead">
            Quick read on habits, risks, and next steps.
          </p>
          <BehaviorInsightsPanel
            :behavior="behaviorPayload"
            @agent-action="onBehaviorAgentAction"
          />
        </div>

        <div class="dash-checking-spend__block">
          <h3 class="dash-subsection">Recent activity</h3>
          <p class="dash-checking-spend__behavior-lead" style="margin-top: -0.35rem">
            Latest lines we use to infer rhythm and recurring costs.
          </p>
          <div class="dash-card" style="padding: 0">
            <div class="dash-activity">
              <div
                v-for="tx in data.recentActivity"
                :key="tx.description + tx.date"
                class="dash-activity__row"
              >
                <div>
                  <p class="dash-activity__desc">{{ tx.description }}</p>
                  <p class="dash-activity__meta">{{ tx.date }} · {{ tx.category }}</p>
                </div>
                <p
                  class="dash-activity__amt"
                  :style="{ color: tx.amount > 0 ? 'var(--color-success)' : 'var(--color-text)' }"
                >
                  {{ tx.amount > 0 ? '+' : '' }}${{ Math.abs(tx.amount).toFixed(2) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { defaultBehaviorInsights } from '~/data/behaviorMock'
import type { BehaviorInsightsPayload } from '~/types/behaviorInsights'

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
  ssr: false,
})

const { data, isLoading, isUsingDummyData } = useFinancialData()
const { user } = useAuth()

const displayName = computed(() => {
  const meta = user.value?.user_metadata as Record<string, unknown> | undefined
  if (meta?.legal_first_name) return String(meta.legal_first_name).trim().split(/\s+/)[0] || ''
  const fullName = meta?.full_name ?? meta?.name
  if (typeof fullName === 'string' && fullName) return fullName.split(' ')[0] || ''
  const email = user.value?.email
  if (email) return email.split('@')[0] || ''
  return ''
})

const today = ref('')
onMounted(() => {
  today.value = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
})

const spendingTotal = computed(
  () => data.value?.spending?.amounts?.reduce((s, a) => s + a, 0) ?? 0,
)

const spendingChartReady = computed(() => {
  const s = data.value?.spending
  return Boolean(s?.labels?.length && s.amounts?.length && spendingTotal.value > 0)
})

const topSpendCategory = computed(() => {
  const d = data.value
  if (!d?.spending?.labels?.length) {
    return { label: '—', amount: 0, pct: 0 }
  }
  let maxI = 0
  let maxAmt = 0
  d.spending.amounts.forEach((amt, i) => {
    if (amt > maxAmt) {
      maxAmt = amt
      maxI = i
    }
  })
  const total = spendingTotal.value || 1
  return {
    label: d.spending.labels[maxI] || 'Other',
    amount: maxAmt,
    pct: Math.round((maxAmt / total) * 100),
  }
})

function isUsableBehavior(b: unknown): b is BehaviorInsightsPayload {
  if (!b || typeof b !== 'object') return false
  const o = b as Record<string, unknown>
  return typeof o.score === 'number' && typeof o.aiSummary === 'string'
}

const behaviorPayload = computed<BehaviorInsightsPayload>(() => {
  const raw = data.value as { behavior?: unknown } | null | undefined
  const b = raw?.behavior
  if (isUsableBehavior(b)) return b
  return defaultBehaviorInsights
})

function onBehaviorAgentAction(payload: { actionId: string; actionLabel: string }) {
  // Wire to FastAPI agent / rules engine (e.g. POST agentBase + /api/agent/actions)
  console.info('[behavior → agent]', payload.actionId, payload.actionLabel)
}

useHead({ title: 'Checking & spending — AI Financial' })
</script>

<style scoped>
.text-warn {
  color: var(--color-warning) !important;
}
</style>
