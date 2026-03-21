<template>
  <div class="app-root">
    <NuxtRouteAnnouncer />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<style scoped>
.app-root {
  min-height: 100vh;
  background: var(--color-bg);
  color: var(--color-text);
}
</style>
