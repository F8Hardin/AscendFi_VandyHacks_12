export const dummyData = {
  user: {
    name: 'Alex Johnson',
    monthlyIncome: 4500,
  },

  accounts: {
    checking: 1247.83,
    savings: 823.50,
    creditScore: 634,
    netWorth: -11628.67,
  },

  risks: {
    overdraft: {
      probability: 0.72,
      level: 'high',
      label: 'Overdraft Risk',
      factors: ['$1,247 balance vs $1,805 in bills due', 'No buffer savings', 'Irregular income deposit dates'],
    },
    missingPayments: {
      probability: 0.58,
      level: 'high',
      label: 'Missing Payments',
      factors: ['Chase Visa minimum due in 4 days', 'Medical bill 12 days overdue', 'Low checking balance'],
    },
    creditShift: {
      probability: 0.41,
      level: 'moderate',
      label: 'Credit Score Drop',
      factors: ['71% credit utilization', 'One late payment in last 90 days', 'No new positive accounts'],
    },
  },

  debts: [
    { name: 'Chase Visa', balance: 3200, rate: 22.99, min: 65, type: 'Credit Card' },
    { name: 'Car Loan',   balance: 8500, rate: 6.90,  min: 285, type: 'Auto'        },
    { name: 'Medical',   balance: 1400, rate: 0,     min: 50,  type: 'Medical'     },
  ],

  spending: {
    labels: ['Housing', 'Food', 'Transport', 'Utilities', 'Entertainment', 'Medical', 'Misc'],
    amounts: [1350, 680, 290, 165, 180, 95, 210],
    colors: ['var(--chart-1)', 'var(--chart-2)', 'var(--chart-3)', 'var(--chart-4)', 'var(--chart-5)', 'var(--chart-6)', 'var(--chart-7)'],
  },

  debtTimeline: {
    labels: ['Now', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb'],
    balances: [13100, 12580, 12040, 11480, 10900, 10300, 9680, 9040, 8380, 7700, 6998, 6272],
  },

  paycheckSplit: {
    labels: ['Needs', 'Debt Payoff', 'Emergency Fund', 'Investments', 'Discretionary'],
    amounts: [2475, 900, 450, 225, 450],
    colors: ['var(--chart-1)', 'var(--color-danger)', 'var(--chart-2)', 'var(--chart-4)', 'var(--chart-3)'],
  },

  recentActivity: [
    { date: 'Mar 20', description: 'Kroger Grocery',    amount: -84.32,  category: 'Food'          },
    { date: 'Mar 19', description: 'Netflix',           amount: -15.99,  category: 'Entertainment' },
    { date: 'Mar 19', description: 'Paycheck Deposit',  amount: 2250.00, category: 'Income'        },
    { date: 'Mar 18', description: 'Shell Gas Station', amount: -52.10,  category: 'Transport'     },
    { date: 'Mar 17', description: 'Chase Visa Min',    amount: -65.00,  category: 'Debt'          },
    { date: 'Mar 16', description: 'Amazon',            amount: -34.99,  category: 'Misc'          },
    { date: 'Mar 15', description: 'Electric Bill',     amount: -112.00, category: 'Utilities'     },
  ],
}
