import { apiClient } from './api-client'

export const auth = {
  isAuthenticated: () => apiClient.isAuthenticated(),

  getAccessToken: () => apiClient.getAccessToken(),

  getRefreshToken: () => apiClient.getRefreshToken(),

  logout: () => apiClient.clearTokens(),

  setTokens: (tokens: { access: string; refresh: string }) => {
    apiClient.setTokens(tokens)
  },
}
