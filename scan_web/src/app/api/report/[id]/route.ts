import { NextRequest, NextResponse } from 'next/server'
import { apiFetch } from '@/lib/api'

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const res = await apiFetch(`/api/v1/scan-results/${id}/report/`)

  if (!res.ok) {
    return NextResponse.json(
      { detail: 'Não foi possível gerar o boletim.' },
      { status: res.status }
    )
  }

  const pdfBuffer = await res.arrayBuffer()
  const contentDisposition = res.headers.get('Content-Disposition') ?? `attachment; filename="boletim_${id}.pdf"`

  return new NextResponse(pdfBuffer, {
    status: 200,
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': contentDisposition,
    },
  })
}
