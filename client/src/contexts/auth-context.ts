import { createContext } from "react";
import type { Role } from "@/app/types";

interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: any, role: Role) => Promise<void>;
  logout: () => void;
  getAccessToken: () => string | null;
  getRefreshToken: () => string | null;
  setTokens: (tokens: { access: string; refresh: string }) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export default AuthContext;