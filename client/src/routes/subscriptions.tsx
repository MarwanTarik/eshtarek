import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard-layout'

export const Route = createFileRoute('/subscriptions')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <DashboardLayout>
      <h1 className='font-bold text-2xl'>Subscriptions</h1>
      <div className="mt-4">
        <p className="text-muted-foreground">Manage user subscriptions and billing.</p>
      </div>
    </DashboardLayout>
  )
}
