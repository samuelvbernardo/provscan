import { apiFetch } from '@/lib/api'
import ScanForm from './ScanForm'
import type { Exam, PaginatedResponse } from '@/lib/definitions'

async function getActiveExams(): Promise<Exam[]> {
  const res = await apiFetch('/api/v1/exams/')
  if (!res.ok) return []
  const data: PaginatedResponse<Exam> = await res.json()
  return data.results.filter((e) => e.is_active)
}

export default async function EscanearPage() {
  const exams = await getActiveExams()

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Escanear Cartão</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Selecione a prova, envie a foto do cartão-resposta e o sistema calculará a nota automaticamente.
        </p>
      </div>

      {exams.length === 0 ? (
        <div className="text-center py-16 text-slate-400 bg-white border border-slate-200 rounded-xl">
          <svg className="w-10 h-10 mx-auto mb-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
          <p className="text-sm">Nenhuma prova ativa. Crie uma prova primeiro.</p>
        </div>
      ) : (
        <ScanForm exams={exams} />
      )}
    </div>
  )
}
