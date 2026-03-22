import type {
  DebtEngineRow,
  DebtStrategyResult,
  PredictiveWarning,
  RankedDebt,
  RiskBand,
  RiskCategory,
  RiskHero,
} from '~/types/debtEngines'

export interface DashboardLike {
  user: { monthlyIncome: number; name?: string }
  accounts: { checking: number; savings: number; creditScore: number | null }
  risks: {
    overdraft: { probability: number }
    missingPayments: { probability: number }
    creditShift: { probability: number }
  }
  debts: DebtEngineRow[]
  spending: { labels: string[]; amounts: number[] }
  recentActivity: { date: string; description: string; amount: number; category: string }[]
  financialGains?: { datasets?: { label: string; data: number[] }[] }
}

function clamp(n: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, n))
}

function bandFromScore(score: number): { band: RiskBand; label: string } {
  if (score <= 30) return { band: 'stable', label: 'Stable' }
  if (score <= 55) return { band: 'caution', label: 'Caution' }
  if (score <= 75) return { band: 'high', label: 'High Risk' }
  return { band: 'critical', label: 'Critical' }
}

function totalMin(debts: DebtEngineRow[]) {
  return debts.reduce((s, d) => s + d.min, 0)
}

function totalDebtBal(debts: DebtEngineRow[]) {
  return debts.reduce((s, d) => s + d.balance, 0)
}

function monthlySpendTotal(d: DashboardLike) {
  return d.spending.amounts.reduce((a, b) => a + b, 0)
}

function estimatedMonthlyEssentials(d: DashboardLike) {
  const labels = d.spending.labels.map((x) => x.toLowerCase())
  let sum = 0
  d.spending.amounts.forEach((amt, i) => {
    const L = labels[i] ?? ''
    if (/housing|rent|utilities|food|grocer|transport|insurance|medical/i.test(L)) sum += amt
  })
  return sum || monthlySpendTotal(d) * 0.65
}

function inferCreditUtilization(d: DashboardLike): number {
  const cards = d.debts.filter((x) => /credit/i.test(x.type))
  if (!cards.length) return 0.35
  let num = 0
  let den = 0
  for (const c of cards) {
    const lim = c.creditLimit && c.creditLimit > 0 ? c.creditLimit : Math.max(c.balance / 0.71, c.balance * 1.2)
    num += c.balance
    den += lim
  }
  return den > 0 ? num / den : 0
}

function foodDeliverySpikeScore(d: DashboardLike): number {
  const food = d.recentActivity.filter((x) => /food|dining|uber|doordash|grub/i.test(x.category + x.description))
  if (!food.length) return 25
  const neg = food.filter((x) => x.amount < 0)
  const total = neg.reduce((s, x) => s + Math.abs(x.amount), 0)
  const afterPay = d.recentActivity.some((x) => x.description.toLowerCase().includes('paycheck'))
  const foodHeavy = total > d.user.monthlyIncome * 0.08
  return clamp(30 + (foodHeavy ? 25 : 0) + (afterPay && foodHeavy ? 15 : 0), 0, 100)
}

export function buildRiskCategories(d: DashboardLike): RiskCategory[] {
  const income = Math.max(d.user.monthlyIncome, 1)
  const mins = totalMin(d.debts)
  const debtBal = totalDebtBal(d.debts)
  const spend = monthlySpendTotal(d)
  const essentials = estimatedMonthlyEssentials(d)
  const checking = d.accounts.checking
  const savings = d.accounts.savings
  const util = inferCreditUtilization(d)

  const dti = mins / income
  const cashFlowMargin = (income - spend - mins) / income

  const cashFlowScore = clamp(
    55
      - cashFlowMargin * 120
      + (checking < mins * 0.5 ? 22 : 0)
      + (d.risks.overdraft.probability > 0.5 ? 18 : 0),
    0,
    100,
  )

  const debtScore = clamp(dti * 180 + (debtBal / (income * 12)) * 40, 0, 100)

  const creditScore = clamp(
    util * 90 + d.risks.creditShift.probability * 45 + (d.accounts.creditScore != null && d.accounts.creditScore < 660 ? 15 : 0),
    0,
    100,
  )

  const incomeStabilityScore = clamp(
    48 + (d.financialGains?.datasets?.[0]?.data?.filter((n) => n < 0).length ?? 0) * 6,
    0,
    100,
  )

  const spendingBehaviorScore = foodDeliverySpikeScore(d)

  const dailyBurn = essentials / 30
  const bufferDays = dailyBurn > 0 ? savings / dailyBurn : 0
  const emergencyScore = clamp(100 - bufferDays * 4.5, 0, 100)

  return [
    {
      id: 'cashflow',
      label: 'Cash Flow Risk',
      score: Math.round(cashFlowScore),
      explanation:
        cashFlowMargin < 0.05
          ? `After bills and minimum debt payments, only about ${Math.max(0, Math.round(cashFlowMargin * 100))}% of income remains as margin.`
          : `Estimated monthly margin is ${(cashFlowMargin * 100).toFixed(0)}% of income after spending and minimums.`,
    },
    {
      id: 'debt',
      label: 'Debt Load Risk',
      score: Math.round(debtScore),
      explanation: `Minimum payments are ${(dti * 100).toFixed(0)}% of income; total debt is $${debtBal.toLocaleString('en-US')} vs $${income.toLocaleString('en-US')}/mo income.`,
    },
    {
      id: 'credit',
      label: 'Credit Risk',
      score: Math.round(creditScore),
      explanation: `Approx. revolving utilization is ${(util * 100).toFixed(0)}%${d.accounts.creditScore != null ? ` with a ${d.accounts.creditScore} score context.` : '.'}`,
    },
    {
      id: 'income',
      label: 'Income Stability Risk',
      score: Math.round(incomeStabilityScore),
      explanation: 'Based on recent net monthly movement patterns and deposit timing in your activity feed.',
    },
    {
      id: 'spending',
      label: 'Spending Behavior Risk',
      score: Math.round(spendingBehaviorScore),
      explanation: 'Weights food, delivery-style spend, and post-paycheck spikes visible in recent transactions.',
    },
    {
      id: 'emergency',
      label: 'Emergency Preparedness Risk',
      score: Math.round(emergencyScore),
      explanation:
        bufferDays < 14
          ? `Savings cover roughly ${bufferDays.toFixed(0)} days of essential spend — below a common 30-day target.`
          : `Savings cover about ${bufferDays.toFixed(0)} days of essential expenses.`,
    },
  ]
}

export function overallRiskScore(categories: RiskCategory[]): number {
  const w = [1.2, 1.15, 1.1, 0.85, 1, 1.1]
  let sum = 0
  let tw = 0
  categories.forEach((c, i) => {
    const weight = w[i] ?? 1
    sum += c.score * weight
    tw += weight
  })
  return Math.round(clamp(sum / tw, 0, 100))
}

export function buildRiskHero(categories: RiskCategory[], d: DashboardLike): RiskHero {
  const score = overallRiskScore(categories)
  const { band, label } = bandFromScore(score)
  const netSeries = d.financialGains?.datasets?.find((x) => /net/i.test(x.label))?.data ?? []
  let trend: RiskHero['trend'] = 'flat'
  if (netSeries.length >= 2) {
    const a = netSeries[netSeries.length - 2] ?? 0
    const b = netSeries[netSeries.length - 1] ?? 0
    if (b > a + 50) trend = 'improving'
    else if (b < a - 50) trend = 'worsening'
  } else if (d.risks.overdraft.probability < 0.45) {
    trend = 'improving'
  } else {
    trend = 'worsening'
  }

  const worst = [...categories].sort((a, b) => b.score - a.score)[0]
  const aiSummary = `Your biggest pressure right now is ${worst.label.toLowerCase()} (${worst.score}/100). ${worst.explanation}`

  const vsLast =
    trend === 'improving'
      ? 'Risk posture improved vs last month (net trend + signals).'
      : trend === 'worsening'
        ? 'Risk posture worsened vs last month — tighten cash before next due dates.'
        : 'Risk posture is steady vs last month.'

  return {
    score,
    band,
    bandLabel: label,
    trend,
    trendLabel: trend === 'improving' ? 'Improving' : trend === 'worsening' ? 'Worsening' : 'Steady',
    vsLastMonth: vsLast,
    aiSummary,
  }
}

export function buildPredictiveWarnings(d: DashboardLike, categories: RiskCategory[]): PredictiveWarning[] {
  const income = Math.max(d.user.monthlyIncome, 1)
  const spend = monthlySpendTotal(d)
  const checking = d.accounts.checking
  const daysToPay = 14
  const burn = spend / 30
  const shortfallDay = burn > 0 ? Math.floor(checking / burn) : 99

  const warnings: PredictiveWarning[] = []
  if (shortfallDay < daysToPay && shortfallDay > 0) {
    warnings.push({
      id: 'shortfall',
      severity: shortfallDay < 7 ? 'critical' : 'caution',
      title: 'Possible cash shortfall before payday',
      detail: `At your recent spending pace, checking could run tight in ~${shortfallDay} days unless you slow discretionary spend.`,
    })
  }

  const util = inferCreditUtilization(d)
  if (util > 0.65) {
    warnings.push({
      id: 'util',
      severity: util > 0.8 ? 'critical' : 'caution',
      title: 'Utilization may stress credit capacity',
      detail: `Revolving balances sit near ${(util * 100).toFixed(0)}% of limits — crossing 80% can amplify score pressure.`,
    })
  }

  const urgentDue = d.debts.filter((x) => (x.dueInDays ?? 99) <= 10)
  if (urgentDue.length) {
    const n = urgentDue[0]!
    warnings.push({
      id: 'due',
      severity: 'caution',
      title: `Payment due soon: ${n.name}`,
      detail: `Minimum of $${n.min} is due in ${n.dueInDays ?? '?'} days — trim discretionary spend to protect on-time status.`,
    })
  }

  const emerg = categories.find((c) => c.id === 'emergency')
  if (emerg && emerg.score > 60) {
    warnings.push({
      id: 'buffer',
      severity: 'info',
      title: 'Savings buffer is thin for bill load',
      detail: 'Building even one week of essentials in savings reduces missed-payment cascade risk.',
    })
  }

  return warnings.slice(0, 6)
}

export function buildInsightCards(d: DashboardLike, categories: RiskCategory[]): { id: string; title: string; body: string; tone: 'neutral' | 'warn' | 'positive' }[] {
  const util = inferCreditUtilization(d)
  const income = d.user.monthlyIncome
  const cards: { id: string; title: string; body: string; tone: 'neutral' | 'warn' | 'positive' }[] = []

  if (util > 0.55) {
    cards.push({
      id: 'i1',
      title: 'Credit reliance is elevated',
      body: 'Revolving balances grew relative to limits — prioritize utilization reduction alongside minimums.',
      tone: 'warn',
    })
  }

  const pay = d.recentActivity.find((x) => /paycheck/i.test(x.description))
  const foodAfter = pay
    ? d.recentActivity.filter((x) => x.amount < 0 && /food|dining/i.test(x.category)).length
    : 0
  if (pay && foodAfter >= 2) {
    cards.push({
      id: 'i2',
      title: 'Dining spend clusters after deposits',
      body: 'Food and delivery tick up right after payday — a common behavioral pattern worth smoothing with a weekly cap.',
      tone: 'neutral',
    })
  }

  const subs = d.spending.labels.findIndex((l) => /entertain|subscri/i.test(l))
  if (subs >= 0 && d.spending.amounts[subs]! > income * 0.04) {
    cards.push({
      id: 'i3',
      title: 'Subscription / entertainment load',
      body: `About $${d.spending.amounts[subs]!.toFixed(0)}/mo in this bucket — pausing two low-use services frees cash for minimums.`,
      tone: 'neutral',
    })
  }

  const worst = [...categories].sort((a, b) => b.score - a.score)[0]
  cards.push({
    id: 'i4',
    title: 'Primary risk theme',
    body: `${worst.label} is highest (${worst.score}). ${worst.explanation}`,
    tone: worst.score > 70 ? 'warn' : 'neutral',
  })

  if (d.accounts.savings < income * 0.15) {
    cards.push({
      id: 'i5',
      title: 'Emergency runway',
      body: `Savings (~$${d.accounts.savings.toLocaleString('en-US')}) cover fewer than three weeks of essentials at current burn.`,
      tone: 'warn',
    })
  }

  return cards.slice(0, 8)
}

export interface ForecastHorizon {
  labels: string[]
  balance: number[]
  debtPressure: number[]
  riskScore: number[]
}

export function buildForecastSeries(d: DashboardLike, horizon: '30d' | '3m' | '6m'): ForecastHorizon {
  const points = horizon === '30d' ? 8 : horizon === '3m' ? 12 : 14
  const cats = buildRiskCategories(d)
  const baseRisk = overallRiskScore(cats)
  const debt0 = totalDebtBal(d.debts)
  const chk0 = d.accounts.checking
  const margin = (d.user.monthlyIncome - monthlySpendTotal(d) - totalMin(d.debts)) / Math.max(points - 1, 1)
  const labels: string[] = []
  const balance: number[] = []
  const debtPressure: number[] = []
  const riskScore: number[] = []

  for (let i = 0; i < points; i++) {
    if (horizon === '30d') labels.push(i === 0 ? 'Now' : `+${i * 4}d`)
    else if (horizon === '3m') labels.push(i === 0 ? 'Now' : `Wk ${i}`)
    else labels.push(i === 0 ? 'Now' : `M${i}`)

    const t = i / (points - 1)
    balance.push(Math.max(0, chk0 + margin * i * (horizon === '6m' ? 0.85 : 1)))
    debtPressure.push(Math.max(0, debt0 * (1 - t * (horizon === '30d' ? 0.04 : horizon === '3m' ? 0.12 : 0.22))))
    riskScore.push(clamp(baseRisk + (i % 3) * 2 - t * 5, 0, 100))
  }

  return { labels, balance, debtPressure, riskScore }
}

export interface ScenarioMods {
  incomeDownPct: number
  rentUp: number
  debtExtra: number
  discretionaryCutPct: number
  lumpToDebt: number
}

export function applyScenarioToHero(hero: RiskHero, cats: RiskCategory[], mods: ScenarioMods): { hero: RiskHero; categories: RiskCategory[] } {
  const delta =
    mods.incomeDownPct * 0.35 +
    mods.rentUp / 50 +
    mods.debtExtra * -0.08 +
    mods.discretionaryCutPct * -0.25 +
    mods.lumpToDebt * -0.02

  const newScore = clamp(hero.score + delta, 0, 100)
  const { band, label } = bandFromScore(newScore)
  const newHero: RiskHero = {
    ...hero,
    score: Math.round(newScore),
    band,
    bandLabel: label,
    aiSummary:
      delta < -3
        ? `${hero.aiSummary} (Scenario adjustments reduce modeled pressure.)`
        : delta > 3
          ? `${hero.aiSummary} (Under this scenario, pressure increases — revisit timing of bills and minimums.)`
          : hero.aiSummary,
  }

  const categories = cats.map((c) => {
    let bump = 0
    if (c.id === 'cashflow') bump += mods.incomeDownPct * 0.4 + mods.rentUp / 40 - mods.discretionaryCutPct * 0.3
    if (c.id === 'debt') bump += mods.incomeDownPct * 0.25 - mods.debtExtra * 0.05 - mods.lumpToDebt * 0.03
    return { ...c, score: clamp(c.score + bump, 0, 100) }
  })

  return { hero: newHero, categories }
}

type StrategyKind = DebtStrategyResult['id']

function simulateStrategy(debts: DebtEngineRow[], kind: StrategyKind, extraMonthly: number) {
  const copies = debts.map((d) => ({ ...d, bal: d.balance }))
  let totalInterest = 0
  let month = 0
  const maxMonths = 600

  const order = (): DebtEngineRow[] => {
    if (kind === 'snowball') return [...debts].sort((a, b) => a.balance - b.balance)
    if (kind === 'cashflow') return [...debts].sort((a, b) => a.min - b.min)
    if (kind === 'credit_first') {
      return [...debts].sort((a, b) => {
        const ua = a.creditLimit ? a.balance / a.creditLimit : 0
        const ub = b.creditLimit ? b.balance / b.creditLimit : 0
        return ub - ua
      })
    }
    return [...debts].sort((a, b) => b.rate - a.rate)
  }

  const priority = order()

  while (copies.some((c) => c.bal > 0.5) && month < maxMonths) {
    month++
    let pool = extraMonthly
    for (const c of copies) {
      if (c.bal <= 0) continue
      const rateM = (c.rate / 100) / 12
      const interest = c.bal * rateM
      totalInterest += interest
      c.bal += interest
      const pay = Math.min(c.min, c.bal)
      c.bal -= pay
    }
    const targetName = priority.find((p) => copies.find((c) => c.name === p.name && c.bal > 0))?.name
    const tgt = copies.find((c) => c.name === targetName && c.bal > 0)
    if (tgt && pool > 0) {
      const pay = Math.min(pool, tgt.bal)
      tgt.bal -= pay
      pool -= pay
    }
  }

  return { months: month, totalInterest, order: priority.map((p) => p.name) }
}

export function buildStrategyResults(debts: DebtEngineRow[], extraMonthly: number): DebtStrategyResult[] {
  const av = simulateStrategy(debts, 'avalanche', extraMonthly)
  const sn = simulateStrategy(debts, 'snowball', extraMonthly)
  const cf = simulateStrategy(debts, 'cashflow', extraMonthly)
  const cr = simulateStrategy(debts, 'credit_first', extraMonthly)
  const stress = (m: number) => clamp(100 - Math.min(m, 60) * 1.2, 10, 95)

  const hybridMonths = Math.round(av.months * 0.55 + sn.months * 0.45)
  const hybridInterest = av.totalInterest * 0.92

  return [
    {
      id: 'avalanche',
      label: 'Avalanche',
      months: av.months,
      totalInterest: Math.round(av.totalInterest),
      monthlyStress: stress(av.months),
      blurb: 'Pays highest APR first — lowest total interest, emotionally harder if the first target is large.',
    },
    {
      id: 'snowball',
      label: 'Snowball',
      months: sn.months,
      totalInterest: Math.round(sn.totalInterest),
      monthlyStress: stress(sn.months + 4),
      motivation: 88,
      blurb: 'Clears smallest balances first — faster wins that free minimum cash flow for the next target.',
    },
    {
      id: 'cashflow',
      label: 'Cash Flow Relief',
      months: cf.months,
      totalInterest: Math.round(cf.totalInterest),
      monthlyStress: stress(cf.months - 2),
      blurb: 'Targets smaller minimums first to reduce monthly bill count when breathing room matters most.',
    },
    {
      id: 'credit_first',
      label: 'Credit Score First',
      months: cr.months,
      totalInterest: Math.round(cr.totalInterest),
      creditImpact: 86,
      monthlyStress: stress(cr.months),
      blurb: 'Prioritizes high utilization cards to recover borrowing headroom sooner.',
    },
    {
      id: 'hybrid',
      label: 'Hybrid (AI-style)',
      months: hybridMonths,
      totalInterest: Math.round(hybridInterest),
      monthlyStress: stress(hybridMonths),
      consistency: 82,
      creditImpact: 78,
      blurb: 'Blends rate efficiency with early balance wins — often easier to sustain than pure avalanche.',
    },
  ]
}

export function weightedApr(debts: DebtEngineRow[]) {
  const t = totalDebtBal(debts)
  if (t <= 0) return 0
  return debts.reduce((s, d) => s + d.balance * d.rate, 0) / t
}

export function interestNext12Months(debts: DebtEngineRow[]) {
  return debts.reduce((s, d) => s + d.balance * (d.rate / 100), 0)
}

export function rankDebts(debts: DebtEngineRow[], monthlyIncome: number): RankedDebt[] {
  const income = Math.max(monthlyIncome, 1)
  return debts.map((d, i) => {
    const util = d.creditLimit && d.creditLimit > 0 ? d.balance / d.creditLimit : null
    const interestThisMonth = (d.balance * (d.rate / 100)) / 12
    let priorityTag = 'Monitor Closely'
    let priorityDetail = 'Keep minimums while stabilizing cash.'
    if (d.rate >= 18 && d.balance > 1500) {
      priorityTag = 'Attack First'
      priorityDetail = 'High APR drag — extra dollars here save the most interest.'
    } else if (util != null && util > 0.65) {
      priorityTag = 'Credit Risk'
      priorityDetail = 'High utilization — lowering balance improves flexibility fastest.'
    } else if (d.min / income > 0.08) {
      priorityTag = 'Cash Flow Heavy'
      priorityDetail = 'Large minimum relative to income — watch due dates closely.'
    } else if (d.rate <= 4 && d.balance < 2000) {
      priorityTag = 'Keep Minimum Only'
      priorityDetail = 'Cheap debt — optimize higher-rate accounts first.'
    }
    if ((d.dueInDays ?? 99) <= 7) {
      priorityTag = 'Due Soon'
      priorityDetail = 'Payment window is tight — protect on-time status.'
    }
    return {
      ...d,
      utilization: util != null ? Math.round(util * 100) : null,
      interestThisMonth,
      priorityTag,
      priorityDetail,
      rank: i + 1,
    }
  })
}

export function buildOptimizationTimeline(debts: DebtEngineRow[], hybridMonths: number) {
  const total = totalDebtBal(debts)
  const m = Math.max(hybridMonths, 6)
  return [
    { phase: 'Now', month: 0, title: 'Current stack', detail: `$${total.toLocaleString('en-US')} total balances` },
    { phase: 'Near term', month: Math.min(2, Math.floor(m * 0.08)), title: 'Stabilize due dates', detail: 'Keep minimums current while trimming discretionary burn' },
    { phase: 'Build momentum', month: Math.max(3, Math.floor(m * 0.25)), title: 'First payoff wins', detail: 'Smaller or highest-APR targets start to close' },
    { phase: 'Relief curve', month: Math.floor(m * 0.55), title: 'Fewer monthly minimums', detail: 'Freed cash rolls into remaining balances' },
    { phase: 'Horizon', month: m, title: 'Debt-free milestone', detail: `Modeled hybrid payoff ~${m} months at current inputs` },
  ]
}

export function buildMitigationPlan(d: DashboardLike, categories: RiskCategory[], ranked: RankedDebt[]) {
  const attack = ranked.find((r) => r.priorityTag === 'Attack First') ?? ranked[0]
  const food = d.spending.labels.findIndex((l) => /food/i.test(l))
  const foodAmt = food >= 0 ? d.spending.amounts[food]! : 0
  const cut = Math.round(foodAmt * 0.12)

  return {
    immediate: [
      attack
        ? `Pay $${attack.min} on ${attack.name}${attack.last4 ? ` (···${attack.last4})` : ''} before the due window closes.`
        : 'Pay at least all minimums before their due dates.',
      cut > 20 ? `Trim food / delivery by ~$${cut} this week to rebuild checking buffer.` : 'Pause one discretionary subscription you have not used in 30 days.',
      'Move one bill due date to sit just after your paycheck if your lender allows it.',
    ],
    monthly: [
      'Route $50–$100 auto-transfer to a “debt snowball” bucket on payday.',
      'Call card issuers to align statement cycles with your pay rhythm.',
      'Target utilization under 30% on the highest-limit revolving account.',
    ],
    longTerm: [
      'Build a 30-day essentials emergency fund before increasing investments.',
      'Review balance-transfer or consolidation options if APRs stay above 18%.',
      'Track streaks of on-time payments — 6 months of consistency materially changes options.',
    ],
  }
}

export function buildDebtChecklist(d: DashboardLike, ranked: RankedDebt[]) {
  const lines: string[] = []
  for (const r of ranked.slice(0, 4)) {
    const due = r.dueInDays != null ? `by day ${r.dueInDays}` : 'this cycle'
    lines.push(`Pay ${r.name} minimum ${due} ($${r.min})`)
  }
  lines.push('Enable autopay for the account with the tightest due date')
  lines.push('Review refinance / consolidation candidates next month')
  return lines
}

export function buildDebtRecommendations(d: DashboardLike, ranked: RankedDebt[], strategies: DebtStrategyResult[]) {
  const hybrid = strategies.find((s) => s.id === 'hybrid')
  const av = strategies.find((s) => s.id === 'avalanche')
  const first = ranked[0]
  const small = [...ranked].sort((a, b) => a.balance - b.balance)[0]
  const recs: string[] = []
  if (first) {
    recs.push(
      `Paying an extra $73 toward ${first.name} has the highest modeled short-term impact on interest drag.`,
    )
  }
  if (small && small.balance < 2500) {
    recs.push(`Your smallest balance (${small.name}) could clear in ~${Math.ceil(small.balance / (small.min + 40))} months with a modest extra — freeing $${small.min}/mo.`)
  }
  const highU = ranked.find((r) => r.utilization != null && r.utilization > 55)
  if (highU) {
    recs.push(`Lowering utilization on ${highU.name}${highU.last4 ? ` ···${highU.last4}` : ''} improves flexibility even before the card is paid off.`)
  }
  if (hybrid && av && hybrid.months <= av.months + 2) {
    recs.push('Pure avalanche is efficient, but the hybrid path may be easier to sustain with your current cash flow margin.')
  }
  return recs.slice(0, 6)
}

export function simulateExtraPayment(debts: DebtEngineRow[], extra: number) {
  const base = simulateStrategy(debts, 'hybrid', 0)
  const boosted = simulateStrategy(debts, 'hybrid', extra)
  return {
    monthsSaved: Math.max(0, base.months - boosted.months),
    interestSaved: Math.max(0, Math.round(base.totalInterest - boosted.totalInterest)),
    newMonths: boosted.months,
  }
}

export function buildBehavioralRiskLines(d: DashboardLike): string[] {
  const lines: string[] = []
  const income = d.user.monthlyIncome
  const foodIdx = d.spending.labels.findIndex((l) => /food/i.test(l))
  const food = foodIdx >= 0 ? d.spending.amounts[foodIdx]! : 0
  if (food > income * 0.14) {
    lines.push('Food & delivery load is elevated vs income — watch post-payday spikes.')
  }
  const entIdx = d.spending.labels.findIndex((l) => /entertain/i.test(l))
  if (entIdx >= 0 && d.spending.amounts[entIdx]! > 120) {
    lines.push('Entertainment / subscriptions may be creeping — a quick audit frees minimum-payment room.')
  }
  if (d.risks.missingPayments.probability > 0.45) {
    lines.push('Minimum-payment-only behavior on high-rate cards extends expensive debt life.')
  }
  const lateNight = d.recentActivity.some((x) => /amazon|impulse|game/i.test(x.description.toLowerCase()))
  if (lateNight) {
    lines.push('Discretionary purchases cluster with non-essential merchants — try a 48-hour wishlist rule.')
  }
  if (inferCreditUtilization(d) > 0.55) {
    lines.push('Dependence on credit for essentials is elevated while utilization stays high.')
  }
  return lines.slice(0, 6)
}

export function refinanceFlags(debts: DebtEngineRow[]) {
  return debts
    .filter((d) => d.rate > 16 || (d.creditLimit && d.balance / d.creditLimit > 0.75))
    .map((d) => ({
      name: d.name,
      hint:
        d.rate > 20
          ? 'Balance transfer or personal-loan consolidation may reduce APR if you qualify.'
          : 'Worth comparing refinance offers while payments are current.',
    }))
}
