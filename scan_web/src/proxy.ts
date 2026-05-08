import { NextRequest, NextResponse } from 'next/server'

const PUBLIC_ROUTES = ['/login']
const API_URL = process.env.API_URL ?? 'http://localhost:8000'

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

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isPublicRoute = PUBLIC_ROUTES.some((route) => pathname.startsWith(route))
  const accessToken = request.cookies.get('access_token')?.value
  const refreshToken = request.cookies.get('refresh_token')?.value

  // Sem nenhum token — acesso negado a rotas privadas
  if (!accessToken && !refreshToken) {
    if (isPublicRoute) return NextResponse.next()
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Access token expirou, mas refresh token ainda existe — tenta renovar
  if (!accessToken && refreshToken) {
    const newAccessToken = await tryRefresh(refreshToken)

    if (!newAccessToken) {
      const response = NextResponse.redirect(new URL('/login', request.url))
      response.cookies.delete('refresh_token')
      return response
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

  // Já autenticado tentando acessar rota pública
  if (accessToken && isPublicRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
