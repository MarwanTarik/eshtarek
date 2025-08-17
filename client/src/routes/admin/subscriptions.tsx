import { createFileRoute} from '@tanstack/react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { SubscriptionUpdateRequest } from '@/app/types'
import { DeleteSubscriptionMutationOptions, SubscriptionsQueryOptions, UpdateSubscriptionMutationOptions } from '@/app/subscriptions'
import { PlansQueryOptions } from '@/app/plans'
import { DashboardLayout } from '@/components/dashboard-layout'
import { Spinner } from '@/components/ui/shadcn-io/spinner';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { SubscriptionsTable } from '@/components/admin/subscriptions/subscriptions-table'
import { SubscriptionFormDialog } from '@/components/admin/subscriptions/subscription-form-dialog'
import { authGuard } from '@/guards/auth-guard'
import { adminDashboardData } from '@/constants/admin-dashboard-sidebar'

export const Route = createFileRoute('/admin/subscriptions')({
  beforeLoad: () => {
    authGuard('/admin/subscriptions');
  },
  component: AdminSubscriptionsPage,
})

function AdminSubscriptionsPage() {
  const [editingSubscriptionId, setEditingSubscriptionId] = useState<string | null>(null);
  const [form, setForm] = useState<SubscriptionUpdateRequest>({});
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const queryClient = useQueryClient();

  const {
    data: subscriptions,
    isPending: isSubscriptionPending,
    isError: isSubscriptionError,
  } = useQuery(SubscriptionsQueryOptions);

  const {
    data: plans,
    isPending: isPlansLoading,
    isError: isPlansError,
  } = useQuery(PlansQueryOptions);

  const updateSubscriptionMutation = useMutation({
    ...UpdateSubscriptionMutationOptions(editingSubscriptionId || ''),
    onSuccess: () => {
      setEditingSubscriptionId(null);
      setForm({});
      queryClient.invalidateQueries(SubscriptionsQueryOptions);
    },
    onError: (error) => {
      console.error('Error updating subscription:', error);
      // TODO: Add toast notification
    },
  });

  const deleteSubscriptionMutation = useMutation({
    ...DeleteSubscriptionMutationOptions(confirmDeleteId || ''),
    onSuccess: () => {
      setConfirmDeleteId(null);
      queryClient.invalidateQueries(SubscriptionsQueryOptions);
    },
    onError: (error) => {
      console.error('Error deleting subscription:', error);
      // TODO: Add toast notification
    },
  });


  const onEditSubscription = (id: string, newSubscriptionData: SubscriptionUpdateRequest) => {
    setEditingSubscriptionId(id);
    setForm(newSubscriptionData);
  }

  const onSubmitEdit = async (formData: SubscriptionUpdateRequest) => {
    if (!editingSubscriptionId) return;

    try {
      await updateSubscriptionMutation.mutateAsync(formData);
    } catch (error) {
      // Error handled in mutation options
    }
  }

  const onCancelEdit = () => {
    setEditingSubscriptionId(null);
    setForm({});
  }

  const onInitiateDelete = (id: string) => {
    setConfirmDeleteId(id);
  }

  const onConfirmDelete = async () => {
    if (!confirmDeleteId) return;

    try {
      await deleteSubscriptionMutation.mutateAsync();
    } catch (error) {
      // Error handled in mutation options
    }
  }

  const onCancelDelete = () => {
    setConfirmDeleteId(null);
  }


  if (isSubscriptionPending || isPlansLoading) {
    return <Spinner className='absolute inset-0 m-auto' variant='circle' />;
  }

  if (isSubscriptionError || isPlansError) {
    return <div>Error loading data</div>;
  }


  return (
    <DashboardLayout defaultData={adminDashboardData}>
      <div>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between gap-4">
              <div>
                <CardTitle>All Subscriptions</CardTitle>
                <CardDescription>Manage tenant subscriptions and their status.</CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            <SubscriptionsTable
              subscriptions={subscriptions}
              onEditSubscription={onEditSubscription}
              onDeleteSubscription={onInitiateDelete}
              onConfirmDelete={onConfirmDelete}
              confirmId={confirmDeleteId}
              onCancelEdit={onCancelDelete} />
          </CardContent>
        </Card>

        <SubscriptionFormDialog
          open={!!editingSubscriptionId}
          onClose={onCancelEdit}
          form={form}
          setForm={setForm}
          handleSubmit={onSubmitEdit}
          plans={plans} />
      </div>
    </DashboardLayout>
  )
}
