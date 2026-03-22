<template>
  <div class="chat-page">
    <div class="chat-page__header">
      <h1 class="chat-page__title">AI Financial Advisor</h1>
      <p class="chat-page__sub">Ask anything about your financial situation</p>
    </div>

    <div class="chat-wrap">
      <!-- Messages -->
      <div ref="messagesEl" class="messages">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          :class="['message', msg.role === 'user' ? 'message--user' : 'message--ai']"
        >
          <div class="message__bubble prose" v-html="renderMarkdown(msg.content)" />
        </div>

        <!-- Live streaming bubble -->
        <template v-if="streaming">
          <!-- Thinking steps (tool calls) -->
          <div v-if="thinkingSteps.length" class="thinking-steps">
            <span
              v-for="(step, i) in thinkingSteps"
              :key="i"
              class="thinking-chip"
            >{{ step }}</span>
          </div>
          <div class="message message--ai">
            <div class="message__bubble prose" v-html="renderMarkdown(streamBuffer) + '<span class=\'cursor\'>▌</span>'" />
          </div>
        </template>
      </div>

      <!-- Error overlay -->
      <div v-if="connectionError" class="status-overlay status-overlay--error">
        <span class="status-overlay__icon">⚠</span>
        <span>
          Agent is not reachable. Make sure both servers are running:<br>
          <code>cd Hackathon &amp;&amp; uvicorn app.main:app --port 8000</code><br>
          <code>cd backend &amp;&amp; npm run dev</code>
        </span>
      </div>

      <!-- Connecting overlay -->
      <div v-else-if="!sessionReady" class="status-overlay status-overlay--connecting">
        <span class="connecting-dot" />
        Connecting to your advisor…
      </div>

      <!-- Input -->
      <form @submit.prevent="send" class="chat-input">
        <textarea
          v-model="input"
          @keydown.enter.exact.prevent="send"
          placeholder="Describe your financial situation or ask a question..."
          rows="2"
          class="chat-input__field"
        />
        <button
          type="submit"
          :disabled="!input.trim() || streaming || !sessionReady || connectionError"
          class="chat-input__btn"
        >
          Send
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'

function renderMarkdown(text: string): string {
  return marked.parse(text, { async: false }) as string
}

definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const config = useRuntimeConfig()
const { buildContext } = useChatFinancialContext()

interface Message { role: 'user' | 'assistant'; content: string }

const messages = ref<Message[]>([{
  role: 'assistant',
  content: "Hello! I'm your AscendFi advisor. Tell me about your financial situation and I'll help you build a recovery plan.",
}])
const input = ref('')
const streaming = ref(false)
const streamBuffer = ref('')
const thinkingSteps = ref<string[]>([])
const messagesEl = ref<HTMLElement | null>(null)

// Session management
const sessionId = ref<string | null>(null)
const sessionReady = computed(() => sessionId.value !== null)
const connectionError = ref(false)

onMounted(async () => {
  try {
    const res = await fetch(`${config.public.agentBase}/agent/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({}),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    sessionId.value = data.sessionId
  } catch (e) {
    console.error('Failed to acquire agent session:', e)
    connectionError.value = true
  }
})

async function send() {
  const text = input.value.trim()
  if (!text || streaming.value || !sessionId.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  streaming.value = true
  streamBuffer.value = ''
  thinkingSteps.value = []
  await nextTick(); scrollToBottom()

  try {
    const res = await fetch(
      `${config.public.agentBase}/agent/chat/${sessionId.value}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          messages: messages.value,
          context: buildContext(),
        }),
      }
    )

    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const reader = res.body!.getReader()
    const decoder = new TextDecoder()

    outer: while (true) {
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
          } else if (event.type === 'tool_start') {
            thinkingSteps.value.push(`Using: ${event.name}`)
          } else if (event.type === 'error') {
            throw new Error(event.message)
          } else if (event.type === 'done') {
            break outer
          }
        } catch {}
      }
    }

    if (streamBuffer.value) {
      messages.value.push({ role: 'assistant', content: streamBuffer.value })
    }
  } catch (e) {
    console.error('Chat stream failed:', e)
    connectionError.value = true
    sessionId.value = null
  } finally {
    streaming.value = false
    streamBuffer.value = ''
    thinkingSteps.value = []
    await nextTick(); scrollToBottom()
  }
}

function scrollToBottom() {
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
}
</script>

<style scoped>
.chat-page { max-width: 760px; margin: 0 auto; }
.chat-page__header { margin-bottom: 1.5rem; }
.chat-page__title { font-size: 1.375rem; font-weight: 700; color: var(--color-text); }
.chat-page__sub { font-size: 0.875rem; color: var(--color-text-muted); margin-top: 0.25rem; }

.chat-wrap {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 12rem);
  position: relative;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  user-select: none;
}

.message { display: flex; }
.message--user { justify-content: flex-end; }
.message--ai { justify-content: flex-start; }
.message__bubble {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  line-height: 1.6;
}

/* Markdown prose styles for AI bubbles */
.message--ai .message__bubble :deep(h1),
.message--ai .message__bubble :deep(h2),
.message--ai .message__bubble :deep(h3) {
  font-weight: 700;
  margin: 0.75rem 0 0.25rem;
  line-height: 1.3;
}
.message--ai .message__bubble :deep(h1) { font-size: 1.05rem; }
.message--ai .message__bubble :deep(h2) { font-size: 0.975rem; }
.message--ai .message__bubble :deep(h3) { font-size: 0.9rem; }
.message--ai .message__bubble :deep(p) { margin: 0.4rem 0; }
.message--ai .message__bubble :deep(p:first-child) { margin-top: 0; }
.message--ai .message__bubble :deep(p:last-child) { margin-bottom: 0; }
.message--ai .message__bubble :deep(ul),
.message--ai .message__bubble :deep(ol) {
  margin: 0.4rem 0;
  padding-left: 1.25rem;
}
.message--ai .message__bubble :deep(li) { margin: 0.2rem 0; }
.message--ai .message__bubble :deep(strong) { font-weight: 600; }
.message--ai .message__bubble :deep(em) { font-style: italic; }
.message--ai .message__bubble :deep(code) {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  padding: 0.1rem 0.3rem;
  font-size: 0.8rem;
  font-family: monospace;
}
.message--ai .message__bubble :deep(hr) {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 0.75rem 0;
}
.message--user .message__bubble {
  background: var(--color-primary);
  color: var(--color-on-primary);
  border-bottom-right-radius: 0.25rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}
.message--ai .message__bubble {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-bottom-left-radius: 0.25rem;
  box-shadow: var(--shadow-card);
}

.thinking-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  padding: 0 0.25rem;
}
.thinking-chip {
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: var(--color-surface-raised);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}

.status-overlay {
  position: absolute;
  inset: 0;
  bottom: 4.5rem; /* sit above input bar */
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
  font-size: 0.875rem;
  border-radius: var(--radius-card) var(--radius-card) 0 0;
  pointer-events: none;
}
.status-overlay--error {
  background: color-mix(in srgb, var(--color-danger-dim) 80%, transparent);
  color: var(--color-danger);
  border-bottom: 1px solid color-mix(in srgb, var(--color-danger) 20%, transparent);
  padding: 0 2rem;
  text-align: center;
  line-height: 1.5;
}
.status-overlay__icon {
  font-size: 1.125rem;
  flex-shrink: 0;
}
.status-overlay--connecting {
  background: transparent;
  color: var(--color-text-muted);
  font-size: 0.8rem;
}
.connecting-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: var(--color-primary);
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: 0.3 } }

.cursor { animation: blink 0.8s infinite; }
@keyframes blink { 0%,100% { opacity: 1 } 50% { opacity: 0 } }

.chat-input {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  border-top: 1px solid var(--color-border);
}
.chat-input__field {
  flex: 1;
  resize: none;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
  border-radius: 0.625rem;
  padding: 0.625rem 0.875rem;
  font-size: 0.875rem;
  color: var(--color-text);
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}
.chat-input__field:focus { border-color: var(--color-primary); }
.chat-input__field::placeholder { color: var(--color-text-faint); }
.chat-input__btn {
  padding: 0 1.25rem;
  background: var(--color-primary);
  color: var(--color-on-primary);
  font-weight: 600;
  font-size: 0.875rem;
  border-radius: 0.625rem;
  border: none;
  cursor: pointer;
  transition: opacity 0.15s;
  align-self: flex-end;
  height: 2.5rem;
}
.chat-input__btn:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
