import { NextRequest, NextResponse } from 'next/server'
import { apiFetch } from '@/lib/api'

export async function GET(request: NextRequest) {
  const examIds = request.nextUrl.searchParams.get('exam_ids') ?? ''

  if (!examIds) {
    return NextResponse.json({ detail: 'Informe ao menos uma prova.' }, { status: 400 })
  }

  const res = await apiFetch(`/api/v1/exams/class-report/?exam_ids=${examIds}`)

  if (!res.ok) {
    return NextResponse.json(
      { detail: 'Não foi possível gerar o relatório.' },
      { status: res.status }
    )
  }

  const pdfBuffer = await res.arrayBuffer()

  return new NextResponse(pdfBuffer, {
    status: 200,
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': 'attachment; filename="relatorio_turmas.pdf"',
    },
  })
}
