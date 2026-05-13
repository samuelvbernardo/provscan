'use client'

import { useActionState, useState } from 'react'
import { createStudent } from '@/app/actions/alunos'

export default function AlunoForm({ classGroupId }: { classGroupId: number }) {
  const [open, setOpen] = useState(false)
  const [state, action, pending] = useActionState(createStudent, undefined)

  return (
    <div>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 transition"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        Novo Aluno
      </button>

      {open && (
        <div className="mt-4 bg-white border border-slate-200 rounded-xl p-6 max-w-md">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Novo aluno</h3>
          <form action={action} className="space-y-4">
            <input type="hidden" name="class_group" value={classGroupId} />

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Número <span className="text-red-500">*</span>
              </label>
              <input
                name="number"
                type="number"
                min={1}
                required
                placeholder="Ex: 25"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Nome <span className="text-red-500">*</span>
              </label>
              <input
                name="name"
                required
                placeholder="Nome completo"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
              />
            </div>

            {state?.error && (
              <p className="text-sm text-red-600">{state.error}</p>
            )}

            <div className="flex gap-2 pt-1">
              <button
                type="submit"
                disabled={pending}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition"
              >
                {pending ? 'Salvando...' : 'Salvar'}
              </button>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 transition"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
