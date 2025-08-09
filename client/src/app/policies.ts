import { mutationOptions, queryOptions } from '@tanstack/react-query'
import type {
  LimitPolicy,
  LimitPolicyCreateRequest,
  LimitPolicyUpdateRequest,
} from './types'
import { apiClient } from '@/lib/api-client'

export const LimitPoliciesQueryOptions = queryOptions<
  Array<LimitPolicy>,
  Error
>({
  queryKey: ['limit-policies', 'all'],
  queryFn: async () => {
    return await apiClient.get<Array<LimitPolicy>>(
      '/api/limit-policies',
    )
  },
})

export const LimitPolicyQueryOptions = (policyId: string) =>
  queryOptions<LimitPolicy, Error>({
    queryKey: ['limit-policies', policyId],
    queryFn: async () => {
      return await apiClient.get<LimitPolicy>(
        `/api/limit-policies/${policyId}`,
      )
    },
  })

export const CreateLimitPolicyMutationOptions = mutationOptions<
  LimitPolicy,
  Error,
  LimitPolicyCreateRequest
>({
  mutationKey: ['limit-policies', 'create'],
  mutationFn: async (policy) => {
    return await apiClient.post<LimitPolicy>(
      '/api/limit-policies',
      policy,
    )
  },
})

export const UpdateLimitPolicyMutationOptions = (policyId: string) =>
  mutationOptions<LimitPolicy, Error, LimitPolicyUpdateRequest>({
    mutationKey: ['limit-policies', 'update'],
    mutationFn: async (data) => {
      return await apiClient.put<LimitPolicy>(
        `/api/limit-policies/${policyId}`,
        data,
      )
    },
  })

export const DeleteLimitPolicyMutationOptions = (policyId: string) =>
  mutationOptions<null, Error>({
    mutationKey: ['limit-policies', 'delete'],
    mutationFn: async () => {
      return await apiClient.delete(`/api/limit-policies/${policyId}`)
    },
  })
