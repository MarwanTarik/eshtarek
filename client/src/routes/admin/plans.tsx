import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import type { LimitPolicyCreateRequest, Plan, PlanCreateRequest } from '@/app/types';
import { SubscriptionsBillingCycle } from '@/app/types'
import { DeletePlanMutationOptions, PlansMutationOptions, PlansQueryOptions, UpdatePlanMutationOptions } from '@/app/plans'
import { CreateLimitPolicyMutationOptions, LimitPoliciesQueryOptions } from '@/app/policies'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { PlanTable } from '@/components/admin/plans/plan-table'
import { PlanFormDialog } from '@/components/admin/plans/plan-form-dialog'
import { Button } from '@/components/ui/button'
import { DashboardLayout } from '@/components/dashboard-layout'
import { authGuard } from '@/guards/auth-guard';
import { adminDashboardData } from '@/constants/admin-dashboard-sidebar';

export const Route = createFileRoute('/admin/plans')({
  beforeLoad: () => {
    authGuard('/admin/plans');
  },
  component: PlansPage,
})

function PlansPage() {
  const queryClient = useQueryClient();

  const {
    data: plansData,
    isPending: plansIsPending,
    isError: plansIsError,
  } = useQuery(PlansQueryOptions);

  const {
    data: policiesData,
    isPending: policiesIsPending,
    isError: policiesIsError,
  } = useQuery(LimitPoliciesQueryOptions);

  const plans = plansData ?? [];
  const [open, setOpen] = useState(false);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<PlanCreateRequest>({
    name: "",
    price: 0,
    billing_cycle: SubscriptionsBillingCycle.MONTHLY,
    description: "",
    billing_duration: 0,
    policy_ids: [],
  });
  const [newPolicy, setNewPolicy] = useState<LimitPolicyCreateRequest>({ metric: '', limit: 0 });

  const createPlanMutation = useMutation(PlansMutationOptions);
  const updatePlanMutation = useMutation(editingId ? UpdatePlanMutationOptions(editingId) : PlansMutationOptions);
  const createPolicyMutation = useMutation(CreateLimitPolicyMutationOptions);
  const deletePlanMutation = useMutation(
    confirmId ? DeletePlanMutationOptions(confirmId) : {
      mutationFn: () => Promise.reject(new Error('No plan ID to delete'))
    }
  );

  const resetForm = () => setForm({
    name: "",
    price: 0,
    billing_cycle: SubscriptionsBillingCycle.MONTHLY,
    description: "",
    billing_duration: 0,
    policy_ids: []
  });

  const onCreate = () => {
    setEditingId(null);
    resetForm();
    setOpen(true);
  };

  const onEdit = (plan: Plan) => {
    setEditingId(plan.id);
    setForm({
      name: plan.name,
      description: plan.description,
      billing_cycle: plan.billing_cycle,
      billing_duration: plan.billing_duration,
      price: plan.price,
      policy_ids: plan.associated_policies.map(p => p.id)
    });
    setOpen(true);
  };

  const onDelete = async (id: string) => {
    if (confirmId === id) {
      try {
        await deletePlanMutation.mutateAsync();
        await queryClient.invalidateQueries({ queryKey: ['plans', 'all'] });
        setConfirmId(null);
      } catch (error) {
        console.error('Failed to delete plan:', error);
        setConfirmId(null);
      }
    } else {
      setConfirmId(id);
    }
  };

  const cancelDelete = () => {
    setConfirmId(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      if (editingId) {
        await updatePlanMutation.mutateAsync(form);
      } else {
        await createPlanMutation.mutateAsync(form);
      }
      await queryClient.invalidateQueries({ queryKey: ['plans', 'all'] });
      setOpen(false);
      setEditingId(null);
      resetForm();
    } catch (e) {
      // TODO: add toast later
      console.log("can't save plan")
    }
  };

  const handleCreatePolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPolicy.metric || !newPolicy.limit) return;
    try {
      const res = await createPolicyMutation.mutateAsync(newPolicy);
      const created = res;
      setForm(prev => ({ ...prev, policy_ids: Array.from(new Set([...prev.policy_ids, created.id])) }));
      setNewPolicy({ metric: '', limit: 0 });
      await queryClient.invalidateQueries({ queryKey: ['limit-policies', 'all'] });
    } catch { }
  };

  if (plansIsPending) {
    return (
      <DashboardLayout defaultData={adminDashboardData}>
        <div>Loading...</div>
      </DashboardLayout>
    );
  }

  if (plansIsError) {
    return (
      <DashboardLayout defaultData={adminDashboardData}>
        <div>Error loading plans</div>
      </DashboardLayout>
    );
  }


  return (
    <DashboardLayout defaultData={adminDashboardData}>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-4">
            <div>
              <CardTitle>All Plans</CardTitle>
              <CardDescription>Preview of your pricing and policy configuration.</CardDescription>
            </div>
            <Button size="sm" className='bg-purple-500 hover:bg-purple-400' onClick={onCreate}>New Plan</Button>
          </div>
        </CardHeader>

        <CardContent>

          <PlanTable plans={plans} onEdit={onEdit} onDelete={onDelete} confirmId={confirmId} onCancelDelete={cancelDelete} />
        </CardContent>
      </Card>

      <div className='flex justify-center align-center mt-4'>
        <PlanFormDialog
          open={open}
          setOpen={(v) => { if (!v) { setEditingId(null); resetForm(); } setOpen(v); }}
          editingId={editingId}
          form={form}
          setForm={setForm}
          newPolicy={newPolicy}
          setNewPolicy={setNewPolicy}
          handleSubmit={handleSubmit}
          handleCreatePolicy={handleCreatePolicy}
          resetForm={resetForm}
          policies={policiesData ?? []}
          policiesIsPending={policiesIsPending}
          policiesIsError={policiesIsError}
          createPlanPending={createPlanMutation.isPending}
          updatePlanPending={updatePlanMutation.isPending}
          createPolicyPending={createPolicyMutation.isPending}
        />
      </div>
    </DashboardLayout>
  )
}

export default PlansPage