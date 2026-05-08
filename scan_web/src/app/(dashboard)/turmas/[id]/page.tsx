import Link from 'next/link'
import { notFound } from 'next/navigation'
import { apiFetch } from '@/lib/api'
import { deleteStudent } from '@/app/actions/alunos'
import AlunoForm from './AlunoForm'
import type { ClassGroup, Student, PaginatedResponse } from '@/lib/definitions'

async function getClassGroup(id: string): Promise<ClassGroup | null> {
  const res = await apiFetch(`/api/v1/class-groups/${id}/`)
  if (!res.ok) return null
  return res.json()
}

async function getStudents(classGroupId: string): Promise<Student[]> {
  const res = await apiFetch(`/api/v1/students/?class_group=${classGroupId}`)
  if (!res.ok) return []
  const data: PaginatedResponse<Student> = await res.json()
  return data.results
}

export default async function TurmaDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const [turma, alunos] = await Promise.all([getClassGroup(id), getStudents(id)])

  if (!turma) notFound()

  return (
    <div>
      <div className="mb-6">
        <Link
          href="/turmas"
          className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-800 transition mb-4"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
          Turmas
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{turma.name}</h1>
            <p className="text-sm text-slate-500 mt-0.5">
              {turma.school_year && <span>{turma.school_year} · </span>}
              {alunos.length} aluno{alunos.length !== 1 ? 's' : ''}
            </p>
          </div>
          <AlunoForm classGroupId={turma.id} />
        </div>
      </div>

      {alunos.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <svg className="w-10 h-10 mx-auto mb-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
          </svg>
          <p className="text-sm">Nenhum aluno cadastrado nessa turma.</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="text-left px-5 py-3 font-medium text-slate-500 w-20">Nº</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Nome</th>
                <th className="text-left px-5 py-3 font-medium text-slate-500">Status</th>
                <th className="px-5 py-3 w-12" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {alunos.map((aluno) => (
                <tr key={aluno.id} className="hover:bg-slate-50 transition">
                  <td className="px-5 py-3.5 font-mono text-slate-500">
                    {String(aluno.number).padStart(2, '0')}
                  </td>
                  <td className="px-5 py-3.5 font-medium text-slate-800">{aluno.name}</td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${aluno.is_active ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                      {aluno.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <form action={deleteStudent}>
                      <input type="hidden" name="id" value={aluno.id} />
                      <input type="hidden" name="class_group" value={turma.id} />
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
