import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard-layout'

export const Route = createFileRoute('/usages')({
    component: UsagesPage,
})

function UsagesPage() {
    return (
        <DashboardLayout>
            <h1 className='font-bold text-2xl'>Usages</h1>
            <div className="mt-4">
                <p className="text-muted-foreground">Track and monitor API usage and metrics.</p>
            </div>
        </DashboardLayout>
    )
}
