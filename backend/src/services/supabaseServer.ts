import { createClient, type SupabaseClient, type User } from '@supabase/supabase-js';
import { SB_ACCESS_COOKIE, SB_REFRESH_COOKIE } from '../config/authCookies';

const url = process.env.SUPABASE_URL || '';
const anon = process.env.SUPABASE_ANON_KEY || '';

export function assertSupabaseEnv(): void {
  if (!url || !anon) {
    throw new Error('Missing SUPABASE_URL or SUPABASE_ANON_KEY');
  }
}

export function createAnonClient(): SupabaseClient {
  assertSupabaseEnv();
  return createClient(url, anon);
}

/** RLS-aware client for the signed-in user (pass access JWT). */
export function createUserClient(accessToken: string): SupabaseClient {
  assertSupabaseEnv();
  return createClient(url, anon, {
    global: {
      headers: { Authorization: `Bearer ${accessToken}` },
    },
  });
}

/**
 * Resolve user + access token from cookies; refresh if access token expired but refresh exists.
 * Returns new tokens when refreshed so caller can update Set-Cookie.
 */
export async function resolveSessionFromCookies(
  cookies: Record<string, string | undefined>
): Promise<
  | {
      ok: true;
      user: User;
      accessToken: string;
      refreshToken: string;
      refreshed: boolean;
      expiresIn?: number;
    }
  | { ok: false }
> {
  assertSupabaseEnv();
  const supabase = createAnonClient();
  const access = cookies[SB_ACCESS_COOKIE];
  const refresh = cookies[SB_REFRESH_COOKIE];

  if (access) {
    const { data, error } = await supabase.auth.getUser(access);
    if (!error && data.user) {
      return {
        ok: true,
        user: data.user,
        accessToken: access,
        refreshToken: refresh || '',
        refreshed: false,
      };
    }
  }

  if (refresh) {
    const { data, error } = await supabase.auth.refreshSession({ refresh_token: refresh });
    if (!error && data.session && data.user) {
      return {
        ok: true,
        user: data.user,
        accessToken: data.session.access_token,
        refreshToken: data.session.refresh_token,
        refreshed: true,
        expiresIn: data.session.expires_in,
      };
    }
  }

  return { ok: false };
}
