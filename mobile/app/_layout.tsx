import 'react-native-url-polyfill/auto'
import { useEffect } from 'react'
import { Stack, router } from 'expo-router'
import { StatusBar } from 'expo-status-bar'
import { GestureHandlerRootView } from 'react-native-gesture-handler'
import { useAuth } from '@/hooks/useAuth'
import { colors } from '@/lib/colors'

export default function RootLayout() {
  const { user, loading } = useAuth()

  useEffect(() => {
    if (loading) return
    if (!user) {
      router.replace('/')
    } else {
      router.replace('/(tabs)/dashboard')
    }
  }, [user, loading])

  return (
    <GestureHandlerRootView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar style="light" />
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.bg } }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="signup" />
        <Stack.Screen name="(tabs)" />
      </Stack>
    </GestureHandlerRootView>
  )
}
