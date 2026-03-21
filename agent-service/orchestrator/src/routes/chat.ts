import { Router, Request, Response } from 'express';
import { sessionStore } from '../services/sessionStore';

const router = Router();

router.post('/:sessionId', async (req: Request, res: Response) => {
  const sessionId = req.params.sessionId as string;
  const session = sessionStore.get(sessionId);

  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }
  if (session.status !== 'ready') {
    res.status(503).json({ error: `Session not ready (status: ${session.status})` });
    return;
  }

  sessionStore.touch(sessionId);

  // Set SSE headers immediately so the browser starts reading
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('X-Accel-Buffering', 'no');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  let upstream: Response | null = null;
  let reader: ReadableStreamDefaultReader<Uint8Array> | null = null;

  // Handle client disconnect
  req.on('close', () => {
    reader?.cancel().catch(() => {});
  });

  try {
    const upstreamRes = await fetch(
      `http://localhost:${session.hostPort}/chat/stream`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req.body),
      }
    );

    if (!upstreamRes.ok || !upstreamRes.body) {
      res.write(`data: ${JSON.stringify({ type: 'error', message: 'Upstream agent failed' })}\n\n`);
      res.end();
      return;
    }

    // Pipe the raw SSE bytes from the container straight to the client
    reader = upstreamRes.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      res.write(decoder.decode(value, { stream: true }));
    }
  } catch (err) {
    // Client disconnected or upstream error
    if (!res.writableEnded) {
      res.write(`data: ${JSON.stringify({ type: 'error', message: String(err) })}\n\n`);
    }
  } finally {
    if (!res.writableEnded) {
      res.end();
    }
  }
});

export default router;
