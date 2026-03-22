<template>
  <div class="goals">
    <header class="goals__hero">
      <p class="goals__eyebrow">Your plan</p>
      <h1 class="goals__title">Financial goals</h1>
      <p class="goals__lead">
        Track a few targets alongside your dashboard. Progress is stored in this session for demo purposes—connect Supabase later to
        persist goals.
      </p>
    </header>

    <form class="goals__form" @submit.prevent="addGoal">
      <input v-model="newTitle" type="text" class="goals__input" placeholder="e.g. $1,500 emergency buffer" aria-label="Goal title" />
      <input v-model.number="newTarget" type="number" min="100" step="50" class="goals__input goals__input--narrow" placeholder="Target $" aria-label="Target amount" />
      <button type="submit" class="goals__btn" :disabled="!newTitle.trim() || newTarget <= 0">Add goal</button>
    </form>

    <ul v-if="list.length" class="goals__list">
      <li v-for="g in list" :key="g.id" class="goals__card">
        <div class="goals__card-head">
          <h2 class="goals__name">{{ g.title }}</h2>
          <button type="button" class="goals__x" aria-label="Remove goal" @click="remove(g.id)">✕</button>
        </div>
        <div class="goals__nums">
          <span>${{ g.current.toLocaleString('en-US') }}</span>
          <span class="goals__of">of ${{ g.target.toLocaleString('en-US') }}</span>
        </div>
        <div class="goals__bar" aria-hidden="true">
          <div class="goals__fill" :style="{ width: pct(g) + '%' }" />
        </div>
        <div class="goals__row">
          <button type="button" class="goals__chip" @click="bump(g, 50)">+$50</button>
          <button type="button" class="goals__chip" @click="bump(g, 100)">+$100</button>
          <button type="button" class="goals__chip" @click="bump(g, 250)">+$250</button>
        </div>
      </li>
    </ul>
    <p v-else class="goals__empty">No goals yet—add one above or start from a preset.</p>

    <div class="goals__presets">
      <p class="goals__preset-label">Quick add</p>
      <button v-for="p in presets" :key="p.title" type="button" class="goals__preset" @click="addPreset(p)">
        {{ p.title }} · ${{ p.target.toLocaleString('en-US') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
  ssr: false,
})

interface Goal {
  id: string
  title: string
  target: number
  current: number
}

const list = ref<Goal[]>([
  { id: crypto.randomUUID(), title: 'Emergency fund (30 days expenses)', target: 4500, current: 823 },
  { id: crypto.randomUUID(), title: 'Pay down Chase Visa', target: 3200, current: 900 },
])

const newTitle = ref('')
const newTarget = ref(1000)

const presets = [
  { title: 'Vacation fund', target: 2000 },
  { title: 'IRA contribution room', target: 6500 },
  { title: 'New laptop', target: 1400 },
]

function addGoal() {
  const t = newTitle.value.trim()
  const n = Number(newTarget.value)
  if (!t || n <= 0) return
  list.value.push({ id: crypto.randomUUID(), title: t, target: n, current: 0 })
  newTitle.value = ''
  newTarget.value = 1000
}

function addPreset(p: { title: string; target: number }) {
  list.value.push({ id: crypto.randomUUID(), title: p.title, target: p.target, current: 0 })
}

function remove(id: string) {
  list.value = list.value.filter((g) => g.id !== id)
}

function bump(g: Goal, n: number) {
  g.current = Math.min(g.target, g.current + n)
}

function pct(g: Goal) {
  if (g.target <= 0) return 0
  return Math.min(100, Math.round((g.current / g.target) * 100))
}

useHead({
  title: 'Goals — AI Financial',
  meta: [{ name: 'description', content: 'Set and track simple financial goals alongside your dashboard.' }],
})
</script>

<style scoped>
.goals {
  max-width: 32rem;
  margin: 0 auto;
}
.goals__hero {
  margin-bottom: 1.25rem;
}
.goals__eyebrow {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-faint);
  margin: 0 0 0.5rem;
}
.goals__title {
  font-size: clamp(1.35rem, 3vw, 1.65rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 0;
  color: var(--color-text);
}
.goals__lead {
  margin: 0.65rem 0 0;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.goals__form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}
.goals__input {
  flex: 1;
  min-width: 10rem;
  padding: 0.55rem 0.75rem;
  border-radius: 0.6rem;
  border: 1px solid var(--color-border);
  font-size: 0.875rem;
  background: var(--color-surface);
  color: var(--color-text);
}
.goals__input--narrow {
  flex: 0 0 7rem;
  min-width: 7rem;
}
.goals__btn {
  padding: 0.55rem 1rem;
  border-radius: 0.6rem;
  border: none;
  font-weight: 700;
  font-size: 0.8125rem;
  background: var(--color-primary);
  color: #000;
  cursor: pointer;
}
.goals__btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.goals__list {
  list-style: none;
  margin: 0 0 1.5rem;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.goals__card {
  padding: 1rem 1.1rem;
  border-radius: 1rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}
.goals__card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}
.goals__name {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-text);
}
.goals__x {
  border: none;
  background: var(--color-surface-raised);
  color: var(--color-text-muted);
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.4rem;
  cursor: pointer;
  line-height: 1;
}
.goals__x:hover {
  color: var(--color-text);
}
.goals__nums {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}
.goals__of {
  font-weight: 500;
  color: var(--color-text-muted);
  margin-left: 0.35rem;
}
.goals__bar {
  height: 8px;
  border-radius: 9999px;
  background: var(--color-surface-raised);
  margin-top: 0.65rem;
  overflow: hidden;
}
.goals__fill {
  height: 100%;
  border-radius: 9999px;
  background: linear-gradient(90deg, var(--color-primary), #16a34a);
  transition: width 0.35s ease;
}
.goals__row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.75rem;
}
.goals__chip {
  padding: 0.35rem 0.65rem;
  border-radius: 9999px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-subtle);
  font-size: 0.72rem;
  font-weight: 650;
  cursor: pointer;
  color: var(--color-text-muted);
}
.goals__chip:hover {
  border-color: var(--color-primary);
  color: var(--color-text);
}
.goals__empty {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-bottom: 1rem;
}
.goals__presets {
  padding-top: 0.5rem;
  border-top: 1px dashed var(--color-border);
}
.goals__preset-label {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-faint);
  margin: 0 0 0.5rem;
}
.goals__preset {
  display: block;
  width: 100%;
  text-align: left;
  margin-bottom: 0.4rem;
  padding: 0.55rem 0.75rem;
  border-radius: 0.6rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface-raised);
  font-size: 0.8125rem;
  color: var(--color-text);
  cursor: pointer;
}
.goals__preset:hover {
  border-color: var(--color-primary);
}
</style>
