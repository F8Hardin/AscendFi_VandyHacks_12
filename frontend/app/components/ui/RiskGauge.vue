<template>
  <div class="risk-gauge" :style="{ '--gauge-color': gaugeColor, '--gauge-bg': gaugeBg }">
    <div class="risk-gauge__ring">
      <svg viewBox="0 0 100 100" class="risk-gauge__svg">
        <!-- Track -->
        <circle cx="50" cy="50" r="38" fill="none" stroke-width="8"
          class="risk-gauge__track" />
        <!-- Progress -->
        <circle cx="50" cy="50" r="38" fill="none" stroke-width="8"
          class="risk-gauge__progress"
          :stroke-dasharray="`${circumference}`"
          :stroke-dashoffset="dashOffset"
          transform="rotate(-90 50 50)" />
      </svg>
      <div class="risk-gauge__center">
        <span class="risk-gauge__pct">{{ pct }}%</span>
      </div>
    </div>
    <p class="risk-gauge__label">{{ label }}</p>
    <span class="risk-gauge__badge" :style="{ background: gaugeBg, color: gaugeColor }">
      {{ levelLabel }}
    </span>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  probability: number  // 0.0 - 1.0
  level: string        // low | moderate | high | critical
  label: string
}>()

const levelColors: Record<string, { color: string; bg: string; label: string }> = {
  low:      { color: '#22c55e', bg: 'rgba(34,197,94,0.12)',    label: 'Low Risk'      },
  moderate: { color: '#f59e0b', bg: 'rgba(245,158,11,0.12)',   label: 'Moderate Risk' },
  high:     { color: '#f97316', bg: 'rgba(249,115,22,0.12)',   label: 'High Risk'     },
  critical: { color: '#ef4444', bg: 'rgba(239,68,68,0.12)',    label: 'Critical'      },
}

const meta = computed(() => levelColors[props.level] ?? levelColors.moderate)
const gaugeColor = computed(() => meta.value.color)
const gaugeBg = computed(() => meta.value.bg)
const levelLabel = computed(() => meta.value.label)
const pct = computed(() => Math.round(props.probability * 100))
const circumference = 2 * Math.PI * 38
const dashOffset = computed(() => circumference - (props.probability * circumference))
</script>

<style scoped>
.risk-gauge {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  text-align: center;
}
.risk-gauge__ring {
  position: relative;
  width: 8rem;
  height: 8rem;
}
.risk-gauge__svg {
  width: 100%;
  height: 100%;
}
.risk-gauge__track {
  stroke: var(--color-surface-raised);
}
.risk-gauge__progress {
  stroke: var(--gauge-color);
  stroke-linecap: round;
  transition: stroke-dashoffset 1s ease;
}
.risk-gauge__center {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.risk-gauge__pct {
  font-size: 1.625rem;
  font-weight: 700;
  color: var(--gauge-color);
}
.risk-gauge__label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
.risk-gauge__badge {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.2rem 0.65rem;
  border-radius: var(--radius-badge);
}
</style>
