'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { cookies } from 'next/headers'
import { apiFetch } from '@/lib/api'
import type { FormState } from '@/lib/definitions'

async function clearSessionAndRedirect(): Promise<never> {
  const cookieStore = await cookies()
  cookieStore.delete('access_token')
  cookieStore.delete('refresh_token')
  redirect('/login')
}

function extractError(data: Record<string, unknown>): string {
  if (data.name) return (data.name as string[])[0]
  if (data.detail) return data.detail as string
  if (data.non_field_errors) return (data.non_field_errors as string[])[0]
  return 'Erro ao criar turma.'
}

export async function createClassGroup(
  _state: FormState,
  formData: FormData
): Promise<FormState> {
  const name = (formData.get('name') as string)?.trim()
  const school_year = (formData.get('school_year') as string)?.trim()

  if (!name) return { error: 'Nome da turma é obrigatório.' }

  let res: Response
  try {
    res = await apiFetch('/api/v1/class-groups/', {
      method: 'POST',
      body: JSON.stringify({ name, school_year: school_year || null, is_active: true }),
    })
  } catch {
    return { error: 'Não foi possível conectar ao servidor.' }
  }

  if (res.status === 401) {
    await clearSessionAndRedirect()
  }

  if (!res.ok) {
    const data = await res.json()
    return { error: extractError(data) }
  }

  revalidatePath('/turmas')
  redirect('/turmas')
}

export async function updateClassGroup(
  _state: FormState,
  formData: FormData
): Promise<FormState> {
  const id = formData.get('id') as string
  const name = (formData.get('name') as string)?.trim()
  const school_year = (formData.get('school_year') as string)?.trim()

  if (!name) return { error: 'Nome da turma é obrigatório.' }

  let res: Response
  try {
    res = await apiFetch(`/api/v1/class-groups/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ name, school_year: school_year || null }),
    })
  } catch {
    return { error: 'Não foi possível conectar ao servidor.' }
  }

  if (res.status === 401) await clearSessionAndRedirect()

  if (!res.ok) {
    const data = await res.json()
    return { error: extractError(data) }
  }

  revalidatePath('/turmas')
  return { ok: true }
}

export async function deleteClassGroup(formData: FormData) {
  const id = formData.get('id') as string
  const res = await apiFetch(`/api/v1/class-groups/${id}/`, { method: 'DELETE' })
  if (res.status === 401) await clearSessionAndRedirect()
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail ?? 'Não foi possível excluir a turma.')
  }
  revalidatePath('/turmas')
}
