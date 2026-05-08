import Link from 'next/link'
import { notFound } from 'next/navigation'
import { apiFetch } from '@/lib/api'
import AlunoForm from './AlunoForm'
import AlunoRow from './AlunoRow'
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
                <th className="px-5 py-3 w-20" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {alunos.map((aluno) => (
                <AlunoRow key={aluno.id} aluno={aluno} classGroupId={turma.id} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
