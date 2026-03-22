import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import sessionRouter from './routes/session';
import chatRouter from './routes/chat';
import authRouter from './routes/auth';
import financeRouter from './routes/finance';
import { startInactivityReaper } from './services/containerManager';

const app = express();

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
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
app.listen(PORT, () => {
  console.log(`[backend] Listening on port ${PORT} (agent sessions + chat proxy)`);
  startInactivityReaper();
});
