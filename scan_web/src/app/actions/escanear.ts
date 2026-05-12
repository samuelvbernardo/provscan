'use server'

import { redirect } from 'next/navigation'
import { cookies } from 'next/headers'
import { apiFetch } from '@/lib/api'
import type { ScanFormState } from '@/lib/definitions'

async function clearSessionAndRedirect(): Promise<never> {
  const cookieStore = await cookies()
  cookieStore.delete('access_token')
  cookieStore.delete('refresh_token')
  redirect('/login')
}

export async function scanExam(
  _state: ScanFormState,
  formData: FormData
): Promise<ScanFormState> {
  const exam_id = formData.get('exam_id') as string
  const image = formData.get('image') as File

  if (!exam_id) return { error: 'Selecione uma prova.' }
  if (!image || image.size === 0) return { error: 'Selecione uma imagem do cartão-resposta.' }

  const body = new FormData()
  body.append('exam_id', exam_id)
  body.append('image', image)

  let res: Response
  try {
    res = await apiFetch('/api/v1/omr/scan/', { method: 'POST', body })
  } catch {
    return { error: 'Não foi possível conectar ao servidor.' }
  }

  if (res.status === 401) await clearSessionAndRedirect()

  if (!res.ok) {
    const friendlyMessages: Record<number, string> = {
      413: 'A imagem é muito grande. Use uma foto menor ou converta para JPEG.',
      422: 'Não foi possível ler o cartão. Verifique se os 4 marcadores aparecem na foto, sem cortes ou reflexos.',
      429: 'Muitas tentativas seguidas. Aguarde alguns segundos e tente novamente.',
      500: 'Erro interno no servidor. Tente novamente em alguns instantes.',
      502: 'Servidor temporariamente indisponível. Tente novamente em alguns segundos.',
      503: 'Servidor temporariamente indisponível. Tente novamente em alguns segundos.',
      504: 'O processamento demorou muito. Tente com uma foto em JPEG ou menor resolução.',
    }

    try {
      const data = await res.json()
      const msg =
        data.detail ??
        data.exam_id?.[0] ??
        data.image?.[0] ??
        friendlyMessages[res.status] ??
        'Erro ao processar o cartão-resposta.'
      return { error: msg }
    } catch {
      // Resposta não-JSON (ex: 502/504 do nginx em HTML)
      const msg =
        friendlyMessages[res.status] ??
        `Erro inesperado do servidor (HTTP ${res.status}). Tente novamente.`
      return { error: msg }
    }
  }

  const result = await res.json()
  return { result }
}
