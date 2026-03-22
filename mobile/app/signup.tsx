import { useState } from 'react'
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ActivityIndicator, ScrollView,
} from 'react-native'
import { Link, router } from 'expo-router'
import { LinearGradient } from 'expo-linear-gradient'
import { useAuth } from '@/hooks/useAuth'
import { colors } from '@/lib/colors'

export default function SignupScreen() {
  const { signUp } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  async function handleSignUp() {
    if (!email || !password) { setError('Enter email and password.'); return }
    if (password.length < 6) { setError('Password must be at least 6 characters.'); return }
    setLoading(true)
    setError('')
    try {
      await signUp(email.trim().toLowerCase(), password, name.trim() || undefined)
      setDone(true)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Sign up failed.')
    } finally {
      setLoading(false)
    }
  }

  if (done) {
    return (
      <LinearGradient colors={['#0f0f11', '#12121a']} style={s.grad}>
        <View style={s.center}>
          <Text style={{ fontSize: 48, marginBottom: 16 }}>📬</Text>
          <Text style={s.doneTitle}>Check your email</Text>
          <Text style={s.doneSub}>We sent a confirmation link to {email}. Click it to activate your account.</Text>
          <TouchableOpacity style={s.btn} onPress={() => router.replace('/')} activeOpacity={0.8}>
            <Text style={s.btnText}>Back to sign in</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    )
  }

  return (
    <LinearGradient colors={['#0f0f11', '#12121a']} style={s.grad}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={s.scroll} keyboardShouldPersistTaps="handled">

          <TouchableOpacity onPress={() => router.back()} style={s.back}>
            <Text style={s.backText}>← Back</Text>
          </TouchableOpacity>

          <View style={s.card}>
            <Text style={s.cardTitle}>Create account</Text>

            <Text style={s.label}>Full name (optional)</Text>
            <TextInput
              style={s.input}
              placeholder="Your name"
              placeholderTextColor={colors.textFaint}
              autoCapitalize="words"
              value={name}
              onChangeText={setName}
            />

            <Text style={s.label}>Email</Text>
            <TextInput
              style={s.input}
              placeholder="you@example.com"
              placeholderTextColor={colors.textFaint}
              keyboardType="email-address"
              autoCapitalize="none"
              value={email}
              onChangeText={setEmail}
            />

            <Text style={s.label}>Password</Text>
            <TextInput
              style={s.input}
              placeholder="Min. 6 characters"
              placeholderTextColor={colors.textFaint}
              secureTextEntry
              value={password}
              onChangeText={setPassword}
              onSubmitEditing={handleSignUp}
            />

            {error ? <Text style={s.error}>{error}</Text> : null}

            <TouchableOpacity style={s.btn} onPress={handleSignUp} disabled={loading} activeOpacity={0.8}>
              {loading
                ? <ActivityIndicator color="#fff" />
                : <Text style={s.btnText}>Create account</Text>
              }
            </TouchableOpacity>

            <View style={s.row}>
              <Text style={s.mutedText}>Already have an account? </Text>
              <Link href="/" asChild>
                <TouchableOpacity><Text style={s.link}>Sign in</Text></TouchableOpacity>
              </Link>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  )
}

const s = StyleSheet.create({
  grad: { flex: 1 },
  scroll: { flexGrow: 1, justifyContent: 'center', padding: 24 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  back: { marginBottom: 24 },
  backText: { color: colors.textMuted, fontSize: 15 },
  card: {
    backgroundColor: colors.surface, borderRadius: 20,
    padding: 24, borderWidth: 1, borderColor: colors.border,
  },
  cardTitle: { fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 20 },
  label: { fontSize: 13, fontWeight: '600', color: colors.textMuted, marginBottom: 6 },
  input: {
    backgroundColor: colors.surfaceRaised, borderRadius: 10,
    borderWidth: 1, borderColor: colors.border,
    color: colors.text, fontSize: 15, padding: 14, marginBottom: 16,
  },
  error: { color: colors.danger, fontSize: 13, marginBottom: 12 },
  btn: {
    backgroundColor: colors.primary, borderRadius: 12,
    paddingVertical: 14, alignItems: 'center', marginBottom: 16,
  },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  row: { flexDirection: 'row', justifyContent: 'center' },
  mutedText: { color: colors.textMuted, fontSize: 14 },
  link: { color: colors.primary, fontWeight: '600', fontSize: 14 },
  doneTitle: { fontSize: 24, fontWeight: '700', color: colors.text, marginBottom: 12, textAlign: 'center' },
  doneSub: { color: colors.textMuted, fontSize: 15, textAlign: 'center', marginBottom: 32, lineHeight: 22 },
})
