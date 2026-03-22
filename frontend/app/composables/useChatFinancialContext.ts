/**
 * Maps dashboard financial data (dummy or future Supabase-backed) into the shape
 * expected by backend_agent/container `ChatRequest.context` (FinancialContext).
 */
export function useChatFinancialContext() {
  const { data } = useFinancialData()

  function buildContext():
    | {
        monthly_income: number
        checking_balance: number
        savings_balance: number
        credit_score: number | null
        bills: { name: string; amount: number; due_date: string; category: string }[]
        debts: {
          name: string
          balance: number
          interest_rate: number
          minimum_payment: number
          type: string
        }[]
        spending_history: { date: string; amount: number; category: string; description?: string }[]
        life_events: string[]
        extra?: Record<string, unknown>
      }
    | undefined {
    const d = data.value
    if (!d) return undefined

    const extra: Record<string, unknown> = { net_worth: d.accounts.netWorth }
    const behavior = (d as { behavior?: unknown }).behavior
    if (behavior !== undefined && behavior !== null) {
      extra.behavior = behavior
    }

    return {
      monthly_income: d.user.monthlyIncome,
      checking_balance: d.accounts.checking,
      savings_balance: d.accounts.savings,
      credit_score: d.accounts.creditScore ?? null,
      bills: [],
      debts: d.debts.map((row) => ({
        name: row.name,
        balance: row.balance,
        interest_rate: row.rate,
        minimum_payment: row.min,
        type: row.type,
      })),
      spending_history: d.recentActivity.map((row) => ({
        date: row.date,
        amount: row.amount,
        category: row.category,
        description: row.description,
      })),
      life_events: [],
      extra,
    }
  }

  return { buildContext }
}
