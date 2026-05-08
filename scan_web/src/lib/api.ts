import { cookies } from 'next/headers'

const API_URL = process.env.API_URL ?? 'http://localhost:8000'

export async function apiFetch(path: string, options?: RequestInit) {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  const isJson = !(options?.body instanceof FormData)

  const headers: Record<string, string> = {
    ...(isJson && { 'Content-Type': 'application/json' }),
    ...(token && { Authorization: `Bearer ${token}` }),
    ...(options?.headers as Record<string, string>),
  }

  return fetch(`${API_URL}${path}`, { ...options, headers })
}
