<template>
  <div class="login-shell">
    <div class="login-card">
      <div class="login-brand">
        <span class="login-brand__logo">↑</span>
        <span class="login-brand__name">AscendFi</span>
      </div>

      <h1 class="login-title">{{ isSignUp ? 'Create account' : 'Sign in' }}</h1>

      <form class="login-form" @submit.prevent="submit">
        <div class="field">
          <label class="field__label">Email</label>
          <input v-model="email" class="field__input" type="email" required autocomplete="email" />
        </div>

        <div class="field">
          <label class="field__label">Password</label>
          <input v-model="password" class="field__input" type="password" required autocomplete="current-password" />
        </div>

        <p v-if="error" class="login-error">{{ error }}</p>
        <p v-if="successMsg" class="login-success">{{ successMsg }}</p>

        <button class="login-btn" type="submit" :disabled="loading">
          {{ loading ? 'Loading…' : isSignUp ? 'Create account' : 'Sign in' }}
        </button>
      </form>

      <button class="login-toggle" @click="isSignUp = !isSignUp">
        {{ isSignUp ? 'Already have an account? Sign in' : "Don't have an account? Sign up" }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { signIn, signUp, loading, error } = useAuth()

const email = ref('')
const password = ref('')
const isSignUp = ref(false)
const successMsg = ref('')

async function submit() {
  successMsg.value = ''
  if (isSignUp.value) {
    const ok = await signUp(email.value, password.value)
    if (ok) successMsg.value = 'Check your email to confirm your account.'
  } else {
    const ok = await signIn(email.value, password.value)
    if (ok) await navigateTo('/')
  }
}
</script>

<style scoped>
.login-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
}
.login-card {
  width: 100%;
  max-width: 380px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  padding: 2rem;
}
.login-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.login-brand__logo {
  font-size: 1.25rem;
  color: var(--color-primary);
  font-weight: 900;
}
.login-brand__name {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.02em;
}
.login-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 1.25rem;
}
.login-form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field__label { font-size: 0.8rem; font-weight: 600; color: var(--color-text-muted); }
.field__input {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  padding: 0.6rem 0.75rem;
  font-size: 0.9rem;
  color: var(--color-text);
  outline: none;
  transition: border-color 0.15s;
}
.field__input:focus { border-color: var(--color-primary); }
.login-error { font-size: 0.8rem; color: var(--color-danger); }
.login-success { font-size: 0.8rem; color: var(--color-success); }
.login-btn {
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.7rem 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.login-toggle {
  margin-top: 1rem;
  width: 100%;
  background: none;
  border: none;
  font-size: 0.78rem;
  color: var(--color-text-muted);
  cursor: pointer;
  text-align: center;
}
.login-toggle:hover { color: var(--color-primary); }
</style>
