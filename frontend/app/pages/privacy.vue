<template>
  <div class="legal">
    <h1 class="legal__title">Privacy policy</h1>
    <p class="legal__updated">Last updated: March 2026</p>
    <div class="legal__body">
      <p>
        AI Financial (AscendFi) is a demonstration and educational project. This policy describes how we intend to
        treat information in a production deployment. In the current hackathon build, demo mode may use only local or
        sample data—review the README and your deployment configuration.
      </p>
      <p>
        We do not sell your personal financial data. When you connect real accounts in the future, access should be
        limited to what you authorize, transmitted over HTTPS, and stored according to your chosen provider (e.g.
        Supabase) and applicable law.
      </p>
      <p>
        AI-generated outputs are not human-reviewed by default. Do not submit secrets or full account credentials into
        chat unless your environment is designed for it.
      </p>
      <p>
        For questions, use your team’s official channels or see <NuxtLink to="/resources">Resources</NuxtLink>.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'marketing' })
useHead({ title: 'Privacy policy — AI Financial' })
</script>

<style scoped>
.legal {
  max-width: 40rem;
  margin: 0 auto;
  padding: 3rem 1.5rem 4rem;
}
.legal__title {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 0.35rem;
}
.legal__updated {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  margin-bottom: 1.75rem;
}
.legal__body p {
  font-size: 0.9375rem;
  line-height: 1.65;
  color: var(--color-text-muted);
  margin: 0 0 1.1rem;
}
.legal__body a {
  color: var(--color-primary);
  text-decoration: none;
}
.legal__body a:hover {
  text-decoration: underline;
}
</style>
