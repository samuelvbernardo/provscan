import { PageHeaderSkeleton, TableSkeleton } from '@/components/ui/PageSkeleton'

export default function ResultadosLoading() {
  return (
    <div>
      <PageHeaderSkeleton />
      <TableSkeleton rows={8} />
    </div>
  )
}
