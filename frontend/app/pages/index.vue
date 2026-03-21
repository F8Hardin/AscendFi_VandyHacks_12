<template>
  <div class="max-w-2xl mx-auto p-6 flex flex-col h-screen">
    <header class="mb-6">
      <h1 class="text-2xl font-bold text-green-400">Financial Recovery AI</h1>
      <p class="text-gray-400 text-sm">Your personal guide to financial stability</p>
    </header>

    <!-- Messages -->
    <div ref="messagesEl" class="flex-1 overflow-y-auto space-y-4 mb-4">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'"
      >
        <div
          :class="[
            'max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap',
            msg.role === 'user'
              ? 'bg-green-700 text-white'
              : 'bg-gray-800 text-gray-100',
          ]"
        >
          {{ msg.content }}
        </div>
      </div>
      <div v-if="streaming" class="flex justify-start">
        <div class="max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed bg-gray-800 text-gray-100 whitespace-pre-wrap">
          {{ streamBuffer }}<span class="animate-pulse">▌</span>
        </div>
      </div>
    </div>

    <!-- Input -->
    <form @submit.prevent="send" class="flex gap-2">
      <textarea
        v-model="input"
        @keydown.enter.exact.prevent="send"
        placeholder="Describe your financial situation..."
        rows="2"
        class="flex-1 resize-none rounded-xl bg-gray-800 border border-gray-700 px-4 py-3 text-sm focus:outline-none focus:border-green-500 placeholder-gray-500"
      />
      <button
        type="submit"
        :disabled="!input.trim() || streaming"
        class="px-5 py-3 bg-green-600 hover:bg-green-500 disabled:opacity-40 rounded-xl text-sm font-medium transition-colors"
      >
        Send
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([
  {
    role: 'assistant',
    content: "Hello! I'm here to help you with your financial recovery journey. Tell me about your current situation — whether it's debt, unexpected expenses, or just feeling overwhelmed financially. There's no judgment here, just practical help.",
  },
])
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

  await nextTick()
  scrollToBottom()

  try {
    const response = await fetch(`${config.public.apiBase}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: messages.value }),
    })

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const data = line.slice(6)
        if (data === '[DONE]') break
        try {
          const parsed = JSON.parse(data)
          streamBuffer.value += parsed.text
          await nextTick()
          scrollToBottom()
        } catch {}
      }
    }

    messages.value.push({ role: 'assistant', content: streamBuffer.value })
  } finally {
    streaming.value = false
    streamBuffer.value = ''
    await nextTick()
    scrollToBottom()
  }
}

function scrollToBottom() {
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}
</script>
