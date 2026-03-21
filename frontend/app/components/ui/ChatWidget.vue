<template>
  <div class="chat-widget" :class="{ 'chat-widget--open': open }">
    <!-- Toggle button -->
    <button class="chat-widget__toggle" @click="open = !open" :aria-label="open ? 'Close chat' : 'Open AI Advisor'">
      <span v-if="!open" class="chat-widget__toggle-icon">💬</span>
      <span v-else class="chat-widget__toggle-icon">✕</span>
      <span v-if="!open" class="chat-widget__toggle-label">AI Advisor</span>
    </button>

    <!-- Chat panel -->
    <Transition name="slide-up">
      <div v-if="open" class="chat-widget__panel">
        <!-- Header -->
        <div class="chat-widget__header">
          <div class="chat-widget__header-info">
            <span class="chat-widget__header-dot" />
            <span class="chat-widget__header-title">AscendFi Advisor</span>
          </div>
          <button class="chat-widget__close" @click="open = false">✕</button>
        </div>

        <!-- Messages -->
        <div ref="messagesEl" class="chat-widget__messages">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="['wm', msg.role === 'user' ? 'wm--user' : 'wm--ai']"
          >
            <div class="wm__bubble">{{ msg.content }}</div>
          </div>
          <div v-if="streaming" class="wm wm--ai">
            <div class="wm__bubble">
              {{ streamBuffer }}<span class="cursor">▌</span>
            </div>
          </div>
        </div>

        <!-- Input -->
        <form @submit.prevent="send" class="chat-widget__input">
          <textarea
            v-model="input"
            @keydown.enter.exact.prevent="send"
            placeholder="Ask about your finances..."
            rows="1"
            class="chat-widget__field"
          />
          <button type="submit" :disabled="!input.trim() || streaming" class="chat-widget__send">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </form>
      </div>
    </Transition>
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

async function send() {
  const text = input.value.trim()
  if (!text || streaming.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  streaming.value = true
  streamBuffer.value = ''
  await nextTick(); scrollToBottom()

  try {
    const res = await fetch(`${config.public.apiBase}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: messages.value }),
    })
    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      for (const line of decoder.decode(value).split('\n')) {
        if (!line.startsWith('data: ')) continue
        const raw = line.slice(6)
        if (raw === '[DONE]') break
        try { streamBuffer.value += JSON.parse(raw).text; await nextTick(); scrollToBottom() } catch {}
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
  flex-direction: column;
  align-items: flex-end;
  gap: 0.75rem;
}

/* ── Toggle button ────────────────────────────────────────────── */
.chat-widget__toggle {
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
.chat-widget__toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 28px rgba(34, 197, 94, 0.45);
}
.chat-widget--open .chat-widget__toggle {
  padding: 0.65rem 0.9rem;
}
.chat-widget__toggle-icon { font-size: 1rem; line-height: 1; }
.chat-widget__toggle-label { line-height: 1; }

/* ── Panel ────────────────────────────────────────────────────── */
.chat-widget__panel {
  width: 360px;
  height: 480px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.55);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Header ───────────────────────────────────────────────────── */
.chat-widget__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-raised);
  flex-shrink: 0;
}
.chat-widget__header-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.chat-widget__header-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  box-shadow: 0 0 6px var(--color-primary);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
.chat-widget__header-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
.chat-widget__close {
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
.chat-widget__close:hover { color: var(--color-text); }

/* ── Messages ─────────────────────────────────────────────────── */
.chat-widget__messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.chat-widget__messages::-webkit-scrollbar { width: 4px; }
.chat-widget__messages::-webkit-scrollbar-track { background: transparent; }
.chat-widget__messages::-webkit-scrollbar-thumb { background: var(--color-border); border-radius: 2px; }

.wm { display: flex; }
.wm--user { justify-content: flex-end; }
.wm--ai  { justify-content: flex-start; }
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
.chat-widget__input {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}
.chat-widget__field {
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
.chat-widget__field:focus { border-color: var(--color-primary); }
.chat-widget__field::placeholder { color: var(--color-text-faint); }
.chat-widget__send {
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
.chat-widget__send:hover:not(:disabled) { transform: scale(1.05); }
.chat-widget__send:disabled { opacity: 0.35; cursor: not-allowed; }

/* ── Transition ───────────────────────────────────────────────── */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}
</style>
