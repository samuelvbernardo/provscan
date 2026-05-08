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

export async function createStudent(
  _state: FormState,
  formData: FormData
): Promise<FormState> {
  const name = (formData.get('name') as string)?.trim()
  const number = formData.get('number') as string
  const class_group = formData.get('class_group') as string

  if (!name) return { error: 'Nome do aluno é obrigatório.' }
  if (!number) return { error: 'Número do aluno é obrigatório.' }

  let res: Response
  try {
    res = await apiFetch('/api/v1/students/', {
      method: 'POST',
      body: JSON.stringify({
        name,
        number: parseInt(number),
        class_group: parseInt(class_group),
        is_active: true,
      }),
    })
  } catch {
    return { error: 'Não foi possível conectar ao servidor.' }
  }

  if (res.status === 401) {
    await clearSessionAndRedirect()
  }

  if (!res.ok) {
    const data = await res.json()
    const msg =
      data.number?.[0] ??
      data.name?.[0] ??
      data.non_field_errors?.[0] ??
      data.detail ??
      'Erro ao cadastrar aluno.'
    return { error: msg }
  }

  revalidatePath(`/turmas/${class_group}`)
}

export async function deleteStudent(formData: FormData) {
  const id = formData.get('id') as string
  const class_group = formData.get('class_group') as string
  try {
    const res = await apiFetch(`/api/v1/students/${id}/`, { method: 'DELETE' })
    if (res.status === 401) await clearSessionAndRedirect()
  } catch {
    // silently fail
  }
  revalidatePath(`/turmas/${class_group}`)
}
