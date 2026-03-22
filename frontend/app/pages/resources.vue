<template>
  <div class="page">
    <h1 class="page__title">Resources</h1>
    <p class="page__lead">
      Quick links to explore the app and backend capabilities. Perfect for demos and onboarding.
    </p>
    <div class="page__cards">
      <NuxtLink to="/dashboard" class="card">
        <h2 class="card__title">Dashboard</h2>
        <p class="card__body">KPIs, risk gauges, charts, and debt snapshot with demo data.</p>
      </NuxtLink>
      <NuxtLink to="/chat" class="card">
        <h2 class="card__title">AI Advisor</h2>
        <p class="card__body">Streaming chat via the Node backend and Docker agent (LM Studio on the host).</p>
      </NuxtLink>
      <a :href="apiDocsUrl" target="_blank" rel="noopener noreferrer" class="card">
        <h2 class="card__title">API docs</h2>
        <p class="card__body">Open <code>/docs</code> when <code>backend_agent/api</code> is running (FastAPI).</p>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'marketing' })

const config = useRuntimeConfig()
const apiDocsUrl = computed(() => {
  const base = String(config.public.apiBase ?? 'http://localhost:8000/api')
  const origin = base.replace(/\/api\/?$/, '')
  return `${origin}/docs`
})

useHead({
  title: 'Resources — AI Financial',
  meta: [{ name: 'description', content: 'Links to dashboard, AI chat, and API documentation.' }],
})
</script>

<style scoped>
.page {
  max-width: 48rem;
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
  font-size: 1.0625rem;
  line-height: 1.65;
  color: var(--color-text-muted);
  margin-bottom: 2rem;
}
.page__cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.card {
  display: block;
  padding: 1.25rem 1.35rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.card:hover {
  border-color: color-mix(in srgb, var(--color-primary) 40%, var(--color-border));
  box-shadow: var(--shadow-card-hover);
}
.card__title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.35rem;
}
.card__body {
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--color-text-muted);
  margin: 0;
}
.card code {
  font-size: 0.8em;
  background: var(--color-surface-raised);
  padding: 0.1rem 0.35rem;
  border-radius: 0.25rem;
}
</style>
