import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

// API_URL é usada apenas no servidor (Server Actions e Route Handlers).
// Não usar NEXT_PUBLIC_ para não expor o endereço interno do backend no bundle do cliente.
const API_URL = process.env.API_URL ?? 'http://localhost:8000'

async function refreshAccessToken(refreshToken: string): Promise<string | null> {
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

export async function apiFetch(path: string, options?: RequestInit) {
  const cookieStore = await cookies()
  let token = cookieStore.get('access_token')?.value
  const refreshToken = cookieStore.get('refresh_token')?.value

  const isJson = !(options?.body instanceof FormData)

  const buildHeaders = (t?: string): Record<string, string> => ({
    ...(isJson && { 'Content-Type': 'application/json' }),
    ...(t && { Authorization: `Bearer ${t}` }),
    ...(options?.headers as Record<string, string>),
  })

  let res = await fetch(`${API_URL}${path}`, { ...options, headers: buildHeaders(token) })

  if (res.status === 401 && refreshToken) {
    const newToken = await refreshAccessToken(refreshToken)
    if (newToken) {
      cookieStore.set('access_token', newToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60,
      })
      token = newToken
      res = await fetch(`${API_URL}${path}`, { ...options, headers: buildHeaders(token) })
    } else {
      cookieStore.delete('access_token')
      cookieStore.delete('refresh_token')
      redirect('/login')
    }
  }

  return res
}
