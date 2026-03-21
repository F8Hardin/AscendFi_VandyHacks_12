import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import sessionRouter from './routes/session';
import chatRouter from './routes/chat';
import { startInactivityReaper } from './services/containerManager';

const app = express();

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
}));
app.use(express.json());
app.use(cookieParser());

app.use('/agent/session', sessionRouter);
app.use('/agent/chat', chatRouter);

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

const PORT = parseInt(process.env.PORT || '3001');
app.listen(PORT, () => {
  console.log(`[orchestrator] Running on port ${PORT}`);
  startInactivityReaper();
});
