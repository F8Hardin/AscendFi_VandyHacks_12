import type { PayoffStressMode } from '~/types/debtEngines'

type ForecastLineDataset = {
  label: string
  data: number[]
  color: string
  fill?: boolean
  dashed?: boolean
}
import type { ScenarioMods } from '~/utils/debtEnginesCore'
import * as core from '~/utils/debtEnginesCore'

function normalizeSeries(values: number[]): number[] {
  if (!values.length) return []
  const lo = Math.min(...values)
  const hi = Math.max(...values)
  if (hi === lo) return values.map(() => 50)
  return values.map((v) => ((v - lo) / (hi - lo)) * 100)
}

export function useDebtPageEngines() {
  const { data } = useFinancialData()

  const scenarioMods = ref<ScenarioMods>({
    incomeDownPct: 0,
    rentUp: 0,
    debtExtra: 0,
    discretionaryCutPct: 0,
    lumpToDebt: 0,
  })

  const forecastHorizon = ref<'30d' | '3m' | '6m'>('30d')
  const payoffStressMode = ref<PayoffStressMode>('balanced')
  const extraPaymentMonthly = ref(0)

  const snapshot = computed(() => (data.value ? (data.value as unknown as core.DashboardLike) : null))

  const riskCategoriesBase = computed(() =>
    snapshot.value ? core.buildRiskCategories(snapshot.value) : [],
  )

  const riskHeroBase = computed(() =>
    snapshot.value && riskCategoriesBase.value.length
      ? core.buildRiskHero(riskCategoriesBase.value, snapshot.value)
      : null,
  )

  const riskWithScenario = computed(() => {
    if (!snapshot.value || !riskHeroBase.value) return null
    return core.applyScenarioToHero(riskHeroBase.value, riskCategoriesBase.value, scenarioMods.value)
  })

  const riskEngine = computed(() => {
    if (!snapshot.value || !riskWithScenario.value) return null
    const { hero, categories } = riskWithScenario.value
    return {
      hero,
      categories,
      warnings: core.buildPredictiveWarnings(snapshot.value, categories),
      insights: core.buildInsightCards(snapshot.value, categories),
      behavioralPatterns: core.buildBehavioralRiskLines(snapshot.value),
    }
  })

  const mitigationPlan = computed(() =>
    snapshot.value && riskCategoriesBase.value.length
      ? core.buildMitigationPlan(
          snapshot.value,
          riskCategoriesBase.value,
          core.rankDebts(snapshot.value.debts, snapshot.value.user.monthlyIncome),
        )
      : null,
  )

  const forecastRaw = computed(() =>
    snapshot.value ? core.buildForecastSeries(snapshot.value, forecastHorizon.value) : null,
  )

  const forecastChart = computed((): { labels: string[]; datasets: ForecastLineDataset[] } => {
    const f = forecastRaw.value
    if (!f) return { labels: [], datasets: [] }
    return {
      labels: f.labels,
      datasets: [
        { label: 'Risk score', data: f.riskScore, color: '#f59e0b', fill: false },
        {
          label: 'Checking (trend index)',
          data: normalizeSeries(f.balance),
          color: '#38bdf8',
          fill: false,
          dashed: true,
        },
        { label: 'Debt (trend index)', data: normalizeSeries(f.debtPressure), color: '#ef4444', fill: false },
      ],
    }
  })

  const debtRanked = computed(() =>
    snapshot.value ? core.rankDebts(snapshot.value.debts, snapshot.value.user.monthlyIncome) : [],
  )

  const strategiesBase = computed(() =>
    snapshot.value ? core.buildStrategyResults(snapshot.value.debts, 0) : [],
  )

  const strategiesWithExtra = computed(() =>
    snapshot.value ? core.buildStrategyResults(snapshot.value.debts, extraPaymentMonthly.value) : [],
  )

  const highlightedStrategy = computed(() => {
    const list = strategiesBase.value
    const m = payoffStressMode.value
    if (m === 'aggressive') return list.find((s) => s.id === 'avalanche') ?? list[0]
    if (m === 'stability') return list.find((s) => s.id === 'cashflow') ?? list[0]
    if (m === 'credit_repair') return list.find((s) => s.id === 'credit_first') ?? list[0]
    return list.find((s) => s.id === 'hybrid') ?? list[0]
  })

  const debtOverview = computed(() => {
    if (!snapshot.value) return null
    const debts = snapshot.value.debts
    const hybrid = strategiesBase.value.find((s) => s.id === 'hybrid')
    const total = debts.reduce((s, d) => s + d.balance, 0)
    const wapr = core.weightedApr(debts)
    const mins = debts.reduce((s, d) => s + d.min, 0)
    const interest12 = Math.round(core.interestNext12Months(debts))
    const months = hybrid?.months ?? 0
    const end = new Date()
    end.setMonth(end.getMonth() + months)
    return {
      total,
      wapr,
      mins,
      interest12,
      hybrid,
      payoffLabel: months ? end.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : '—',
    }
  })

  const extraPaymentImpact = computed(() =>
    snapshot.value ? core.simulateExtraPayment(snapshot.value.debts, extraPaymentMonthly.value) : null,
  )

  const refinanceHints = computed(() =>
    snapshot.value ? core.refinanceFlags(snapshot.value.debts) : [],
  )

  const optimizationTimeline = computed(() => {
    if (!snapshot.value) return []
    const hy = strategiesBase.value.find((s) => s.id === 'hybrid')
    return core.buildOptimizationTimeline(snapshot.value.debts, hy?.months ?? 24)
  })

  const debtRecommendations = computed(() =>
    snapshot.value && debtRanked.value.length
      ? core.buildDebtRecommendations(snapshot.value, debtRanked.value, strategiesBase.value)
      : [],
  )

  const debtChecklist = computed(() =>
    snapshot.value ? core.buildDebtChecklist(snapshot.value, debtRanked.value) : [],
  )

  const behavioralMilestones = computed(() => [
    { title: 'On-time payments', value: '5 mo', sub: 'Streak helps keep options open' },
    { title: 'Interest drag vs last month', value: '−8%', sub: 'Minimums + small extra payments' },
    { title: 'Next milestone', value: 'Kill one minimum', sub: 'Closest small balance in your stack' },
  ])

  const scenarioStressLabel = computed(() => {
    const m = scenarioMods.value
    const parts: string[] = []
    if (m.incomeDownPct) parts.push(`Income −${m.incomeDownPct}%`)
    if (m.rentUp) parts.push(`Rent +$${m.rentUp}`)
    if (m.debtExtra) parts.push(`Debt +$${m.debtExtra}/mo`)
    if (m.discretionaryCutPct) parts.push(`Discretionary −${m.discretionaryCutPct}%`)
    if (m.lumpToDebt) parts.push(`Lump $${m.lumpToDebt} → debt`)
    return parts.length ? parts.join(' · ') : 'Baseline'
  })

  return {
    data,
    scenarioMods,
    forecastHorizon,
    payoffStressMode,
    extraPaymentMonthly,
    riskEngine,
    mitigationPlan,
    forecastChart,
    forecastRaw,
    debtRanked,
    strategiesBase,
    strategiesWithExtra,
    highlightedStrategy,
    debtOverview,
    extraPaymentImpact,
    refinanceHints,
    optimizationTimeline,
    debtRecommendations,
    debtChecklist,
    behavioralMilestones,
    scenarioStressLabel,
  }
}
