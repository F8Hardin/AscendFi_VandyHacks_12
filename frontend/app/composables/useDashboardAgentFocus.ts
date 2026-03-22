export type DashboardAgentId =
  | 'checking_behavior_risk'
  | 'debt_predictions'
  | 'autonomous_wealth_investment'

/**
 * Maps the current dashboard route to the agent focus sent in chat `context.extra.dashboard_agent`.
 */
export function useDashboardAgentFocus() {
  const route = useRoute()

  const dashboardAgent = computed<DashboardAgentId>(() => {
    const p = route.path
    if (p.startsWith('/dashboard/debt')) return 'debt_predictions'
    if (p.startsWith('/dashboard/autonomous')) return 'autonomous_wealth_investment'
    return 'checking_behavior_risk'
  })

  const agentTitle = computed(() => {
    switch (dashboardAgent.value) {
      case 'debt_predictions':
        return 'Debt & forecasts'
      case 'autonomous_wealth_investment':
        return 'Wealth & investing'
      default:
        return 'Behavior & risk'
    }
  })

  const agentShortLabel = computed(() => {
    switch (dashboardAgent.value) {
      case 'debt_predictions':
        return 'Debt AI'
      case 'autonomous_wealth_investment':
        return 'Wealth AI'
      default:
        return 'Spending AI'
    }
  })

  const welcomeMessage = computed(() => {
    switch (dashboardAgent.value) {
      case 'debt_predictions':
        return "Hi — I'm tuned for debt and payoff strategy. Ask about balances, snowball vs avalanche, or what might happen if you miss a payment."
      case 'autonomous_wealth_investment':
        return "Hi — I'm focused on wealth building and investment-style ideas for your autonomous plan. Ask about emergency funds, allocation, or long-term growth."
      default:
        return "Hi — I'm focused on spending behavior and short-term risk (cash flow, habits, overdraft risk). Ask about your patterns or how to stabilize this month."
    }
  })

  const focusSwitchNote = computed(() => {
    switch (dashboardAgent.value) {
      case 'debt_predictions':
        return "You've switched to Debt & predictions. I'll prioritize debt accounts, payoff order, and forecasts from here."
      case 'autonomous_wealth_investment':
        return "You've switched to Autonomous finance. I'll prioritize savings targets, wealth building, and investment-style next steps."
      default:
        return "You've switched to Checking & spending. I'll prioritize behavior, budgeting, and near-term financial risk."
    }
  })

  return {
    dashboardAgent,
    agentTitle,
    agentShortLabel,
    welcomeMessage,
    focusSwitchNote,
  }
}
