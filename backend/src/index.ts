import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import sessionRouter from './routes/session';
import chatRouter from './routes/chat';
import authRouter from './routes/auth';
import financeRouter from './routes/finance';
import { startInactivityReaper, startPoolWarming } from './services/containerManager';

const app = express();

const ALLOWED_ORIGINS = [
  process.env.FRONTEND_URL || 'http://localhost:3000',
  'http://localhost:3000',
  'http://[::]:3000',
  'http://[::1]:3000',
  'http://127.0.0.1:3000',
];

app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (server-to-server, curl)
    if (!origin) return callback(null, true);
    if (ALLOWED_ORIGINS.includes(origin)) return callback(null, true);
    callback(new Error(`CORS: origin not allowed — ${origin}`));
  },
  credentials: true,
}));
app.use(express.json());
app.use(cookieParser());

app.use('/api/auth', authRouter);
app.use('/api/finance', financeRouter);
app.use('/agent/session', sessionRouter);
app.use('/agent/chat', chatRouter);

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

const PORT = parseInt(process.env.PORT || '3001');
app.listen(PORT, '0.0.0.0', () => {
  console.log(`[backend] Listening on port ${PORT} (agent sessions + chat proxy)`);
  startInactivityReaper();
  startPoolWarming();
});
