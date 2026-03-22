export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return

  const { isLoggedIn, sessionReady, fetchSession } = useAuth()
  if (!sessionReady.value) {
    await fetchSession()
  }

  if (!isLoggedIn.value) return

  const redirect = typeof to.query.redirect === 'string' ? to.query.redirect : ''
  if (redirect.startsWith('/') && !redirect.startsWith('//')) {
    return navigateTo(redirect)
  }
  return navigateTo('/dashboard')
})
