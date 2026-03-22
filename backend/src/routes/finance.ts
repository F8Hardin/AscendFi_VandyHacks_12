import { Router, type Request, type Response } from 'express';
import { attachSessionCookies } from '../config/authCookies';
import { createUserClient, resolveSessionFromCookies } from '../services/supabaseServer';
import { buildFinanceDashboard } from '../services/buildFinanceDashboard';
import { enrichDashboardWithAI } from '../services/buildFinanceDashboard';

const router = Router();

const PYTHON_AGENT_URL = process.env.PYTHON_AGENT_URL || 'http://localhost:8000';

router.get('/dashboard', async (req: Request, res: Response) => {
  try {
    const cookies = req.cookies as Record<string, string | undefined>;
    const session = await resolveSessionFromCookies(cookies);
    if (!session.ok) {
      res.status(401).json({ message: 'Unauthorized' });
      return;
    }

    if (session.refreshed) {
      attachSessionCookies(res, session.accessToken, session.refreshToken, session.expiresIn ?? 3600);
    }

    const supabase = createUserClient(session.accessToken);
    // Build base dashboard from Supabase then enrich with Python AI risk scores
    const payload = await buildFinanceDashboard(supabase, session.user.id);
    const enriched = await enrichDashboardWithAI(payload);
    res.json(enriched);
  } catch (e) {
    res.status(500).json({ message: String(e) });
  }
});

/** POST /api/finance/invest — deduct from checking and record an investment transaction. */
router.post('/invest', async (req: Request, res: Response) => {
  try {
    const cookies = req.cookies as Record<string, string | undefined>;
    const session = await resolveSessionFromCookies(cookies);
    if (!session.ok) {
      res.status(401).json({ message: 'Unauthorized' });
      return;
    }

    if (session.refreshed) {
      attachSessionCookies(res, session.accessToken, session.refreshToken, session.expiresIn ?? 3600);
    }

    const { symbol, shares, pricePerShare, name } = req.body as {
      symbol?: string;
      shares?: number;
      pricePerShare?: number;
      name?: string;
    };

    if (!symbol || !shares || !pricePerShare) {
      res.status(400).json({ message: 'symbol, shares, and pricePerShare are required' });
      return;
    }

    const totalCost = Number(shares) * Number(pricePerShare);
    if (totalCost <= 0) {
      res.status(400).json({ message: 'Invalid purchase amount' });
      return;
    }

    const supabase = createUserClient(session.accessToken);

    // Fetch current checking balance
    const { data: profile } = await supabase
      .from('profiles')
      .select('checking_balance')
      .eq('id', session.user.id)
      .maybeSingle();

    const currentBalance = Number(profile?.checking_balance ?? 0);
    if (currentBalance < totalCost) {
      res.status(400).json({ message: 'Insufficient funds in checking account' });
      return;
    }

    const newBalance = Math.round((currentBalance - totalCost) * 100) / 100;

    // Deduct from checking balance
    await supabase
      .from('profiles')
      .update({ checking_balance: newBalance })
      .eq('id', session.user.id);

    // Record as a transaction
    const today = new Date().toISOString().split('T')[0];
    await supabase.from('transactions').insert({
      user_id: session.user.id,
      occurred_on: today,
      description: `Buy ${Number(shares).toFixed(4).replace(/\.?0+$/, '')} ${symbol.toUpperCase()} @ $${Number(pricePerShare).toFixed(2)}`,
      amount: -totalCost,
      category: 'Investment',
    });

    res.json({ success: true, newCheckingBalance: newBalance, totalCost });
  } catch (e) {
    res.status(500).json({ message: String(e) });
  }
});

/** GET /api/finance/portfolio — compute holdings from investment transactions. */
router.get('/portfolio', async (req: Request, res: Response) => {
  try {
    const cookies = req.cookies as Record<string, string | undefined>;
    const session = await resolveSessionFromCookies(cookies);
    if (!session.ok) {
      res.status(401).json({ message: 'Unauthorized' });
      return;
    }

    if (session.refreshed) {
      attachSessionCookies(res, session.accessToken, session.refreshToken, session.expiresIn ?? 3600);
    }

    const supabase = createUserClient(session.accessToken);
    const { data: txs } = await supabase
      .from('transactions')
      .select('description, amount, occurred_on')
      .eq('user_id', session.user.id)
      .eq('category', 'Investment')
      .order('occurred_on', { ascending: true });

    // Parse holdings: "Buy 2 AAPL @ $185.42"
    const holdings: Record<string, { symbol: string; shares: number; totalCost: number }> = {};
    for (const tx of txs ?? []) {
      const match = (tx.description as string | null)?.match(/^(Buy|Sell)\s+([\d.]+)\s+(\w+)\s+@\s+\$([\d.]+)/i);
      if (!match) continue;
      const [, action, sharesStr, sym, priceStr] = match;
      const s = parseFloat(sharesStr!);
      const p = parseFloat(priceStr!);
      const key = sym!.toUpperCase();
      if (!holdings[key]) holdings[key] = { symbol: key, shares: 0, totalCost: 0 };
      if (action!.toLowerCase() === 'buy') {
        holdings[key]!.shares += s;
        holdings[key]!.totalCost += s * p;
      } else {
        const sellFrac = Math.min(s / (holdings[key]!.shares || 1), 1);
        holdings[key]!.totalCost -= holdings[key]!.totalCost * sellFrac;
        holdings[key]!.shares = Math.max(0, holdings[key]!.shares - s);
      }
    }

    const result = Object.values(holdings)
      .filter((h) => h.shares > 0.0001)
      .map((h) => ({
        symbol: h.symbol,
        shares: Math.round(h.shares * 10000) / 10000,
        avgCost: h.shares > 0 ? Math.round((h.totalCost / h.shares) * 100) / 100 : 0,
      }));

    res.json({ holdings: result });
  } catch (e) {
    res.status(500).json({ message: String(e) });
  }
});

/** GET /api/finance/market/* — proxy market data requests to Python agent */
router.get('/market/:path(*)', async (req: Request, res: Response) => {
  try {
    const path = req.params.path;
    const qs = new URLSearchParams(req.query as Record<string, string>).toString();
    const url = `${PYTHON_AGENT_URL}/api/market/${path}${qs ? '?' + qs : ''}`;

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10_000);
    const upstream = await fetch(url, { signal: controller.signal });
    clearTimeout(timeout);

    if (!upstream.ok) {
      res.status(upstream.status).json({ message: 'Market data unavailable' });
      return;
    }
    const data = await upstream.json();
    res.json(data);
  } catch (e) {
    res.status(503).json({ message: 'Market data service unreachable', error: String(e) });
  }
});

export default router;
