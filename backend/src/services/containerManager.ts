import Dockerode from 'dockerode';
import { sessionStore, SessionRecord } from './sessionStore';

const docker = new Dockerode();

const PORT_RANGE_START = parseInt(process.env.PORT_RANGE_START || '8100');
const PORT_RANGE_END = parseInt(process.env.PORT_RANGE_END || '8200');
const CONTAINER_PORT = process.env.CONTAINER_PORT || '8080';
const AGENT_IMAGE = process.env.AGENT_IMAGE || 'ascendfi-backend-agent:latest';
const INACTIVITY_TIMEOUT_MS = parseInt(process.env.INACTIVITY_TIMEOUT_MS || '900000');

const usedPorts = new Set<number>();

function allocatePort(): number {
  for (let p = PORT_RANGE_START; p <= PORT_RANGE_END; p++) {
    if (!usedPorts.has(p)) {
      usedPorts.add(p);
      return p;
    }
  }
  throw new Error(`No available ports in range ${PORT_RANGE_START}-${PORT_RANGE_END}`);
}

function releasePort(port: number): void {
  usedPorts.delete(port);
}

async function waitForHealthy(port: number, timeoutMs = 20000): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(`http://localhost:${port}/health`);
      if (res.ok) return;
    } catch {
      // container not ready yet
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`Container on port ${port} did not become healthy within ${timeoutMs}ms`);
}

export async function createContainer(sessionId: string): Promise<SessionRecord> {
  const hostPort = allocatePort();

  const container = await docker.createContainer({
    Image: AGENT_IMAGE,
    ExposedPorts: { [`${CONTAINER_PORT}/tcp`]: {} },
    HostConfig: {
      PortBindings: {
        [`${CONTAINER_PORT}/tcp`]: [{ HostPort: String(hostPort) }],
      },
      ExtraHosts: ['host.docker.internal:host-gateway'], // required on Linux
    },
    Env: [
      `BACKEND_URL=${process.env.AGENT_BACKEND_URL || 'http://host.docker.internal:8000'}`,
      `LM_STUDIO_BASE_URL=${process.env.LM_STUDIO_BASE_URL || 'http://host.docker.internal:1234/v1'}`,
      `LM_STUDIO_MODEL=${process.env.LM_STUDIO_MODEL || 'local-model'}`,
    ],
  });

  const record: SessionRecord = {
    sessionId,
    containerId: container.id,
    hostPort,
    status: 'starting',
    createdAt: Date.now(),
    lastUsedAt: Date.now(),
  };
  sessionStore.set(record);

  await container.start();

  try {
    await waitForHealthy(hostPort);
    sessionStore.updateStatus(sessionId, 'ready');
    record.status = 'ready';
    console.log(`[backend] Agent container ready for session ${sessionId} on port ${hostPort}`);
  } catch (err) {
    // Health check timed out — clean up
    await destroySession(sessionId);
    throw err;
  }

  return record;
}

export async function destroySession(sessionId: string): Promise<void> {
  const record = sessionStore.get(sessionId);
  if (!record) return;

  sessionStore.updateStatus(sessionId, 'dead');
  sessionStore.delete(sessionId);
  releasePort(record.hostPort);

  try {
    const container = docker.getContainer(record.containerId);
    await container.stop({ t: 5 });
    await container.remove({ force: true });
    console.log(`[backend] Destroyed agent container for session ${sessionId}`);
  } catch (err) {
    // Container may have already exited — log and move on
    console.warn(`[backend] Failed to cleanly remove container ${record.containerId}:`, err);
  }
}

export function startInactivityReaper(): void {
  setInterval(async () => {
    const now = Date.now();
    const stale = sessionStore
      .getAll()
      .filter((s) => s.status === 'ready' && now - s.lastUsedAt > INACTIVITY_TIMEOUT_MS);

    for (const session of stale) {
      console.log(`[backend] Reaping inactive session ${session.sessionId}`);
      await destroySession(session.sessionId);
    }
  }, 60_000);
}
