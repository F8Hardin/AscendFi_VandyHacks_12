<template>
  <div class="page">
    <h1 class="page__title">Get started</h1>
    <p class="page__lead">Create your account to open the dashboard and AI advisor.</p>

    <form class="page__form" @submit.prevent="onSubmit">
      <div class="page__row">
        <label class="page__field">
          <span class="page__label">Legal first name</span>
          <input
            v-model.trim="legalFirstName"
            type="text"
            class="page__input"
            name="legal-first-name"
            autocomplete="given-name"
            required
          />
        </label>
        <label class="page__field">
          <span class="page__label">Legal last name</span>
          <input
            v-model.trim="legalLastName"
            type="text"
            class="page__input"
            name="legal-last-name"
            autocomplete="family-name"
            required
          />
        </label>
      </div>

      <label class="page__field">
        <span class="page__label">State</span>
        <select v-model="stateCode" class="page__select" required>
          <option disabled value="">Select your state</option>
          <option v-for="s in US_STATES" :key="s.code" :value="s.code">{{ s.name }}</option>
        </select>
      </label>

      <label class="page__field">
        <span class="page__label">Email</span>
        <input
          v-model.trim="email"
          type="email"
          class="page__input"
          placeholder="you@example.com"
          autocomplete="email"
          required
        />
      </label>

      <label class="page__field">
        <span class="page__label">Password</span>
        <input
          v-model="password"
          type="password"
          class="page__input"
          placeholder="••••••••"
          autocomplete="new-password"
          minlength="8"
          required
        />
      </label>

      <div class="page__field page__field--human">
        <span class="page__label">Verify you are a human</span>
        <p class="page__human-hint">Protected by Cloudflare Turnstile.</p>
        <ClientOnly>
          <TurnstileWidget
            :site-key="turnstileSiteKey"
            @verified="onTurnstileVerified"
            @expired="onTurnstileExpired"
          />
          <template #fallback>
            <div class="page__turnstile-placeholder">Loading verification…</div>
          </template>
        </ClientOnly>
      </div>

      <label class="page__consent">
        <input v-model="consentAccepted" type="checkbox" class="page__checkbox" required />
        <span class="page__consent-text">
          I accept the
          <NuxtLink to="/terms" class="page__inline-link" @click.stop>Terms of use</NuxtLink>
          and
          <NuxtLink to="/privacy" class="page__inline-link" @click.stop>Privacy policy</NuxtLink>
          .
        </span>
      </label>

      <p v-if="displayError" class="page__error">{{ displayError }}</p>
      <p v-if="successMsg" class="page__success">{{ successMsg }}</p>

      <button type="submit" class="page__cta" :disabled="loading || !canSubmit">
        {{ loading ? 'Loading…' : 'Next' }}
      </button>
    </form>

    <p class="page__hint">
      Already have an account?
      <NuxtLink :to="loginLink" class="page__link">Log in</NuxtLink>
    </p>

    <p class="page__hint page__hint--sub">
      <NuxtLink to="/" class="page__link page__link--muted">← Back to home</NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { US_STATES } from '~/utils/usStates'

definePageMeta({
  layout: 'marketing',
  middleware: ['guest'],
})

const route = useRoute()
const config = useRuntimeConfig()
const { signUp, loading, error } = useAuth()

const legalFirstName = ref('')
const legalLastName = ref('')
const stateCode = ref('')
const email = ref('')
const password = ref('')
const consentAccepted = ref(false)
const successMsg = ref('')
const formError = ref('')
const turnstileToken = ref<string | null>(null)

const turnstileSiteKey = computed(() => (config.public.turnstileSiteKey as string)?.trim() ?? '')
const needsTurnstile = computed(() => turnstileSiteKey.value.length > 0)

const canSubmit = computed(() => {
  if (!consentAccepted.value) return false
  if (needsTurnstile.value && !turnstileToken.value) return false
  return true
})

const displayError = computed(() => formError.value || error.value)

const loginLink = computed(() => {
  const r = route.query.redirect
  if (typeof r === 'string' && r.startsWith('/') && !r.startsWith('//')) {
    return { path: '/login', query: { redirect: r } }
  }
  return '/login'
})

useHead({
  title: 'Get started — AI Financial',
  meta: [{ name: 'description', content: 'Create an AI Financial account.' }],
})

function onTurnstileVerified(token: string) {
  turnstileToken.value = token
  formError.value = ''
}

function onTurnstileExpired() {
  turnstileToken.value = null
}

async function onSubmit() {
  successMsg.value = ''
  formError.value = ''
  error.value = null

  if (!consentAccepted.value) {
    formError.value = 'Please accept the terms and privacy policy to continue.'
    return
  }

  if (needsTurnstile.value && !turnstileToken.value) {
    formError.value = 'Please complete the human verification.'
    return
  }

  if (needsTurnstile.value && turnstileToken.value) {
    try {
      await $fetch('/api/turnstile', {
        method: 'POST',
        body: { token: turnstileToken.value },
      })
    } catch (e: unknown) {
      const msg =
        e && typeof e === 'object' && 'data' in e && e.data && typeof (e.data as { message?: string }).message === 'string'
          ? (e.data as { message: string }).message
          : 'Human verification failed. Please try again.'
      formError.value = msg
      turnstileToken.value = null
      return
    }
  }

  const result = await signUp(email.value, password.value, {
    legalFirstName: legalFirstName.value,
    legalLastName: legalLastName.value,
    stateCode: stateCode.value,
  })

  if (!result.ok) return

  if (result.needsEmailConfirmation) {
    successMsg.value = 'Check your email to confirm your account, then log in.'
    return
  }

  successMsg.value = 'Account ready. Redirecting…'
  await navigateTo(typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard')
}
</script>

<style scoped>
.page {
  max-width: 32rem;
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
.page__row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
@media (min-width: 520px) {
  .page__row {
    grid-template-columns: 1fr 1fr;
  }
}
.page__field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.page__field--human {
  margin-top: 0.25rem;
}
.page__human-hint {
  margin: 0 0 0.35rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
.page__turnstile-placeholder {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  padding: 0.75rem 0;
}
.page__label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
}
.page__input,
.page__select {
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
.page__select {
  cursor: pointer;
  appearance: none;
  background-image: linear-gradient(45deg, transparent 50%, var(--color-text-muted) 50%),
    linear-gradient(135deg, var(--color-text-muted) 50%, transparent 50%);
  background-position: calc(100% - 1.15rem) 55%, calc(100% - 0.75rem) 55%;
  background-size: 5px 5px, 5px 5px;
  background-repeat: no-repeat;
}
.page__input:focus,
.page__select:focus {
  border-color: var(--color-primary);
}
.page__input::placeholder {
  color: var(--color-text-faint);
}
.page__consent {
  display: flex;
  gap: 0.65rem;
  align-items: flex-start;
  cursor: pointer;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}
.page__checkbox {
  margin-top: 0.2rem;
  flex-shrink: 0;
  width: 1rem;
  height: 1rem;
  accent-color: var(--color-primary);
}
.page__consent-text {
  flex: 1;
}
.page__inline-link {
  color: var(--color-primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.page__inline-link:hover {
  filter: brightness(1.08);
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
  color: var(--color-text-muted);
}
.page__hint--sub {
  margin-top: 0.75rem;
}
.page__link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
}
.page__link:hover {
  text-decoration: underline;
}
.page__link--muted {
  font-weight: 500;
  color: var(--color-text-muted);
}
</style>
