import { useState } from 'react'
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ActivityIndicator, ScrollView,
} from 'react-native'
import { Link, router } from 'expo-router'
import { LinearGradient } from 'expo-linear-gradient'
import { useAuth } from '@/hooks/useAuth'
import { colors } from '@/lib/colors'

export default function LoginScreen() {
  const { signIn } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLogin() {
    if (!email || !password) { setError('Enter email and password.'); return }
    setLoading(true)
    setError('')
    try {
      await signIn(email.trim().toLowerCase(), password)
      router.replace('/(tabs)/dashboard')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Login failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <LinearGradient colors={['#0f0f11', '#12121a']} style={s.grad}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={s.kav}>
        <ScrollView contentContainerStyle={s.scroll} keyboardShouldPersistTaps="handled">

          {/* Brand */}
          <View style={s.brand}>
            <Text style={s.logo}>⬆</Text>
            <Text style={s.title}>AscendFi</Text>
            <Text style={s.sub}>AI-powered personal finance</Text>
          </View>

          {/* Card */}
          <View style={s.card}>
            <Text style={s.cardTitle}>Sign in</Text>

            <Text style={s.label}>Email</Text>
            <TextInput
              style={s.input}
              placeholder="you@example.com"
              placeholderTextColor={colors.textFaint}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              value={email}
              onChangeText={setEmail}
            />

            <Text style={s.label}>Password</Text>
            <TextInput
              style={s.input}
              placeholder="••••••••"
              placeholderTextColor={colors.textFaint}
              secureTextEntry
              autoComplete="password"
              value={password}
              onChangeText={setPassword}
              onSubmitEditing={handleLogin}
            />

            {error ? <Text style={s.error}>{error}</Text> : null}

            <TouchableOpacity style={s.btn} onPress={handleLogin} disabled={loading} activeOpacity={0.8}>
              {loading
                ? <ActivityIndicator color="#fff" />
                : <Text style={s.btnText}>Sign in</Text>
              }
            </TouchableOpacity>

            <View style={s.row}>
              <Text style={s.mutedText}>Don't have an account? </Text>
              <Link href="/signup" asChild>
                <TouchableOpacity><Text style={s.link}>Sign up</Text></TouchableOpacity>
              </Link>
            </View>

            {/* Demo shortcut */}
            <TouchableOpacity
              style={s.demoBtn}
              onPress={() => router.replace('/(tabs)/dashboard')}
              activeOpacity={0.7}
            >
              <Text style={s.demoBtnText}>Continue with demo data →</Text>
            </TouchableOpacity>
          </View>

        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  )
}

const s = StyleSheet.create({
  grad: { flex: 1 },
  kav: { flex: 1 },
  scroll: { flexGrow: 1, justifyContent: 'center', padding: 24 },
  brand: { alignItems: 'center', marginBottom: 36 },
  logo: { fontSize: 48, marginBottom: 8 },
  title: { fontSize: 32, fontWeight: '800', color: colors.text, letterSpacing: -0.5 },
  sub: { fontSize: 14, color: colors.textMuted, marginTop: 4 },
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
  row: { flexDirection: 'row', justifyContent: 'center', marginBottom: 12 },
  mutedText: { color: colors.textMuted, fontSize: 14 },
  link: { color: colors.primary, fontWeight: '600', fontSize: 14 },
  demoBtn: { alignItems: 'center', paddingVertical: 8 },
  demoBtnText: { color: colors.textFaint, fontSize: 13 },
})
