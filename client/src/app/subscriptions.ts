import { mutationOptions, queryOptions } from '@tanstack/react-query'
import type {
  Subscription,
  SubscriptionCreateRequest,
  SubscriptionUpdateRequest,
} from './types'
import { apiClient } from '@/lib/api-client'

export const SubscriptionsQueryOptions = queryOptions<
  Array<Subscription>,
  Error
>({
  queryKey: ['subscriptions', 'all'],
  queryFn: async () => {
    return await apiClient.get<Array<Subscription>>(
      '/api/subscriptions',
    )
  },
})

export const SubscriptionQueryOptions = (subscriptionId: string) =>
  queryOptions<Subscription, Error>({
    queryKey: ['subscriptions', subscriptionId],
    queryFn: async () => {
      return await apiClient.get<Subscription>(
        `/api/subscriptions/${subscriptionId}`,
      )
    },
  })

export const CreateSubscriptionMutationOptions = mutationOptions<
  Subscription,
  Error,
  SubscriptionCreateRequest
>({
  mutationKey: ['subscriptions', 'create'],
  mutationFn: async (subscription) => {
    return await apiClient.post<Subscription>(
      '/api/subscriptions',
      subscription,
    )
  },
})

export const UpdateSubscriptionMutationOptions = (subscriptionId: string) =>
  mutationOptions<Subscription, Error, SubscriptionUpdateRequest>({
    mutationKey: ['subscriptions', 'update'],
    mutationFn: async (data) => {
      return await apiClient.put<Subscription>(
        `/api/subscriptions/${subscriptionId}`,
        data,
      )
    },
  })

export const DeleteSubscriptionMutationOptions = (subscriptionId: string) =>
  mutationOptions<null, Error>({
    mutationKey: ['subscriptions', 'delete'],
    mutationFn: async () => {
      return await apiClient.delete<null>(
        `/api/subscriptions/${subscriptionId}`,
      )
    },
  })
