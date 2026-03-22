/**
 * Auth via Node backend + Supabase (httpOnly session cookies on the API origin).
 */
export type AuthUser = {
  id: string
  email?: string
  user_metadata?: Record<string, unknown>
  app_metadata?: Record<string, unknown>
}

export type SignUpResult = { ok: true; needsEmailConfirmation: boolean } | { ok: false }

function backendBase(): string {
  const config = useRuntimeConfig()
  return String(config.public.agentBase || 'http://localhost:3120')
}

export function useAuth() {
  const user = useState<AuthUser | null>('auth-user', () => null)
  const sessionReady = useState('auth-session-ready', () => false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isLoggedIn = computed(() => !!user.value)

  async function fetchSession() {
    if (import.meta.server) return
    try {
      const data = await $fetch<{ user: AuthUser | null }>(`${backendBase()}/api/auth/me`, {
        credentials: 'include',
      })
      user.value = data.user
    } catch {
      user.value = null
    } finally {
      sessionReady.value = true
    }
  }

  async function signIn(email: string, password: string) {
    loading.value = true
    error.value = null
    try {
      await $fetch(`${backendBase()}/api/auth/sign-in`, {
        method: 'POST',
        body: { email, password },
        credentials: 'include',
      })
      await fetchSession()
      return true
    } catch (e: unknown) {
      const msg =
        e && typeof e === 'object' && 'data' in e && e.data && typeof (e.data as { message?: string }).message === 'string'
          ? (e.data as { message: string }).message
          : 'Sign in failed'
      error.value = msg
      return false
    } finally {
      loading.value = false
    }
  }

  async function signUp(
    email: string,
    password: string,
    profile?: { legalFirstName: string; legalLastName: string; stateCode: string },
  ): Promise<SignUpResult> {
    loading.value = true
    error.value = null
    try {
      const res = await $fetch<{ user: AuthUser | null; needsEmailConfirmation?: boolean }>(
        `${backendBase()}/api/auth/sign-up`,
        {
          method: 'POST',
          body: { email, password, profile },
          credentials: 'include',
        },
      )
      if (res.needsEmailConfirmation) {
        user.value = null
        return { ok: true, needsEmailConfirmation: true }
      }
      await fetchSession()
      return { ok: true, needsEmailConfirmation: false }
    } catch (e: unknown) {
      const msg =
        e && typeof e === 'object' && 'data' in e && e.data && typeof (e.data as { message?: string }).message === 'string'
          ? (e.data as { message: string }).message
          : 'Sign up failed'
      error.value = msg
      return { ok: false }
    } finally {
      loading.value = false
    }
  }

  async function signOut() {
    loading.value = true
    try {
      await $fetch(`${backendBase()}/api/auth/sign-out`, {
        method: 'POST',
        credentials: 'include',
      }).catch(() => {})
      user.value = null
      sessionReady.value = true
    } finally {
      loading.value = false
    }
    await navigateTo('/login')
  }

  return {
    user,
    sessionReady,
    isLoggedIn,
    loading,
    error,
    fetchSession,
    signIn,
    signUp,
    signOut,
  }
}
