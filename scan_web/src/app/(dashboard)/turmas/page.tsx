import Link from 'next/link'
import { apiFetch } from '@/lib/api'
import TurmaForm from './TurmaForm'
import TurmaRow from './TurmaRow'
import type { ClassGroup, PaginatedResponse } from '@/lib/definitions'

async function getClassGroups(page: number): Promise<PaginatedResponse<ClassGroup>> {
  const res = await apiFetch(`/api/v1/class-groups/?page=${page}`)
  if (!res.ok) return { count: 0, next: null, previous: null, results: [] }
  return res.json()
}

function Pagination({ page, count }: { page: number; count: number }) {
  const pageSize = 10
  const totalPages = Math.ceil(count / pageSize)
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-between px-5 py-3 border-t border-slate-200 bg-slate-50">
      <p className="text-xs text-slate-500">
        Página {page} de {totalPages} ({count} turma{count !== 1 ? 's' : ''})
      </p>
      <div className="flex gap-2">
        {page > 1 && (
          <Link
            href={`?page=${page - 1}`}
            className="rounded px-3 py-1 text-xs font-medium text-slate-600 border border-slate-300 hover:bg-white transition"
          >
            Anterior
          </Link>
        )}
        {page < totalPages && (
          <Link
            href={`?page=${page + 1}`}
            className="rounded px-3 py-1 text-xs font-medium text-slate-600 border border-slate-300 hover:bg-white transition"
          >
            Próxima
          </Link>
        )}
      </div>
    </div>
  )
}

export default async function TurmasPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>
}) {
  const { page: pageParam } = await searchParams
  const page = Math.max(1, parseInt(pageParam ?? '1') || 1)
  const data = await getClassGroups(page)
  const turmas = data.results

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Turmas</h1>
          <p className="text-sm text-slate-500 mt-0.5">{data.count} turma{data.count !== 1 ? 's' : ''} cadastrada{data.count !== 1 ? 's' : ''}</p>
        </div>
        <TurmaForm />
      </div>

      {turmas.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <svg className="w-10 h-10 mx-auto mb-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
          </svg>
          <p className="text-sm">Nenhuma turma cadastrada ainda.</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="text-left px-5 py-3 font-medium text-slate-500">Nome</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Ano / Série</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Alunos</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Status</th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {turmas.map((turma) => (
                <TurmaRow key={turma.id} turma={turma} />
              ))}
            </tbody>
          </table>
          <Pagination page={page} count={data.count} />
        </div>
      )}
    </div>
  )
}
