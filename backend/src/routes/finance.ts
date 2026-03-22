import { Router, type Request, type Response } from 'express';
import { attachSessionCookies } from '../config/authCookies';
import { createUserClient, resolveSessionFromCookies } from '../services/supabaseServer';
import { buildFinanceDashboard } from '../services/buildFinanceDashboard';

const router = Router();

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
    const payload = await buildFinanceDashboard(supabase, session.user.id);
    res.json(payload);
  } catch (e) {
    res.status(500).json({ message: String(e) });
  }
});

export default router;
