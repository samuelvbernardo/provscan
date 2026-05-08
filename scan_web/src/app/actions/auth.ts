'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import type { AuthFormState } from '@/lib/definitions'

const API_URL = process.env.API_URL ?? 'http://localhost:8000'

export async function login(state: AuthFormState, formData: FormData): Promise<AuthFormState> {
  const email = formData.get('email') as string
  const password = formData.get('password') as string

  if (!email || !password) {
    return { error: 'Preencha todos os campos.' }
  }

  let data: { access: string; refresh: string }

  try {
    const res = await fetch(`${API_URL}/api/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    if (res.status === 401 || res.status === 400) {
      return { error: 'Email ou senha incorretos.' }
    }

    if (!res.ok) {
      return { error: 'Erro inesperado. Tente novamente.' }
    }

    data = await res.json()
  } catch {
    return { error: 'Não foi possível conectar ao servidor.' }
  }

  const cookieStore = await cookies()

  cookieStore.set('access_token', data.access, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60,
  })

  cookieStore.set('refresh_token', data.refresh, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7,
  })

  redirect('/dashboard')
}

export async function logout() {
  const cookieStore = await cookies()
  cookieStore.delete('access_token')
  cookieStore.delete('refresh_token')
  redirect('/login')
}
