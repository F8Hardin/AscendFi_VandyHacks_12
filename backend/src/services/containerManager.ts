import { exec, spawn } from 'child_process';
import * as path from 'path';
import { promisify } from 'util';
import { v4 as uuidv4 } from 'uuid';
import Dockerode from 'dockerode';
import { sessionStore, SessionRecord } from './sessionStore';

const execAsync = promisify(exec);

// ── Config ────────────────────────────────────────────────────────────────────
const PORT_RANGE_START = parseInt(process.env.PORT_RANGE_START || '8100');
const PORT_RANGE_END = parseInt(process.env.PORT_RANGE_END || '8200');
const CONTAINER_PORT = process.env.CONTAINER_PORT || '8080';
const AGENT_IMAGE = process.env.AGENT_IMAGE || 'ascendfi-backend-agent:latest';
const INACTIVITY_TIMEOUT_MS = parseInt(process.env.INACTIVITY_TIMEOUT_MS || '900000');
const HEALTH_CHECK_TIMEOUT_MS = parseInt(process.env.HEALTH_CHECK_TIMEOUT_MS || '120000');

// Pool: containers pre-warmed on startup so sessions are assigned instantly.
const POOL_DEFAULT_SIZE = parseInt(process.env.POOL_DEFAULT_SIZE || '1');
const POOL_MAX_SIZE = parseInt(process.env.POOL_MAX_SIZE || '3');

// Direct agent mode: skip Docker/distrobox entirely and run the agent as a local
// uvicorn process. All sessions share the single instance. Good for fast dev iteration.
// Set DIRECT_AGENT_MODE=1 to enable.
const DIRECT_AGENT_MODE = process.env.DIRECT_AGENT_MODE === '1' || process.env.DIRECT_AGENT_MODE === 'true';
const DIRECT_AGENT_PORT = parseInt(process.env.DIRECT_AGENT_PORT || '8080');
// Path to the agent directory containing app/main.py. Defaults to sibling ../agent.
const DIRECT_AGENT_PATH = process.env.DIRECT_AGENT_PATH ||
  path.resolve(__dirname, '../../../agent');

// Devbox mode: run docker commands inside the distrobox dev container
// Set DEVBOX_MODE=1 to use the devbox from ~/setup-dev-box.sh
const DEVBOX_MODE = process.env.DEVBOX_MODE === '1' || process.env.DEVBOX_MODE === 'true';
const DEVBOX_NAME = process.env.DEVBOX_NAME || 'devbox';
// DEVBOX_ROOT=1 (default) matches SETUP_DOCKER=1 — rootful container with Docker support
const DEVBOX_ROOT = process.env.DEVBOX_ROOT !== '0';

// ── Docker abstraction ────────────────────────────────────────────────────────

// Direct Dockerode client (used when DEVBOX_MODE=false)
const docker = DEVBOX_MODE ? null : new Dockerode();

// Timeout for docker commands run inside devbox (ms). vfs storage is slow to copy.
const DEVBOX_EXEC_TIMEOUT_MS = parseInt(process.env.DEVBOX_EXEC_TIMEOUT_MS || '120000');

/** Verify the devbox container exists, throwing immediately if not. */
async function assertDevboxExists(): Promise<void> {
  const listCmd = DEVBOX_ROOT
    ? 'distrobox list --root --no-color 2>/dev/null || distrobox list --root'
    : 'distrobox list --no-color 2>/dev/null || distrobox list';
  const { stdout } = await execAsync(listCmd, { timeout: 5000 });
  if (!stdout.includes(DEVBOX_NAME)) {
    throw new Error(
      `Devbox container '${DEVBOX_NAME}' does not exist. ` +
      `Run: SETUP_DOCKER=1 ~/setup-dev-box.sh`,
    );
  }
}

/** Run a shell command inside the devbox container */
function devboxExec(cmd: string): Promise<{ stdout: string; stderr: string }> {
  const enterArgs = DEVBOX_ROOT ? `--root ${DEVBOX_NAME}` : DEVBOX_NAME;
  return execAsync(
    `distrobox enter ${enterArgs} -- bash -c ${JSON.stringify(cmd)}`,
    { timeout: DEVBOX_EXEC_TIMEOUT_MS },
  );
}

// ── Port allocation ───────────────────────────────────────────────────────────

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

/**
 * Scan Docker for already-running agent containers.
 * - Marks their ports as used so allocatePort() skips them.
 * - Health-checks each one and adds healthy containers to the pool
 *   so they can be claimed immediately rather than being wasted or recreated.
 */
async function syncUsedPortsFromDocker(): Promise<void> {
  try {
    let lines: { id: string; name: string; ports: string }[] = [];

    if (DEVBOX_MODE) {
      const { stdout } = await devboxExec(
        "sudo docker ps --format '{{.ID}}\\t{{.Names}}\\t{{.Ports}}'",
      );
      lines = stdout
        .split('\n')
        .filter(Boolean)
        .map((line) => {
          const [id, name, ports] = line.split('\t');
          return { id, name: name ?? '', ports: ports ?? '' };
        });
    } else {
      const containers = await docker!.listContainers();
      lines = containers.map((c) => ({
        id: c.Id,
        name: c.Names[0] ?? '',
        ports: c.Ports.map((p) => `${p.PublicPort}->`).join(' '),
      }));
    }

    const reclaimed: number[] = [];
    const skipped: number[] = [];

    for (const { id, name, ports } of lines) {
      // Only care about our agent containers
      if (!name.includes('ascendfi-agent')) continue;

      const match = ports.match(/:(\d+)->/);
      if (!match) continue;
      const port = parseInt(match[1]);
      if (port < PORT_RANGE_START || port > PORT_RANGE_END) continue;

      usedPorts.add(port);

      // Health-check — if healthy, add to pool for immediate reuse
      try {
        const res = await fetch(`http://localhost:${port}/health`, { signal: AbortSignal.timeout(5000) });
        if (res.ok) {
          pool.push({ containerId: id, hostPort: port });
          reclaimed.push(port);
        } else {
          console.log(`[orchestrator] Container on port ${port} returned status ${res.status} — skipping`);
          skipped.push(port);
        }
      } catch (err) {
        console.log(`[orchestrator] Container on port ${port} unreachable: ${err}`);
        skipped.push(port);
      }
    }

    if (reclaimed.length > 0) {
      console.log(`[orchestrator] Reclaimed ${reclaimed.length} existing agent container(s) into pool (ports: ${reclaimed.join(', ')})`);
    }
    if (skipped.length > 0) {
      console.log(`[orchestrator] Skipped ${skipped.length} unhealthy/unreachable container(s) (ports: ${skipped.join(', ')})`);
    }
  } catch {
    // Non-fatal — worst case we start fresh
  }
}

// ── Health check ──────────────────────────────────────────────────────────────

async function waitForHealthy(port: number, timeoutMs = HEALTH_CHECK_TIMEOUT_MS): Promise<void> {
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

// ── Container lifecycle — devbox path ─────────────────────────────────────────

async function createContainerDevbox(sessionId: string, hostPort: number): Promise<string> {
  await assertDevboxExists();

  // Ensure dockerd is running inside the devbox. ~/bin/docker-start is idempotent
  // (a no-op if dockerd is already up) and was installed by setup-dev-box.sh.
  console.log('[orchestrator] Ensuring dockerd is running inside devbox...');
  try {
    await devboxExec('export PATH="$HOME/bin:$PATH"; docker-start');
  } catch (err) {
    throw new Error(`Failed to start dockerd inside devbox: ${err}`);
  }

  const backendUrl = 'http://host.docker.internal:8000';
  const lmBase = process.env.LM_STUDIO_BASE_URL || 'http://host.docker.internal:1234/v1';
  const lmModel = process.env.LM_STUDIO_MODEL || 'local-model';

  const envFlags = [
    `-e BACKEND_URL=${backendUrl}`,
    `-e LM_STUDIO_BASE_URL=${lmBase}`,
    `-e LM_STUDIO_MODEL=${lmModel}`,
  ].join(' ');

  const cmd = [
    'sudo docker run -d',
    `--name ascendfi-agent-${sessionId}`,
    `--add-host host.docker.internal:host-gateway`,
    `-p ${hostPort}:${CONTAINER_PORT}`,
    envFlags,
    AGENT_IMAGE,
  ].join(' ');

  const { stdout } = await devboxExec(cmd);
  return stdout.trim(); // returns container ID
}

async function stopContainerDevbox(containerId: string): Promise<void> {
  await devboxExec(`sudo docker stop --time 5 ${containerId} && sudo docker rm -f ${containerId}`);
}

// ── Container lifecycle — direct Docker path ──────────────────────────────────

async function createContainerDirect(sessionId: string, hostPort: number): Promise<string> {
  const container = await docker!.createContainer({
    Image: AGENT_IMAGE,
    ExposedPorts: { [`${CONTAINER_PORT}/tcp`]: {} },
    HostConfig: {
      PortBindings: {
        [`${CONTAINER_PORT}/tcp`]: [{ HostPort: String(hostPort) }],
      },
      ExtraHosts: ['host.docker.internal:host-gateway'],
    },
    Env: [
      `BACKEND_URL=${process.env.AGENT_BACKEND_URL || 'http://host.docker.internal:8000'}`,
      `LM_STUDIO_BASE_URL=${process.env.LM_STUDIO_BASE_URL || 'http://host.docker.internal:1234/v1'}`,
      `LM_STUDIO_MODEL=${process.env.LM_STUDIO_MODEL || 'local-model'}`,
    ],
  });
  await container.start();
  return container.id;
}

async function stopContainerDirect(containerId: string): Promise<void> {
  const container = docker!.getContainer(containerId);
  await container.stop({ t: 5 });
  await container.remove({ force: true });
}

// ── Direct agent mode ─────────────────────────────────────────────────────────

/** Spawn a local uvicorn process for the agent and wait until it's healthy. */
async function startDirectAgent(): Promise<void> {
  // Check if already running
  try {
    const res = await fetch(`http://localhost:${DIRECT_AGENT_PORT}/health`, {
      signal: AbortSignal.timeout(1000),
    });
    if (res.ok) {
      console.log(`[orchestrator] Direct agent already running on port ${DIRECT_AGENT_PORT}`);
      return;
    }
  } catch {
    // Not running yet — start it
  }

  // Prefer venv python if present
  const venvPython = path.join(DIRECT_AGENT_PATH, 'venv', 'bin', 'python');
  const python = (() => {
    try { require('fs').accessSync(venvPython); return venvPython; } catch { return 'python3'; }
  })();

  console.log(`[orchestrator] Starting direct agent (${DIRECT_AGENT_PATH}) on port ${DIRECT_AGENT_PORT}...`);
  const proc = spawn(
    python,
    ['-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', String(DIRECT_AGENT_PORT)],
    {
      cwd: DIRECT_AGENT_PATH,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: { ...process.env },
    },
  );

  proc.stdout?.on('data', (d) => process.stdout.write(`[agent] ${d}`));
  proc.stderr?.on('data', (d) => process.stderr.write(`[agent] ${d}`));
  proc.on('exit', (code) => console.warn(`[orchestrator] Direct agent exited (code ${code})`));

  await waitForHealthy(DIRECT_AGENT_PORT, 60000);
  console.log(`[orchestrator] Direct agent ready on port ${DIRECT_AGENT_PORT}`);
}

// ── Container pool ────────────────────────────────────────────────────────────

type PoolEntry = { containerId: string; hostPort: number };

const pool: PoolEntry[] = [];
let poolWarmingCount = 0;

/** Fill the pool up to POOL_DEFAULT_SIZE, respecting POOL_MAX_SIZE total. */
async function warmPool(): Promise<void> {
  const totalContainers = sessionStore.getAll().length + pool.length + poolWarmingCount;
  const needed = Math.min(
    POOL_DEFAULT_SIZE - pool.length - poolWarmingCount,
    POOL_MAX_SIZE - totalContainers,
  );

  for (let i = 0; i < needed; i++) {
    poolWarmingCount++;
    const poolId = `pool-${uuidv4()}`;
    (async () => {
      try {
        const hostPort = allocatePort();
        const containerId = DEVBOX_MODE
          ? await createContainerDevbox(poolId, hostPort)
          : await createContainerDirect(poolId, hostPort);
        await waitForHealthy(hostPort);
        pool.push({ containerId, hostPort });
        console.log(`[orchestrator] Pool container ready on port ${hostPort} (pool size: ${pool.length}/${POOL_DEFAULT_SIZE})`);
      } catch (err) {
        console.warn('[orchestrator] Failed to warm pool container:', err);
      } finally {
        poolWarmingCount--;
      }
    })();
  }
}

// ── Public API ────────────────────────────────────────────────────────────────

export async function createContainer(sessionId: string): Promise<SessionRecord> {
  // Direct mode: no containers — all sessions share the single local agent process
  if (DIRECT_AGENT_MODE) {
    const record: SessionRecord = {
      sessionId,
      containerId: 'direct',
      hostPort: DIRECT_AGENT_PORT,
      status: 'ready',
      createdAt: Date.now(),
      lastUsedAt: Date.now(),
    };
    sessionStore.set(record);
    sessionStore.updateStatus(sessionId, 'ready');
    console.log(`[orchestrator] Direct mode: assigned session ${sessionId} to port ${DIRECT_AGENT_PORT}`);
    return record;
  }

  // Claim a pre-warmed container from the pool if available
  const poolEntry = pool.shift();

  let hostPort: number;
  let containerId: string;

  if (poolEntry) {
    hostPort = poolEntry.hostPort;
    containerId = poolEntry.containerId;
    console.log(`[orchestrator] Assigned pool container on port ${hostPort} to session ${sessionId}`);
  } else {
    // Pool empty — create on demand
    console.log(`[orchestrator] Pool empty, creating container on demand for session ${sessionId}...`);
    hostPort = allocatePort();

    const record: SessionRecord = {
      sessionId,
      containerId: '',
      hostPort,
      status: 'starting',
      createdAt: Date.now(),
      lastUsedAt: Date.now(),
    };
    sessionStore.set(record);

    try {
      containerId = DEVBOX_MODE
        ? await createContainerDevbox(sessionId, hostPort)
        : await createContainerDirect(sessionId, hostPort);
    } catch (err) {
      await destroySession(sessionId);
      throw err;
    }

    record.containerId = containerId;
    sessionStore.set(record);

    try {
      await waitForHealthy(hostPort);
    } catch (err) {
      await destroySession(sessionId);
      throw err;
    }
  }

  const record: SessionRecord = {
    sessionId,
    containerId,
    hostPort,
    status: 'ready',
    createdAt: Date.now(),
    lastUsedAt: Date.now(),
  };
  sessionStore.set(record);
  sessionStore.updateStatus(sessionId, 'ready');
  console.log(
    `[orchestrator] Container ready for session ${sessionId} on port ${hostPort}` +
    (DEVBOX_MODE ? ` (devbox: ${DEVBOX_NAME})` : ''),
  );

  // Refill pool in background
  warmPool().catch((err) => console.warn('[orchestrator] Pool refill error:', err));

  return record;
}

export async function destroySession(sessionId: string): Promise<void> {
  const record = sessionStore.get(sessionId);
  if (!record) return;

  sessionStore.updateStatus(sessionId, 'dead');
  sessionStore.delete(sessionId);

  // Direct mode: nothing to tear down — the shared process keeps running
  if (DIRECT_AGENT_MODE) return;

  releasePort(record.hostPort);

  if (!record.containerId) return;

  try {
    if (DEVBOX_MODE) {
      await stopContainerDevbox(record.containerId);
    } else {
      await stopContainerDirect(record.containerId);
    }
    console.log(`[backend] Destroyed agent container for session ${sessionId}`);
  } catch (err) {
    console.warn(`[backend] Failed to cleanly remove container ${record.containerId}:`, err);
  }

  // Refill pool after a container is freed
  warmPool().catch((err) => console.warn('[orchestrator] Pool refill error:', err));
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

/** Start pre-warming the pool. Call once at server startup. */
export function startPoolWarming(): void {
  if (DIRECT_AGENT_MODE) {
    console.log(`[orchestrator] Direct agent mode — starting local uvicorn on port ${DIRECT_AGENT_PORT}`);
    startDirectAgent().catch((err) => console.warn('[orchestrator] Failed to start direct agent:', err));
    return;
  }

  console.log(`[orchestrator] Pre-warming pool (target: ${POOL_DEFAULT_SIZE}, max: ${POOL_MAX_SIZE})...`);
  (async () => {
    // Ensure dockerd is up first — port bindings on existing containers aren't
    // restored until dockerd is fully running, so sync must happen after this.
    try {
      await devboxExec('export PATH="$HOME/bin:$PATH"; docker-start');
    } catch (err) {
      console.warn('[orchestrator] Could not ensure dockerd is running:', err);
    }
    await syncUsedPortsFromDocker();
    await warmPool();
  })().catch((err) => console.warn('[orchestrator] Initial pool warm error:', err));
}
