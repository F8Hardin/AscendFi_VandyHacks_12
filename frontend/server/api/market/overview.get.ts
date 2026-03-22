/**
 * GET /api/market/overview
 * Proxies to Python FastAPI /api/market/overview
 */
export default defineEventHandler(async (event) => {
  void event
  const config = useRuntimeConfig()
  const pythonUrl = (config as Record<string, unknown>).pythonAgentUrl as string ?? 'http://localhost:8000'

  try {
    const data = await $fetch(`${pythonUrl}/api/market/overview`, { timeout: 10_000 })
    return data
  } catch {
    return { market_snapshot: {}, error: 'Market overview unavailable' }
  }
})
