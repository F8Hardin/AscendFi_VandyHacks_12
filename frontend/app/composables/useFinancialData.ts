/**
 * Financial dashboard data composable.
 *
 * Priority (when logged in):
 *   1. Node backend `/api/finance/dashboard` — reads real Supabase data and enriches
 *      it with Python AI risk scores (accounts, debts, transactions → AI risks, charts)
 *   2. Python agent `/api/agent/dashboard` — AI-computed metrics from DEFAULT_PROFILE
 *      (fallback when Supabase is unreachable or user is not logged in)
 *   3. Static dummy data — when both backends are unreachable or useDummyData is true
 *
 * On sign-up, the backend seeds the user's Supabase tables with realistic demo
 * financial data, so every new account has a fully populated dashboard immediately.
 */
import { dummyData } from '~/data/dummy'

type DashboardPayload = typeof dummyData

/** Default profile used when calling the AI agent without real Supabase data. */
const DEFAULT_PROFILE = {
  name:          dummyData.user.name,
  monthlyIncome: dummyData.user.monthlyIncome,
  checking:      dummyData.accounts.checking,
  savings:       dummyData.accounts.savings,
  creditScore:   dummyData.accounts.creditScore,
  age:           30,
  debts:         dummyData.debts,
  transactions:  dummyData.recentActivity,
  recentActivity: dummyData.recentActivity,
}

export function useFinancialData() {
  const config = useRuntimeConfig()
  const useDummy = config.public.useDummyData === 'true' || config.public.useDummyData === true
  const { isLoggedIn } = useAuth()

  const liveData   = ref<DashboardPayload | null>(null)  // Supabase + AI enriched
  const aiData     = ref<DashboardPayload | null>(null)  // AI-only fallback
  const isLoading  = ref(false)
  const isUsingDummyData = ref(useDummy)
  const aiError    = ref<string | null>(null)

  // ── Live path: Supabase + AI enrichment (Node backend) ─────────────────────
  async function refreshLive() {
    if (import.meta.server || !isLoggedIn.value) {
      liveData.value = null
      return
    }
    isLoading.value = true
    try {
      liveData.value = await $fetch<DashboardPayload>(
        `${String(config.public.agentBase)}/api/finance/dashboard`,
        { credentials: 'include' },
      )
      isUsingDummyData.value = false
      aiError.value = null
    } catch {
      liveData.value = null
    } finally {
      isLoading.value = false
    }
  }

  // ── AI-only path: Python agent with a given profile (no Supabase) ───────────
  async function refreshAI(profile?: Record<string, unknown>) {
    if (import.meta.server) return
    isLoading.value = true
    aiError.value   = null
    try {
      aiData.value = await $fetch<DashboardPayload>('/api/agent/dashboard', {
        method: 'POST',
        body:   { profile: profile ?? DEFAULT_PROFILE },
      })
      isUsingDummyData.value = false
    } catch (err: unknown) {
      aiError.value = err instanceof Error ? err.message : String(err)
      aiData.value  = null
      isUsingDummyData.value = true
    } finally {
      isLoading.value = false
    }
  }

  // On mount: choose the right path based on auth state
  onMounted(async () => {
    if (useDummy) return
    if (isLoggedIn.value) {
      // Logged in: fetch real Supabase data (already AI-enriched by Node backend)
      await refreshLive()
    } else {
      // Not logged in: call Python AI with default demo profile
      await refreshAI()
    }
  })

  // Re-fetch when auth state changes
  watch(isLoggedIn, async (loggedIn) => {
    if (useDummy) return
    if (loggedIn) {
      await refreshLive()
    } else {
      liveData.value = null
      await refreshAI()
    }
  })

  // Resolved data: Supabase-live > AI-fallback > static dummy
  const data = computed<DashboardPayload | null>(() => {
    if (useDummy)         return dummyData
    if (liveData.value)   return liveData.value
    if (aiData.value)     return aiData.value
    if (isLoading.value)  return null      // show skeleton
    return dummyData                        // last resort
  })

  return {
    data,
    isLoading,
    isUsingDummyData,
    aiError,
    /** Re-fetch and AI-enrich from Supabase (requires login). */
    refreshLive,
    /** Re-run AI computation with an optional custom profile. */
    refreshAI,
  }
}
