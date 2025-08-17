import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard-layout'
import { authGuard } from '@/guards/auth-guard';
import { adminDashboardData } from '@/constants/admin-dashboard-sidebar';

export const Route = createFileRoute('/admin/dashboard')({
  beforeLoad: () => {
    authGuard('/admin/dashboard');
  },
  component: AdminDashboardPage,
})

function AdminDashboardPage() {
  return (
    <DashboardLayout defaultData={adminDashboardData}>
      <h1 className='font-bold text-2xl'>Admin Dashboard</h1>
      <div className="mt-4">
        <p className="text-muted-foreground">Welcome to the admin dashboard. Use the sidebar to navigate to different sections.</p>
      </div>
    </DashboardLayout>
  )
}
