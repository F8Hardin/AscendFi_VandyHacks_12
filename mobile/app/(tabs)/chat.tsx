import { useState, useRef, useCallback } from 'react'
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  FlatList, KeyboardAvoidingView, Platform, ActivityIndicator,
} from 'react-native'
import { AGENT_ROOT } from '@/lib/api'
import { colors } from '@/lib/colors'

interface Message { id: string; role: 'user' | 'assistant'; text: string; thinking?: boolean }

const SYSTEM_INTRO: Message = {
  id: 'intro',
  role: 'assistant',
  text: "Hi, I'm ARIA — your AI financial advisor. Ask me anything about your finances, spending habits, debt payoff strategies, or investments.",
}

export default function ChatTab() {
  const [messages, setMessages] = useState<Message[]>([SYSTEM_INTRO])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const listRef = useRef<FlatList>(null)
  const abortRef = useRef<AbortController | null>(null)

  const appendChunk = useCallback((id: string, chunk: string) => {
    setMessages(prev =>
      prev.map(m => m.id === id ? { ...m, text: m.text + chunk, thinking: false } : m)
    )
  }, [])

  async function sendMessage() {
    const text = input.trim()
    if (!text || streaming) return
    setInput('')

    const userMsg: Message = { id: Date.now().toString(), role: 'user', text }
    const assistantId = (Date.now() + 1).toString()
    const thinkingMsg: Message = { id: assistantId, role: 'assistant', text: '', thinking: true }

    setMessages(prev => [...prev, userMsg, thinkingMsg])
    setStreaming(true)

    // Scroll to bottom
    setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 100)

    abortRef.current = new AbortController()

    try {
      const history = messages
        .filter(m => !m.thinking && m.id !== 'intro')
        .map(m => ({ role: m.role, content: m.text }))

      const response = await fetch(`${AGENT_ROOT}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...history, { role: 'user', content: text }] }),
        signal: abortRef.current.signal,
      })

      if (!response.ok || !response.body) throw new Error(`${response.status}`)

      // Read SSE stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          if (!raw || raw === '[DONE]') continue
          try {
            const evt = JSON.parse(raw) as { type: string; text?: string }
            if (evt.type === 'token' && evt.text) {
              appendChunk(assistantId, evt.text)
              listRef.current?.scrollToEnd({ animated: false })
            } else if (evt.type === 'done') {
              break
            }
          } catch { /* ignore malformed lines */ }
        }
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantId
              ? { ...m, text: 'Could not reach ARIA. Make sure the Python agent is running on port 8000.', thinking: false }
              : m
          )
        )
      }
    } finally {
      setStreaming(false)
      abortRef.current = null
    }
  }

  function stopStream() {
    abortRef.current?.abort()
    setStreaming(false)
  }

  function renderMessage({ item }: { item: Message }) {
    const isUser = item.role === 'user'
    return (
      <View style={[s.bubble, isUser ? s.userBubble : s.aiBubble]}>
        {!isUser && (
          <View style={s.ariaBadge}>
            <Text style={s.ariaBadgeText}>✨ ARIA</Text>
          </View>
        )}
        {item.thinking ? (
          <View style={s.thinkingRow}>
            <ActivityIndicator size="small" color={colors.primary} />
            <Text style={s.thinkingText}>ARIA is thinking…</Text>
          </View>
        ) : (
          <Text style={[s.bubbleText, isUser && s.userBubbleText]}>{item.text}</Text>
        )}
      </View>
    )
  }

  return (
    <KeyboardAvoidingView
      style={s.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={88}
    >
      {/* Header */}
      <View style={s.header}>
        <Text style={s.headerTitle}>✨ ARIA</Text>
        <Text style={s.headerSub}>AI financial advisor</Text>
      </View>

      {/* Messages */}
      <FlatList
        ref={listRef}
        data={messages}
        keyExtractor={m => m.id}
        renderItem={renderMessage}
        contentContainerStyle={s.msgList}
        onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
      />

      {/* Input */}
      <View style={s.inputRow}>
        <TextInput
          style={s.input}
          placeholder="Ask ARIA about your finances…"
          placeholderTextColor={colors.textFaint}
          value={input}
          onChangeText={setInput}
          multiline
          maxLength={500}
          onSubmitEditing={sendMessage}
          blurOnSubmit={false}
          editable={!streaming}
        />
        <TouchableOpacity
          style={[s.sendBtn, streaming && s.stopBtn]}
          onPress={streaming ? stopStream : sendMessage}
          activeOpacity={0.8}
          disabled={!input.trim() && !streaming}
        >
          <Text style={s.sendBtnText}>{streaming ? '■' : '↑'}</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  )
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  header: {
    paddingTop: 60, paddingHorizontal: 16, paddingBottom: 12,
    borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  headerTitle: { fontSize: 22, fontWeight: '800', color: colors.text },
  headerSub: { fontSize: 12, color: colors.textMuted, marginTop: 2 },
  msgList: { padding: 16, paddingBottom: 8, gap: 12 },
  bubble: { maxWidth: '82%', borderRadius: 16, padding: 12 },
  aiBubble: {
    alignSelf: 'flex-start', backgroundColor: colors.surface,
    borderWidth: 1, borderColor: colors.border, borderBottomLeftRadius: 4,
  },
  userBubble: {
    alignSelf: 'flex-end', backgroundColor: colors.primary, borderBottomRightRadius: 4,
  },
  ariaBadge: { marginBottom: 4 },
  ariaBadgeText: { fontSize: 11, color: colors.primary, fontWeight: '700' },
  bubbleText: { fontSize: 15, color: colors.text, lineHeight: 22 },
  userBubbleText: { color: '#fff' },
  thinkingRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  thinkingText: { fontSize: 13, color: colors.textMuted, fontStyle: 'italic' },
  inputRow: {
    flexDirection: 'row', padding: 12, gap: 8,
    borderTopWidth: 1, borderTopColor: colors.border,
    backgroundColor: colors.surface, alignItems: 'flex-end',
  },
  input: {
    flex: 1, backgroundColor: colors.surfaceRaised, borderRadius: 20,
    borderWidth: 1, borderColor: colors.border,
    color: colors.text, fontSize: 15, paddingHorizontal: 14, paddingVertical: 10,
    maxHeight: 100,
  },
  sendBtn: {
    width: 40, height: 40, borderRadius: 20, backgroundColor: colors.primary,
    alignItems: 'center', justifyContent: 'center',
  },
  stopBtn: { backgroundColor: colors.danger },
  sendBtnText: { color: '#fff', fontSize: 18, fontWeight: '700', lineHeight: 22 },
})
