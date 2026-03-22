import type { Response } from 'express';

export const SB_ACCESS_COOKIE = 'sb-access-token';
export const SB_REFRESH_COOKIE = 'sb-refresh-token';

const WEEK_MS = 7 * 24 * 60 * 60 * 1000;

export function cookieOptions(maxAgeMs: number) {
  return {
    httpOnly: true,
    sameSite: 'lax' as const,
    secure: process.env.NODE_ENV === 'production',
    path: '/',
    maxAge: maxAgeMs,
  };
}

export function attachSessionCookies(res: Response, accessToken: string, refreshToken: string, expiresIn: number) {
  res.cookie(SB_ACCESS_COOKIE, accessToken, cookieOptions(Math.max(expiresIn * 1000, 60_000)));
  res.cookie(SB_REFRESH_COOKIE, refreshToken, cookieOptions(WEEK_MS));
}

export function clearSessionCookies(res: Response) {
  res.clearCookie(SB_ACCESS_COOKIE, { path: '/' });
  res.clearCookie(SB_REFRESH_COOKIE, { path: '/' });
}
