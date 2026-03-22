import type { SupabaseClient } from '@supabase/supabase-js';

const SPENDING_COLORS = [
  'var(--chart-1)',
  'var(--chart-2)',
  'var(--chart-3)',
  'var(--chart-4)',
  'var(--chart-5)',
  'var(--chart-6)',
  'var(--chart-7)',
];

type RiskRow = {
  slug: string;
  probability: number;
  level: string;
  label: string;
  factors: unknown;
};

function defaultRisks() {
  return {
    overdraft: {
      probability: 0,
      level: 'low',
      label: 'Overdraft Risk',
      factors: [] as string[],
    },
    missingPayments: {
      probability: 0,
      level: 'low',
      label: 'Missing Payments',
      factors: [] as string[],
    },
    creditShift: {
      probability: 0,
      level: 'low',
      label: 'Credit Score Drop',
      factors: [] as string[],
    },
  };
}

function normalizeFactors(f: unknown): string[] {
  if (Array.isArray(f)) return f.map((x) => String(x));
  return [];
}

function mapRisks(rows: RiskRow[]) {
  const out = defaultRisks();
  const bySlug = Object.fromEntries(rows.map((r) => [r.slug, r]));
  const apply = (slug: string, key: keyof ReturnType<typeof defaultRisks>) => {
    const r = bySlug[slug];
    if (!r) return;
    const factors = normalizeFactors(r.factors);
    out[key] = {
      probability: Number(r.probability),
      level: r.level,
      label: r.label,
      factors,
    };
  };
  apply('overdraft', 'overdraft');
  apply('missing_payments', 'missingPayments');
  apply('credit_shift', 'creditShift');
  return out;
}

export async function buildFinanceDashboard(supabase: SupabaseClient, userId: string) {
  const { data: profile, error: pErr } = await supabase.from('profiles').select('*').eq('id', userId).maybeSingle();

  if (pErr) {
    throw new Error(pErr.message);
  }

  const [{ data: debts }, { data: riskRows }, { data: txRows }, { data: seriesRows }] = await Promise.all([
    supabase.from('debts').select('*').eq('user_id', userId).order('sort_order', { ascending: true }),
    supabase.from('risk_indicators').select('*').eq('user_id', userId),
    supabase.from('transactions').select('*').eq('user_id', userId).order('occurred_on', { ascending: false }).limit(40),
    supabase.from('financial_chart_series').select('*').eq('user_id', userId),
  ]);

  const displayName =
    profile?.display_name?.trim() ||
    [profile?.legal_first_name, profile?.legal_last_name].filter(Boolean).join(' ').trim() ||
    'Member';

  const monthlyIncome = profile?.monthly_income != null ? Number(profile.monthly_income) : 0;
  const checking = profile?.checking_balance != null ? Number(profile.checking_balance) : 0;
  const savings = profile?.savings_balance != null ? Number(profile.savings_balance) : 0;
  const creditScore = profile?.credit_score != null ? profile.credit_score : null;
  const netWorth = profile?.net_worth != null ? Number(profile.net_worth) : 0;

  const debtsOut =
    debts?.map((d) => ({
      name: d.name,
      balance: Number(d.balance),
      rate: Number(d.interest_rate),
      min: Number(d.minimum_payment),
      type: d.debt_type || 'Other',
    })) ?? [];

  const risks = mapRisks((riskRows ?? []) as RiskRow[]);

  const seriesMap = Object.fromEntries((seriesRows ?? []).map((s) => [s.series_key, s]));

  const spendingSeries = seriesMap['spending_breakdown'];
  let spending = {
    labels: [] as string[],
    amounts: [] as number[],
    colors: [] as string[],
  };
  if (spendingSeries?.labels && spendingSeries?.datasets) {
    try {
      const labels = spendingSeries.labels as string[];
      const ds = spendingSeries.datasets as { amounts?: number[] }[];
      const amounts = ds[0]?.amounts ?? [];
      spending = {
        labels,
        amounts,
        colors: labels.map((_, i) => SPENDING_COLORS[i % SPENDING_COLORS.length]),
      };
    } catch {
      /* fall through to aggregate */
    }
  }
  if (spending.labels.length === 0 && txRows?.length) {
    const byCat = new Map<string, number>();
    for (const t of txRows) {
      if (Number(t.amount) >= 0) continue;
      const c = t.category || 'Misc';
      byCat.set(c, (byCat.get(c) || 0) + Math.abs(Number(t.amount)));
    }
    const entries = [...byCat.entries()].sort((a, b) => b[1] - a[1]);
    spending = {
      labels: entries.map(([k]) => k),
      amounts: entries.map(([, v]) => Math.round(v * 100) / 100),
      colors: entries.map((_, i) => SPENDING_COLORS[i % SPENDING_COLORS.length]),
    };
  }

  const debtTimeline =
    seriesMap['debt_timeline']?.labels && seriesMap['debt_timeline']?.datasets
      ? {
          labels: seriesMap['debt_timeline'].labels as string[],
          datasets: seriesMap['debt_timeline'].datasets as Record<string, unknown>[],
        }
      : {
          labels: [] as string[],
          datasets: [] as Record<string, unknown>[],
        };

  const financialGains =
    seriesMap['financial_gains']?.labels && seriesMap['financial_gains']?.datasets
      ? {
          labels: seriesMap['financial_gains'].labels as string[],
          datasets: seriesMap['financial_gains'].datasets as Record<string, unknown>[],
        }
      : {
          labels: [] as string[],
          datasets: [] as Record<string, unknown>[],
        };

  const paycheckSplit =
    seriesMap['paycheck_split']?.labels && seriesMap['paycheck_split']?.datasets
      ? (() => {
          const labels = seriesMap['paycheck_split'].labels as string[];
          const ds = seriesMap['paycheck_split'].datasets as { amounts?: number[] }[];
          const amounts = ds[0]?.amounts ?? [];
          return {
            labels,
            amounts,
            colors: labels.map((_, i) => SPENDING_COLORS[i % SPENDING_COLORS.length]),
          };
        })()
      : {
          labels: [] as string[],
          amounts: [] as number[],
          colors: [] as string[],
        };

  const recentActivity =
    txRows?.map((t) => ({
      date: t.occurred_on,
      description: t.description || t.category,
      amount: Number(t.amount),
      category: t.category,
    })) ?? [];

  // Optional `behavior` (same shape as frontend `BehaviorInsightsPayload`) can be added
  // when the AI agent pipeline writes insights — until then the UI falls back to defaults.

  return {
    user: {
      name: displayName,
      monthlyIncome,
    },
    accounts: {
      checking,
      savings,
      creditScore,
      netWorth,
    },
    risks,
    debts: debtsOut,
    spending,
    debtTimeline,
    financialGains,
    paycheckSplit,
    recentActivity,
  };
}
