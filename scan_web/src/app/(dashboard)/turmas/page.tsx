import Link from 'next/link'
import { apiFetch } from '@/lib/api'
import { deleteClassGroup } from '@/app/actions/turmas'
import TurmaForm from './TurmaForm'
import type { ClassGroup, PaginatedResponse } from '@/lib/definitions'

async function getClassGroups(): Promise<ClassGroup[]> {
  const res = await apiFetch('/api/v1/class-groups/')
  if (!res.ok) return []
  const data: PaginatedResponse<ClassGroup> = await res.json()
  return data.results
}

export default async function TurmasPage() {
  const turmas = await getClassGroups()

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Turmas</h1>
          <p className="text-sm text-slate-500 mt-0.5">{turmas.length} turma{turmas.length !== 1 ? 's' : ''} cadastrada{turmas.length !== 1 ? 's' : ''}</p>
        </div>
        <TurmaForm />
      </div>

      {turmas.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <svg className="w-10 h-10 mx-auto mb-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
          </svg>
          <p className="text-sm">Nenhuma turma cadastrada ainda.</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="text-left px-5 py-3 font-medium text-slate-500">Nome</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Ano / Série</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Alunos</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Status</th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {turmas.map((turma) => (
                <tr key={turma.id} className="hover:bg-slate-50 transition">
                  <td className="px-5 py-3.5 font-medium text-slate-800">{turma.name}</td>
                  <td className="px-5 py-3.5 text-slate-500">{turma.school_year ?? '—'}</td>
                  <td className="px-5 py-3.5 text-slate-500">{turma.students_count}</td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${turma.is_active ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                      {turma.is_active ? 'Ativa' : 'Inativa'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        href={`/turmas/${turma.id}`}
                        className="text-indigo-600 hover:text-indigo-800 font-medium text-sm transition"
                      >
                        Ver alunos
                      </Link>
                      <form action={deleteClassGroup}>
                        <input type="hidden" name="id" value={turma.id} />
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
      )}
    </div>
  )
}
