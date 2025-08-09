import { mutationOptions, queryOptions } from '@tanstack/react-query'
import type {
  Plan,
  PlanCreateRequest,
  PlanUpdateRequest,
} from './types'
import { apiClient } from '@/lib/api-client'

export const PlansMutationOptions = mutationOptions<
  Plan,
  Error,
  PlanCreateRequest
>({
  mutationKey: ['plans', 'create'],
  mutationFn: async (plan) => {
    return await apiClient.post<Plan>('/api/plans', plan)
  },
})

export const PlansQueryOptions = queryOptions<Array<Plan>, Error>({
  queryKey: ['plans', 'all'],
  queryFn: async () => {
    return await apiClient.get<Array<Plan>>('/api/plans')
  },
})

export const PlanQueryOptions = (planId: string) =>
  queryOptions<Plan, Error>({
    queryKey: ['plans', planId],
    queryFn: async () => {
      return await apiClient.get<Plan>(`/api/plans/${planId}`)
    },
  })

export const UpdatePlanMutationOptions = (planId: string) =>
  mutationOptions<Plan, Error, PlanUpdateRequest>({
    mutationKey: ['plans', 'update'],
    mutationFn: async (data) => {
      return await apiClient.put<Plan>(
        `/api/plans/${planId}`,
        data,
      )
    },
  })

export const DeletePlanMutationOptions = (planId: string) =>
  mutationOptions<null, Error>({
    mutationKey: ['plans', 'delete'],
    mutationFn: async () => {
      return await apiClient.delete(`/api/plans/${planId}`)
    },
  })
