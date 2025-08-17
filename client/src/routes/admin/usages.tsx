import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard-layout'
import { authGuard } from '@/guards/auth-guard';
import { adminDashboardData } from '@/constants/admin-dashboard-sidebar';

export const Route = createFileRoute('/admin/usages')({
    beforeLoad: () => {
        authGuard('/admin/usages');
    },
    component: UsagesPage,
})

function UsagesPage() {
    return (
        <DashboardLayout defaultData={adminDashboardData}>
            <h1 className='font-bold text-2xl'>Usages</h1>
            <div className="mt-4">
                <p className="text-muted-foreground">Track and monitor API usage and metrics.</p>
            </div>
        </DashboardLayout>
    )
}
