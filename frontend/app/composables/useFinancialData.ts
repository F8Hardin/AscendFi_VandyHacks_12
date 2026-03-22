/**
 * Financial dashboard data: dummy mode or live payload from Node backend (Supabase).
 */
import { dummyData } from '~/data/dummy'

type DashboardPayload = typeof dummyData

export function useFinancialData() {
  const config = useRuntimeConfig()
  const useDummy =
    config.public.useDummyData === 'true' || config.public.useDummyData === true
  const { isLoggedIn } = useAuth()

  const liveData = ref<DashboardPayload | null>(null)
  const isLoading = ref(false)
  const isUsingDummyData = ref(useDummy)

  async function refreshLive() {
    if (import.meta.server || useDummy || !isLoggedIn.value) {
      liveData.value = null
      return
    }
    isLoading.value = true
    try {
      liveData.value = await $fetch<DashboardPayload>(`${String(config.public.agentBase)}/api/finance/dashboard`, {
        credentials: 'include',
      })
    } catch {
      liveData.value = null
    } finally {
      isLoading.value = false
    }
  }

  watch(
    [isLoggedIn, () => useDummy],
    () => {
      refreshLive()
    },
    { immediate: true },
  )

  const data = computed<DashboardPayload | null>(() => {
    if (!isLoggedIn.value) return null
    if (useDummy) return dummyData
    return liveData.value
  })

  return { data, isLoading, isUsingDummyData, refreshLive }
}
