'use client'

import Link from 'next/link'
import { useActionState, useState } from 'react'
import { createExam } from '@/app/actions/provas'
import type { ClassGroup } from '@/lib/definitions'

const OPTIONS = ['A', 'B', 'C', 'D', 'E']

export default function ExamForm({ classGroups }: { classGroups: ClassGroup[] }) {
  const [state, action, pending] = useActionState(createExam, undefined)
  const [questionsCount, setQuestionsCount] = useState(10)
  const [optionsCount, setOptionsCount] = useState(4)
  const [answers, setAnswers] = useState<string[]>(Array(10).fill(''))

  function handleQuestionsCount(raw: string) {
    const value = Math.min(30, Math.max(8, parseInt(raw) || 8))
    setQuestionsCount(value)
    setAnswers((prev) => {
      const next = Array(value).fill('')
      for (let i = 0; i < Math.min(prev.length, value); i++) next[i] = prev[i]
      return next
    })
  }

  function handleOptionsCount(value: number) {
    setOptionsCount(value)
    const valid = OPTIONS.slice(0, value)
    setAnswers((prev) => prev.map((a) => (valid.includes(a) ? a : '')))
  }

  function setAnswer(index: number, option: string) {
    setAnswers((prev) => {
      const next = [...prev]
      next[index] = next[index] === option ? '' : option
      return next
    })
  }

  const filled = answers.filter(Boolean).length

  return (
    <form action={action} className="space-y-6">
      <input type="hidden" name="answer_key" value={JSON.stringify(answers)} />

      {/* Título */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1.5">
          Título <span className="text-red-500">*</span>
        </label>
        <input
          name="title"
          required
          placeholder="Ex: Prova de Matemática — 1º Bimestre"
          className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
        />
      </div>

      {/* Descrição */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1.5">Descrição</label>
        <textarea
          name="description"
          rows={2}
          placeholder="Observações sobre a prova (opcional)"
          className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 resize-none"
        />
      </div>

      {/* Turmas */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1.5">
          Turmas <span className="text-red-500">*</span>
        </label>
        {classGroups.length === 0 ? (
          <p className="text-sm text-slate-400">Nenhuma turma cadastrada.</p>
        ) : (
          <div className="rounded-lg border border-slate-200 divide-y divide-slate-100 max-h-48 overflow-y-auto">
            {classGroups.map((t) => (
              <label
                key={t.id}
                className="flex items-center gap-3 px-3.5 py-2.5 cursor-pointer hover:bg-slate-50 transition"
              >
                <input
                  type="checkbox"
                  name="class_groups"
                  value={t.id}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-sm text-slate-700">{t.name}</span>
                {t.school_year && (
                  <span className="text-xs text-slate-400 ml-auto">{t.school_year}</span>
                )}
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Nº questões + alternativas */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Nº de questões
            <span className="ml-1 text-xs font-normal text-slate-400">(8–30)</span>
          </label>
          <input
            name="questions_count"
            type="number"
            min={8}
            max={30}
            value={questionsCount}
            onChange={(e) => handleQuestionsCount(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Alternativas</label>
          <div className="flex gap-2">
            {[4, 5].map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => handleOptionsCount(n)}
                className={`flex-1 py-2.5 rounded-lg border text-sm font-medium transition ${
                  optionsCount === n
                    ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                    : 'border-slate-300 text-slate-600 hover:border-slate-400'
                }`}
              >
                {n} alt.
              </button>
            ))}
          </div>
          <input type="hidden" name="options_count" value={optionsCount} />
        </div>
      </div>

      {/* Gabarito */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <label className="text-sm font-medium text-slate-700">
            Gabarito <span className="text-red-500">*</span>
          </label>
          <span className={`text-xs font-medium ${filled === questionsCount ? 'text-green-600' : 'text-slate-400'}`}>
            {filled}/{questionsCount} preenchidas
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          {Array.from({ length: questionsCount }, (_, i) => (
            <div
              key={i}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-100"
            >
              <span className="text-xs font-mono text-slate-400 w-5 text-right shrink-0">
                {i + 1}
              </span>
              <div className="flex gap-1 flex-1">
                {OPTIONS.slice(0, optionsCount).map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => setAnswer(i, opt)}
                    className={`flex-1 py-1.5 rounded text-xs font-bold transition ${
                      answers[i] === opt
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'bg-white border border-slate-200 text-slate-400 hover:border-indigo-300 hover:text-indigo-600'
                    }`}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Erro */}
      {state?.error && (
        <div className="flex items-start gap-2.5 rounded-lg bg-red-50 border border-red-200 px-3.5 py-3">
          <svg className="w-4 h-4 text-red-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
          </svg>
          <p className="text-sm text-red-700">{state.error}</p>
        </div>
      )}

      {/* Botões */}
      <div className="flex gap-2 pt-2">
        <button
          type="submit"
          disabled={pending}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition"
        >
          {pending && (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          )}
          {pending ? 'Criando...' : 'Criar Prova'}
        </button>
        <Link
          href="/provas"
          className="rounded-lg px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 transition"
        >
          Cancelar
        </Link>
      </div>
    </form>
  )
}
