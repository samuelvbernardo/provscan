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

export async function createExam(
  _state: FormState,
  formData: FormData
): Promise<FormState> {
  const title = (formData.get('title') as string)?.trim()
  const description = (formData.get('description') as string)?.trim()
  const class_groups = formData.getAll('class_groups').map((id) => parseInt(id as string))
  const questions_count = parseInt(formData.get('questions_count') as string)
  const options_count = parseInt(formData.get('options_count') as string)
  const answer_key_raw = formData.get('answer_key') as string

  if (!title) return { error: 'Título da prova é obrigatório.' }
  if (class_groups.length === 0) return { error: 'Selecione ao menos uma turma.' }

  let answer_key: string[]
  try {
    answer_key = JSON.parse(answer_key_raw)
  } catch {
    return { error: 'Gabarito inválido.' }
  }

  const unanswered = answer_key.findIndex((a) => !a)
  if (unanswered !== -1) {
    return { error: `Questão ${unanswered + 1} sem resposta. Preencha todo o gabarito.` }
  }

  let res: Response
  try {
    res = await apiFetch('/api/v1/exams/', {
      method: 'POST',
      body: JSON.stringify({
        title,
        description: description || null,
        class_groups,
        questions_count,
        options_count,
        answer_key,
        is_active: true,
      }),
    })
  } catch {
    return { error: 'Não foi possível conectar ao servidor.' }
  }

  if (res.status === 401) await clearSessionAndRedirect()

  if (!res.ok) {
    const data = await res.json()
    const msg =
      data.answer_key?.[0] ??
      data.title?.[0] ??
      data.class_group?.[0] ??
      data.detail ??
      'Erro ao criar prova.'
    return { error: msg }
  }

  revalidatePath('/provas')
  redirect('/provas')
}

export async function deleteExam(formData: FormData) {
  const id = formData.get('id') as string
  const res = await apiFetch(`/api/v1/exams/${id}/`, { method: 'DELETE' })
  if (res.status === 401) await clearSessionAndRedirect()
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail ?? 'Não foi possível excluir a prova.')
  }
  revalidatePath('/provas')
}
