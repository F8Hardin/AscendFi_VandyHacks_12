import type { BehaviorInsightsPayload } from '~/types/behaviorInsights'

/**
 * Rich demo payload for **Behavior & AI insights** on the Checking & spending tab.
 *
 * Loaded when:
 * - `NUXT_PUBLIC_USE_DUMMY_DATA=true` → merged into `dummyData.behavior`
 * - Live API omits `behavior` → `dashboard/index.vue` falls back to this object
 *
 * Replace with `GET /api/finance/dashboard` → `{ behavior: ... }` when the agent is wired.
 */
export const defaultBehaviorInsights: BehaviorInsightsPayload = {
  score: 58,
  scoreBand: 'unstable',
  trend: {
    direction: 'down',
    text: 'Declining this week — late-night and weekend clusters are up',
  },
  aiSummary:
    "Here’s the honest read: you’re doing fine on planned bills, but discretionary spend is leaking through small, frequent charges—especially after 9PM and on Sundays. That pattern doesn’t look scary in any single transaction, but it compounds: it nibbles your buffer and makes surprise bills feel bigger than they are. If we tame the timing (not necessarily the fun), your month-to-month stress drops a lot—and I can help you automate the nudges so you don’t have to white-knuckle it.",

  patterns: {
    timeOfDay: {
      headline: 'You spend about 42% more after 9PM vs your daytime average',
      byHour: [
        { label: '6a', amount: 8 },
        { label: '8a', amount: 28 },
        { label: '10a', amount: 44 },
        { label: '12p', amount: 92 },
        { label: '2p', amount: 36 },
        { label: '4p', amount: 48 },
        { label: '6p', amount: 118 },
        { label: '8p', amount: 138 },
        { label: '10p', amount: 172 },
        { label: '12a', amount: 95 },
      ],
    },
    dayPattern: {
      headline: 'Highest spending on Fridays & Sundays',
      detail:
        'Fridays: dining + rideshare + “one more thing” retail. Sundays: delivery, groceries top-ups, and subscription renewals hitting the same day as leisure spend.',
    },
    triggers: [
      'Impulse purchases detected after long inactivity (3+ hours quiet, then 2–4 small charges within 25 minutes).',
      'Spend velocity increases within 48 hours of income deposits—mostly food delivery, shopping, and entertainment.',
      'Higher approval of “just this once” amounts between 10PM–1AM, often under $35 each but repeating 3–5x per week.',
    ],
    categories: [
      {
        headline: 'Food delivery up 27% vs last month',
        detail:
          'Order count +18%, average ticket +8%. Peak days: Sun, Fri. Cheapest win: batch-cook Sundays or set a soft weekly cap.',
      },
      {
        headline: 'Subscriptions: two services underutilized',
        detail:
          'Streaming bundle B and fitness app C logged almost no opens in 30 days—~$28/mo combined sitting idle.',
      },
      {
        headline: 'Shopping “misc” is spiky, not steady',
        detail:
          'Amazon / convenience retail shows burst patterns (4 days with spend, then quiet)—classic boredom or stress triggers.',
      },
      {
        headline: 'Transport is predictable; food is not',
        detail:
          'Gas and transit are flat week-over-week; variance is almost entirely meals and delivery—good target for rules.',
      },
    ],
  },

  risks: [
    {
      id: 'impulse-week',
      title: 'Impulse spending flagged 6 times this week',
      body: 'Unrelated merchants in tight windows suggest reactive buying rather than a planned list.',
      level: 'high',
      probability: 0.78,
    },
    {
      id: 'overspend-5d',
      title: 'Elevated chance of overspend in the next 5 days',
      body: 'Utilities + rent timing overlaps with your Friday–Sunday spend habit in the model.',
      level: 'medium',
      probability: 0.64,
    },
    {
      id: 'income-threshold',
      title: 'Discretionary spend above modeled “safe lane” for your income',
      body: 'Delivery + shopping + entertainment = ~22% of take-home vs a 15% comfort target in this demo profile.',
      level: 'medium',
      probability: 0.71,
    },
    {
      id: 'weekend-cluster',
      title: 'Weekend cluster risk: Sunday night repeat pattern',
      body: 'Past 8 weeks: 6 Sundays had above-median spend; often starts with delivery, then add-on retail.',
      level: 'low',
      probability: 0.38,
    },
  ],

  forecast: {
    next7Spend: 412,
    changePct: 18,
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    projectedSpend: [48, 52, 47, 55, 78, 82, 50],
    alerts: [
      'High probability of impulse-style purchases this weekend (model confidence driven by day-of-week + time-of-day history).',
      'Friday 6–10PM window is your #1 spend hotspot—consider a soft guard or pre-set “fun budget” before Friday hits.',
    ],
    aiMessage:
      'If the next 4 weeks look like the last 4, your emergency savings milestone lands about two months later than your stated target—not because of rent, but because of recurring small discretionary drift. Tightening delivery and late-night caps alone closes most of that gap in the simulation.',
  },

  recommendations: [
    {
      id: 'guard-late',
      title: 'Limit late-night purchases',
      detail:
        'Quiet-hours guard: gentle friction after 10PM (SMS or in-app) before charges post—proven to cut reactive buys without killing flexibility.',
      actionLabel: 'Activate Spending Guard',
    },
    {
      id: 'delivery-cap',
      title: 'Trim food delivery by ~$50/week',
      detail:
        'A weekly soft cap with rollover keeps spontaneity but stops autopilot. Pair with one “cook night” reminder on Sundays.',
      actionLabel: 'Set Budget',
    },
    {
      id: 'subs-audit',
      title: 'Pause unused subscriptions',
      detail:
        'Two low-usage services = ~$28/mo. Pausing for 60 days is reversible and frees buffer immediately.',
      actionLabel: 'Review Now',
    },
    {
      id: 'friday-bucket',
      title: 'Pre-load a Friday “fun” bucket',
      detail:
        'Move $80 to a labeled sub-account or envelope Friday morning—when it’s empty, the rule is “pause,” not shame.',
      actionLabel: 'Create Bucket',
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
    weekLabels: ['Jan W1', 'Jan W2', 'Jan W3', 'Feb W1', 'Feb W2', 'Feb W3'],
    scores: [48, 52, 49, 55, 54, 58],
    disciplineNote:
      'Impulse spending ↓ 23% vs last week (you skipped late-night orders Tue–Thu). Behavior score uptick is mostly from timing, not deprivation.',
  },

  goals: {
    items: [
      { name: 'Debt payoff pace', aligned: false },
      { name: 'Emergency savings', aligned: true },
      { name: 'Investment readiness', aligned: false },
    ],
    debtProgress: 0.34,
    savingsProgress: 0.41,
    investmentReadiness: 0.22,
  },

  profile: {
    archetypeId: 'reactive_buyer',
    title: 'The Reactive Buyer',
    emoji: '🧭',
    description:
      'You spend more when emotionally charged or after long quiet stretches—then you “catch up” with a burst of small purchases that feel harmless individually.',
    strengths: [
      'You adjust quickly when you see the pattern spelled out',
      'Mid-week resets work for you better than “monthly resolutions”',
    ],
    weaknesses: [
      'Late-night vulnerability (10PM–1AM)',
      'Post-paycheck splurge window (first 48 hours after deposit)',
    ],
  },
}
