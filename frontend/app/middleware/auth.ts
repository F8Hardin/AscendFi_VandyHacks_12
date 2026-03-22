export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return

  const { isLoggedIn, sessionReady, fetchSession } = useAuth()
  if (!sessionReady.value) {
    await fetchSession()
  }

  if (!isLoggedIn.value) {
    return navigateTo({
      path: '/login',
      query: { redirect: to.fullPath },
    })
  }
})
