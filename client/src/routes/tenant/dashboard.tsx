import { createFileRoute } from "@tanstack/react-router";
import { authGuard } from "@/guards/auth-guard";
import { DashboardLayout } from "@/components/dashboard-layout";
import { tenantSideBarData } from "@/constants/tenant-dashboard-sidebar";

export const Route = createFileRoute('/tenant/dashboard')({
    beforeLoad: () => {
        authGuard('/tenant/dashboard')
    },
    component: TenantDashboard,
})


function TenantDashboard() {
    return (
        <DashboardLayout defaultData={tenantSideBarData}>
            <h1 className='font-bold text-2xl'>Tenant Dashboard</h1>
            <div className="mt-4">
                <p className="text-muted-foreground">Welcome to the tenant dashboard. Use the sidebar to navigate to different sections.</p>
            </div>
        </DashboardLayout>
    );
}

