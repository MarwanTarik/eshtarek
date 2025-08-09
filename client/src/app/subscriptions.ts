import { mutationOptions, queryOptions } from '@tanstack/react-query'
import type {
  ApiResponse,
  Subscription,
  SubscriptionCreateRequest,
  SubscriptionUpdateRequest,
} from './types'
import { apiClient } from '@/lib/api-client'

export const SubscriptionsQueryOptions = queryOptions<
  ApiResponse<Array<Subscription>>,
  Error
>({
  queryKey: ['subscriptions', 'all'],
  queryFn: async () => {
    return await apiClient.get<ApiResponse<Array<Subscription>>>(
      '/api/subscriptions',
    )
  },
})

export const SubscriptionQueryOptions = (subscriptionId: string) =>
  queryOptions<ApiResponse<Subscription>, Error>({
    queryKey: ['subscriptions', subscriptionId],
    queryFn: async () => {
      return await apiClient.get<ApiResponse<Subscription>>(
        `/api/subscriptions/${subscriptionId}`,
      )
    },
  })

export const CreateSubscriptionMutationOptions = mutationOptions<
  ApiResponse<Subscription>,
  Error,
  SubscriptionCreateRequest
>({
  mutationKey: ['subscriptions', 'create'],
  mutationFn: async (subscription) => {
    return await apiClient.post<ApiResponse<Subscription>>(
      '/api/subscriptions',
      subscription,
    )
  },
})

export const UpdateSubscriptionMutationOptions = (subscriptionId: string) =>
  mutationOptions<ApiResponse<Subscription>, Error, SubscriptionUpdateRequest>({
    mutationKey: ['subscriptions', 'update'],
    mutationFn: async (data) => {
      return await apiClient.put<ApiResponse<Subscription>>(
        `/api/subscriptions/${subscriptionId}`,
        data,
      )
    },
  })

export const DeleteSubscriptionMutationOptions = (subscriptionId: string) =>
  mutationOptions<ApiResponse<null>, Error>({
    mutationKey: ['subscriptions', 'delete'],
    mutationFn: async () => {
      return await apiClient.delete<ApiResponse<null>>(
        `/api/subscriptions/${subscriptionId}`,
      )
    },
  })
