import { mutationOptions, queryOptions } from '@tanstack/react-query'
import type {
  ApiResponse,
  Plan,
  PlanCreateRequest,
  PlanUpdateRequest,
} from './types'
import { apiClient } from '@/lib/api-client'

export const PlansMutationOptions = mutationOptions<
  ApiResponse<Plan>,
  Error,
  PlanCreateRequest
>({
  mutationKey: ['plans', 'create'],
  mutationFn: async (plan) => {
    return await apiClient.post<ApiResponse<Plan>>('/api/plans', plan)
  },
})

export const PlansQueryOptions = queryOptions<ApiResponse<Array<Plan>>, Error>({
  queryKey: ['plans', 'all'],
  queryFn: async () => {
    return await apiClient.get<ApiResponse<Array<Plan>>>('/api/plans')
  },
})

export const PlanQueryOptions = (planId: string) =>
  queryOptions<ApiResponse<Plan>, Error>({
    queryKey: ['plans', planId],
    queryFn: async () => {
      return await apiClient.get<ApiResponse<Plan>>(`/api/plans/${planId}`)
    },
  })

export const UpdatePlanMutationOptions = (planId: string) =>
  mutationOptions<ApiResponse<Plan>, Error, PlanUpdateRequest>({
    mutationKey: ['plans', 'update'],
    mutationFn: async (data) => {
      return await apiClient.put<ApiResponse<Plan>>(
        `/api/plans/${planId}`,
        data,
      )
    },
  })

export const DeletePlanMutationOptions = (planId: string) =>
  mutationOptions<ApiResponse<null>, Error>({
    mutationKey: ['plans', 'delete'],
    mutationFn: async () => {
      return await apiClient.delete<ApiResponse<null>>(`/api/plans/${planId}`)
    },
  })
