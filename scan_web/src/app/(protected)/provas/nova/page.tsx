import Link from 'next/link'
import { apiFetch } from '@/lib/api'
import ExamForm from './ExamForm'
import type { ClassGroup, PaginatedResponse } from '@/lib/definitions'

async function getClassGroups(): Promise<ClassGroup[]> {
  const res = await apiFetch('/api/v1/class-groups/')
  if (!res.ok) return []
  const data: PaginatedResponse<ClassGroup> = await res.json()
  return data.results
}

export default async function NovaProvaPage() {
  const turmas = await getClassGroups()

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <Link
          href="/provas"
          className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-800 transition mb-4"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
          Provas
        </Link>
        <h1 className="text-2xl font-bold text-slate-900">Nova Prova</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          O cartão-resposta em PDF será gerado automaticamente.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <ExamForm classGroups={turmas} />
      </div>
    </div>
  )
}
