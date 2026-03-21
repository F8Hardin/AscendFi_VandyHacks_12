<template>
  <div class="app-shell">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar__brand">
        <span class="sidebar__logo">↑</span>
        <span class="sidebar__name">AscendFi</span>
      </div>

      <nav class="sidebar__nav">
        <NuxtLink to="/" class="nav-item" active-class="nav-item--active">
          <span class="nav-item__icon">⬛</span> Dashboard
        </NuxtLink>
        <NuxtLink to="/chat" class="nav-item" active-class="nav-item--active">
          <span class="nav-item__icon">💬</span> AI Advisor
        </NuxtLink>
      </nav>

      <div class="sidebar__footer">
        <div v-if="isUsingDummyData" class="demo-badge">DEMO DATA</div>
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
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
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
.sidebar__footer { padding-top: 1rem; }
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
