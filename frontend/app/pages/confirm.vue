<template>
  <div class="confirm">
    <p class="confirm__text">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const message = ref('Confirming your email…')
const config = useRuntimeConfig()
const { fetchSession } = useAuth()

onMounted(async () => {
  const hash = window.location.hash?.startsWith('#') ? window.location.hash.slice(1) : window.location.hash
  const params = new URLSearchParams(hash)
  const access_token = params.get('access_token')
  const refresh_token = params.get('refresh_token')

  if (!access_token || !refresh_token) {
    message.value = 'Invalid confirmation link. Try signing in.'
    await navigateTo('/login')
    return
  }

  try {
    await $fetch(`${String(config.public.agentBase)}/api/auth/session`, {
      method: 'POST',
      body: { access_token, refresh_token },
      credentials: 'include',
    })
    await fetchSession()
    message.value = 'Success! Redirecting…'
    await navigateTo('/dashboard')
  } catch {
    message.value = 'Could not complete sign-in. Try logging in manually.'
    await navigateTo('/login')
  }
})

useHead({
  title: 'Confirm email — AI Financial',
})
</script>

<style scoped>
.confirm {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--color-bg);
  color: var(--color-text);
}
.confirm__text {
  font-size: 1rem;
  color: var(--color-text-muted);
}
</style>
