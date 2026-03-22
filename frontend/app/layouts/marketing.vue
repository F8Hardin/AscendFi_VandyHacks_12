<template>
  <div class="marketing">
    <Transition name="product-scrim">
      <button
        v-if="productMenuOpen"
        type="button"
        class="marketing__dropdown-scrim"
        aria-label="Close product menu"
        @click="closeProductMenu"
      />
    </Transition>

    <header class="marketing__header">
      <div class="marketing__header-inner">
        <NuxtLink to="/" class="marketing__brand" aria-label="AI Financial home">
          <span class="marketing__logo">↑</span>
          <span class="marketing__name">AI Financial</span>
        </NuxtLink>

        <nav class="marketing__nav" aria-label="Primary">
          <div ref="productDropdownEl" class="marketing__nav-dropdown">
            <button
              id="product-menu-button"
              type="button"
              class="marketing__nav-dropdown-toggle"
              :class="{
                'marketing__nav-dropdown-toggle--active': isProductRoute,
                'marketing__nav-dropdown-toggle--open': productMenuOpen,
              }"
              :aria-expanded="productMenuOpen"
              aria-haspopup="true"
              aria-controls="product-menu"
              @click.stop="toggleProductMenu"
            >
              <span class="marketing__nav-dropdown-label">Product</span>
              <svg
                class="marketing__chevron"
                width="14"
                height="14"
                viewBox="0 0 14 14"
                fill="none"
                aria-hidden="true"
              >
                <path
                  d="M3.5 5.25L7 8.75L10.5 5.25"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </button>

            <Transition name="product-panel">
              <div
                v-if="productMenuOpen"
                id="product-menu"
                ref="productPanelEl"
                class="marketing__dropdown-panel"
              >
                <div class="marketing__dropdown-glow" aria-hidden="true" />
                <div class="marketing__dropdown-handle" aria-hidden="true" />
                <header class="marketing__dropdown-header">
                  <p class="marketing__dropdown-kicker">What we offer</p>
                  <p class="marketing__dropdown-headline">Five capabilities for financial recovery</p>
                  <p class="marketing__dropdown-sub">
                    From live dashboards to AI planning—each piece works alone or together.
                  </p>
                </header>

                <nav class="marketing__dropdown-nav" aria-label="Product capabilities">
                  <ul class="marketing__dropdown-list">
                    <li v-for="item in productOfferings" :key="item.id">
                      <NuxtLink
                        :to="`/product#${item.id}`"
                        class="marketing__dropdown-item"
                        :class="`marketing__dropdown-item--accent-${item.accent}`"
                        @click="closeProductMenu"
                      >
                        <span class="marketing__dropdown-item-icon" aria-hidden="true">{{ item.icon }}</span>
                        <span class="marketing__dropdown-item-text">
                          <span class="marketing__dropdown-item-title">{{ item.title }}</span>
                          <span class="marketing__dropdown-item-desc">{{ item.description }}</span>
                        </span>
                        <span class="marketing__dropdown-item-arrow" aria-hidden="true">
                          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                            <path
                              d="M6.75 4.5L11.25 9L6.75 13.5"
                              stroke="currentColor"
                              stroke-width="1.5"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              opacity="0.5"
                            />
                          </svg>
                        </span>
                      </NuxtLink>
                    </li>
                  </ul>
                </nav>

                <footer class="marketing__dropdown-footer">
                  <NuxtLink to="/product" class="marketing__dropdown-cta" @click="closeProductMenu">
                    <span>Full product overview</span>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                      <path
                        d="M3 8H13M13 8L9 4M13 8L9 12"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </NuxtLink>
                  <NuxtLink to="/resources" class="marketing__dropdown-secondary" @click="closeProductMenu">
                    API &amp; developer docs
                  </NuxtLink>
                </footer>
              </div>
            </Transition>
          </div>
          <NuxtLink to="/resources" class="marketing__nav-link" active-class="marketing__nav-link--active">
            Resources
          </NuxtLink>
          <NuxtLink to="/about" class="marketing__nav-link" active-class="marketing__nav-link--active">
            About
          </NuxtLink>
        </nav>

        <div class="marketing__actions">
          <NuxtLink to="/login" class="marketing__btn marketing__btn--ghost">
            Log in
          </NuxtLink>
          <NuxtLink
            :to="{ path: '/get-started', query: { redirect: '/dashboard' } }"
            class="marketing__btn marketing__btn--primary"
          >
            Get started
          </NuxtLink>
        </div>
      </div>
    </header>

    <main class="marketing__main">
      <slot />
    </main>

    <footer class="marketing__footer">
      <div class="marketing__footer-inner">
        <div class="marketing__footer-grid">
          <div class="marketing__footer-col">
            <h2 class="marketing__footer-heading">Product</h2>
            <ul class="marketing__footer-list">
              <li><NuxtLink to="/product">Overview</NuxtLink></li>
              <li><NuxtLink to="/dashboard">Dashboard</NuxtLink></li>
              <li><NuxtLink to="/chat">AI advisor</NuxtLink></li>
              <li><NuxtLink to="/resources">Resources &amp; API</NuxtLink></li>
            </ul>
          </div>
          <div class="marketing__footer-col">
            <h2 class="marketing__footer-heading">Trust &amp; security</h2>
            <ul class="marketing__footer-list">
              <li><NuxtLink to="/about">How we handle data</NuxtLink></li>
              <li><NuxtLink to="/resources">Demo vs. live data</NuxtLink></li>
              <li><span class="marketing__footer-note">Encryption in transit (HTTPS)</span></li>
              <li><span class="marketing__footer-note">No selling of personal financial data</span></li>
            </ul>
          </div>
          <div class="marketing__footer-col">
            <h2 class="marketing__footer-heading">Legal</h2>
            <ul class="marketing__footer-list">
              <li><NuxtLink to="/privacy">Privacy policy</NuxtLink></li>
              <li><NuxtLink to="/terms">Terms of use</NuxtLink></li>
              <li><NuxtLink to="/about">About</NuxtLink></li>
            </ul>
          </div>
          <div class="marketing__footer-col">
            <h2 class="marketing__footer-heading">Account</h2>
            <ul class="marketing__footer-list">
              <li><NuxtLink to="/login">Log in</NuxtLink></li>
              <li>
                <NuxtLink :to="{ path: '/get-started', query: { redirect: '/dashboard' } }">Get started</NuxtLink>
              </li>
            </ul>
            <p class="marketing__footer-col-note">
              Questions? See <NuxtLink to="/resources">Resources</NuxtLink> for API docs and demo setup.
            </p>
          </div>
        </div>

        <div class="marketing__footer-sponsor" role="note">
          <p class="marketing__footer-sponsor-label">Sponsor &amp; maintainer</p>
          <p class="marketing__footer-sponsor-name">Capital One</p>
          <p class="marketing__footer-sponsor-copy">
            AI Financial (AscendFi) is sponsored and maintained with support from Capital One as part of innovation
            and education initiatives. This site is not an official Capital One product or service.
          </p>
        </div>

        <div class="marketing__footer-disclosures">
          <p>
            <strong>Important.</strong> AI Financial provides educational tools and AI-generated insights only. Nothing
            here is personalized investment, tax, or legal advice. Past or projected performance is not a guarantee of
            future results. Verify all information with a qualified professional before acting.
          </p>
          <p>
            Demo mode uses sample data. When live connections are enabled, you remain responsible for your accounts and
            decisions. AI outputs may be inaccurate or incomplete—always review before you rely on them.
          </p>
        </div>

        <div class="marketing__footer-bottom">
          <div class="marketing__footer-brand">
            <span class="marketing__logo marketing__logo--sm">↑</span>
            <span>AI Financial</span>
          </div>
          <p class="marketing__footer-copyright">
            © {{ year }} AscendFi · VandyHacks 12 · All rights reserved
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const year = new Date().getFullYear()
const route = useRoute()

const productOfferings = [
  {
    id: 'recovery-dashboard',
    title: 'Recovery dashboard',
    description: 'KPIs, risk gauges, charts, paycheck split, and activity in one recovery-focused view.',
    icon: '▣',
    accent: 'info',
  },
  {
    id: 'predictive-risk',
    title: 'Predictive risk',
    description: 'Missed payments, 30-day overdraft odds, and credit-shift signals before they hit your wallet.',
    icon: '◎',
    accent: 'danger',
  },
  {
    id: 'debt-optimization',
    title: 'Debt optimization',
    description: 'Avalanche, snowball, or hybrid—timelines, totals, and interest saved vs. minimums only.',
    icon: '◇',
    accent: 'success',
  },
  {
    id: 'behavioral-spending',
    title: 'Behavioral spending',
    description: 'Category trends, anomalies, and life-event context so advice matches real behavior.',
    icon: '◉',
    accent: 'warning',
  },
  {
    id: 'ai-planning',
    title: 'AI advisor & planning',
    description: 'Streaming chat plus autonomous paycheck splits, EF targets, and investment ideas.',
    icon: '✦',
    accent: 'violet',
  },
] as const

const productMenuOpen = ref(false)
const productDropdownEl = ref<HTMLElement | null>(null)
const productPanelEl = ref<HTMLElement | null>(null)

const isProductRoute = computed(() => route.path === '/product')

function closeProductMenu() {
  productMenuOpen.value = false
}

function toggleProductMenu() {
  productMenuOpen.value = !productMenuOpen.value
}

watch(() => route.fullPath, () => {
  closeProductMenu()
})

watch(productMenuOpen, async (open) => {
  if (!open) return
  await nextTick()
  const first = productPanelEl.value?.querySelector<HTMLElement>('.marketing__dropdown-item')
  first?.focus()
})

function onDocClick(e: MouseEvent) {
  const el = productDropdownEl.value
  if (el && !el.contains(e.target as Node)) closeProductMenu()
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') closeProductMenu()
}

onMounted(() => {
  document.addEventListener('click', onDocClick)
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocClick)
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.marketing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  color: var(--color-text);
}

.marketing__header {
  position: sticky;
  top: 0;
  z-index: 50;
  border-bottom: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  box-shadow: var(--shadow-nav);
}

.marketing__header-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0.875rem 1.5rem;
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-areas:
    'brand actions'
    'nav nav';
  align-items: center;
  gap: 0.875rem 1rem;
}

@media (min-width: 900px) {
  .marketing__header-inner {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    gap: 1rem;
  }
}

.marketing__brand {
  grid-area: brand;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--color-text);
  flex-shrink: 0;
  justify-self: start;
}

.marketing__logo {
  font-size: 1.35rem;
  font-weight: 900;
  color: var(--color-primary);
  line-height: 1;
}

.marketing__logo--sm {
  font-size: 1.1rem;
}

.marketing__name {
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.marketing__nav {
  grid-area: nav;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 1.25rem;
  padding-top: 0.25rem;
  border-top: 1px solid var(--color-border);
}

@media (min-width: 900px) {
  .marketing__nav {
    flex: 1;
    justify-content: center;
    padding-top: 0;
    border-top: none;
    gap: 1.75rem;
  }
}

.marketing__nav-link {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.marketing__nav-link:hover {
  color: var(--color-text);
}

.marketing__nav-link--active {
  color: var(--color-primary);
}

/* ── Product dropdown (UX) ─────────────────────────────────── */
.marketing__dropdown-scrim {
  display: none;
}

@media (max-width: 899px) {
  .marketing__dropdown-scrim {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 40;
    margin: 0;
    padding: 0;
    border: none;
    background: rgba(29, 29, 31, 0.38);
    backdrop-filter: blur(8px) saturate(120%);
    -webkit-backdrop-filter: blur(8px) saturate(120%);
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
  }
}

.marketing__nav-dropdown {
  position: relative;
  z-index: 60;
}

.marketing__nav-dropdown-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.65rem;
  margin: -0.45rem -0.5rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-muted);
  transition:
    color 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.marketing__nav-dropdown-toggle:hover {
  color: var(--color-text);
  background: color-mix(in srgb, var(--color-surface-raised) 80%, transparent);
}

.marketing__nav-dropdown-toggle--active:not(.marketing__nav-dropdown-toggle--open) {
  color: var(--color-primary);
}

.marketing__nav-dropdown-toggle--open,
.marketing__nav-dropdown-toggle:focus-visible {
  color: var(--color-text);
  background: var(--color-surface-raised);
  border-color: var(--color-border);
  outline: none;
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--color-primary) 25%, transparent);
}

.marketing__nav-dropdown-toggle--open .marketing__chevron {
  transform: rotate(180deg);
}

.marketing__chevron {
  flex-shrink: 0;
  opacity: 0.75;
  transition: transform 0.22s cubic-bezier(0.34, 1.2, 0.64, 1);
}

.marketing__dropdown-panel {
  position: absolute;
  z-index: 70;
  top: calc(100% + 0.65rem);
  left: 0;
  width: min(26rem, calc(100vw - 2rem));
  overflow: hidden;
  padding: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.9) inset,
    0 4px 6px rgba(0, 0, 0, 0.03),
    0 24px 48px rgba(0, 0, 0, 0.1),
    0 0 60px color-mix(in srgb, var(--color-primary) 6%, transparent);
}

.marketing__dropdown-glow {
  position: absolute;
  inset: -40% -20% auto;
  height: 12rem;
  background: radial-gradient(
    ellipse 70% 60% at 50% 0%,
    color-mix(in srgb, var(--color-primary) 10%, transparent),
    transparent 72%
  );
  pointer-events: none;
}

.marketing__dropdown-handle {
  display: none;
}

.marketing__dropdown-header {
  position: relative;
  padding: 1.15rem 1.25rem 1rem;
  border-bottom: 1px solid var(--color-border);
}

.marketing__dropdown-kicker {
  margin: 0 0 0.35rem;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-primary);
}

.marketing__dropdown-headline {
  margin: 0 0 0.4rem;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.25;
  color: var(--color-text);
}

.marketing__dropdown-sub {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--color-text-muted);
}

.marketing__dropdown-nav {
  position: relative;
  max-height: min(58vh, 22rem);
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 0.5rem;
  scrollbar-width: thin;
  scrollbar-color: var(--color-border) transparent;
}

.marketing__dropdown-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.marketing__dropdown-item {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 0.8rem 0.85rem;
  border-radius: 0.65rem;
  text-decoration: none;
  color: inherit;
  border: 1px solid transparent;
  transition:
    background 0.16s ease,
    border-color 0.16s ease,
    transform 0.16s ease;
}

.marketing__dropdown-item:hover {
  background: var(--color-surface-raised);
  border-color: var(--color-border);
}

.marketing__dropdown-item:focus-visible {
  outline: none;
  background: var(--color-surface-raised);
  border-color: color-mix(in srgb, var(--color-primary) 45%, var(--color-border));
  box-shadow: 0 0 0 2px var(--color-primary-glow);
}

.marketing__dropdown-item:active {
  transform: scale(0.992);
}

.marketing__dropdown-item-icon {
  flex-shrink: 0;
  width: 2.35rem;
  height: 2.35rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  border-radius: 0.55rem;
  background: var(--dd-icon-bg, var(--color-surface-raised));
  color: var(--dd-icon-fg, var(--color-text-muted));
  transition: transform 0.2s ease;
}

.marketing__dropdown-item:hover .marketing__dropdown-item-icon {
  transform: scale(1.05);
}

.marketing__dropdown-item--accent-info .marketing__dropdown-item-icon {
  --dd-icon-bg: var(--color-info-dim);
  --dd-icon-fg: var(--color-info);
}

.marketing__dropdown-item--accent-danger .marketing__dropdown-item-icon {
  --dd-icon-bg: var(--color-danger-dim);
  --dd-icon-fg: var(--color-danger);
}

.marketing__dropdown-item--accent-success .marketing__dropdown-item-icon {
  --dd-icon-bg: var(--color-success-dim);
  --dd-icon-fg: var(--color-success);
}

.marketing__dropdown-item--accent-warning .marketing__dropdown-item-icon {
  --dd-icon-bg: var(--color-warning-dim);
  --dd-icon-fg: var(--color-warning);
}

.marketing__dropdown-item--accent-violet .marketing__dropdown-item-icon {
  --dd-icon-bg: rgba(124, 58, 237, 0.12);
  --dd-icon-fg: #6d28d9;
}

.marketing__dropdown-item-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.marketing__dropdown-item-title {
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--color-text);
}

.marketing__dropdown-item-desc {
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}

.marketing__dropdown-item-arrow {
  flex-shrink: 0;
  align-self: center;
  color: var(--color-text-faint);
  transition:
    color 0.16s ease,
    transform 0.2s ease;
}

.marketing__dropdown-item:hover .marketing__dropdown-item-arrow {
  color: var(--color-primary);
  transform: translateX(2px);
}

.marketing__dropdown-footer {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
  padding: 0.85rem 1rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-subtle);
}

.marketing__dropdown-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  text-decoration: none;
  color: var(--color-on-primary);
  background: var(--color-primary);
  transition: filter 0.15s ease, transform 0.15s ease;
}

.marketing__dropdown-cta:hover {
  filter: brightness(1.05);
}

.marketing__dropdown-cta:active {
  transform: scale(0.98);
}

.marketing__dropdown-secondary {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 0.15s ease;
}

.marketing__dropdown-secondary:hover {
  color: var(--color-primary);
}

@media (max-width: 899px) {
  .marketing__nav-dropdown {
    width: 100%;
  }

  .marketing__dropdown-panel {
    position: fixed;
    left: 0;
    right: 0;
    top: auto;
    bottom: 0;
    width: 100%;
    max-height: min(85vh, 32rem);
    margin-top: 0;
    border-radius: 1.125rem 1.125rem 0 0;
    border-bottom: none;
    display: flex;
    flex-direction: column;
    padding-bottom: env(safe-area-inset-bottom, 0);
    box-shadow:
      0 -8px 32px rgba(0, 0, 0, 0.1),
      0 0 0 1px rgba(255, 255, 255, 0.95) inset;
  }

  .marketing__dropdown-handle {
    display: block;
    width: 2.25rem;
    height: 4px;
    margin: 0.55rem auto 0;
    border-radius: 9999px;
    background: var(--color-border);
    flex-shrink: 0;
  }

  .marketing__dropdown-nav {
    flex: 1;
    min-height: 0;
    max-height: none;
  }
}

/* Panel + scrim motion */
.product-panel-enter-active,
.product-panel-leave-active {
  transition:
    opacity 0.2s cubic-bezier(0.33, 1, 0.68, 1),
    transform 0.24s cubic-bezier(0.33, 1, 0.68, 1);
}

.product-panel-enter-from,
.product-panel-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 899px) {
  .product-panel-enter-from,
  .product-panel-leave-to {
    transform: translateY(16px);
  }
}

.product-scrim-enter-active,
.product-scrim-leave-active {
  transition: opacity 0.22s ease;
}

.product-scrim-enter-from,
.product-scrim-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .marketing__chevron,
  .marketing__dropdown-item,
  .marketing__dropdown-item-icon,
  .marketing__dropdown-item-arrow,
  .marketing__dropdown-cta,
  .marketing__nav-dropdown-toggle {
    transition: none;
  }

  .product-panel-enter-active,
  .product-panel-leave-active,
  .product-scrim-enter-active,
  .product-scrim-leave-active {
    transition: none;
  }

  .product-panel-enter-from,
  .product-panel-leave-to {
    transform: none;
  }
}

.marketing__actions {
  grid-area: actions;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-self: end;
  flex-shrink: 0;
}

.marketing__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  white-space: nowrap;
}

.marketing__btn--ghost {
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  background: transparent;
}

.marketing__btn--ghost:hover {
  color: var(--color-text);
  background: var(--color-surface-raised);
  border-color: var(--color-text-faint);
}

.marketing__btn--primary {
  background: var(--color-primary);
  color: var(--color-on-primary);
  border: 1px solid var(--color-primary);
}

.marketing__btn--primary:hover {
  filter: brightness(1.08);
}

.marketing__main {
  flex: 1;
}

.marketing__footer {
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  margin-top: auto;
}

.marketing__footer-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 3rem 1.5rem 2.5rem;
}

.marketing__footer-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  padding-bottom: 2.5rem;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}

@media (min-width: 640px) {
  .marketing__footer-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 900px) {
  .marketing__footer-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem 1.5rem;
  }
}

.marketing__footer-heading {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-text-faint);
  margin: 0 0 1rem;
}

.marketing__footer-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.marketing__footer-list a {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.marketing__footer-list a:hover,
.marketing__footer-list a.router-link-active {
  color: var(--color-primary);
}

.marketing__footer-note {
  font-size: 0.8125rem;
  color: var(--color-text-faint);
  line-height: 1.45;
}

.marketing__footer-col-note {
  margin: 1rem 0 0;
  font-size: 0.75rem;
  line-height: 1.55;
  color: var(--color-text-faint);
}

.marketing__footer-col-note a {
  color: var(--color-primary);
  text-decoration: none;
}

.marketing__footer-col-note a:hover {
  text-decoration: underline;
}

.marketing__footer-sponsor {
  margin-top: 2rem;
  padding: 1.5rem 1.25rem;
  border-radius: var(--radius-card);
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  text-align: center;
}

.marketing__footer-sponsor-label {
  margin: 0 0 0.35rem;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--color-text-faint);
}

.marketing__footer-sponsor-name {
  margin: 0 0 0.75rem;
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

.marketing__footer-sponsor-copy {
  margin: 0;
  max-width: 40rem;
  margin-inline: auto;
  font-size: 0.8125rem;
  line-height: 1.6;
  color: var(--color-text-muted);
}

.marketing__footer-disclosures {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--color-border);
}

.marketing__footer-disclosures p {
  margin: 0 0 1rem;
  font-size: 0.7rem;
  line-height: 1.65;
  color: var(--color-text-faint);
  max-width: 52rem;
}

.marketing__footer-disclosures p:last-child {
  margin-bottom: 0;
}

.marketing__footer-disclosures strong {
  color: var(--color-text-muted);
  font-weight: 600;
}

.marketing__footer-bottom {
  margin-top: 2rem;
  padding-top: 1.75rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-align: center;
}

.marketing__footer-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 700;
  font-size: 0.95rem;
  margin: 0;
}

.marketing__footer-copyright {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-text-faint);
}
</style>
