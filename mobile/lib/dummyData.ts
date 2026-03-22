import type { DashboardData } from '@/hooks/useFinancialData'

export const DUMMY_DATA: DashboardData = {
  user: { name: 'Demo User', monthlyIncome: 5000 },
  accounts: { checking: 1240.50, savings: 820.00, creditScore: 648, netWorth: -8500 },
  risks: {
    overdraft: { probability: 0.42, level: 'moderate', label: 'Overdraft Risk', factors: ['Low checking buffer', 'Rent due in 3 days'] },
    missingPayments: { probability: 0.18, level: 'low', label: 'Missed Payment', factors: ['All bills covered this month'] },
    creditShift: { probability: 0.65, level: 'high', label: 'Credit Score Drop', factors: ['High credit utilization', 'Recent hard inquiry'] },
  },
  debts: [
    { name: 'Visa Credit Card', balance: 4500, rate: 22.99, min: 90, type: 'credit_card', dueInDays: 12 },
    { name: 'Student Loan', balance: 18200, rate: 5.50, min: 185, type: 'student_loan', dueInDays: 22 },
    { name: 'Car Loan', balance: 6800, rate: 7.25, min: 280, type: 'auto', dueInDays: 8 },
  ],
  spending: {
    labels: ['Housing', 'Food', 'Transport', 'Subscriptions', 'Other'],
    amounts: [1400, 480, 320, 95, 210],
    colors: ['#6366f1', '#22c55e', '#f59e0b', '#38bdf8', '#a78bfa'],
  },
  debtTimeline: {
    labels: ['Now', 'Month 3', 'Month 6', 'Month 9', 'Year 1', 'Year 2'],
    datasets: [{ label: 'Total Debt', data: [29500, 28200, 26800, 25200, 23500, 18000], color: '#ef4444' }],
  },
  financialGains: {
    labels: ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
    datasets: [
      { label: 'Net Monthly Gain', data: [120, 240, 80, 310, 190, 420], color: '#22c55e' },
      { label: 'Savings Balance', data: [400, 500, 420, 620, 700, 820], color: '#6366f1', dashed: true },
    ],
  },
  paycheckSplit: {
    labels: ['Needs', 'Debt Payoff', 'Emergency Fund', 'Investments', 'Discretionary'],
    amounts: [2000, 750, 300, 250, 700],
    colors: ['#6366f1', '#ef4444', '#22c55e', '#38bdf8', '#f59e0b'],
  },
  behavior: {
    score: 52,
    scoreBand: 'At Risk',
    trend: 'improving',
    aiSummary: 'Your spending patterns show improvement. High credit utilization is your biggest risk — paying down the Visa card will have the most impact on your score.',
    recommendations: [
      { priority: 'high', title: 'Pay down Visa card', description: 'Add $200/mo to your Visa to save $840 in interest and boost credit score.', impact: 'Save $840/year' },
      { priority: 'medium', title: 'Build $500 emergency buffer', description: 'You\'re $320 short of a minimal safety net.', impact: 'Reduce overdraft risk by 40%' },
      { priority: 'low', title: 'Review subscriptions', description: '$95/mo in subscriptions — audit for unused services.', impact: 'Potential $30-50/mo savings' },
    ],
    profile: { archetype: 'Financial Survivor', emoji: '🆘' },
  },
  recentActivity: [
    { date: '2026-03-21', description: 'Paycheck deposit', amount: 2500, category: 'Income' },
    { date: '2026-03-20', description: 'Whole Foods', amount: -82.40, category: 'Food' },
    { date: '2026-03-19', description: 'Netflix', amount: -15.99, category: 'Subscriptions' },
    { date: '2026-03-18', description: 'Gas station', amount: -45.00, category: 'Transport' },
    { date: '2026-03-17', description: 'Rent payment', amount: -1400, category: 'Housing' },
    { date: '2026-03-15', description: 'Visa minimum payment', amount: -90, category: 'Debt' },
  ],
}
