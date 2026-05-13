import Link from 'next/link'
import { apiFetch } from '@/lib/api'
import type { ClassGroup, Exam, PaginatedResponse, ScanResult } from '@/lib/definitions'

const emptyPage = <T,>(): PaginatedResponse<T> => ({
  count: 0,
  next: null,
  previous: null,
  results: [],
})

async function getPage<T>(path: string): Promise<PaginatedResponse<T>> {
  const res = await apiFetch(path)
  if (!res.ok) return emptyPage<T>()
  return res.json()
}

async function getDashboardData() {
  const [classGroups, exams, scanResults] = await Promise.all([
    getPage<ClassGroup>('/api/v1/class-groups/?page=1'),
    getPage<Exam>('/api/v1/exams/?page=1'),
    getPage<ScanResult>('/api/v1/scan-results/?page=1'),
  ])

  return { classGroups, exams, scanResults }
}

function scorePercent(result: ScanResult) {
  if (result.total_questions <= 0) return 0
  return Math.round((result.score / result.total_questions) * 100)
}

function averageRecentScore(results: ScanResult[]) {
  const scored = results.filter((result) => result.total_questions > 0)
  if (scored.length === 0) return null

  const total = scored.reduce((sum, result) => sum + scorePercent(result), 0)
  return Math.round(total / scored.length)
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function StatCard({
  label,
  value,
  detail,
  href,
}: {
  label: string
  value: string | number
  detail: string
  href: string
}) {
  return (
    <Link
      href={href}
      className="rounded-lg border border-slate-200 bg-white px-4 py-4 transition hover:border-indigo-200 hover:bg-indigo-50/30"
    >
      <span className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</span>
      <strong className="mt-2 block text-2xl font-bold text-slate-900">{value}</strong>
      <span className="mt-1 block text-xs text-slate-500">{detail}</span>
    </Link>
  )
}

function QuickAction({
  href,
  title,
  description,
}: {
  href: string
  title: string
  description: string
}) {
  return (
    <Link
      href={href}
      className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3 transition hover:border-indigo-200 hover:bg-indigo-50/30"
    >
      <span className="min-w-0">
        <span className="block text-sm font-semibold text-slate-800">{title}</span>
        <span className="mt-0.5 block text-xs text-slate-500">{description}</span>
      </span>
      <svg
        className="h-4 w-4 shrink-0 text-slate-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
      </svg>
    </Link>
  )
}

function ScoreBadge({ result }: { result: ScanResult }) {
  const pct = scorePercent(result)
  const cls =
    pct >= 70
      ? 'bg-green-50 text-green-700'
      : pct >= 50
      ? 'bg-yellow-50 text-yellow-700'
      : 'bg-red-50 text-red-700'

  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${cls}`}>
      {pct}%
    </span>
  )
}

export default async function DashboardPage() {
  const { classGroups, exams, scanResults } = await getDashboardData()
  const recentResults = scanResults.results.slice(0, 5)
  const recentExams = exams.results.slice(0, 4)
  const avgScore = averageRecentScore(recentResults)
  const warningsCount = recentResults.reduce((sum, result) => sum + result.warnings.length, 0)
  const activeExams = recentExams.filter((exam) => exam.is_active).length

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 sm:text-2xl">Dashboard</h1>
          <p className="mt-0.5 text-sm text-slate-500">Resumo das turmas, provas e leituras recentes.</p>
        </div>
        <Link
          href="/escanear"
          className="inline-flex w-fit items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3.75 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0 1 3.75 9.375v-4.5ZM3.75 14.625c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5a1.125 1.125 0 0 1-1.125-1.125v-4.5ZM13.5 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0 1 13.5 9.375v-4.5Z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6.75 6.75h.75v.75h-.75v-.75ZM6.75 16.5h.75v.75h-.75v-.75ZM16.5 6.75h.75v.75h-.75v-.75Z"
            />
          </svg>
          Escanear cartão
        </Link>
      </div>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Turmas"
          value={classGroups.count}
          detail="Turmas cadastradas no sistema"
          href="/turmas"
        />
        <StatCard
          label="Provas"
          value={exams.count}
          detail={`${activeExams} ativa${activeExams !== 1 ? 's' : ''} entre as recentes`}
          href="/provas"
        />
        <StatCard
          label="Leituras"
          value={scanResults.count}
          detail={`${warningsCount} aviso${warningsCount !== 1 ? 's' : ''} nas últimas leituras`}
          href="/resultados"
        />
        <StatCard
          label="Média recente"
          value={avgScore === null ? '-' : `${avgScore}%`}
          detail="Considera as últimas leituras listadas"
          href="/resultados"
        />
      </section>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <section className="rounded-xl border border-slate-200 bg-white">
          <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-800">Últimas leituras</h2>
              <p className="mt-0.5 text-xs text-slate-500">Resultados mais recentes processados pelo OMR.</p>
            </div>
            <Link href="/resultados" className="text-sm font-medium text-indigo-600 hover:text-indigo-800">
              Ver todos
            </Link>
          </div>

          {recentResults.length === 0 ? (
            <div className="px-5 py-10 text-center text-sm text-slate-400">
              Nenhuma leitura registrada ainda.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {recentResults.map((result) => (
                <Link
                  key={result.id}
                  href={`/resultados/${result.id}`}
                  className="flex items-center justify-between gap-4 px-5 py-3.5 transition hover:bg-slate-50"
                >
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-medium text-slate-800">{result.exam_title}</span>
                    <span className="mt-0.5 block truncate text-xs text-slate-500">
                      {result.student_identified
                        ? result.student_name
                        : result.student_number && result.student_number !== '??' && result.student_number !== '?'
                        ? `Nº ${result.student_number}`
                        : 'Aluno não identificado'}{' '}
                      · {formatDate(result.created_at)}
                    </span>
                  </span>
                  <span className="flex shrink-0 items-center gap-2">
                    {result.warnings.length > 0 && (
                      <span className="hidden rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700 sm:inline-flex">
                        {result.warnings.length} aviso{result.warnings.length !== 1 ? 's' : ''}
                      </span>
                    )}
                    <ScoreBadge result={result} />
                  </span>
                </Link>
              ))}
            </div>
          )}
        </section>

        <div className="space-y-6">
          <section className="space-y-2">
            <h2 className="text-sm font-semibold text-slate-800">Ações rápidas</h2>
            <QuickAction href="/turmas" title="Gerenciar turmas" description="Cadastrar turmas e alunos" />
            <QuickAction href="/provas/nova" title="Criar prova" description="Gerar cartão-resposta em PDF" />
            <QuickAction href="/escanear" title="Escanear cartão" description="Processar uma nova leitura" />
          </section>

          <section className="rounded-xl border border-slate-200 bg-white">
            <div className="border-b border-slate-200 px-5 py-4">
              <h2 className="text-sm font-semibold text-slate-800">Provas recentes</h2>
            </div>
            {recentExams.length === 0 ? (
              <div className="px-5 py-8 text-sm text-slate-400">Nenhuma prova cadastrada.</div>
            ) : (
              <div className="divide-y divide-slate-100">
                {recentExams.map((exam) => (
                  <Link
                    key={exam.id}
                    href="/provas"
                    className="flex items-center justify-between gap-3 px-5 py-3.5 transition hover:bg-slate-50"
                  >
                    <span className="min-w-0">
                      <span className="block truncate text-sm font-medium text-slate-800">{exam.title}</span>
                      <span className="mt-0.5 block text-xs text-slate-500">
                        {exam.questions_count} questões · {exam.options_count} alternativas
                      </span>
                    </span>
                    <span
                      className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
                        exam.is_active ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'
                      }`}
                    >
                      {exam.is_active ? 'Ativa' : 'Inativa'}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}
