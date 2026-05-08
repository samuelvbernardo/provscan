import Link from 'next/link'
import { notFound } from 'next/navigation'
import { apiFetch } from '@/lib/api'
import type { ScanResult, Exam } from '@/lib/definitions'

async function getScanResult(id: string): Promise<ScanResult | null> {
  const res = await apiFetch(`/api/v1/scan-results/${id}/`)
  if (res.status === 404) return null
  if (!res.ok) return null
  return res.json()
}

async function getExam(id: number): Promise<Exam | null> {
  const res = await apiFetch(`/api/v1/exams/${id}/`)
  if (!res.ok) return null
  return res.json()
}

function ScoreRing({ score, total }: { score: number; total: number }) {
  const pct = total > 0 ? Math.round((score / total) * 100) : 0
  const color = pct >= 70 ? 'text-green-600' : pct >= 50 ? 'text-yellow-600' : 'text-red-600'
  const bg = pct >= 70 ? 'bg-green-50' : pct >= 50 ? 'bg-yellow-50' : 'bg-red-50'
  const border = pct >= 70 ? 'border-green-200' : pct >= 50 ? 'border-yellow-200' : 'border-red-200'
  return (
    <div className={`flex flex-col items-center justify-center w-28 h-28 rounded-full border-4 ${border} ${bg}`}>
      <span className={`text-3xl font-bold ${color}`}>{score}</span>
      <span className="text-xs text-slate-500 font-medium">de {total}</span>
      <span className={`text-xs font-semibold ${color}`}>{pct}%</span>
    </div>
  )
}

export default async function ResultadoDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const result = await getScanResult(id)
  if (!result) notFound()

  const exam = await getExam(result.exam)
  const answerKey = exam?.answer_key ?? []

  const date = new Date(result.created_at).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <Link
          href="/resultados"
          className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-800 transition mb-4"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
          Resultados
        </Link>
        <h1 className="text-2xl font-bold text-slate-900">{result.exam_title}</h1>
        <p className="text-sm text-slate-500 mt-0.5">{date}</p>
      </div>

      {/* Header card */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 mb-4">
        <div className="flex items-center gap-5 flex-wrap">
          <ScoreRing score={result.score} total={result.total_questions} />
          <div className="flex-1 min-w-0 space-y-2">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-slate-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
              </svg>
              {result.student_identified ? (
                <span className="text-sm font-medium text-slate-800">
                  {result.student_name}
                  <span className="ml-1.5 text-xs font-normal text-slate-400">nº {result.student_number}</span>
                </span>
              ) : (
                <span className="text-sm text-slate-400 italic">
                  Aluno não identificado
                  {result.student_number && result.student_number !== '??' && (
                    <span className="ml-1 not-italic text-xs">(nº lido: {result.student_number})</span>
                  )}
                </span>
              )}
            </div>

            {exam && (
              <div className="flex flex-wrap gap-3 text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
                  </svg>
                  {exam.class_group_name}
                </span>
                <span>{exam.questions_count} questões · {exam.options_count} alternativas</span>
              </div>
            )}
          </div>
        </div>

        {result.warnings.length > 0 && (
          <div className="mt-4 space-y-1.5">
            {result.warnings.map((w, i) => (
              <div key={i} className="flex items-start gap-2 rounded-lg bg-amber-50 border border-amber-200 px-3 py-2">
                <svg className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                </svg>
                <p className="text-xs text-amber-800">{w}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Answers grid */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 mb-4">
        <h2 className="text-sm font-semibold text-slate-700 mb-3">Respostas por questão</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          {result.answers.map((given, i) => {
            const correct = answerKey[i]
            const isCorrect = given !== null && given === correct
            const isBlank = given === null || given === undefined
            return (
              <div
                key={i}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
                  isBlank
                    ? 'bg-slate-50 border-slate-200'
                    : isCorrect
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <span className="text-xs font-mono text-slate-400 w-5 text-right shrink-0">{i + 1}</span>
                <div className="flex items-center gap-1.5 flex-1">
                  <span className={`text-sm font-bold w-6 text-center ${
                    isBlank ? 'text-slate-400' : isCorrect ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {isBlank ? '—' : given}
                  </span>
                  {!isBlank && !isCorrect && correct && (
                    <>
                      <svg className="w-3.5 h-3.5 text-red-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                      </svg>
                      <span className="text-xs text-slate-500">
                        correto: <span className="font-semibold text-green-700">{correct}</span>
                      </span>
                    </>
                  )}
                  {isCorrect && (
                    <svg className="w-3.5 h-3.5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                    </svg>
                  )}
                  {isBlank && <span className="text-xs text-slate-400">em branco</span>}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Imagem do cartão */}
      {result.image && (
        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-3">Imagem do cartão-resposta</h2>
          <img
            src={result.image}
            alt="Cartão-resposta"
            className="w-full rounded-lg object-contain max-h-96 border border-slate-100"
          />
        </div>
      )}
    </div>
  )
}
