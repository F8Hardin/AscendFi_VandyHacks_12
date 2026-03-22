import type { BehaviorInsightsPayload } from '~/types/behaviorInsights'

/**
 * Demo **Behavior & AI insights** — kept short so the UI doesn’t overwhelm.
 * API can return longer strings later; the panel also caps how many cards it shows.
 */
export const defaultBehaviorInsights: BehaviorInsightsPayload = {
  score: 58,
  scoreBand: 'unstable',
  trend: {
    direction: 'down',
    text: 'Slipping this week — more late-night spend',
  },
  aiSummary:
    'Most bills are fine; the leak is small night-and-weekend purchases. Taming those protects your buffer without cutting the fun entirely.',

  patterns: {
    timeOfDay: {
      headline: '~40% more spend after 9PM',
      byHour: [
        { label: '8a', amount: 30 },
        { label: '12p', amount: 85 },
        { label: '4p', amount: 45 },
        { label: '8p', amount: 125 },
        { label: '10p', amount: 160 },
        { label: '12a', amount: 90 },
      ],
    },
    dayPattern: {
      headline: 'Peaks on Fri & Sun',
      detail: 'Dining and delivery cluster those days.',
    },
    triggers: [
      'Quiet spell, then several small charges in under half an hour.',
      'Extra discretionary right after payday.',
    ],
    categories: [
      {
        headline: 'Delivery up ~27% vs last month',
        detail: 'Try a weekly cap or one cook-at-home night.',
      },
      {
        headline: 'Two subscriptions barely used',
        detail: '~$28/mo idle — easy pause candidates.',
      },
    ],
  },

  risks: [
    {
      id: 'impulse-week',
      title: 'Six impulse-style buys this week',
      body: 'Tight clusters across different merchants.',
      level: 'high',
      probability: 0.78,
    },
    {
      id: 'overspend-5d',
      title: 'Higher overspend risk next few days',
      body: 'Bills stack mid-week while weekend habit is active.',
      level: 'medium',
      probability: 0.64,
    },
  ],

  forecast: {
    next7Spend: 380,
    changePct: 14,
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    projectedSpend: [45, 48, 44, 52, 72, 68, 51],
    alerts: ['Weekend impulse risk is elevated vs your usual pattern.'],
    aiMessage:
      'At this pace, your savings target slips by roughly two months — mostly from delivery and unplanned weekend spend.',
  },

  recommendations: [
    {
      id: 'guard-late',
      title: 'Quiet hours guard',
      detail: 'Nudge before charges after 10PM.',
      actionLabel: 'Spending Guard',
    },
    {
      id: 'delivery-cap',
      title: 'Cap delivery ~$50/week',
      detail: 'Soft limit with flexibility.',
      actionLabel: 'Set budget',
    },
    {
      id: 'subs-audit',
      title: 'Pause unused subs',
      detail: 'Free ~$28/mo quickly.',
      actionLabel: 'Review',
    },
  ],

  controlDefaults: {
    spendingGuard: false,
    impulseDelay: true,
    categoryLimits: [
      { category: 'Food', max: 400 },
      { category: 'Entertainment', max: 120 },
      { category: 'Shopping', max: 200 },
    ],
    dailyAlertThreshold: 100,
  },

  trends: {
    weekLabels: ['W1', 'W2', 'W3', 'W4', 'W5', 'W6'],
    scores: [50, 52, 49, 54, 56, 58],
    disciplineNote: 'Impulse buys down vs last week — score inching up.',
  },

  goals: {
    items: [
      { name: 'Debt payoff', aligned: false },
      { name: 'Emergency savings', aligned: true },
    ],
    debtProgress: 0.34,
    savingsProgress: 0.41,
    investmentReadiness: 0.22,
  },

  profile: {
    archetypeId: 'reactive_buyer',
    title: 'Reactive buyer',
    emoji: '🧭',
    description: 'Spend ticks up after idle time or stress — lots of small buys that add up.',
    strengths: ['Responds well to simple nudges'],
    weaknesses: ['Late nights & right after payday'],
  },
}
