export default defineNuxtRouteMiddleware((to) => {
  const { isLoggedIn } = useAuth()
  if (!isLoggedIn.value) return

  const redirect = typeof to.query.redirect === 'string' ? to.query.redirect : ''
  if (redirect.startsWith('/') && !redirect.startsWith('//')) {
    return navigateTo(redirect)
  }
  return navigateTo('/dashboard')
})
