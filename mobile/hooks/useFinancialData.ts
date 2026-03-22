import { useState, useCallback } from 'react'
import { AGENT_BASE, apiPost } from '@/lib/api'
import { supabase } from '@/lib/supabase'
import { DUMMY_DATA } from '@/lib/dummyData'

export type RiskLevel = 'high' | 'moderate' | 'low'

export interface DashboardData {
  user: { name: string; monthlyIncome: number }
  accounts: { checking: number; savings: number; creditScore: number | null; netWorth?: number }
  risks: Record<string, { probability: number; level: RiskLevel; label: string; factors: string[] }>
  debts: Array<{ name: string; balance: number; rate: number; min: number; type: string; dueInDays: number }>
  spending: { labels: string[]; amounts: number[]; colors: string[] }
  debtTimeline: { labels: string[]; datasets: Array<{ label: string; data: number[]; color: string }> }
  financialGains: { labels: string[]; datasets: Array<{ label: string; data: number[]; color: string; dashed?: boolean }> }
  paycheckSplit: { labels: string[]; amounts: number[]; colors: string[] }
  behavior?: {
    score?: number
    scoreBand?: string
    trend?: string
    aiSummary?: string
    recommendations?: Array<{ priority: string; title: string; description: string; impact?: string }>
    profile?: { archetype?: string; emoji?: string }
  }
  recentActivity: Array<{ date: string; description: string; amount: number; category: string }>
}

export function useFinancialData() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isUsingDummyData, setIsUsingDummyData] = useState(false)
  const [aiError, setAiError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setAiError(null)

    try {
      // Try to build a profile from Supabase user metadata
      const { data: sessionData } = await supabase.auth.getSession()
      const user = sessionData.session?.user

      const profile = user
        ? {
            monthly_income: (user.user_metadata?.monthly_income as number | undefined) ?? 5000,
            checking_balance: (user.user_metadata?.checking_balance as number | undefined) ?? 1200,
            savings_balance: (user.user_metadata?.savings_balance as number | undefined) ?? 800,
            credit_score: (user.user_metadata?.credit_score as number | undefined) ?? 650,
            debts: (user.user_metadata?.debts as unknown[] | undefined) ?? [],
            bills: (user.user_metadata?.bills as unknown[] | undefined) ?? [],
            spending_history: [],
            life_events: [],
          }
        : null

      const result = await apiPost<DashboardData>(`${AGENT_BASE}/dashboard`, profile ?? {})
      setData(result)
      setIsUsingDummyData(false)
    } catch (err) {
      // Fall back to built-in demo data
      setAiError(err instanceof Error ? err.message : String(err))
      setData(DUMMY_DATA)
      setIsUsingDummyData(true)
    } finally {
      setIsLoading(false)
    }
  }, [])

  return { data, isLoading, isUsingDummyData, aiError, refresh }
}
