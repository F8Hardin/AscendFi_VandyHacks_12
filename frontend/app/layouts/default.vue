<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar__left">
        <button
          type="button"
          class="topbar__menu-btn"
          :aria-expanded="menuOpen"
          aria-controls="app-drawer"
          @click="menuOpen = true"
        >
          <span class="topbar__burger" aria-hidden="true" />
          <span class="topbar__menu-label">Menu</span>
        </button>
      </div>

      <nav v-if="showDashTabs" class="topbar__tabs" aria-label="Dashboard sections">
        <div class="topbar__tab-rail" :class="topbarTabRailClass">
          <NuxtLink
            to="/dashboard"
            class="topbar__tab"
            data-dash-tab="cash"
            :class="{ 'topbar__tab--active': isDashCash }"
          >
            <span class="topbar__tab-short">Cash</span>
            <span class="topbar__tab-full">Checking &amp; spending</span>
          </NuxtLink>
          <NuxtLink
            to="/dashboard/debt"
            class="topbar__tab"
            data-dash-tab="debt"
            :class="{ 'topbar__tab--active': isDashDebt }"
          >
            <span class="topbar__tab-short">Debt</span>
            <span class="topbar__tab-full">Debt &amp; predictions</span>
          </NuxtLink>
          <NuxtLink
            to="/dashboard/autonomous"
            class="topbar__tab"
            data-dash-tab="auto"
            :class="{ 'topbar__tab--active': isDashAuto }"
          >
            <span class="topbar__tab-short">Auto</span>
            <span class="topbar__tab-full">Autonomous finance</span>
          </NuxtLink>
        </div>
      </nav>
      <div v-else class="topbar__tabs topbar__tabs--placeholder">
        <span class="topbar__page-label">{{ pageLabel }}</span>
      </div>

      <div class="topbar__right">
        <div v-if="isUsingDummyData" class="topbar__demo">Demo data</div>
        <button type="button" class="topbar__logout" @click="onLogout">Log out</button>
      </div>
    </header>

    <Transition name="drawer-fade">
      <div
        v-if="menuOpen"
        class="drawer-scrim"
        aria-hidden="true"
        @click="menuOpen = false"
      />
    </Transition>
    <Transition name="drawer-slide">
      <aside
        v-if="menuOpen"
        id="app-drawer"
        class="drawer"
        role="dialog"
        aria-label="App menu"
      >
        <div class="drawer__head">
          <NuxtLink to="/" class="drawer__brand" @click="menuOpen = false">
            <span class="drawer__logo">↑</span>
            <span>AI Financial</span>
          </NuxtLink>
          <button type="button" class="drawer__close" aria-label="Close menu" @click="menuOpen = false">✕</button>
        </div>

        <div class="drawer__snapshot" aria-label="Account snapshot">
          <template v-if="isLoggedIn && financialSnapshot">
            <div class="drawer__snap-row">
              <span class="drawer__snap-label">Cash (checking)</span>
              <span class="drawer__snap-value">{{ formatMoney(financialSnapshot.checking) }}</span>
            </div>
            <div class="drawer__snap-row">
              <span class="drawer__snap-label">Savings</span>
              <span class="drawer__snap-value">{{ formatMoney(financialSnapshot.savings) }}</span>
            </div>
            <div class="drawer__snap-row drawer__snap-row--debt">
              <span class="drawer__snap-label">Total debt</span>
              <span class="drawer__snap-value drawer__snap-value--debt">{{ formatMoney(financialSnapshot.totalDebt) }}</span>
            </div>
          </template>
          <p v-else-if="isLoggedIn" class="drawer__snap-hint">Load your dashboard to see live balances.</p>
          <p v-else class="drawer__snap-hint">Sign in to see your balance and debt snapshot.</p>
        </div>

        <nav class="drawer__nav" aria-label="App">
          <p class="drawer__nav-label">Navigate</p>
          <NuxtLink to="/dashboard" class="drawer__link" @click="menuOpen = false">
            <span class="drawer__link-icon" aria-hidden="true">⌂</span>
            Dashboard
          </NuxtLink>
          <NuxtLink to="/capital-one" class="drawer__link" @click="menuOpen = false">
            <span class="drawer__link-icon" aria-hidden="true">◇</span>
            Capital One offers
          </NuxtLink>
          <NuxtLink to="/invest" class="drawer__link" @click="menuOpen = false">
            <span class="drawer__link-icon" aria-hidden="true">↗</span>
            Investments
          </NuxtLink>
          <NuxtLink to="/goals" class="drawer__link" @click="menuOpen = false">
            <span class="drawer__link-icon" aria-hidden="true">◎</span>
            Goals
          </NuxtLink>
          <NuxtLink to="/chat" class="drawer__link" @click="menuOpen = false">
            <span class="drawer__link-icon" aria-hidden="true">✳</span>
            AI Advisor
          </NuxtLink>
          <NuxtLink to="/settings" class="drawer__link" @click="menuOpen = false">
            <span class="drawer__link-icon" aria-hidden="true">⚙</span>
            Settings
          </NuxtLink>
        </nav>
      </aside>
    </Transition>

    <main class="main-content" :class="{ 'main-content--dashboard': showDashTabs }">
      <slot />
    </main>

    <ClientOnly>
      <ChatWidget v-if="showDashTabs" />
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { data: financialData, isUsingDummyData } = useFinancialData()
const { signOut, isLoggedIn } = useAuth()

const menuOpen = ref(false)

const financialSnapshot = computed(() => {
  const d = financialData.value
  if (!d) return null
  const totalDebt = d.debts.reduce((s, row) => s + row.balance, 0)
  return {
    checking: d.accounts.checking,
    savings: d.accounts.savings,
    totalDebt,
  }
})

function formatMoney(n: number) {
  const sign = n < 0 ? '−' : ''
  return `${sign}$${Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const showDashTabs = computed(() => route.path.startsWith('/dashboard'))

const isDashCash = computed(
  () => route.path === '/dashboard' || route.path === '/dashboard/',
)
const isDashDebt = computed(() => route.path.startsWith('/dashboard/debt'))
const isDashAuto = computed(() => route.path.startsWith('/dashboard/autonomous'))

const topbarTabRailClass = computed(() => {
  if (isDashCash.value) return 'topbar__tab-rail--cash'
  if (isDashDebt.value) return 'topbar__tab-rail--debt'
  if (isDashAuto.value) return 'topbar__tab-rail--auto'
  return ''
})

const pageLabel = computed(() => {
  if (route.path.startsWith('/chat')) return 'AI Advisor'
  if (route.path.startsWith('/capital-one')) return 'Capital One'
  if (route.path.startsWith('/invest')) return 'Investments'
  if (route.path.startsWith('/goals')) return 'Goals'
  if (route.path.startsWith('/settings')) return 'Settings'
  return 'AI Financial'
})

watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false
  },
)

async function onLogout() {
  await signOut()
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--color-bg);
  display: flex;
  flex-direction: column;
}

.topbar {
  display: grid;
  grid-template-columns: minmax(7rem, 1fr) minmax(0, 3fr) minmax(7rem, 1fr);
  align-items: center;
  gap: 0.75rem;
  padding: 0.55rem 1rem 0.65rem;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: var(--shadow-nav);
}

.topbar__left {
  display: flex;
  justify-content: flex-start;
}

.topbar__menu-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.65rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.topbar__menu-btn:hover {
  background: var(--color-surface-raised);
  border-color: var(--color-text-faint);
}

.topbar__burger {
  display: block;
  width: 1rem;
  height: 2px;
  background: currentColor;
  border-radius: 1px;
  box-shadow: 0 -5px 0 currentColor, 0 5px 0 currentColor;
}

.topbar__menu-label {
  letter-spacing: 0.02em;
}

.topbar__tabs {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.topbar__tab-rail {
  display: flex;
  align-items: stretch;
  padding: 0.2rem;
  border-radius: 9999px;
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border);
  gap: 0.15rem;
  max-width: 100%;
}
.topbar__tab-rail--cash {
  box-shadow: 0 0 0 1px color-mix(in srgb, #2563eb 12%, transparent);
}
.topbar__tab-rail--debt {
  box-shadow: 0 0 0 1px color-mix(in srgb, #c2410c 12%, transparent);
}
.topbar__tab-rail--auto {
  box-shadow: 0 0 0 1px color-mix(in srgb, #6d28d9 12%, transparent);
}

.topbar__tabs--placeholder {
  justify-content: center;
}

.topbar__page-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.topbar__tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.42rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 650;
  color: var(--color-text-muted);
  text-decoration: none;
  white-space: nowrap;
  border: 1px solid transparent;
  transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}
.topbar__tab:hover {
  color: var(--color-text);
  background: color-mix(in srgb, var(--color-surface) 70%, transparent);
}
.topbar__tab-short {
  display: none;
}
.topbar__tab-full {
  display: inline;
}
.topbar__tab--active[data-dash-tab='cash'] {
  color: #1d4ed8;
  background: #fff;
  border-color: color-mix(in srgb, #2563eb 22%, transparent);
  box-shadow: 0 1px 3px rgba(37, 99, 235, 0.12);
}
.topbar__tab--active[data-dash-tab='debt'] {
  color: #9a3412;
  background: #fff;
  border-color: color-mix(in srgb, #c2410c 25%, transparent);
  box-shadow: 0 1px 3px rgba(194, 65, 12, 0.12);
}
.topbar__tab--active[data-dash-tab='auto'] {
  color: #5b21b6;
  background: #fff;
  border-color: color-mix(in srgb, #6d28d9 25%, transparent);
  box-shadow: 0 1px 3px rgba(109, 40, 217, 0.12);
}

.topbar__right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.65rem;
}

.topbar__demo {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #b45309;
  background: rgba(245, 158, 11, 0.14);
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
}

.topbar__logout {
  padding: 0.45rem 0.85rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-muted);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.topbar__logout:hover {
  background: var(--color-surface-raised);
  color: var(--color-text);
}

.drawer-scrim {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.35);
  z-index: 150;
  backdrop-filter: blur(2px);
}

.drawer {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: min(18rem, 88vw);
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  z-index: 160;
  box-shadow: 8px 0 32px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

.drawer__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.drawer__brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 1rem;
  color: var(--color-text);
  text-decoration: none;
}
.drawer__logo {
  color: var(--color-primary);
  font-weight: 900;
}

.drawer__close {
  width: 2rem;
  height: 2rem;
  border: none;
  border-radius: 0.5rem;
  background: var(--color-surface-raised);
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}
.drawer__close:hover {
  color: var(--color-text);
}

.drawer__snapshot {
  margin: 0 1rem;
  padding: 0.85rem 0.95rem;
  border-radius: 0.75rem;
  background: linear-gradient(145deg, var(--color-surface-raised), var(--color-surface));
  border: 1px solid var(--color-border);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.6) inset;
}
.drawer__snap-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
  padding: 0.35rem 0;
  font-size: 0.8125rem;
}
.drawer__snap-row + .drawer__snap-row {
  border-top: 1px solid color-mix(in srgb, var(--color-border) 80%, transparent);
}
.drawer__snap-label {
  color: var(--color-text-muted);
  font-weight: 500;
}
.drawer__snap-value {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}
.drawer__snap-value--debt {
  color: #c2410c;
}
.drawer__snap-row--debt .drawer__snap-label {
  font-weight: 600;
  color: var(--color-text);
}
.drawer__snap-hint {
  margin: 0;
  font-size: 0.78rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}

.drawer__nav {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  gap: 0.25rem;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.drawer__nav-label {
  margin: 0 0 0.35rem 0.35rem;
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-text-faint);
}

.drawer__link {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.65rem 0.85rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text);
  text-decoration: none;
  transition: background 0.15s;
}
.drawer__link-icon {
  width: 1.25rem;
  text-align: center;
  font-size: 0.95rem;
  opacity: 0.85;
}
.drawer__link:hover {
  background: var(--color-surface-raised);
}
.drawer__link.router-link-active {
  background: color-mix(in srgb, var(--color-primary) 12%, var(--color-surface-raised));
  font-weight: 650;
}

.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.22s ease;
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(-100%);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.75rem 1.25rem 2.5rem;
}
.main-content--dashboard {
  background: radial-gradient(120% 80% at 50% -10%, color-mix(in srgb, var(--color-primary) 6%, transparent), transparent),
    var(--color-bg);
  /* Room for fixed ChatWidget bubble (bottom-right) */
  padding-bottom: 5.5rem;
}

@media (max-width: 900px) {
  .topbar {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    gap: 0.5rem;
  }
  .topbar__left,
  .topbar__right {
    justify-content: center;
  }
  .topbar__tabs {
    order: 3;
    width: 100%;
  }
  .topbar__tab-rail {
    width: 100%;
    justify-content: center;
  }
  .topbar__tab {
    flex: 1;
    justify-content: center;
    text-align: center;
    padding-inline: 0.4rem;
  }
  .topbar__tab-short {
    display: inline;
  }
  .topbar__tab-full {
    display: none;
  }
}
</style>
