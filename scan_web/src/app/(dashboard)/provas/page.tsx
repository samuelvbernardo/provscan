import Link from 'next/link'
import { apiFetch } from '@/lib/api'
import { deleteExam } from '@/app/actions/provas'
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
    <div className="flex items-center justify-between px-5 py-3 border-t border-slate-200 bg-slate-50">
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
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Provas</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {data.count} prova{data.count !== 1 ? 's' : ''} cadastrada{data.count !== 1 ? 's' : ''}
          </p>
        </div>
        <Link
          href="/provas/nova"
          className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 transition"
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
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="text-left px-5 py-3 font-medium text-slate-500">Título</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Turma</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Questões</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Status</th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {provas.map((prova) => (
                <tr key={prova.id} className="hover:bg-slate-50 transition">
                  <td className="px-5 py-3.5">
                    <p className="font-medium text-slate-800">{prova.title}</p>
                    {prova.description && (
                      <p className="text-xs text-slate-400 mt-0.5 truncate max-w-xs">{prova.description}</p>
                    )}
                  </td>
                  <td className="px-5 py-3.5 text-slate-500">{prova.class_group_name}</td>
                  <td className="px-5 py-3.5 text-slate-500">
                    {prova.questions_count}q · {prova.options_count} alt.
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${prova.is_active ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                      {prova.is_active ? 'Ativa' : 'Inativa'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center justify-end gap-3">
                      {prova.template_file && (
                        <a
                          href={prova.template_file}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium text-sm transition"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                          </svg>
                          Cartão
                        </a>
                      )}
                      <form action={deleteExam}>
                        <input type="hidden" name="id" value={prova.id} />
                        <button
                          type="submit"
                          className="text-slate-400 hover:text-red-500 transition"
                          title="Excluir"
                        >
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                          </svg>
                        </button>
                      </form>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination page={page} count={data.count} />
        </div>
      )}
    </div>
  )
}
