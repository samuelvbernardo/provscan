import { PageHeaderSkeleton, TableSkeleton } from '@/components/ui/PageSkeleton'

export default function ProvasLoading() {
  return (
    <div>
      <PageHeaderSkeleton />
      <TableSkeleton rows={6} />
    </div>
  )
}
