<template>
  <div class="inv">
    <header class="inv__hero">
      <p class="inv__eyebrow">Research · Not a broker</p>
      <h1 class="inv__title">Stocks &amp; index funds</h1>
      <p class="inv__lead">
        Browse common index funds and large-cap names for learning. AscendFi does not execute trades or hold securities—confirm any
        decision with a licensed professional.
      </p>
    </header>

    <div class="inv__warn">
      Investments can lose value. Past performance does not guarantee future results.
    </div>

    <section class="inv__block">
      <h2 class="inv__h2">Popular index funds (ETFs)</h2>
      <p class="inv__sub">Low-cost diversification; expense ratios change—verify on the fund site.</p>
      <div class="inv__table-wrap">
        <table class="inv__table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th>Theme</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in etfs" :key="row.sym">
              <td class="inv__sym">{{ row.sym }}</td>
              <td>{{ row.name }}</td>
              <td class="inv__muted">{{ row.theme }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="inv__block">
      <h2 class="inv__h2">Watchlist (demo)</h2>
      <p class="inv__sub">Hypothetical last prices for UI only—not live market data.</p>
      <ul class="inv__watch">
        <li v-for="s in stocks" :key="s.sym">
          <span class="inv__sym">{{ s.sym }}</span>
          <span class="inv__co">{{ s.co }}</span>
          <span class="inv__px">${{ s.px.toFixed(2) }}</span>
          <span class="inv__ch" :class="{ 'inv__ch--up': s.ch >= 0 }">{{ s.ch >= 0 ? '+' : '' }}{{ s.ch.toFixed(2) }}%</span>
        </li>
      </ul>
    </section>

    <section class="inv__block inv__block--card">
      <h2 class="inv__h2">Before you invest</h2>
      <ul class="inv__check">
        <li>Emergency fund first if your <NuxtLink to="/dashboard/debt">risk score</NuxtLink> is elevated.</li>
        <li>Use tax-advantaged accounts (401k, IRA) when eligible.</li>
        <li>Rebalance on a schedule, not on headlines.</li>
      </ul>
      <NuxtLink to="/chat" class="inv__ai">Ask the AI Advisor about allocation →</NuxtLink>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
  ssr: false,
})

const etfs = [
  { sym: 'VOO', name: 'Vanguard S&P 500 ETF', theme: 'US large cap' },
  { sym: 'VTI', name: 'Vanguard Total Stock Market ETF', theme: 'Broad US' },
  { sym: 'VXUS', name: 'Vanguard Total International Stock ETF', theme: 'Non-US' },
  { sym: 'BND', name: 'Vanguard Total Bond Market ETF', theme: 'Core bonds' },
  { sym: 'AGG', name: 'iShares Core US Aggregate Bond ETF', theme: 'US investment-grade bonds' },
]

const stocks = [
  { sym: 'AAPL', co: 'Apple Inc.', px: 178.42, ch: 0.35 },
  { sym: 'MSFT', co: 'Microsoft Corp.', px: 402.11, ch: -0.12 },
  { sym: 'JPM', co: 'JPMorgan Chase & Co.', px: 182.65, ch: 0.58 },
  { sym: 'VTI', co: 'Vanguard Total Stock', px: 252.3, ch: 0.21 },
]

useHead({
  title: 'Investments — AI Financial',
  meta: [{ name: 'description', content: 'Educational ETF and stock watchlist — not brokerage or advice.' }],
})
</script>

<style scoped>
.inv {
  max-width: 44rem;
  margin: 0 auto;
}
.inv__hero {
  margin-bottom: 1rem;
}
.inv__eyebrow {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-faint);
  margin: 0 0 0.5rem;
}
.inv__title {
  font-size: clamp(1.35rem, 3vw, 1.65rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 0;
  color: var(--color-text);
}
.inv__lead {
  margin: 0.65rem 0 0;
  font-size: 0.9rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.inv__warn {
  padding: 0.75rem 1rem;
  border-radius: 0.65rem;
  background: color-mix(in srgb, var(--color-primary) 8%, var(--color-surface));
  border: 1px solid var(--color-border);
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
}
.inv__block {
  margin-bottom: 1.75rem;
}
.inv__block--card {
  padding: 1.15rem 1.2rem;
  border-radius: 1rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}
.inv__h2 {
  font-size: 1rem;
  font-weight: 750;
  margin: 0 0 0.35rem;
  color: var(--color-text);
}
.inv__sub {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}
.inv__table-wrap {
  overflow-x: auto;
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}
.inv__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}
.inv__table th,
.inv__table td {
  padding: 0.6rem 0.85rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.inv__table th {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-faint);
  background: var(--color-surface-raised);
}
.inv__table tbody tr:last-child td {
  border-bottom: none;
}
.inv__sym {
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}
.inv__muted {
  color: var(--color-text-muted);
}
.inv__watch {
  list-style: none;
  margin: 0;
  padding: 0;
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}
.inv__watch li {
  display: grid;
  grid-template-columns: 3.5rem 1fr auto auto;
  gap: 0.65rem;
  align-items: center;
  padding: 0.65rem 0.85rem;
  font-size: 0.8125rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}
.inv__watch li:last-child {
  border-bottom: none;
}
.inv__co {
  color: var(--color-text-muted);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.inv__px {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}
.inv__ch {
  font-size: 0.75rem;
  font-weight: 700;
  color: #dc2626;
  font-variant-numeric: tabular-nums;
}
.inv__ch--up {
  color: #16a34a;
}
.inv__check {
  margin: 0 0 1rem;
  padding-left: 1.1rem;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.inv__check li + li {
  margin-top: 0.35rem;
}
.inv__check :deep(a) {
  color: var(--color-primary-dim);
  font-weight: 600;
  text-decoration: none;
}
.inv__ai {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-primary-dim);
  text-decoration: none;
}
.inv__ai:hover {
  text-decoration: underline;
}
</style>
