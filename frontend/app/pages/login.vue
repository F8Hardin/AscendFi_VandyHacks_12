<template>
  <div class="page">
    <h1 class="page__title">{{ isSignUp ? 'Create account' : 'Sign in' }}</h1>
    <p class="page__lead">
      {{ isSignUp ? 'Create an account to get started.' : 'Sign in to open the dashboard and AI advisor.' }}
    </p>

    <form class="page__form" @submit.prevent="onSubmit">
      <label class="page__field">
        <span class="page__label">Email</span>
        <input v-model="email" type="email" class="page__input" placeholder="you@example.com" autocomplete="username" required />
      </label>
      <label class="page__field">
        <span class="page__label">Password</span>
        <input
          v-model="password"
          type="password"
          class="page__input"
          placeholder="••••••••"
          autocomplete="current-password"
          required
        />
      </label>
      <p v-if="error" class="page__error">{{ error }}</p>
      <p v-if="successMsg" class="page__success">{{ successMsg }}</p>
      <button type="submit" class="page__cta" :disabled="loading">
        {{ loading ? 'Loading…' : isSignUp ? 'Create account' : 'Sign in' }}
      </button>
    </form>

    <p class="page__hint">
      <button type="button" class="page__toggle" @click="isSignUp = !isSignUp">
        {{ isSignUp ? 'Already have an account? Sign in' : "Don't have an account? Sign up" }}
      </button>
    </p>

    <p class="page__hint">
      <NuxtLink to="/" class="page__link">← Back to home</NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'marketing',
  middleware: ['guest'],
})

const route = useRoute()
const { signIn, signUp, loading, error } = useAuth()

const email = ref('')
const password = ref('')
const isSignUp = ref(false)
const successMsg = ref('')

useHead({
  title: 'Log in — AI Financial',
  meta: [{ name: 'description', content: 'Sign in to access dashboard and AI advisor.' }],
})

function safeRedirectPath(): string {
  const r = route.query.redirect
  if (typeof r !== 'string' || !r.startsWith('/') || r.startsWith('//')) return '/dashboard'
  return r
}

async function onSubmit() {
  successMsg.value = ''
  if (isSignUp.value) {
    const ok = await signUp(email.value, password.value)
    if (ok) successMsg.value = 'Check your email to confirm your account.'
  } else {
    const ok = await signIn(email.value, password.value)
    if (ok) await navigateTo(safeRedirectPath())
  }
}
</script>

<style scoped>
.page {
  max-width: 28rem;
  margin: 0 auto;
  padding: 3rem 1.5rem 4rem;
}
.page__title {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 1rem;
}
.page__lead {
  font-size: 1rem;
  line-height: 1.65;
  color: var(--color-text-muted);
  margin-bottom: 1.75rem;
}
.page__form {
  padding: 1.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.page__field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.page__label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
}
.page__input {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface-raised);
  color: var(--color-text);
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.15s;
}
.page__input:focus {
  border-color: var(--color-primary);
}
.page__input::placeholder {
  color: var(--color-text-faint);
}
.page__error {
  margin: 0;
  font-size: 0.8rem;
  color: var(--color-danger);
}
.page__success {
  margin: 0;
  font-size: 0.8rem;
  color: var(--color-success);
}
.page__toggle {
  background: none;
  border: none;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0;
}
.page__toggle:hover {
  color: var(--color-primary);
}
.page__cta {
  display: inline-flex;
  width: 100%;
  justify-content: center;
  padding: 0.7rem 1.25rem;
  margin-top: 0.25rem;
  background: var(--color-primary);
  color: var(--color-on-primary);
  font-weight: 600;
  font-size: 0.9rem;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: filter 0.15s, opacity 0.15s;
}
.page__cta:hover:not(:disabled) {
  filter: brightness(1.06);
}
.page__cta:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.page__hint {
  margin: 1.5rem 0 0;
  font-size: 0.875rem;
  text-align: center;
}
.page__link {
  color: var(--color-primary);
  text-decoration: none;
}
.page__link:hover {
  text-decoration: underline;
}
</style>
