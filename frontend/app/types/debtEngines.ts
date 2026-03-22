/** Dashboard debt row — optional fields enriched in dummy / API. */
export interface DebtEngineRow {
  name: string
  balance: number
  rate: number
  min: number
  type: string
  dueInDays?: number
  creditLimit?: number
  last4?: string
}

export type RiskBand = 'stable' | 'caution' | 'high' | 'critical'

export interface RiskCategory {
  id: string
  label: string
  score: number
  explanation: string
}

export interface PredictiveWarning {
  id: string
  severity: 'info' | 'caution' | 'critical'
  title: string
  detail: string
}

export interface RiskHero {
  score: number
  band: RiskBand
  bandLabel: string
  trend: 'improving' | 'flat' | 'worsening'
  trendLabel: string
  vsLastMonth: string
  aiSummary: string
}

export interface DebtStrategyResult {
  id: 'avalanche' | 'snowball' | 'cashflow' | 'credit_first' | 'hybrid'
  label: string
  months: number
  totalInterest: number
  monthlyStress: number
  motivation?: number
  consistency?: number
  creditImpact?: number
  blurb: string
}

export interface RankedDebt extends DebtEngineRow {
  utilization: number | null
  interestThisMonth: number
  priorityTag: string
  priorityDetail: string
  rank: number
}

export type PayoffStressMode = 'aggressive' | 'balanced' | 'stability' | 'credit_repair'
