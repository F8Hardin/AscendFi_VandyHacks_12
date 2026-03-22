/**
 * API client — auto-detects the dev machine's LAN IP from Expo's host URI
 * so a physical phone on the same WiFi connects without any manual config.
 *
 * When you run `npx expo start`, Expo prints a QR code that encodes the
 * LAN address of your machine. This module reads that address and builds
 * the correct API base URLs automatically.
 */

import Constants from 'expo-constants'

function getDevMachineIp(): string | null {
  // hostUri looks like "192.168.1.42:8081" in Expo Go on LAN
  const hostUri = Constants.expoConfig?.hostUri
  if (hostUri) return hostUri.split(':')[0] ?? null
  return null
}

function buildBase(port: number, path = ''): string {
  const override =
    port === 8000
      ? process.env.EXPO_PUBLIC_API_BASE
      : process.env.EXPO_PUBLIC_NODE_BASE

  if (override) return override.replace(/\/$/, '')

  const ip = getDevMachineIp()
  if (ip) return `http://${ip}:${port}${path}`

  // Last-resort fallback (works in simulators)
  return `http://localhost:${port}${path}`
}

/** Python FastAPI agent  →  http://<machine-ip>:8000/api */
export const AGENT_BASE = buildBase(8000, '/api')

/** Node.js backend       →  http://<machine-ip>:3001 */
export const NODE_BASE = buildBase(3001)

/** Python agent root (for /chat/stream)  →  http://<machine-ip>:8000 */
export const AGENT_ROOT = buildBase(8000)

// ─── Typed fetch helpers ──────────────────────────────────────────────────────

export async function apiFetch<T = unknown>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options?.headers ?? {}) },
    ...options,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${url}`)
  return res.json() as Promise<T>
}

export async function apiPost<T = unknown>(url: string, body: unknown): Promise<T> {
  return apiFetch<T>(url, { method: 'POST', body: JSON.stringify(body) })
}
