/**
 * useAuth — thin interface over Supabase authentication.
 *
 * The landing page (and any future page) should call these methods directly.
 * Supabase-specific imports are contained here so swapping providers only
 * requires changes to this file.
 */
export function useAuth() {
  const supabase = useSupabaseClient()
  const user = useSupabaseUser()
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!user.value)

  async function signIn(email: string, password: string) {
    loading.value = true
    error.value = null
    const { error: err } = await supabase.auth.signInWithPassword({ email, password })
    if (err) error.value = err.message
    loading.value = false
    return !err
  }

  async function signUp(email: string, password: string) {
    loading.value = true
    error.value = null
    const { error: err } = await supabase.auth.signUp({ email, password })
    if (err) error.value = err.message
    loading.value = false
    return !err
  }

  async function signOut() {
    loading.value = true
    await supabase.auth.signOut()
    loading.value = false
    await navigateTo('/login')
  }

  return { user, isAuthenticated, loading, error, signIn, signUp, signOut }
}
