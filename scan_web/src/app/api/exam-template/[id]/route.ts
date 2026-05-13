import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from 'next/server'

const API_URL = (process.env.API_URL ?? 'http://localhost:8000').replace(/\/$/, '')

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const token = (await cookies()).get('access_token')?.value

  const res = await fetch(`${API_URL}/api/v1/exams/${id}/template/`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })

  if (!res.ok) {
    return NextResponse.json(
      { detail: 'Não foi possível baixar o cartão-resposta.' },
      { status: res.status }
    )
  }

  const contentDisposition =
    res.headers.get('Content-Disposition') ?? `attachment; filename="cartao_resposta_${id}.pdf"`

  return new NextResponse(res.body, {
    status: res.status,
    headers: {
      'Content-Type': res.headers.get('Content-Type') ?? 'application/pdf',
      'Content-Disposition': contentDisposition,
    },
  })
}
