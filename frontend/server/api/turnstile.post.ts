/**
 * Verifies a Cloudflare Turnstile token server-side.
 * Set NUXT_TURNSTILE_SECRET_KEY; if unset, verification is skipped (local demo only).
 */
export default defineEventHandler(async (event) => {
  const { token } = await readBody<{ token?: string }>(event)
  if (!token?.trim()) {
    throw createError({ statusCode: 400, statusMessage: 'Missing Turnstile token' })
  }

  const secret = useRuntimeConfig(event).turnstileSecretKey as string
  if (!secret) {
    return { success: true as const, skipped: true }
  }

  const body = new URLSearchParams()
  body.set('secret', secret)
  body.set('response', token.trim())

  const data = await $fetch<{ success: boolean; 'error-codes'?: string[] }>(
    'https://challenges.cloudflare.com/turnstile/v0/siteverify',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    },
  )

  if (!data.success) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Human verification failed. Please try again.',
    })
  }

  return { success: true as const }
})
