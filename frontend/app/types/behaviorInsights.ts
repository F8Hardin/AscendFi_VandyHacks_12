/**
 * Shape for AI / agent-backed spending behavior (Checking tab).
 * Backend can return `behavior` on the finance dashboard payload; until then the UI uses defaults.
 */
export type BehaviorScoreBand = 'disciplined' | 'unstable' | 'risky'

export type BehaviorTrendDirection = 'up' | 'down' | 'steady'

export interface BehaviorRiskItem {
  id: string
  title: string
  body: string
  level: 'low' | 'medium' | 'high'
  /** 0–1, surfaced as % in UI */
  probability: number
}

export interface BehaviorRecommendation {
  id: string
  title: string
  detail: string
  actionLabel: string
}

export interface BehaviorCategoryLimit {
  category: string
  max: number
}

export interface BehaviorInsightsPayload {
  score: number
  scoreBand: BehaviorScoreBand
  trend: { direction: BehaviorTrendDirection; text: string }
  aiSummary: string
  patterns: {
    timeOfDay: { headline: string; byHour: { label: string; amount: number }[] }
    dayPattern: { headline: string; detail: string }
    triggers: string[]
    categories: { headline: string; detail: string }[]
  }
  risks: BehaviorRiskItem[]
  forecast: {
    next7Spend: number
    changePct: number
    labels: string[]
    projectedSpend: number[]
    alerts: string[]
    aiMessage: string
  }
  recommendations: BehaviorRecommendation[]
  controlDefaults: {
    spendingGuard: boolean
    impulseDelay: boolean
    categoryLimits: BehaviorCategoryLimit[]
    dailyAlertThreshold: number
  }
  trends: {
    weekLabels: string[]
    scores: number[]
    disciplineNote: string
  }
  goals: {
    items: { name: string; aligned: boolean }[]
    debtProgress: number
    savingsProgress: number
    investmentReadiness: number
  }
  profile: {
    archetypeId: string
    title: string
    emoji: string
    description: string
    strengths: string[]
    weaknesses: string[]
  }
}
