/**
 * Data composable — single source of truth for all financial data.
 * Toggle NUXT_PUBLIC_USE_DUMMY_DATA=true for local dev / demos.
 * Set to false and plug in Supabase fetch logic below when ready.
 */
import { dummyData } from '~/data/dummy'

export function useFinancialData() {
  const config = useRuntimeConfig()
  const useDummy = config.public.useDummyData === 'true' || config.public.useDummyData === true

  const data = ref(useDummy ? dummyData : null)
  const isLoading = ref(!useDummy)
  const isUsingDummyData = ref(useDummy)

  if (!useDummy) {
    // ── Supabase / real API fetch goes here ──────────────────────────────
    // const { data: user } = await useSupabaseClient()...
    // Populate `data.value` with the same shape as dummyData
    // ────────────────────────────────────────────────────────────────────
    isLoading.value = false
  }

  return { data, isLoading, isUsingDummyData }
}
