<template>
  <div class="page">
    <header class="page__hero">
      <h1 class="page__title">Product</h1>
      <p class="page__lead">
        AI Financial (AscendFi) bundles five complementary capabilities—dashboard intelligence, predictive risk, debt
        optimization, behavioral spending, and AI-guided planning—so recovery is measurable, not motivational noise.
      </p>
      <NuxtLink :to="{ path: '/get-started', query: { redirect: '/dashboard' } }" class="page__cta">Get started</NuxtLink>
    </header>

    <section id="recovery-dashboard" class="page__section page__anchor">
      <div class="page__section-icon" style="--icon-bg: var(--color-info-dim); --icon-fg: var(--color-info)">▣</div>
      <h2 class="page__section-title">Recovery dashboard</h2>
      <p class="page__section-lead">
        A single view built for financial recovery—not a generic banking home screen.
      </p>
      <ul class="page__bullets">
        <li>Monthly income, checking balance, total debt, and credit score at a glance</li>
        <li>Animated risk gauges for overdraft, missed payments, and credit-shift outlook</li>
        <li>Spending breakdown and debt payoff projection charts</li>
        <li>Recommended paycheck split and active debts with minimums and APR context</li>
        <li>Recent activity feed to connect cash flow to decisions</li>
      </ul>
    </section>

    <section id="predictive-risk" class="page__section page__section--alt page__anchor">
      <div class="page__section-icon" style="--icon-bg: var(--color-danger-dim); --icon-fg: var(--color-danger)">◎</div>
      <h2 class="page__section-title">Predictive risk</h2>
      <p class="page__section-lead">
        Surface problems early so you can act before fees, hits to credit, or cash crunches compound.
      </p>
      <ul class="page__bullets">
        <li><strong>Missing payments</strong> — estimated probability of falling behind on upcoming bills</li>
        <li><strong>Overdraft</strong> — 30-day likelihood based on balances, timing, and obligations</li>
        <li><strong>Credit score shifts</strong> — directional signals when a meaningful change may be ahead</li>
      </ul>
      <p class="page__api-note">
        Backend: <code>POST /api/predict/missing-payments</code>, <code>…/overdraft</code>, <code>…/credit-score</code>
      </p>
    </section>

    <section id="debt-optimization" class="page__section page__anchor">
      <div class="page__section-icon" style="--icon-bg: var(--color-primary-glow); --icon-fg: var(--color-primary)">◇</div>
      <h2 class="page__section-title">Debt optimization</h2>
      <p class="page__section-lead">
        Turn scattered balances into a concrete payoff sequence you can follow month by month.
      </p>
      <ul class="page__bullets">
        <li>Ingest balances, APRs, and minimums across cards, loans, and other liabilities</li>
        <li>Compare <strong>avalanche</strong>, <strong>snowball</strong>, and <strong>hybrid</strong> strategies</li>
        <li>Output a timeline with estimated payoff date and total interest saved vs. minimums-only</li>
      </ul>
      <p class="page__api-note">Backend: <code>POST /api/debt/optimize</code></p>
    </section>

    <section id="behavioral-spending" class="page__section page__section--alt page__anchor">
      <div class="page__section-icon" style="--icon-bg: var(--color-info-dim); --icon-fg: var(--color-info)">◎</div>
      <h2 class="page__section-title">Behavioral spending</h2>
      <p class="page__section-lead">
        Understand <em>how</em> you spend—not only <em>how much</em>—so coaching fits your real life.
      </p>
      <ul class="page__bullets">
        <li>Category-level habits and month-over-month trends</li>
        <li>Anomaly detection on unusual spikes or pattern breaks</li>
        <li>Context for life-event-driven spending (job change, medical, move, family changes)</li>
      </ul>
      <p class="page__api-note">Backend: <code>POST /api/spending/analyze</code></p>
    </section>

    <section id="ai-planning" class="page__section page__anchor">
      <div class="page__section-icon" style="--icon-bg: var(--color-warning-dim); --icon-fg: var(--color-warning)">✦</div>
      <h2 class="page__section-title">AI advisor &amp; autonomous planning</h2>
      <p class="page__section-lead">
        Conversational guidance plus structured plans—same agent stack, two ways to engage.
      </p>
      <ul class="page__bullets">
        <li>
          <strong>AI advisor</strong> — streaming chat over SSE; ask about your situation and next steps with pluggable
          models (e.g. Claude or LM Studio)
        </li>
        <li>
          <strong>Autonomous finance</strong> — suggested paycheck allocation across needs, debt paydown, emergency
          savings, investments, and discretionary spend
        </li>
        <li>Emergency fund targets and investment vehicle ideas tuned to your current financial picture</li>
      </ul>
      <p class="page__api-note">
        Backend: <code>POST /api/chat/stream</code>, <code>POST /api/finance/autonomous-plan</code>
      </p>
    </section>

    <footer class="page__footer">
      <NuxtLink :to="{ path: '/get-started', query: { redirect: '/dashboard' } }" class="page__cta">Get started</NuxtLink>
      <NuxtLink to="/resources" class="page__cta page__cta--ghost">Resources &amp; API</NuxtLink>
    </footer>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'marketing' })

useHead({
  title: 'Product — AI Financial',
  meta: [{ name: 'description', content: 'Five offerings: dashboard, risk, debt, behavior, and AI planning.' }],
})
</script>

<style scoped>
.page {
  max-width: 44rem;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 4rem;
}
.page__hero {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--color-border);
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
  margin-bottom: 1.5rem;
}
.page__cta {
  display: inline-flex;
  padding: 0.65rem 1.25rem;
  background: var(--color-primary);
  color: var(--color-on-primary);
  font-weight: 600;
  font-size: 0.9rem;
  border-radius: 0.5rem;
  text-decoration: none;
}
.page__cta:hover {
  filter: brightness(1.06);
}
.page__cta--ghost {
  background: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-border);
}
.page__cta--ghost:hover {
  background: var(--color-surface-raised);
  filter: none;
}
.page__anchor {
  scroll-margin-top: 5.5rem;
}
.page__section {
  padding: 2rem 0;
  border-bottom: 1px solid var(--color-border);
}
.page__section--alt {
  background: var(--color-bg-subtle);
  margin-left: -1.5rem;
  margin-right: -1.5rem;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
  border-bottom: none;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}
.page__section-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.625rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  background: var(--icon-bg);
  color: var(--icon-fg);
  margin-bottom: 1rem;
}
.page__section-title {
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 0.5rem;
}
.page__section-lead {
  font-size: 0.9375rem;
  line-height: 1.55;
  color: var(--color-text-muted);
  margin: 0 0 1rem;
}
.page__bullets {
  margin: 0;
  padding-left: 1.2rem;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  line-height: 1.65;
}
.page__bullets li {
  margin-bottom: 0.5rem;
}
.page__bullets strong {
  color: var(--color-text);
}
.page__api-note {
  margin: 1.25rem 0 0;
  font-size: 0.72rem;
  color: var(--color-text-faint);
  line-height: 1.5;
}
.page__api-note code {
  font-size: 0.68rem;
  background: var(--color-bg);
  padding: 0.15rem 0.35rem;
  border-radius: 0.25rem;
  border: 1px solid var(--color-border);
}
.page__section--alt .page__api-note code {
  background: var(--color-bg);
}
.page__footer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 2rem;
}
</style>
