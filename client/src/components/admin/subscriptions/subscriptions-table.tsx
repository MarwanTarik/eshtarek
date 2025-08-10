import type { Subscription, SubscriptionUpdateRequest } from "@/app/types";
import type { Column, ColumnDef, Row } from "@tanstack/react-table";
import {
  TableBody,
  TableCell,
  TableColumnHeader,
  TableHead,
  TableHeader,
  TableHeaderGroup,
  TableProvider,
  TableRow,
} from '@/components/ui/shadcn-io/table';

export interface SubscriptionsTableProps {
  onEditSubscription: (id: string, newSubscriptionData: SubscriptionUpdateRequest) => void;
  onCancelEdit: () => void;
  onDeleteSubscription: (id: string) => void;
  onConfirmDelete: () => void;
  subscriptions: Array<Subscription>;
  confirmId?: string | null;
}

export function SubscriptionsTable({ onEditSubscription, onCancelEdit, onDeleteSubscription, onConfirmDelete, subscriptions, confirmId }: SubscriptionsTableProps) {
  const columns: Array<ColumnDef<Subscription>> = [
    {
      accessorKey: 'id',
      header: ({ column }: { column: Column<Subscription> }) => (
        <TableColumnHeader column={column} title="ID" />
      ),
      cell: ({ row }: { row: Row<Subscription> }) => row.original.id,
    },
    {
      accessorKey: 'userId',
      header: ({ column }: { column: Column<Subscription> }) => (
        <TableColumnHeader column={column} title="User ID" />
      ),
      cell: ({ row }: { row: Row<Subscription> }) => row.original.created_by_user_id,
    },
    {
      accessorKey: 'plan',
      header: ({ column }: { column: Column<Subscription> }) => (
        <TableColumnHeader column={column} title="Plan" />
      ),
      cell: ({ row }: { row: Row<Subscription> }) => row.original.plan.name,
    },
    {
      accessorKey: 'tenantId',
      header: ({ column }: { column: Column<Subscription> }) => (
        <TableColumnHeader column={column} title="Tenant ID" />
      ),
      cell: ({ row }: { row: Row<Subscription> }) => row.original.tenant.id,
    },
    {
      accessorKey: 'status',
      header: ({ column }: { column: Column<Subscription> }) => (
        <TableColumnHeader column={column} title="Status" />
      ),
      cell: ({ row }: { row: Row<Subscription> }) => row.original.status,
    },
    {
      accessorKey: 'createdAt',
      header: ({ column }: { column: Column<Subscription> }) => (
        <TableColumnHeader column={column} title="Created At" />
      ),
      cell: ({ row }: { row: Row<Subscription> }) => row.original.created_at,
    },
    {
      accessorKey: 'updatedAt',
      header: ({ column }: { column: Column<Subscription> }) => (
        <TableColumnHeader column={column} title="Updated At" />
      ),
      cell: ({ row }: { row: Row<Subscription> }) => row.original.updated_at,
    },
    {
      accessorKey: 'actions',
      header: ({ column }: { column: Column<Subscription> }) => (
        <TableColumnHeader column={column} title="Actions" />
      ),
      cell: ({ row }: { row: Row<Subscription> }) => (
        <div>
          <button className='btn btn-primary' onClick={() => onEditSubscription(row.original.id, { plan_id: row.original.plan.id })}>Edit</button>
          {
            (confirmId === row.original.id) ? (
              <div className='flex gap-2'>
                <button className='btn btn-danger' onClick={() => onConfirmDelete()}>Confirm Delete</button>
                <button className='btn btn-secondary' onClick={onCancelEdit}>Cancel</button>
              </div>
            ) : (
              <button className='btn btn-danger' onClick={() => onDeleteSubscription(row.original.id)}>Delete</button>
            )
          }
        </div>
      ),
    }
  ]

  return (
    <TableProvider columns={columns} data={subscriptions}>
      <TableHeader>
        {({ headerGroup }) => (
          <TableHeaderGroup headerGroup={headerGroup} key={headerGroup.id}>
            {({ header }) => <TableHead header={header} key={header.id} />}
          </TableHeaderGroup>
        )}
      </TableHeader>
      <TableBody>
        {({ row }) => (
          <TableRow key={row.id} row={row}>
            {({ cell }) => <TableCell cell={cell} key={cell.id} />}
          </TableRow>
        )}
      </TableBody>
    </TableProvider>
  );
}
