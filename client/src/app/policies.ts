import { mutationOptions, queryOptions } from '@tanstack/react-query'
import type {
  ApiResponse,
  LimitPolicy,
  LimitPolicyCreateRequest,
  LimitPolicyUpdateRequest,
} from './types'
import { apiClient } from '@/lib/api-client'

export const LimitPoliciesQueryOptions = queryOptions<
  ApiResponse<Array<LimitPolicy>>,
  Error
>({
  queryKey: ['limit-policies', 'all'],
  queryFn: async () => {
    return await apiClient.get<ApiResponse<Array<LimitPolicy>>>(
      '/api/limit-policies',
    )
  },
})

export const LimitPolicyQueryOptions = (policyId: string) =>
  queryOptions<ApiResponse<LimitPolicy>, Error>({
    queryKey: ['limit-policies', policyId],
    queryFn: async () => {
      return await apiClient.get<ApiResponse<LimitPolicy>>(
        `/api/limit-policies/${policyId}`,
      )
    },
  })

export const CreateLimitPolicyMutationOptions = mutationOptions<
  ApiResponse<LimitPolicy>,
  Error,
  LimitPolicyCreateRequest
>({
  mutationKey: ['limit-policies', 'create'],
  mutationFn: async (policy) => {
    return await apiClient.post<ApiResponse<LimitPolicy>>(
      '/api/limit-policies',
      policy,
    )
  },
})

export const UpdateLimitPolicyMutationOptions = (policyId: string) =>
  mutationOptions<ApiResponse<LimitPolicy>, Error, LimitPolicyUpdateRequest>({
    mutationKey: ['limit-policies', 'update'],
    mutationFn: async (data) => {
      return await apiClient.put<ApiResponse<LimitPolicy>>(
        `/api/limit-policies/${policyId}`,
        data,
      )
    },
  })

export const DeleteLimitPolicyMutationOptions = (policyId: string) =>
  mutationOptions<ApiResponse<null>, Error>({
    mutationKey: ['limit-policies', 'delete'],
    mutationFn: async () => {
      return await apiClient.delete<ApiResponse<null>>(
        `/api/limit-policies/${policyId}`,
      )
    },
  })
