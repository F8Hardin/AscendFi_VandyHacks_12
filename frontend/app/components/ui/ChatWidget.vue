<template>
  <div class="chat-widget" :style="containerStyle">
    <!-- Closed: pill toggle button -->
    <template v-if="!open">
      <button class="chat-toggle" @click="toggle" aria-label="Open AI Advisor">
        <span class="chat-toggle__icon">💬</span>
        <span class="chat-toggle__label">AI Advisor</span>
      </button>
    </template>

    <!-- Open: [drag tab] + [panel] side by side -->
    <template v-else>
      <!-- Curved drag tab on left edge -->
      <div
        class="chat-drag-tab"
        :class="{ 'chat-drag-tab--active': isDragging }"
        @mousedown.prevent="onDragStart"
        title="Drag to move"
      >
        <span class="chat-drag-tab__grip"><span /><span /><span /></span>
      </div>

      <!-- Panel -->
      <div class="chat-panel" :style="{ width: size.w + 'px', height: size.h + 'px' }">
        <!-- Header -->
        <div class="chat-panel__header">
          <div class="chat-panel__header-info">
            <span class="chat-panel__dot" />
            <span class="chat-panel__title">AscendFi Advisor</span>
          </div>
          <button class="chat-panel__close" @click="open = false" aria-label="Close chat">✕</button>
        </div>

        <!-- Messages -->
        <div ref="messagesEl" class="chat-panel__messages">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="['wm', msg.role === 'user' ? 'wm--user' : 'wm--ai']"
          >
            <div class="wm__bubble">{{ msg.content }}</div>
          </div>
          <div v-if="streaming" class="wm wm--ai">
            <div class="wm__bubble">{{ streamBuffer }}<span class="cursor">▌</span></div>
          </div>
        </div>

        <!-- Input -->
        <form @submit.prevent="send" class="chat-panel__input">
          <textarea
            v-model="input"
            @keydown.enter.exact.prevent="send"
            placeholder="Ask about your finances..."
            rows="1"
            class="chat-panel__field"
          />
          <button type="submit" :disabled="!input.trim() || streaming" class="chat-panel__send">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </form>

        <!-- Resize grip -->
        <div class="chat-resize-grip" @mousedown.prevent="onResizeStart" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()

interface Message { role: 'user' | 'assistant'; content: string }

const open = ref(false)
const messages = ref<Message[]>([{
  role: 'assistant',
  content: "Hi! I'm your AscendFi advisor. Ask me anything about your financial situation.",
}])
const input = ref('')
const streaming = ref(false)
const streamBuffer = ref('')
const messagesEl = ref<HTMLElement>()
const sessionId = ref<string | null>(null)

// ── Position & size ──────────────────────────────────────────────
const TAB_W = 22
const pos = ref({ x: 0, y: 0 })
const size = ref({ w: 360, h: 480 })
const posInited = ref(false)
const isDragging = ref(false)
const isResizing = ref(false)
const MIN_W = 280, MIN_H = 320, MAX_W = 720, MAX_H = 860

const containerStyle = computed(() => {
  if (!open.value) {
    // Closed: anchor to bottom-right via CSS defaults
    return {}
  }
  return {
    top: pos.value.y + 'px',
    left: pos.value.x + 'px',
    bottom: 'auto',
    right: 'auto',
  }
})

async function toggle() {
  open.value = true
  if (!posInited.value) {
    pos.value = {
      x: window.innerWidth - TAB_W - size.value.w - 24,
      y: window.innerHeight - size.value.h - 24,
    }
    posInited.value = true
  }
  if (!sessionId.value) {
    try {
      const res = await fetch(`${config.public.agentBase}/agent/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({}),
      })
      const data = await res.json()
      sessionId.value = data.sessionId
    } catch (e) {
      console.error('Failed to acquire agent session:', e)
    }
  }
}

// ── Drag (move) ──────────────────────────────────────────────────
let dragOrigin = { mx: 0, my: 0, px: 0, py: 0 }

function onDragStart(e: MouseEvent) {
  isDragging.value = true
  dragOrigin = { mx: e.clientX, my: e.clientY, px: pos.value.x, py: pos.value.y }
  document.body.style.userSelect = 'none'
  window.addEventListener('mousemove', onDragMove)
  window.addEventListener('mouseup', onDragEnd)
}

function onDragMove(e: MouseEvent) {
  pos.value = {
    x: Math.max(0, Math.min(window.innerWidth - TAB_W - size.value.w, dragOrigin.px + e.clientX - dragOrigin.mx)),
    y: Math.max(0, Math.min(window.innerHeight - size.value.h, dragOrigin.py + e.clientY - dragOrigin.my)),
  }
}

function onDragEnd() {
  isDragging.value = false
  document.body.style.userSelect = ''
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', onDragEnd)
}

// ── Resize ───────────────────────────────────────────────────────
let resizeOrigin = { mx: 0, my: 0, w: 0, h: 0 }

function onResizeStart(e: MouseEvent) {
  isResizing.value = true
  resizeOrigin = { mx: e.clientX, my: e.clientY, w: size.value.w, h: size.value.h }
  document.body.style.userSelect = 'none'
  window.addEventListener('mousemove', onResizeMove)
  window.addEventListener('mouseup', onResizeEnd)
}

function onResizeMove(e: MouseEvent) {
  size.value = {
    w: Math.max(MIN_W, Math.min(MAX_W, resizeOrigin.w + e.clientX - resizeOrigin.mx)),
    h: Math.max(MIN_H, Math.min(MAX_H, resizeOrigin.h + e.clientY - resizeOrigin.my)),
  }
}

function onResizeEnd() {
  isResizing.value = false
  document.body.style.userSelect = ''
  window.removeEventListener('mousemove', onResizeMove)
  window.removeEventListener('mouseup', onResizeEnd)
}

onUnmounted(() => {
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', onDragEnd)
  window.removeEventListener('mousemove', onResizeMove)
  window.removeEventListener('mouseup', onResizeEnd)
  document.body.style.userSelect = ''
})

// ── Chat ─────────────────────────────────────────────────────────
async function send() {
  const text = input.value.trim()
  if (!text || streaming.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  if (!sessionId.value) {
    messages.value.push({ role: 'assistant', content: 'CONNECTION ERROR: Please contact system admin' })
    return
  }
  streaming.value = true
  streamBuffer.value = ''
  await nextTick(); scrollToBottom()

  try {
    let res: Response
    try {
      res = await fetch(
        `${config.public.agentBase}/agent/chat/${sessionId.value}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ messages: messages.value }),
        }
      )
    } catch {
      messages.value.push({ role: 'assistant', content: 'CONNECTION ERROR: Please contact system admin' })
      return
    }
    if (!res.ok) {
      messages.value.push({ role: 'assistant', content: 'CONNECTION ERROR: Please contact system admin' })
      return
    }
    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      for (const line of decoder.decode(value, { stream: true }).split('\n')) {
        if (!line.startsWith('data: ')) continue
        const raw = line.slice(6).trim()
        if (!raw) continue
        try {
          const event = JSON.parse(raw)
          if (event.type === 'token') {
            streamBuffer.value += event.text
            await nextTick(); scrollToBottom()
          }
        } catch {}
      }
    }
    messages.value.push({ role: 'assistant', content: streamBuffer.value })
  } finally {
    streaming.value = false
    streamBuffer.value = ''
    await nextTick(); scrollToBottom()
  }
}

function scrollToBottom() {
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
}
</script>

<style scoped>
/* ── Widget container ─────────────────────────────────────────── */
.chat-widget {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 1000;
  display: flex;
  align-items: center;
}

/* ── Closed: toggle pill ──────────────────────────────────────── */
.chat-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.1rem;
  background: var(--color-primary);
  color: #000;
  font-weight: 700;
  font-size: 0.875rem;
  border: none;
  border-radius: 9999px;
  cursor: pointer;
  box-shadow: 0 4px 24px rgba(34, 197, 94, 0.35);
  transition: transform 0.15s, box-shadow 0.15s;
}
.chat-toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 28px rgba(34, 197, 94, 0.45);
}
.chat-toggle__icon { font-size: 1rem; line-height: 1; }
.chat-toggle__label { line-height: 1; }

/* ── Curved drag tab (left edge) ──────────────────────────────── */
.chat-drag-tab {
  width: 22px;
  height: 64px;
  flex-shrink: 0;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
  border-right: none;
  border-radius: 10px 0 0 10px;
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  box-shadow: -3px 0 10px rgba(0, 0, 0, 0.3);
}
.chat-drag-tab:hover { background: var(--color-border); }
.chat-drag-tab--active { cursor: grabbing; background: var(--color-border); }

.chat-drag-tab__grip {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}
.chat-drag-tab__grip span {
  display: block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--color-text-muted);
}

/* ── Panel ────────────────────────────────────────────────────── */
.chat-panel {
  position: relative;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.55);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Header ───────────────────────────────────────────────────── */
.chat-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-raised);
  flex-shrink: 0;
}
.chat-panel__header-info { display: flex; align-items: center; gap: 0.5rem; }
.chat-panel__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  box-shadow: 0 0 6px var(--color-primary);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}
.chat-panel__title { font-size: 0.875rem; font-weight: 600; color: var(--color-text); }
.chat-panel__close {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 0.875rem;
  line-height: 1;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: color 0.15s;
}
.chat-panel__close:hover { color: var(--color-text); }

/* ── Messages ─────────────────────────────────────────────────── */
.chat-panel__messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.chat-panel__messages::-webkit-scrollbar { width: 4px; }
.chat-panel__messages::-webkit-scrollbar-track { background: transparent; }
.chat-panel__messages::-webkit-scrollbar-thumb { background: var(--color-border); border-radius: 2px; }

.wm { display: flex; }
.wm--user { justify-content: flex-end; }
.wm--ai   { justify-content: flex-start; }
.wm__bubble {
  max-width: 85%;
  padding: 0.6rem 0.875rem;
  border-radius: 1rem;
  font-size: 0.8125rem;
  line-height: 1.55;
  white-space: pre-wrap;
}
.wm--user .wm__bubble {
  background: var(--color-primary-dim);
  color: #fff;
  border-bottom-right-radius: 0.25rem;
}
.wm--ai .wm__bubble {
  background: var(--color-surface-raised);
  color: var(--color-text);
  border-bottom-left-radius: 0.25rem;
}
.cursor { animation: blink 0.8s infinite; }
@keyframes blink { 0%,100% { opacity: 1 } 50% { opacity: 0 } }

/* ── Input ────────────────────────────────────────────────────── */
.chat-panel__input {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}
.chat-panel__field {
  flex: 1;
  resize: none;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
  border-radius: 0.625rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-text);
  font-family: inherit;
  outline: none;
  line-height: 1.4;
  max-height: 100px;
  overflow-y: auto;
  transition: border-color 0.15s;
  field-sizing: content;
}
.chat-panel__field:focus { border-color: var(--color-primary); }
.chat-panel__field::placeholder { color: var(--color-text-faint); }
.chat-panel__send {
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  background: var(--color-primary);
  color: #000;
  border: none;
  border-radius: 0.625rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.15s, transform 0.15s;
}
.chat-panel__send:hover:not(:disabled) { transform: scale(1.05); }
.chat-panel__send:disabled { opacity: 0.35; cursor: not-allowed; }

/* ── Resize grip (bottom-right corner) ────────────────────────── */
.chat-resize-grip {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  cursor: nwse-resize;
  z-index: 1;
}
.chat-resize-grip::after {
  content: '';
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 10px;
  height: 10px;
  background: repeating-linear-gradient(
    -45deg,
    var(--color-text-faint) 0,
    var(--color-text-faint) 1px,
    transparent 1px,
    transparent 3px
  );
  opacity: 0.5;
  border-radius: 1px;
}
.chat-resize-grip:hover::after { opacity: 1; }
</style>
