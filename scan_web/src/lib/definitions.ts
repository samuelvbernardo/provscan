export type AuthFormState =
  | {
      error?: string
    }
  | undefined

export type FormState =
  | {
      error?: string
      ok?: boolean
    }
  | undefined

export type ClassGroup = {
  id: number
  name: string
  school_year: string | null
  is_active: boolean
  students_count: number
}

export type Student = {
  id: number
  class_group: number
  name: string
  number: number
  is_active: boolean
}

export type Exam = {
  id: number
  title: string
  description: string | null
  class_groups: number[]
  class_group_names: string[]
  questions_count: number
  options_count: number
  answer_key: string[]
  template_file: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type PaginatedResponse<T> = {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type ScanResult = {
  id: number
  exam: number
  exam_title: string
  student: number | null
  student_name: string | null
  student_identified: boolean
  student_number: string
  answers: (string | null)[]
  score: number
  total_questions: number
  image: string | null
  warnings: string[]
  created_at: string
  updated_at: string
}

export type ScanFormState =
  | {
      error?: string
      result?: ScanResult
    }
  | undefined
