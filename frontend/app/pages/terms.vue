<template>
  <div class="legal">
    <h1 class="legal__title">Terms of use</h1>
    <p class="legal__updated">Last updated: March 2026</p>
    <div class="legal__body">
      <p>
        By using AI Financial (AscendFi), you agree these terms apply to the software as offered in your environment
        (e.g. local demo, hackathon deployment). The service is provided “as is” for education and experimentation.
      </p>
      <p>
        Nothing on this site is an offer of banking, brokerage, insurance, or legal services. AI outputs are
        informational only and may be wrong. You are solely responsible for financial and legal decisions.
      </p>
      <p>
        AI Financial is sponsored and maintained with support from Capital One for innovation and education; it is not
        an official Capital One product, and Capital One’s consumer terms do not govern this demo unless separately
        agreed.
      </p>
      <p>
        We may update these terms as the project evolves. Continued use after changes constitutes acceptance of the
        updated terms.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'marketing' })
useHead({ title: 'Terms of use — AI Financial' })
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
</style>
