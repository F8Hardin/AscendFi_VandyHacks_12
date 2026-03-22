<template>
  <div class="stat-card" :class="{ 'stat-card--dash': variant === 'dash' }">
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
withDefaults(
  defineProps<{
    label: string
    value: string
    sub?: string
    subClass?: string
    iconBg?: string
    valueColor?: string
    /** Compact metrics row on dashboard tabs */
    variant?: 'default' | 'dash'
  }>(),
  { variant: 'default' },
)
</script>

<style scoped>
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  padding: 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.stat-card:hover {
  box-shadow: var(--shadow-card-hover);
}
.stat-card--dash {
  border-radius: 1rem;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.8) inset, 0 1px 2px rgba(0, 0, 0, 0.04);
  background: linear-gradient(165deg, var(--color-surface) 0%, var(--color-surface-raised) 100%);
}
.stat-card--dash:hover {
  transform: translateY(-1px);
}
.stat-card--dash .stat-card__icon {
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
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
.stat-card__body {
  min-width: 0;
}
.stat-card__value {
  font-size: clamp(1rem, 2.5vw, 1.5rem);
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
}
.stat-card__sub {
  font-size: 0.75rem;
  margin-top: 0.25rem;
  color: var(--color-text-muted);
}
</style>
