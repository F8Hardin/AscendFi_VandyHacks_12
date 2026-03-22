import { Router, type Request, type Response } from 'express';
import { attachSessionCookies, clearSessionCookies } from '../config/authCookies';
import { createAnonClient, resolveSessionFromCookies } from '../services/supabaseServer';

const router = Router();

router.post('/sign-in', async (req: Request, res: Response) => {
  try {
    const email = typeof req.body?.email === 'string' ? req.body.email : '';
    const password = typeof req.body?.password === 'string' ? req.body.password : '';
    if (!email || !password) {
      res.status(400).json({ message: 'Email and password required' });
      return;
    }

    const supabase = createAnonClient();
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error || !data.session) {
      res.status(401).json({ message: error?.message || 'Invalid credentials' });
      return;
    }

    attachSessionCookies(res, data.session.access_token, data.session.refresh_token, data.session.expires_in);
    res.json({ user: data.user });
  } catch (e) {
    res.status(500).json({ message: String(e) });
  }
});

router.post('/sign-up', async (req: Request, res: Response) => {
  try {
    const email = typeof req.body?.email === 'string' ? req.body.email : '';
    const password = typeof req.body?.password === 'string' ? req.body.password : '';
    const profile = req.body?.profile as
      | { legalFirstName?: string; legalLastName?: string; stateCode?: string }
      | undefined;

    if (!email || !password) {
      res.status(400).json({ message: 'Email and password required' });
      return;
    }

    const supabase = createAnonClient();
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: profile
        ? {
            data: {
              legal_first_name: profile.legalFirstName,
              legal_last_name: profile.legalLastName,
              state: profile.stateCode,
            },
          }
        : undefined,
    });

    if (error) {
      res.status(400).json({ message: error.message });
      return;
    }

    if (data.session) {
      attachSessionCookies(res, data.session.access_token, data.session.refresh_token, data.session.expires_in);
    }

    res.json({
      user: data.user,
      needsEmailConfirmation: !data.session,
    });
  } catch (e) {
    res.status(500).json({ message: String(e) });
  }
});

/** After email confirmation, front-end sends tokens from URL hash to establish cookies. */
router.post('/session', async (req: Request, res: Response) => {
  try {
    const access_token = typeof req.body?.access_token === 'string' ? req.body.access_token : '';
    const refresh_token = typeof req.body?.refresh_token === 'string' ? req.body.refresh_token : '';
    if (!access_token || !refresh_token) {
      res.status(400).json({ message: 'access_token and refresh_token required' });
      return;
    }

    const supabase = createAnonClient();
    const { data, error } = await supabase.auth.setSession({ access_token, refresh_token });
    if (error || !data.session || !data.user) {
      res.status(401).json({ message: error?.message || 'Invalid session' });
      return;
    }

    attachSessionCookies(res, data.session.access_token, data.session.refresh_token, data.session.expires_in);
    res.json({ user: data.user });
  } catch (e) {
    res.status(500).json({ message: String(e) });
  }
});

router.post('/sign-out', async (_req: Request, res: Response) => {
  clearSessionCookies(res);
  res.json({ ok: true });
});

router.get('/me', async (req: Request, res: Response) => {
  try {
    const cookies = req.cookies as Record<string, string | undefined>;
    const session = await resolveSessionFromCookies(cookies);
    if (!session.ok) {
      res.json({ user: null });
      return;
    }

    if (session.refreshed) {
      attachSessionCookies(res, session.accessToken, session.refreshToken, session.expiresIn ?? 3600);
      res.json({ user: session.user });
      return;
    }

    res.json({ user: session.user });
  } catch (e) {
    res.status(500).json({ message: String(e) });
  }
});

export default router;
