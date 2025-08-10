import type { Plan } from '@/app/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

export interface PlanTableProps {
    plans: Array<Plan>
    onEdit: (plan: Plan) => void
    onDelete: (id: string) => void
    confirmId?: string | null
    onCancelDelete?: () => void
}

export function PlanTable({ plans, onEdit, onDelete, confirmId, onCancelDelete }: PlanTableProps) {
    return (
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Billing Cycle</TableHead>
                    <TableHead>Policies</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {plans.map(plan => (
                    <TableRow key={plan.id}>
                        <TableCell>{plan.name}</TableCell>
                        <TableCell>{plan.price}</TableCell>
                        <TableCell><Badge variant="secondary">{plan.billing_cycle}</Badge></TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                            {plan.associated_policies.length ? (
                                <div className="flex flex-wrap gap-2">
                                    {plan.associated_policies.map((p, i) => (
                                        <Badge key={i} variant="outline">{p.metric}/{p.limit}</Badge>
                                    ))}
                                </div>
                            ) : (
                                <span>No policies</span>
                            )}
                        </TableCell>
                        <TableCell className="text-right space-x-2">
                            <Button className='hover:bg-gray-50' size="sm" variant="outline" onClick={() => onEdit(plan)}>Edit</Button>
                            {confirmId === plan.id ? (
                                <>
                                    <Button
                                        className='bg-red-600 hover:bg-red-500'
                                        size="sm"
                                        variant="destructive"
                                        onClick={() => onDelete(plan.id)}
                                    >
                                        Confirm Delete
                                    </Button>
                                    <Button
                                        className='hover:bg-gray-50'
                                        size="sm"
                                        variant="outline"
                                        onClick={onCancelDelete}
                                    >
                                        Cancel
                                    </Button>
                                </>
                            ) : (
                                <Button
                                    className='bg-red-500 hover:bg-red-400'
                                    size="sm"
                                    variant="destructive"
                                    onClick={() => onDelete(plan.id)}
                                >
                                    Delete
                                </Button>
                            )}
                        </TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    )
}
