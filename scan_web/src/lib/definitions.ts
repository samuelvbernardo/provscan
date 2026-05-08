export type AuthFormState =
  | {
      error?: string
    }
  | undefined

export type FormState =
  | {
      error?: string
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

export type PaginatedResponse<T> = {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
