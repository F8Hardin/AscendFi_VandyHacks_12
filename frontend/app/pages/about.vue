<template>
  <div class="page">
    <h1 class="page__title">About us</h1>
    <p class="page__lead">
      AI Financial is the public name for <strong class="page__strong">AscendFi</strong>, built at
      <strong class="page__strong">VandyHacks 12</strong>. We combine a Nuxt frontend with a FastAPI backend and
      pluggable AI agents to help people see risk early, pay down debt smarter, and move toward stability.
    </p>
    <p class="page__body">
      The stack is intentionally hackathon-practical: demo financial data today, Supabase and real accounts when you
      wire them in. Same APIs power the dashboard visuals and the conversational advisor.
    </p>
    <div class="page__actions">
      <NuxtLink to="/dashboard" class="page__cta page__cta--primary">Get started</NuxtLink>
      <NuxtLink to="/login" class="page__cta page__cta--ghost">Log in</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'marketing' })

useHead({
  title: 'About — AI Financial',
  meta: [{ name: 'description', content: 'About AscendFi / AI Financial and VandyHacks 12.' }],
})
</script>

<style scoped>
.page {
  max-width: 42rem;
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
  margin-bottom: 1.25rem;
}
.page__strong {
  color: var(--color-text);
  font-weight: 600;
}
.page__body {
  font-size: 0.9375rem;
  line-height: 1.65;
  color: var(--color-text-muted);
  margin-bottom: 2rem;
}
.page__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.page__cta {
  display: inline-flex;
  padding: 0.65rem 1.25rem;
  font-weight: 600;
  font-size: 0.9rem;
  border-radius: 0.5rem;
  text-decoration: none;
}
.page__cta--primary {
  background: var(--color-primary);
  color: var(--color-on-primary);
}
.page__cta--primary:hover {
  filter: brightness(1.06);
}
.page__cta--ghost {
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
}
.page__cta--ghost:hover {
  color: var(--color-text);
  background: var(--color-surface);
}
</style>
