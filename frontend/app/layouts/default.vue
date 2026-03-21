<template>
  <div class="app-shell">
    <main ref="mainEl" class="main-content drag-scroll">
      <slot />
    </main>

    <!-- Floating chat widget -->
    <ChatWidget />
  </div>
</template>

<script setup lang="ts">
const { signOut } = useAuth()
const mainEl = useDragScroll()
</script>

<style scoped>
.app-shell {
  height: 100vh;
  overflow: hidden;
  background: var(--color-bg);
  display: flex;
  flex-direction: column;
}
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}
</style>
