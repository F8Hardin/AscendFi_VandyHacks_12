import { Router, Request, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { sessionStore } from '../services/sessionStore';
import { createContainer } from '../services/containerManager';

const router = Router();

router.post('/', async (req: Request, res: Response) => {
  // Check if this client already has a live session via cookie
  const existingId: string | undefined = req.cookies?.ascendfi_session;
  if (existingId) {
    const existing = sessionStore.get(existingId);
    if (existing && existing.status === 'ready') {
      sessionStore.touch(existingId);
      res.json({ sessionId: existingId, status: 'existing' });
      return;
    }
  }

  // Create a new session
  const sessionId = uuidv4();
  try {
    await createContainer(sessionId);
  } catch (err) {
    console.error('[orchestrator] Failed to create container:', err);
    res.status(503).json({ error: 'Failed to start agent container', detail: String(err) });
    return;
  }

  res.cookie('ascendfi_session', sessionId, {
    httpOnly: false,  // frontend JS needs to read it
    sameSite: 'lax',
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
  });
  res.json({ sessionId, status: 'created' });
});

export default router;
