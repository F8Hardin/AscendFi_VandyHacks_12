/**
 * POST /api/agent/dashboard
 *
 * Server-side Nuxt route that calls the Python FastAPI's /api/dashboard
 * endpoint and returns an AI-computed DashboardPayload.
 *
 * The client sends the user's financial profile; this route forwards it to
 * the Python agent running on NUXT_PYTHON_AGENT_URL (default: localhost:8000)
 * and proxies the result back to the browser.
 *
 * Falls back gracefully — callers should catch HTTP errors and show dummy data.
 */
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const body = await readBody(event)

  const pythonUrl: string =
    (config as Record<string, unknown>).pythonAgentUrl as string
    ?? 'http://localhost:8000'

  try {
    const response = await $fetch(`${pythonUrl}/api/dashboard`, {
      method: 'POST',
      body,
      // Give the agents up to 60 s to compute (they call LLMs + calculators)
      timeout: 60_000,
    })
    return response
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err)
    throw createError({
      statusCode: 503,
      statusMessage: `AI agent unavailable: ${msg}`,
    })
  }
})
