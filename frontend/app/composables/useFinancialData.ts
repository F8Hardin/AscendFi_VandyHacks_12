/**
 * Data composable — single source of truth for all financial data.
 * Toggle NUXT_PUBLIC_USE_DUMMY_DATA=true for local dev / demos.
 * Set to false and plug in Supabase fetch logic below when ready.
 *
 * Data is only populated when the user is logged in. Logged-out visitors
 * always receive null regardless of the dummy-data flag.
 */
import { dummyData } from '~/data/dummy'

export function useFinancialData() {
  const config = useRuntimeConfig()
  const useDummy = config.public.useDummyData === 'true' || config.public.useDummyData === true
  const { isLoggedIn } = useAuth()

  const data = computed(() => {
    if (!isLoggedIn.value) return null
    if (useDummy) return dummyData
    return null // real fetch result would go here
  })

  const isLoading = ref(false)
  const isUsingDummyData = ref(useDummy)

  if (!useDummy && isLoggedIn.value) {
    // ── Supabase / real API fetch goes here ──────────────────────────────
    // const { data: user } = await useSupabaseClient()...
    // Populate `data.value` with the same shape as dummyData
    // ────────────────────────────────────────────────────────────────────
  }

  return { data, isLoading, isUsingDummyData }
}
