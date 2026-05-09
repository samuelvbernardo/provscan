'use client'

import { useActionState, useRef, useState } from 'react'
import { scanExam } from '@/app/actions/escanear'
import type { Exam, ScanResult } from '@/lib/definitions'

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

function ResultPanel({ result, answerKey }: { result: ScanResult; answerKey: string[] }) {
  return (
    <div className="mt-6 space-y-5">
      <div className="bg-white border border-slate-200 rounded-xl p-5">
        <div className="flex items-center gap-5 flex-wrap">
          <ScoreRing score={result.score} total={result.total_questions} />
          <div className="flex-1 min-w-0 space-y-1.5">
            <h2 className="text-base font-semibold text-slate-800">{result.exam_title}</h2>
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-slate-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
              </svg>
              {result.student_identified ? (
                <span className="text-sm text-slate-700 font-medium">
                  {result.student_name}
                  <span className="ml-1.5 text-xs font-normal text-slate-400">nº {result.student_number}</span>
                </span>
              ) : (
                <span className="text-sm text-slate-400 italic">
                  Aluno não identificado
                  {result.student_number && result.student_number !== '?' && (
                    <span className="ml-1 not-italic text-xs text-slate-400">(nº lido: {result.student_number})</span>
                  )}
                </span>
              )}
            </div>
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

      <div className="bg-white border border-slate-200 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-slate-700 mb-3">Respostas por questão</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          {result.answers.map((given, i) => {
            const correct = answerKey[i]
            const isCorrect = given === correct
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
                  {!isBlank && !isCorrect && (
                    <>
                      <svg className="w-3.5 h-3.5 text-red-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                      </svg>
                      <span className="text-xs text-slate-500">correto: <span className="font-semibold text-green-700">{correct}</span></span>
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
    </div>
  )
}

export default function ScanForm({ exams }: { exams: Exam[] }) {
  const [state, action, pending] = useActionState(scanExam, undefined)
  const [selectedExam, setSelectedExam] = useState<Exam | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  function handleExamChange(id: string) {
    const exam = exams.find((e) => e.id === parseInt(id)) ?? null
    setSelectedExam(exam)
  }

  function handleFile(file: File | undefined) {
    if (!file) return
    setFileName(file.name)
    const url = URL.createObjectURL(file)
    setPreview(url)
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && fileInputRef.current) {
      const dt = new DataTransfer()
      dt.items.add(file)
      fileInputRef.current.files = dt.files
      handleFile(file)
    }
  }

  return (
    <div>
      <form action={action} className="bg-white border border-slate-200 rounded-xl p-6 space-y-5">
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Para uma boa leitura
          </p>
          <ul className="mt-2 space-y-1 text-xs text-slate-600">
            <li>Os 4 marcadores pretos precisam aparecer na foto.</li>
            <li>A folha não pode estar cortada.</li>
            <li>A imagem precisa estar razoavelmente focada.</li>
            <li>Evite sombra forte ou reflexo.</li>
            <li>O cartão deve estar minimamente plano.</li>
          </ul>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Prova <span className="text-red-500">*</span>
          </label>
          <select
            name="exam_id"
            required
            defaultValue=""
            onChange={(e) => handleExamChange(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
          >
            <option value="" disabled>Selecione uma prova...</option>
            {exams.map((e) => (
              <option key={e.id} value={e.id}>
                {e.title} — {e.class_group_names.join(', ')}
              </option>
            ))}
          </select>
          {selectedExam && (
            <p className="mt-1 text-xs text-slate-400">
              {selectedExam.questions_count} questões · {selectedExam.options_count} alternativas
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Imagem do cartão-resposta <span className="text-red-500">*</span>
          </label>
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => fileInputRef.current?.click()}
            className="relative cursor-pointer rounded-lg border-2 border-dashed border-slate-300 hover:border-indigo-400 transition bg-slate-50 hover:bg-indigo-50/30 flex flex-col items-center justify-center min-h-40 overflow-hidden"
          >
            {preview ? (
              <img src={preview} alt="preview" className="max-h-56 object-contain p-2" />
            ) : (
              <div className="flex flex-col items-center gap-2 py-8 px-4 text-center">
                <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
                </svg>
                <p className="text-sm text-slate-500">
                  Arraste a imagem aqui ou <span className="text-indigo-600 font-medium">clique para selecionar</span>
                </p>
                <p className="text-xs text-slate-400">JPG, PNG, WEBP, HEIC ou HEIF</p>
              </div>
            )}
          </div>
          {fileName && (
            <p className="mt-1.5 text-xs text-slate-500 truncate">{fileName}</p>
          )}
          <input
            ref={fileInputRef}
            type="file"
            name="image"
            accept="image/jpeg,image/png,image/webp,image/heic,image/heif"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
        </div>

        {state?.error && (
          <div className="flex items-start gap-2.5 rounded-lg bg-red-50 border border-red-200 px-3.5 py-3">
            <svg className="w-4 h-4 text-red-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
            </svg>
            <p className="text-sm text-red-700">{state.error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={pending}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition"
        >
          {pending ? (
            <>
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Processando...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0 1 3.75 9.375v-4.5ZM3.75 14.625c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5a1.125 1.125 0 0 1-1.125-1.125v-4.5ZM13.5 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0 1 13.5 9.375v-4.5Z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 6.75h.75v.75h-.75v-.75ZM6.75 16.5h.75v.75h-.75v-.75ZM16.5 6.75h.75v.75h-.75v-.75Z" />
              </svg>
              Processar Cartão
            </>
          )}
        </button>
      </form>

      {state?.result && selectedExam && (
        <ResultPanel result={state.result} answerKey={selectedExam.answer_key} />
      )}
    </div>
  )
}
