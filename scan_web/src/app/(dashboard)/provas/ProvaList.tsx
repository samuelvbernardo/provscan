'use client'

import { useState } from 'react'
import { deleteExam } from '@/app/actions/provas'
import type { Exam } from '@/lib/definitions'

function DownloadIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
    </svg>
  )
}

export default function ProvaList({ provas }: { provas: Exam[] }) {
  const [selected, setSelected] = useState<Set<number>>(new Set())

  function toggle(id: number) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  function toggleAll() {
    setSelected((prev) =>
      prev.size === provas.length ? new Set() : new Set(provas.map((p) => p.id))
    )
  }

  const allChecked = selected.size === provas.length && provas.length > 0
  const someChecked = selected.size > 0 && selected.size < provas.length

  function handleDownload() {
    const ids = Array.from(selected).join(',')
    const a = document.createElement('a')
    a.href = `/api/class-report?exam_ids=${ids}`
    a.download = 'relatorio_turmas.pdf'
    a.click()
  }

  return (
    <>
      <div className="sm:hidden space-y-3">
        {provas.map((prova) => (
          <div
            key={prova.id}
            className={`border rounded-lg p-4 bg-white ${selected.has(prova.id) ? 'border-indigo-300 ring-1 ring-indigo-100' : 'border-slate-200'}`}
          >
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={selected.has(prova.id)}
                onChange={() => toggle(prova.id)}
                className="mt-1 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
              <div className="min-w-0 flex-1">
                <h2 className="font-semibold text-slate-900 truncate">{prova.title}</h2>
                <p className="text-xs text-slate-500 mt-1">
                  {prova.questions_count}q · {prova.options_count} alt.
                </p>
                <p className="text-xs text-slate-400 mt-1 truncate">
                  {prova.class_group_names.join(', ') || 'Sem turma'}
                </p>
              </div>
              <span className={`shrink-0 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${prova.is_active ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                {prova.is_active ? 'Ativa' : 'Inativa'}
              </span>
            </div>

            <div className="mt-3 flex items-center justify-between gap-3">
              <a
                href={`/api/exam-template/${prova.id}`}
                className="inline-flex items-center gap-1 text-sm font-medium text-indigo-600"
              >
                <DownloadIcon />
                Cartão
              </a>
              <form action={deleteExam}>
                <input type="hidden" name="id" value={prova.id} />
                <button type="submit" className="text-xs font-medium text-red-500">
                  Excluir
                </button>
              </form>
            </div>
          </div>
        ))}
      </div>

      <div className="hidden sm:block bg-white border border-slate-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="px-4 py-3 w-10">
                <input
                  type="checkbox"
                  checked={allChecked}
                  ref={(el) => { if (el) el.indeterminate = someChecked }}
                  onChange={toggleAll}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
              </th>
              <th className="text-left px-5 py-3 font-medium text-slate-500">Título</th>
              <th className="text-left px-5 py-3 font-medium text-slate-500">Turma</th>
              <th className="text-left px-5 py-3 font-medium text-slate-500">Questões</th>
              <th className="text-left px-5 py-3 font-medium text-slate-500">Status</th>
              <th className="px-5 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {provas.map((prova) => (
              <tr
                key={prova.id}
                className={`transition ${selected.has(prova.id) ? 'bg-indigo-50/60' : 'hover:bg-slate-50'}`}
              >
                <td className="px-4 py-3.5 text-center">
                  <input
                    type="checkbox"
                    checked={selected.has(prova.id)}
                    onChange={() => toggle(prova.id)}
                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                  />
                </td>
                <td className="px-5 py-3.5">
                  <p className="font-medium text-slate-800">{prova.title}</p>
                  {prova.description && (
                    <p className="text-xs text-slate-400 mt-0.5 truncate max-w-xs">{prova.description}</p>
                  )}
                </td>
                <td className="px-5 py-3.5 text-slate-500">{prova.class_group_names.join(', ') || '—'}</td>
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
                    <a
                      href={`/api/exam-template/${prova.id}`}
                      className="flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium text-sm transition"
                    >
                      <DownloadIcon />
                      Cartão
                    </a>
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
      </div>

      {/* Sticky bar */}
      {selected.size > 0 && (
        <div className="fixed bottom-4 left-3 right-3 sm:bottom-6 sm:left-1/2 sm:right-auto sm:-translate-x-1/2 z-50">
          <div className="flex items-center justify-between gap-3 bg-slate-900 text-white rounded-xl px-4 sm:px-5 py-3 shadow-xl">
            <span className="text-sm">
              <span className="font-semibold">{selected.size}</span>{' '}
              <span className="hidden sm:inline">prova{selected.size !== 1 ? 's' : ''} selecionada{selected.size !== 1 ? 's' : ''}</span>
            </span>
            <button
              onClick={() => setSelected(new Set())}
              className="text-xs text-slate-400 hover:text-white transition"
            >
              Limpar
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 rounded-lg bg-indigo-500 hover:bg-indigo-400 px-3 sm:px-4 py-1.5 text-sm font-semibold transition"
            >
              <DownloadIcon />
              Gerar relatório
            </button>
          </div>
        </div>
      )}
    </>
  )
}
