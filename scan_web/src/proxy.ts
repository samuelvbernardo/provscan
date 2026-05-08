import { NextRequest, NextResponse } from 'next/server'

const PUBLIC_ROUTES = ['/login']

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isPublicRoute = PUBLIC_ROUTES.some((route) => pathname.startsWith(route))
  const hasToken = request.cookies.has('access_token')

  if (!hasToken && !isPublicRoute) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  if (hasToken && isPublicRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
