import { NextRequest, NextResponse } from 'next/server'

const PUBLIC_ROUTES = ['/login']
const API_URL = (process.env.API_URL ?? 'http://localhost:8000').replace(/\/$/, '')

function isJwtExpired(token: string, skewSeconds = 30) {
  try {
    const payload = token.split('.')[1]
    if (!payload) return true

    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')
    const decoded = JSON.parse(atob(padded)) as { exp?: number }
    if (typeof decoded.exp !== 'number') return true

    return decoded.exp <= Math.floor(Date.now() / 1000) + skewSeconds
  } catch {
    return true
  }
}

async function tryRefresh(refreshToken: string): Promise<string | null> {
  try {
    const res = await fetch(`${API_URL}/api/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    })
    if (!res.ok) return null
    const data = await res.json()
    return data.access ?? null
  } catch {
    return null
  }
}

function redirectToLogin(request: NextRequest) {
  const response = NextResponse.redirect(new URL('/login?expired=1', request.url))
  response.cookies.delete('access_token')
  response.cookies.delete('refresh_token')
  return response
}

function continueWithoutSession() {
  const response = NextResponse.next()
  response.cookies.delete('access_token')
  response.cookies.delete('refresh_token')
  return response
}

export async function proxy(request: NextRequest) {
  const { pathname, searchParams } = request.nextUrl
  const isPublicRoute = PUBLIC_ROUTES.some((route) => pathname.startsWith(route))
  const forceLogin = isPublicRoute && searchParams.get('expired') === '1'
  const accessToken = request.cookies.get('access_token')?.value
  const refreshToken = request.cookies.get('refresh_token')?.value
  const hasValidAccessToken = Boolean(accessToken && !isJwtExpired(accessToken))

  if (forceLogin) {
    return continueWithoutSession()
  }

  if (!hasValidAccessToken && refreshToken) {
    const newAccessToken = await tryRefresh(refreshToken)

    if (!newAccessToken) {
      return isPublicRoute ? continueWithoutSession() : redirectToLogin(request)
    }

    const destination = isPublicRoute ? new URL('/dashboard', request.url) : null
    const response = destination
      ? NextResponse.redirect(destination)
      : NextResponse.next()

    response.cookies.set('access_token', newAccessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60,
    })

    return response
  }

  if (!hasValidAccessToken && !refreshToken) {
    if (isPublicRoute) return NextResponse.next()
    return redirectToLogin(request)
  }

  if (hasValidAccessToken && isPublicRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
