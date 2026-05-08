'use client'

import { useActionState, useEffect, useState } from 'react'
import { updateStudent, deleteStudent } from '@/app/actions/alunos'
import type { Student } from '@/lib/definitions'

const INPUT =
  'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20'

export default function AlunoRow({
  aluno,
  classGroupId,
}: {
  aluno: Student
  classGroupId: number
}) {
  const [editing, setEditing] = useState(false)
  const [state, action, pending] = useActionState(updateStudent, undefined)

  useEffect(() => {
    if (state?.ok) setEditing(false)
  }, [state])

  if (editing) {
    return (
      <tr className="bg-indigo-50/60">
        <td colSpan={4} className="px-5 py-4">
          <p className="text-xs font-semibold text-indigo-700 mb-3">Editar aluno</p>
          <form action={action} className="flex flex-wrap items-end gap-3">
            <input type="hidden" name="id" value={aluno.id} />
            <input type="hidden" name="class_group" value={classGroupId} />

            <div className="w-24">
              <label className="block text-xs font-medium text-slate-600 mb-1">
                Número <span className="text-red-500">*</span>
              </label>
              <input
                name="number"
                type="number"
                min={1}
                required
                defaultValue={aluno.number}
                className={INPUT}
              />
            </div>

            <div className="flex-1 min-w-48">
              <label className="block text-xs font-medium text-slate-600 mb-1">
                Nome <span className="text-red-500">*</span>
              </label>
              <input
                name="name"
                required
                defaultValue={aluno.name}
                className={INPUT}
              />
            </div>

            {state?.error && (
              <p className="w-full text-xs text-red-600">{state.error}</p>
            )}

            <div className="flex gap-2">
              <button
                type="submit"
                disabled={pending}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition"
              >
                {pending ? 'Salvando...' : 'Salvar'}
              </button>
              <button
                type="button"
                onClick={() => setEditing(false)}
                className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 transition"
              >
                Cancelar
              </button>
            </div>
          </form>
        </td>
      </tr>
    )
  }

  return (
    <tr className="hover:bg-slate-50 transition">
      <td className="px-5 py-3.5 font-mono text-slate-500">
        {String(aluno.number).padStart(2, '0')}
      </td>
      <td className="px-5 py-3.5 font-medium text-slate-800">{aluno.name}</td>
      <td className="px-5 py-3.5">
        <span
          className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
            aluno.is_active ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'
          }`}
        >
          {aluno.is_active ? 'Ativo' : 'Inativo'}
        </span>
      </td>
      <td className="px-5 py-3.5 text-right">
        <div className="flex items-center justify-end gap-2">
          <button
            onClick={() => setEditing(true)}
            className="text-slate-400 hover:text-indigo-500 transition"
            title="Editar"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125" />
            </svg>
          </button>
          <form action={deleteStudent}>
            <input type="hidden" name="id" value={aluno.id} />
            <input type="hidden" name="class_group" value={classGroupId} />
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
  )
}
