<template>
  <div class="set">
    <header class="set__hero">
      <p class="set__eyebrow">Account</p>
      <h1 class="set__title">Settings</h1>
      <p class="set__lead">Preferences and session controls for this device.</p>
    </header>

    <section class="set__card">
      <h2 class="set__h2">Profile</h2>
      <p v-if="user?.email" class="set__row">
        <span class="set__k">Signed in as</span>
        <span class="set__v">{{ user.email }}</span>
      </p>
      <p v-else class="set__muted">Loading profile…</p>
    </section>

    <section class="set__card">
      <h2 class="set__h2">Data source</h2>
      <p class="set__row">
        <span class="set__k">Demo data</span>
        <span class="set__v">{{ isUsingDummyData ? 'On' : 'Off' }}</span>
      </p>
      <p class="set__hint">
        Toggle <code>NUXT_PUBLIC_USE_DUMMY_DATA</code> in <code>frontend/.env</code> and restart the dev server to switch live vs demo
        payloads.
      </p>
    </section>

    <section class="set__card">
      <h2 class="set__h2">Notifications</h2>
      <label class="set__toggle">
        <input v-model="notifDemo" type="checkbox" disabled />
        <span>Payment reminders (coming soon)</span>
      </label>
      <label class="set__toggle">
        <input v-model="weeklyDemo" type="checkbox" disabled />
        <span>Weekly summary email (coming soon)</span>
      </label>
    </section>

    <section class="set__card">
      <h2 class="set__h2">Session</h2>
      <button type="button" class="set__logout" @click="onLogout">Log out on this device</button>
    </section>

    <p class="set__foot">AscendFi · hackathon build</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
  ssr: false,
})

const { user, signOut } = useAuth()
const { isUsingDummyData } = useFinancialData()

const notifDemo = ref(false)
const weeklyDemo = ref(false)

async function onLogout() {
  await signOut()
}

useHead({
  title: 'Settings — AI Financial',
  meta: [{ name: 'description', content: 'Account settings and preferences.' }],
})
</script>

<style scoped>
.set {
  max-width: 28rem;
  margin: 0 auto;
}
.set__hero {
  margin-bottom: 1.5rem;
}
.set__eyebrow {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-faint);
  margin: 0 0 0.5rem;
}
.set__title {
  font-size: clamp(1.35rem, 3vw, 1.65rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 0;
  color: var(--color-text);
}
.set__lead {
  margin: 0.65rem 0 0;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.set__card {
  padding: 1.1rem 1.15rem;
  border-radius: 1rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  margin-bottom: 1rem;
  box-shadow: var(--shadow-card);
}
.set__h2 {
  font-size: 0.82rem;
  font-weight: 750;
  margin: 0 0 0.75rem;
  color: var(--color-text);
}
.set__row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  margin: 0;
  font-size: 0.875rem;
}
.set__k {
  color: var(--color-text-muted);
}
.set__v {
  font-weight: 650;
  color: var(--color-text);
  word-break: break-all;
  text-align: right;
}
.set__muted {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-muted);
}
.set__hint {
  margin: 0.65rem 0 0;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-text-faint);
}
.set__hint code {
  font-size: 0.68rem;
  padding: 0.1rem 0.3rem;
  border-radius: 0.3rem;
  background: var(--color-bg-subtle);
}
.set__toggle {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  margin-bottom: 0.55rem;
  cursor: not-allowed;
  opacity: 0.75;
}
.set__toggle:last-child {
  margin-bottom: 0;
}
.set__logout {
  width: 100%;
  padding: 0.6rem 1rem;
  border-radius: 0.65rem;
  border: 1px solid #dc2626;
  background: transparent;
  color: #dc2626;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
}
.set__logout:hover {
  background: rgba(220, 38, 38, 0.06);
}
.set__foot {
  margin: 1.5rem 0 0;
  font-size: 0.72rem;
  color: var(--color-text-faint);
  text-align: center;
}
</style>
