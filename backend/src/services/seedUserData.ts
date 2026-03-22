/**
 * seedUserData
 *
 * Inserts a full set of realistic demo financial data into Supabase for a
 * newly-registered user.  Called from the sign-up route (and from the
 * email-confirmation route so users who need to confirm still get seeded).
 *
 * Data matches the shape expected by buildFinanceDashboard and the frontend:
 *   - profiles   (UPDATE — row already created by DB trigger)
 *   - debts
 *   - bills
 *   - transactions  (45 days of history)
 *   - risk_indicators
 *   - financial_chart_series
 *
 * Auth strategy:
 *   - If SUPABASE_SERVICE_ROLE_KEY is set → use service-role client (bypasses RLS, always works)
 *   - Else if accessToken is provided → use user-JWT client (works if session was returned on signup)
 *   - Otherwise → skip seeding (log a warning)
 */

import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL || '';
const ANON_KEY = process.env.SUPABASE_ANON_KEY || '';
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

// ── Client factory ─────────────────────────────────────────────────────────────

function makeSeedClient(accessToken?: string): SupabaseClient | null {
  if (!SUPABASE_URL) return null;

  // Prefer service role — bypasses RLS, works even when email confirmation is required
  if (SERVICE_ROLE_KEY) {
    return createClient(SUPABASE_URL, SERVICE_ROLE_KEY, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
  }

  // Fall back to user JWT (only works when the session was returned immediately)
  if (accessToken && ANON_KEY) {
    return createClient(SUPABASE_URL, ANON_KEY, {
      global: { headers: { Authorization: `Bearer ${accessToken}` } },
      auth: { autoRefreshToken: false, persistSession: false },
    });
  }

  return null;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Format a past date as YYYY-MM-DD */
function daysAgo(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().split('T')[0];
}

// ── Seed data definitions ─────────────────────────────────────────────────────

const PROFILE_SEED = {
  monthly_income: 4500,
  checking_balance: 1247.83,
  savings_balance: 823.50,
  credit_score: 634,
  net_worth: -11628.67,
  life_events: [] as string[],
};

function buildDebts(userId: string) {
  return [
    {
      user_id: userId,
      name: 'Chase Visa',
      balance: 3200.00,
      interest_rate: 22.99,
      minimum_payment: 65.00,
      debt_type: 'Credit Card',
      sort_order: 1,
    },
    {
      user_id: userId,
      name: 'Car Loan',
      balance: 8500.00,
      interest_rate: 6.90,
      minimum_payment: 285.00,
      debt_type: 'Auto',
      sort_order: 2,
    },
    {
      user_id: userId,
      name: 'Medical',
      balance: 1400.00,
      interest_rate: 0.00,
      minimum_payment: 50.00,
      debt_type: 'Medical',
      sort_order: 3,
    },
  ];
}

function buildBills(userId: string) {
  const today = new Date();
  const due = (daysFromNow: number) => {
    const d = new Date(today);
    d.setDate(d.getDate() + daysFromNow);
    return d.toISOString().split('T')[0];
  };
  return [
    { user_id: userId, name: 'Chase Visa Minimum', amount: 65.00,  due_date: due(4),  category: 'Debt' },
    { user_id: userId, name: 'Car Loan',           amount: 285.00, due_date: due(12), category: 'Debt' },
    { user_id: userId, name: 'Medical Bill',        amount: 50.00,  due_date: due(18), category: 'Medical' },
    { user_id: userId, name: 'Electric Bill',       amount: 112.00, due_date: due(8),  category: 'Utilities' },
    { user_id: userId, name: 'Internet',            amount: 53.00,  due_date: due(15), category: 'Utilities' },
    { user_id: userId, name: 'Netflix',             amount: 15.99,  due_date: due(21), category: 'Entertainment' },
    { user_id: userId, name: 'Rent',                amount: 1350.00, due_date: due(6), category: 'Housing' },
  ];
}

function buildTransactions(userId: string) {
  // 45 days of realistic transactions. Positive = income, negative = expense.
  const rows: {
    user_id: string;
    occurred_on: string;
    amount: number;
    category: string;
    description: string;
  }[] = [
    // ── Income (bi-weekly paychecks) ──────────────────────────────────────────
    { user_id: userId, occurred_on: daysAgo(1),  amount:  2250.00, category: 'Income',        description: 'Paycheck Deposit' },
    { user_id: userId, occurred_on: daysAgo(15), amount:  2250.00, category: 'Income',        description: 'Paycheck Deposit' },
    { user_id: userId, occurred_on: daysAgo(29), amount:  2250.00, category: 'Income',        description: 'Paycheck Deposit' },
    { user_id: userId, occurred_on: daysAgo(43), amount:  2250.00, category: 'Income',        description: 'Paycheck Deposit' },

    // ── Housing ───────────────────────────────────────────────────────────────
    { user_id: userId, occurred_on: daysAgo(2),  amount: -1350.00, category: 'Housing',       description: 'Rent Payment' },
    { user_id: userId, occurred_on: daysAgo(32), amount: -1350.00, category: 'Housing',       description: 'Rent Payment' },

    // ── Food & Groceries ─────────────────────────────────────────────────────
    { user_id: userId, occurred_on: daysAgo(1),  amount:  -84.32,  category: 'Food',          description: 'Kroger Grocery' },
    { user_id: userId, occurred_on: daysAgo(4),  amount:  -52.18,  category: 'Food',          description: 'Walmart Grocery' },
    { user_id: userId, occurred_on: daysAgo(7),  amount:  -38.45,  category: 'Food',          description: 'Chick-fil-A' },
    { user_id: userId, occurred_on: daysAgo(9),  amount:  -67.21,  category: 'Food',          description: 'Kroger Grocery' },
    { user_id: userId, occurred_on: daysAgo(12), amount:  -24.99,  category: 'Food',          description: 'DoorDash' },
    { user_id: userId, occurred_on: daysAgo(14), amount:  -91.43,  category: 'Food',          description: 'Costco' },
    { user_id: userId, occurred_on: daysAgo(18), amount:  -43.75,  category: 'Food',          description: 'Publix Grocery' },
    { user_id: userId, occurred_on: daysAgo(21), amount:  -31.20,  category: 'Food',          description: 'Chipotle' },
    { user_id: userId, occurred_on: daysAgo(24), amount:  -78.90,  category: 'Food',          description: 'Kroger Grocery' },
    { user_id: userId, occurred_on: daysAgo(28), amount:  -19.50,  category: 'Food',          description: 'Starbucks' },
    { user_id: userId, occurred_on: daysAgo(31), amount:  -55.60,  category: 'Food',          description: 'Whole Foods' },
    { user_id: userId, occurred_on: daysAgo(37), amount:  -42.00,  category: 'Food',          description: 'Chick-fil-A' },
    { user_id: userId, occurred_on: daysAgo(41), amount:  -82.10,  category: 'Food',          description: 'Walmart Grocery' },

    // ── Transport ─────────────────────────────────────────────────────────────
    { user_id: userId, occurred_on: daysAgo(2),  amount:  -52.10,  category: 'Transport',     description: 'Shell Gas Station' },
    { user_id: userId, occurred_on: daysAgo(12), amount: -285.00,  category: 'Debt',          description: 'Car Loan Payment' },
    { user_id: userId, occurred_on: daysAgo(16), amount:  -48.75,  category: 'Transport',     description: 'BP Gas Station' },
    { user_id: userId, occurred_on: daysAgo(33), amount:  -61.20,  category: 'Transport',     description: 'Shell Gas Station' },
    { user_id: userId, occurred_on: daysAgo(42), amount:  -285.00, category: 'Debt',          description: 'Car Loan Payment' },

    // ── Utilities ─────────────────────────────────────────────────────────────
    { user_id: userId, occurred_on: daysAgo(8),  amount: -112.00,  category: 'Utilities',     description: 'Electric Bill' },
    { user_id: userId, occurred_on: daysAgo(10), amount:  -53.00,  category: 'Utilities',     description: 'Internet — Xfinity' },
    { user_id: userId, occurred_on: daysAgo(38), amount: -109.00,  category: 'Utilities',     description: 'Electric Bill' },
    { user_id: userId, occurred_on: daysAgo(40), amount:  -53.00,  category: 'Utilities',     description: 'Internet — Xfinity' },

    // ── Entertainment / Subscriptions ─────────────────────────────────────────
    { user_id: userId, occurred_on: daysAgo(2),  amount:  -15.99,  category: 'Entertainment', description: 'Netflix' },
    { user_id: userId, occurred_on: daysAgo(5),  amount:  -12.99,  category: 'Entertainment', description: 'Spotify' },
    { user_id: userId, occurred_on: daysAgo(11), amount:  -59.99,  category: 'Entertainment', description: 'GameStop' },
    { user_id: userId, occurred_on: daysAgo(20), amount:  -14.99,  category: 'Entertainment', description: 'Hulu' },
    { user_id: userId, occurred_on: daysAgo(32), amount:  -15.99,  category: 'Entertainment', description: 'Netflix' },
    { user_id: userId, occurred_on: daysAgo(35), amount:  -12.99,  category: 'Entertainment', description: 'Spotify' },

    // ── Medical ───────────────────────────────────────────────────────────────
    { user_id: userId, occurred_on: daysAgo(6),  amount:  -35.00,  category: 'Medical',       description: 'CVS Pharmacy' },
    { user_id: userId, occurred_on: daysAgo(18), amount:  -50.00,  category: 'Medical',       description: 'Medical Bill Payment' },
    { user_id: userId, occurred_on: daysAgo(44), amount:  -50.00,  category: 'Medical',       description: 'Medical Bill Payment' },

    // ── Debt payments ─────────────────────────────────────────────────────────
    { user_id: userId, occurred_on: daysAgo(4),  amount:  -65.00,  category: 'Debt',          description: 'Chase Visa Minimum' },
    { user_id: userId, occurred_on: daysAgo(34), amount:  -65.00,  category: 'Debt',          description: 'Chase Visa Minimum' },

    // ── Misc / Shopping ───────────────────────────────────────────────────────
    { user_id: userId, occurred_on: daysAgo(3),  amount:  -34.99,  category: 'Misc',          description: 'Amazon' },
    { user_id: userId, occurred_on: daysAgo(13), amount:  -22.49,  category: 'Misc',          description: 'Target' },
    { user_id: userId, occurred_on: daysAgo(22), amount:  -89.99,  category: 'Misc',          description: 'Amazon' },
    { user_id: userId, occurred_on: daysAgo(30), amount:  -47.50,  category: 'Misc',          description: 'HomeDepot' },
    { user_id: userId, occurred_on: daysAgo(39), amount:  -29.00,  category: 'Misc',          description: 'Walgreens' },
  ];

  return rows;
}

function buildRiskIndicators(userId: string) {
  return [
    {
      user_id: userId,
      slug: 'overdraft',
      probability: 0.72,
      level: 'high',
      label: 'Overdraft Risk',
      factors: JSON.stringify([
        '$1,247 balance vs $1,805 in bills due',
        'No buffer savings',
        'Irregular income deposit dates',
      ]),
    },
    {
      user_id: userId,
      slug: 'missing_payments',
      probability: 0.58,
      level: 'high',
      label: 'Missing Payments',
      factors: JSON.stringify([
        'Chase Visa minimum due in 4 days',
        'Medical bill 12 days overdue',
        'Low checking balance',
      ]),
    },
    {
      user_id: userId,
      slug: 'credit_shift',
      probability: 0.41,
      level: 'moderate',
      label: 'Credit Score Drop',
      factors: JSON.stringify([
        '71% credit utilization',
        'One late payment in last 90 days',
        'No new positive accounts',
      ]),
    },
  ];
}

function buildChartSeries(userId: string) {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const now = new Date();
  const futureMonths = Array.from({ length: 11 }, (_, i) =>
    months[(now.getMonth() + i + 1) % 12]
  );
  const pastMonths = Array.from({ length: 6 }, (_, i) =>
    months[(now.getMonth() - 5 + i + 12) % 12]
  );

  return [
    // Debt payoff timeline
    {
      user_id: userId,
      series_key: 'debt_timeline',
      labels: JSON.stringify(['Now', ...futureMonths]),
      datasets: JSON.stringify([
        {
          label: 'Total Debt',
          data: [13100, 12580, 12040, 11480, 10900, 10300, 9680, 9040, 8380, 7700, 6998, 6272],
          color: '#ef4444',
          fill: true,
        },
      ]),
    },
    // Financial gains
    {
      user_id: userId,
      series_key: 'financial_gains',
      labels: JSON.stringify(pastMonths),
      datasets: JSON.stringify([
        {
          label: 'Net Monthly Gain',
          data: [-820, -340, 150, 280, 520, 730],
          color: '#22c55e',
          fill: true,
        },
        {
          label: 'Savings Balance',
          data: [0, 0, 150, 430, 950, 1680],
          color: '#3b82f6',
          fill: false,
          dashed: true,
        },
      ]),
    },
    // Paycheck split
    {
      user_id: userId,
      series_key: 'paycheck_split',
      labels: JSON.stringify(['Needs', 'Debt Payoff', 'Emergency Fund', 'Investments', 'Discretionary']),
      datasets: JSON.stringify([{ amounts: [2475, 900, 450, 225, 450] }]),
    },
    // Spending breakdown
    {
      user_id: userId,
      series_key: 'spending_breakdown',
      labels: JSON.stringify(['Housing', 'Food', 'Transport', 'Utilities', 'Entertainment', 'Medical', 'Misc']),
      datasets: JSON.stringify([{ amounts: [1350, 680, 290, 165, 180, 95, 210] }]),
    },
  ];
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Seed all demo financial data for a newly created user.
 *
 * Safe to call multiple times — uses upsert/insert-if-not-exists so re-seeding
 * an already-seeded account is harmless.
 *
 * @param userId   auth.users UUID
 * @param accessToken  user's JWT access token (optional — falls back to service role key)
 */
export async function seedUserData(userId: string, accessToken?: string): Promise<void> {
  const supabase = makeSeedClient(accessToken);

  if (!supabase) {
    console.warn(
      '[seed] Cannot seed: set SUPABASE_SERVICE_ROLE_KEY in backend/.env, ' +
      'or ensure sign-up returns a session (disable email confirmation in Supabase).'
    );
    return;
  }

  console.log(`[seed] Seeding demo financial data for user ${userId}…`);

  try {
    // 1. Update profile row (already created by DB trigger) with financial data
    const { error: pErr } = await supabase
      .from('profiles')
      .update(PROFILE_SEED)
      .eq('id', userId);
    if (pErr) console.warn('[seed] profiles update:', pErr.message);

    // 2. Debts — only insert if user has none yet
    const { data: existingDebts } = await supabase
      .from('debts')
      .select('id')
      .eq('user_id', userId)
      .limit(1);

    if (!existingDebts?.length) {
      const { error: dErr } = await supabase.from('debts').insert(buildDebts(userId));
      if (dErr) console.warn('[seed] debts insert:', dErr.message);
    }

    // 3. Bills — only insert if user has none yet
    const { data: existingBills } = await supabase
      .from('bills')
      .select('id')
      .eq('user_id', userId)
      .limit(1);

    if (!existingBills?.length) {
      const { error: bErr } = await supabase.from('bills').insert(buildBills(userId));
      if (bErr) console.warn('[seed] bills insert:', bErr.message);
    }

    // 4. Transactions — only insert if user has none yet
    const { data: existingTx } = await supabase
      .from('transactions')
      .select('id')
      .eq('user_id', userId)
      .limit(1);

    if (!existingTx?.length) {
      const { error: tErr } = await supabase.from('transactions').insert(buildTransactions(userId));
      if (tErr) console.warn('[seed] transactions insert:', tErr.message);
    }

    // 5. Risk indicators — upsert (slug is unique per user)
    const { error: rErr } = await supabase
      .from('risk_indicators')
      .upsert(buildRiskIndicators(userId), { onConflict: 'user_id,slug' });
    if (rErr) console.warn('[seed] risk_indicators upsert:', rErr.message);

    // 6. Chart series — upsert (series_key is unique per user)
    const { error: cErr } = await supabase
      .from('financial_chart_series')
      .upsert(buildChartSeries(userId), { onConflict: 'user_id,series_key' });
    if (cErr) console.warn('[seed] financial_chart_series upsert:', cErr.message);

    console.log(`[seed] ✓ Demo data seeded for user ${userId}`);
  } catch (err) {
    console.error('[seed] Unexpected error:', err);
  }
}
