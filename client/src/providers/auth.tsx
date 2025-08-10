import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import type { ReactNode } from "react";
import type { User } from "@/app/types";
import { Role } from "@/app/types";
import { auth } from "@/lib/auth";
import {
  AdminRegistrationMutationOptions,
  LoginMutationOptions,
  TenantRegistrationMutationOptions,
} from "@/app/authentication";
import AuthContext from "@/contexts/auth-context";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const loginMutation = useMutation(LoginMutationOptions)
  const adminSignupMutation = useMutation(AdminRegistrationMutationOptions)
  const tenantSignupMutation = useMutation(TenantRegistrationMutationOptions)
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = () => {
    try {
      if (auth.isAuthenticated()) {
        const token = auth.getRefreshToken();

        if (!token) {
          auth.logout();
          return;
        }

        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser({
          id: payload.id || payload.user_id || '',
          email: payload.email,
          name: payload.name,
          role: payload.role,
          created_at: payload.created_at || new Date().toISOString(),
          updated_at: payload.updated_at || new Date().toISOString(),
        });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      auth.logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await loginMutation.mutateAsync({ email, password });

      const token = response.access
      const payload = JSON.parse(atob(token.split('.')[1]))

      setUser({
        id: payload.id || payload.user_id || '',
        email: payload.email,
        name: payload.name,
        role: payload.role,
        created_at: payload.created_at || new Date().toISOString(),
        updated_at: payload.updated_at || new Date().toISOString(),
      });

      auth.setTokens({
        access: response.access,
        refresh: response.refresh,
      });
    }
    finally {
      setIsLoading(false);
    }
  };

  const signup = async (data: any, role: Role) => {
    setIsLoading(true);
    try {
      let response;
      if (role === Role.PLATFORM_ADMIN) {
        response = await adminSignupMutation.mutateAsync(data);
      } else if (role === Role.TENANT_ADMIN) {
        response = await tenantSignupMutation.mutateAsync(data);
      } else {
        throw new Error('Invalid role for signup');
      }

      // After successful signup, you might want to automatically log in the user
      // or redirect them to login page. For now, we'll just handle the success.
      console.log('Signup successful:', response);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    auth.logout();
    setUser(null);
  };

  const value = {
    user,
    isLoading,
    isAuthenticated: auth.isAuthenticated(),
    login,
    signup,
    logout,
    getAccessToken: auth.getAccessToken,
    getRefreshToken: auth.getRefreshToken,
    setTokens: (tokens: { access: string; refresh: string }) => {
      auth.setTokens(tokens);
      checkAuthStatus();
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
