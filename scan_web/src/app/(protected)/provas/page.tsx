import Link from 'next/link'
import { apiFetch } from '@/lib/api'
import ProvaList from './ProvaList'
import type { Exam, PaginatedResponse } from '@/lib/definitions'

async function getExams(page: number): Promise<PaginatedResponse<Exam>> {
  const res = await apiFetch(`/api/v1/exams/?page=${page}`)
  if (!res.ok) return { count: 0, next: null, previous: null, results: [] }
  return res.json()
}

function Pagination({ page, count }: { page: number; count: number }) {
  const pageSize = 10
  const totalPages = Math.ceil(count / pageSize)
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-between px-5 py-3 border-t border-slate-200 bg-slate-50 rounded-b-xl">
      <p className="text-xs text-slate-500">
        Página {page} de {totalPages} ({count} prova{count !== 1 ? 's' : ''})
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

export default async function ProvasPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>
}) {
  const { page: pageParam } = await searchParams
  const page = Math.max(1, parseInt(pageParam ?? '1') || 1)
  const data = await getExams(page)
  const provas = data.results

  return (
    <div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-5 sm:mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Provas</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {data.count} prova{data.count !== 1 ? 's' : ''} cadastrada{data.count !== 1 ? 's' : ''}
          </p>
        </div>
        <Link
          href="/provas/nova"
          className="inline-flex w-fit items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 transition"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Nova Prova
        </Link>
      </div>

      {provas.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <svg className="w-10 h-10 mx-auto mb-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
          <p className="text-sm">Nenhuma prova cadastrada ainda.</p>
        </div>
      ) : (
        <>
          <ProvaList provas={provas} />
          <Pagination page={page} count={data.count} />
        </>
      )}
    </div>
  )
}
