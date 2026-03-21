const SESSION_COOKIE = 'ai_financial_session'

/**
 * Demo auth: session cookie so SSR middleware can gate routes before Supabase/real auth.
 */
export function useAuth() {
  const session = useCookie<string | null>(SESSION_COOKIE, {
    default: () => null,
    maxAge: 60 * 60 * 24 * 14,
    path: '/',
    sameSite: 'lax',
  })

  const isLoggedIn = computed(() => Boolean(session.value))

  function login() {
    session.value = 'authenticated'
  }

  function logout() {
    session.value = null
  }

  return { session, isLoggedIn, login, logout }
}
