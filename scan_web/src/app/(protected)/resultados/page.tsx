import Link from 'next/link'
import { apiFetch } from '@/lib/api'
import type { ScanResult, PaginatedResponse } from '@/lib/definitions'

async function getScanResults(page: number): Promise<PaginatedResponse<ScanResult>> {
  const res = await apiFetch(`/api/v1/scan-results/?page=${page}`)
  if (!res.ok) return { count: 0, next: null, previous: null, results: [] }
  return res.json()
}

function ScoreBadge({ score, total }: { score: number; total: number }) {
  const pct = total > 0 ? Math.round((score / total) * 100) : 0
  const cls =
    pct >= 70
      ? 'bg-green-50 text-green-700'
      : pct >= 50
      ? 'bg-yellow-50 text-yellow-700'
      : 'bg-red-50 text-red-700'
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
      {score}/{total}
      <span className="font-normal opacity-70">({pct}%)</span>
    </span>
  )
}

function Pagination({ page, count }: { page: number; count: number }) {
  const pageSize = 10
  const totalPages = Math.ceil(count / pageSize)
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-between px-5 py-3 border-t border-slate-200 bg-slate-50">
      <p className="text-xs text-slate-500">
        Página {page} de {totalPages} ({count} resultado{count !== 1 ? 's' : ''})
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

export default async function ResultadosPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>
}) {
  const { page: pageParam } = await searchParams
  const page = Math.max(1, parseInt(pageParam ?? '1') || 1)
  const data = await getScanResults(page)
  const results = data.results

  return (
    <div>
      <div className="mb-5 sm:mb-6">
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Resultados</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          {data.count} leitura{data.count !== 1 ? 's' : ''} realizada{data.count !== 1 ? 's' : ''}
        </p>
      </div>

      {results.length === 0 ? (
        <div className="text-center py-16 text-slate-400 bg-white border border-slate-200 rounded-xl">
          <svg className="w-10 h-10 mx-auto mb-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z" />
          </svg>
          <p className="text-sm">Nenhum cartão escaneado ainda.</p>
          <Link href="/escanear" className="mt-3 inline-block text-sm text-indigo-600 hover:underline font-medium">
            Escanear primeiro cartão
          </Link>
        </div>
      ) : (
        <>
        <div className="sm:hidden space-y-3">
          {results.map((r) => (
            <div key={r.id} className="bg-white border border-slate-200 rounded-lg p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h2 className="font-semibold text-slate-900 truncate">{r.exam_title}</h2>
                  <p className="text-xs text-slate-500 mt-1">
                    {r.student_identified
                      ? r.student_name
                      : r.student_number && r.student_number !== '??' && r.student_number !== '?'
                      ? `Nº ${r.student_number}`
                      : 'Aluno não identificado'}
                  </p>
                </div>
                <ScoreBadge score={r.score} total={r.total_questions} />
              </div>
              <div className="mt-3 flex items-center justify-between gap-3">
                {r.warnings.length > 0 ? (
                  <span className="text-xs text-amber-700">{r.warnings.length} aviso{r.warnings.length !== 1 ? 's' : ''}</span>
                ) : (
                  <span className="text-xs text-slate-400">Sem avisos</span>
                )}
                <Link href={`/resultados/${r.id}`} className="text-sm font-medium text-indigo-600">
                  Detalhes
                </Link>
              </div>
            </div>
          ))}
          <Pagination page={page} count={data.count} />
        </div>

        <div className="hidden sm:block bg-white border border-slate-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="text-left px-5 py-3 font-medium text-slate-500">Prova</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Aluno</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Nota</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Avisos</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Data</th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {results.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50 transition">
                  <td className="px-5 py-3.5">
                    <p className="font-medium text-slate-800">{r.exam_title}</p>
                  </td>
                  <td className="px-5 py-3.5">
                    {r.student_identified ? (
                      <span className="text-slate-700">{r.student_name}</span>
                    ) : (
                      <span className="text-slate-400 italic text-xs">
                        {r.student_number && r.student_number !== '??' && r.student_number !== '?'
                          ? `Nº ${r.student_number} (não encontrado)`
                          : 'Não identificado'}
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-3.5">
                    <ScoreBadge score={r.score} total={r.total_questions} />
                  </td>
                  <td className="px-5 py-3.5">
                    {r.warnings.length > 0 ? (
                      <span className="inline-flex items-center gap-1 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5">
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                        </svg>
                        {r.warnings.length} aviso{r.warnings.length !== 1 ? 's' : ''}
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400">—</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5 text-slate-500 text-xs whitespace-nowrap">
                    {new Date(r.created_at).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Link
                      href={`/resultados/${r.id}`}
                      className="text-sm text-indigo-600 hover:text-indigo-800 font-medium transition"
                    >
                      Ver detalhes
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination page={page} count={data.count} />
        </div>
        </>
      )}
    </div>
  )
}
