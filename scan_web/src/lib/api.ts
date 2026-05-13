import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

// API_URL is used only on the server: Server Components, Server Actions, and Route Handlers.
const API_URL = (process.env.API_URL ?? 'http://localhost:8000').replace(/\/$/, '')

async function backendFetch(path: string, options?: RequestInit): Promise<Response> {
  try {
    return await fetch(`${API_URL}${path}`, options)
  } catch (error) {
    console.error('Backend request failed', error)
    return Response.json(
      { detail: 'Nao foi possivel conectar ao servidor.' },
      { status: 503 }
    )
  }
}

async function refreshAccessToken(refreshToken: string): Promise<string | null> {
  const res = await backendFetch('/api/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken }),
  })
  if (!res.ok) return null
  const data = await res.json()
  return data.access ?? null
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

  let res = await backendFetch(path, { ...options, headers: buildHeaders(token) })

  if (res.status === 401 && refreshToken) {
    const newToken = await refreshAccessToken(refreshToken)
    if (newToken) {
      token = newToken
      res = await backendFetch(path, { ...options, headers: buildHeaders(token) })
    } else {
      redirect('/login?expired=1')
    }
  }

  return res
}
