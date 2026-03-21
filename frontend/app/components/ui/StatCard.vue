<template>
  <div class="stat-card">
    <div class="stat-card__icon" :style="{ background: iconBg }">
      <slot name="icon" />
    </div>
    <div class="stat-card__body">
      <p class="stat-card__label">{{ label }}</p>
      <p class="stat-card__value" :style="{ color: valueColor }">{{ value }}</p>
      <p v-if="sub" class="stat-card__sub" :class="subClass">{{ sub }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string
  sub?: string
  subClass?: string
  iconBg?: string
  valueColor?: string
}>()
</script>

<style scoped>
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  padding: 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}
.stat-card__icon {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.625rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-card__label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}
.stat-card__value {
  font-size: 1.625rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
}
.stat-card__sub {
  font-size: 0.75rem;
  margin-top: 0.25rem;
  color: var(--color-text-muted);
}
</style>
