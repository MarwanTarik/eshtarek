import { mutationOptions } from '@tanstack/react-query'
import type {
  AdminRegistrationRequest,
  ApiResponse,
  LoginRequest,
  TenantRegistrationRequest,
  TokenResponse,
} from './types'
import { apiClient } from '@/lib/api-client'

export const AdminRegistrationMutationOptions = mutationOptions<
  TokenResponse,
  Error,
  AdminRegistrationRequest
>({
  mutationKey: ['auth', 'admin'],
  mutationFn: async (request) => {
    const response = await apiClient.post<TokenResponse>(
      '/api/admin/auth/register',
      request,
    )
    apiClient.setTokens(response)
    return response
  },
})

export const TenantRegistrationMutationOptions = mutationOptions<
  TokenResponse,
  Error,
  TenantRegistrationRequest
>({
  mutationKey: ['auth', 'tenant'],
  mutationFn: async (request) => {
    const response = await apiClient.post<TokenResponse>(
      '/api/tenant/auth/register',
      request,
    )
    apiClient.setTokens(response)
    return response
  },
})

export const LogoutMutationOptions = mutationOptions<
  ApiResponse<null>,
  Error,
  null
>({
  mutationKey: ['auth', 'logout'],
  mutationFn: async () => {
    const response = await apiClient.post<ApiResponse<null>>('/api/auth/logout')
    apiClient.clearTokens()
    return response
  },
})

export const LoginMutationOptions = mutationOptions<
  TokenResponse,
  Error,
  LoginRequest
>({
  mutationKey: ['auth', 'login'],
  mutationFn: async (request) => {
    const response = await apiClient.post<TokenResponse>(
      '/api/auth/login',
      request,
    )
    apiClient.setTokens(response)
    return response
  },
})
