import { Dialog, DialogContent, DialogOverlay, DialogTitle } from '@radix-ui/react-dialog'
import type { LimitPolicyCreateRequest, PlanCreateRequest } from '@/app/types';
import { SubscriptionsBillingCycle } from '@/app/types'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'

interface PlanFormDialogProps {
    open: boolean
    setOpen: (v: boolean) => void
    editingId: string | null
    form: PlanCreateRequest
    setForm: React.Dispatch<React.SetStateAction<PlanCreateRequest>>
    newPolicy: LimitPolicyCreateRequest
    setNewPolicy: React.Dispatch<React.SetStateAction<LimitPolicyCreateRequest>>
    handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void
    handleCreatePolicy: (e: React.FormEvent) => void
    resetForm: () => void
    policies: Array<{ id: string; metric: string; limit: number }>
    policiesIsPending: boolean
    policiesIsError: boolean
    createPlanPending: boolean
    updatePlanPending: boolean
    createPolicyPending: boolean
}

export function PlanFormDialog({
    open,
    setOpen,
    editingId,
    form,
    setForm,
    newPolicy,
    setNewPolicy,
    handleSubmit,
    handleCreatePolicy,
    resetForm,
    policies,
    policiesIsPending,
    policiesIsError,
    createPlanPending,
    updatePlanPending,
    createPolicyPending,
}: PlanFormDialogProps) {
    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogOverlay className="fixed inset-0 5black/50 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
            <DialogContent className="max-w-2xl  z-[60] shadow-2xl rounded-lg p-6 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0">
                <DialogTitle>{editingId ? 'Edit Plan' : 'Create Plan'}</DialogTitle>
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid gap-4 sm:grid-cols-2">
                        <div className="space-y-1.5">
                            <Label>Plan Name</Label>
                            <Input
                                placeholder="Plan Name"
                                value={form.name}
                                onChange={(e) => setForm({ ...form, name: e.target.value })}
                            />
                        </div>
                        <div className="space-y-1.5">
                            <Label>Price</Label>
                            <Input
                                type="number"
                                placeholder="Price"
                                value={form.price}
                                onChange={(e) => setForm({ ...form, price: parseFloat(e.target.value) })}
                            />
                        </div>
                        <div className="space-y-1.5 sm:col-span-2">
                            <Label>Description</Label>
                            <Input
                                placeholder="Description"
                                value={form.description}
                                onChange={(e) => setForm({ ...form, description: e.target.value })}
                            />
                        </div>



                        <div className="space-y-1.5">
                            <Label>Billing Duration {form.billing_cycle === SubscriptionsBillingCycle.MONTHLY ? '(months)' : '(years)'}</Label>
                            <Input
                                type="number"
                                placeholder="Billing Duration"
                                value={form.billing_duration}
                                onChange={(e) => setForm({ ...form, billing_duration: parseInt(e.target.value) })}
                            />
                        </div>

                        <div className="space-y-1.5 ">
                            <Label>Billing Cycle</Label>
                            <Select
                                value={form.billing_cycle}
                                onValueChange={(value) => setForm({ ...form, billing_cycle: value as SubscriptionsBillingCycle })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a billing cycle" />
                                </SelectTrigger>
                                <SelectContent className='z-[9999]'>
                                    <SelectItem value={SubscriptionsBillingCycle.MONTHLY}>Monthly</SelectItem>
                                    <SelectItem value={SubscriptionsBillingCycle.ANNUALLY}>Yearly</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2 sm:col-span-2">
                            <Label>Attach Limit Policies</Label>
                            <div className="border rounded-md p-3 max-h-48 overflow-auto space-y-2">
                                {policiesIsPending && <div className="text-sm text-muted-foreground">Loading policies...</div>}
                                {policiesIsError && <div className="text-sm text-destructive">Error loading policies</div>}
                                {!policiesIsPending && !policiesIsError && (policies.length ? (
                                    policies.map(p => {
                                        const checked = form.policy_ids.includes(p.id)
                                        return (
                                            <label key={p.id} className="flex items-center gap-2 text-sm cursor-pointer">
                                                <Checkbox
                                                    checked={checked}
                                                    onCheckedChange={(val) => {
                                                        setForm(prev => ({
                                                            ...prev,
                                                            policy_ids: val ? [...prev.policy_ids, p.id] : prev.policy_ids.filter(id => id !== p.id)
                                                        }))
                                                    }}
                                                />
                                                <span>{p.metric} / {p.limit}</span>
                                            </label>
                                        )
                                    })
                                ) : (
                                    <div className="text-sm text-muted-foreground">No policies yet.</div>
                                ))}
                            </div>
                        </div>
                        <div className="space-y-2 sm:col-span-2 border rounded-md p-3">
                            <Label className="text-sm font-medium">Create & attach new policy</Label>
                            <div className="flex flex-col sm:flex-row gap-2">
                                <Input
                                    placeholder="Metric"
                                    value={newPolicy.metric}
                                    onChange={(e) => setNewPolicy(p => ({ ...p, metric: e.target.value }))}
                                />
                                <Input
                                    type="number"
                                    placeholder="Limit"
                                    value={newPolicy.limit}
                                    onChange={(e) => setNewPolicy(p => ({ ...p, limit: parseInt(e.target.value) }))}
                                />
                                <Button type="button" className='bg-purple-500 hover:bg-purple-400'  size="sm" onClick={handleCreatePolicy} disabled={createPolicyPending}>
                                    {createPolicyPending ? 'Adding...' : 'Add'}
                                </Button>
                            </div>
                        </div>
                    </div>
                    <div className="flex justify-end gap-2">
                        <Button type="button" variant="outline"  onClick={() => { setOpen(false); /* editingId state managed above */ resetForm(); }}>Cancel</Button>
                        <Button type="submit" className='bg-purple-500 hover:bg-purple-400' disabled={createPlanPending || updatePlanPending}>
                            {editingId ? (updatePlanPending ? 'Saving...' : 'Save Changes') : (createPlanPending ? 'Creating...' : 'Create Plan')}
                        </Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    )
}
