<template>
  <div class="app-shell">
    <!-- Sidebar -->
    <aside class="sidebar">
      <NuxtLink to="/" class="sidebar__brand" aria-label="AI Financial home">
        <span class="sidebar__logo">↑</span>
        <span class="sidebar__name">AI Financial</span>
      </NuxtLink>

      <nav class="sidebar__nav">
        <NuxtLink to="/dashboard" class="nav-item" active-class="nav-item--active">
          <span class="nav-item__icon">⬛</span> Dashboard
        </NuxtLink>
        <NuxtLink to="/chat" class="nav-item" active-class="nav-item--active">
          <span class="nav-item__icon">💬</span> AI Advisor
        </NuxtLink>
      </nav>

      <div class="sidebar__footer">
        <div v-if="isUsingDummyData" class="demo-badge">DEMO DATA</div>
        <button type="button" class="sidebar__logout" @click="onLogout">Log out</button>
      </div>
    </aside>

    <!-- Main -->
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const { isUsingDummyData } = useFinancialData()
const { signOut } = useAuth()

async function onLogout() {
  await signOut()
}
</script>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: color-mix(in srgb, var(--color-surface) 92%, var(--color-bg));
  border-right: 1px solid var(--color-border);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  position: fixed;
  top: 0; left: 0; bottom: 0;
}
.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  padding: 0 0.25rem;
  text-decoration: none;
  color: inherit;
}
.sidebar__logo {
  font-size: 1.25rem;
  color: var(--color-primary);
  font-weight: 900;
}
.sidebar__name {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.02em;
}
.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.nav-item:hover {
  background: var(--color-surface-raised);
  color: var(--color-text);
}
.nav-item--active {
  background: var(--color-primary-glow);
  color: var(--color-primary);
}
.nav-item__icon { font-size: 0.9rem; }
.sidebar__footer {
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.sidebar__logout {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-muted);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.sidebar__logout:hover {
  background: var(--color-surface-raised);
  color: var(--color-text);
  border-color: var(--color-text-faint);
}
.demo-badge {
  background: rgba(245,158,11,0.15);
  color: #f59e0b;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 0.3rem 0.75rem;
  border-radius: 9999px;
  text-align: center;
}
.main-content {
  margin-left: 220px;
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}
</style>
