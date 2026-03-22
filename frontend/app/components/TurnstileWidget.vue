<template>
  <div class="turnstile">
    <div v-if="!siteKey" class="turnstile__fallback">
      Add <code>NUXT_PUBLIC_TURNSTILE_SITE_KEY</code> to enable Cloudflare Turnstile.
    </div>
    <div v-else ref="hostEl" class="turnstile__host" />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  siteKey: string
}>()

const emit = defineEmits<{
  verified: [token: string]
  expired: []
}>()

const hostEl = ref<HTMLElement | null>(null)
let widgetId: string | undefined

declare global {
  interface Window {
    turnstile?: {
      render: (el: HTMLElement | string, options: Record<string, unknown>) => string
      reset: (id: string) => void
      remove: (id: string) => void
    }
  }
}

function mountWidget() {
  const el = hostEl.value
  const key = props.siteKey?.trim()
  if (!el || !key || !import.meta.client) return
  if (typeof window.turnstile === 'undefined') return

  if (widgetId) {
    try {
      window.turnstile.remove(widgetId)
    } catch {
      /* ignore */
    }
    widgetId = undefined
  }

  el.innerHTML = ''
  widgetId = window.turnstile.render(el, {
    sitekey: key,
    callback: (token: string) => emit('verified', token),
    'expired-callback': () => emit('expired'),
    'error-callback': () => emit('expired'),
  })
}

function ensureScript(): Promise<void> {
  if (!import.meta.client) return Promise.resolve()
  if (window.turnstile) return Promise.resolve()

  return new Promise((resolve, reject) => {
    const existing = document.querySelector('script[data-cf-turnstile-api]')
    if (existing) {
      if (window.turnstile) {
        resolve()
        return
      }
      existing.addEventListener('load', () => resolve(), { once: true })
      existing.addEventListener('error', () => reject(new Error('Turnstile script failed')), { once: true })
      return
    }
    const s = document.createElement('script')
    s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'
    s.async = true
    s.defer = true
    s.dataset.cfTurnstileApi = '1'
    s.onload = () => resolve()
    s.onerror = () => reject(new Error('Turnstile script failed'))
    document.head.appendChild(s)
  })
}

onMounted(async () => {
  if (!props.siteKey?.trim()) return
  try {
    await ensureScript()
    await nextTick()
    mountWidget()
  } catch {
    emit('expired')
  }
})

onUnmounted(() => {
  if (import.meta.client && widgetId && window.turnstile) {
    try {
      window.turnstile.remove(widgetId)
    } catch {
      /* ignore */
    }
  }
})

watch(
  () => props.siteKey,
  async () => {
    if (!import.meta.client || !props.siteKey?.trim()) return
    try {
      await ensureScript()
      await nextTick()
      mountWidget()
    } catch {
      emit('expired')
    }
  },
)

defineExpose({
  reset() {
    if (widgetId && window.turnstile) window.turnstile.reset(widgetId)
  },
})
</script>

<style scoped>
.turnstile__host {
  min-height: 4.25rem;
  display: flex;
  align-items: center;
}
.turnstile__fallback {
  font-size: 0.8rem;
  line-height: 1.45;
  color: var(--color-text-muted);
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px dashed var(--color-border);
  background: var(--color-surface-raised);
}
.turnstile__fallback code {
  font-size: 0.72rem;
}
</style>
