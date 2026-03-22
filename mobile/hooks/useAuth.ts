import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import type { User } from '@supabase/supabase-js'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get current session
    supabase.auth.getSession().then(({ data }) => {
      setUser(data.session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth state changes
    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
    })

    return () => listener.subscription.unsubscribe()
  }, [])

  async function signIn(email: string, password: string) {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
  }

  async function signUp(email: string, password: string, fullName?: string) {
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: fullName } },
    })
    if (error) throw error
  }

  async function signOut() {
    await supabase.auth.signOut()
  }

  const displayName =
    (user?.user_metadata?.legal_first_name as string | undefined)?.split(' ')[0] ||
    (user?.user_metadata?.full_name as string | undefined)?.split(' ')[0] ||
    user?.email?.split('@')[0] ||
    ''

  return { user, loading, displayName, signIn, signUp, signOut }
}
