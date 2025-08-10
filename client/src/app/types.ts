export enum Role {
  PLATFORM_ADMIN = 'platform_admin',
  TENANT_ADMIN = 'tenant_admin',
  TENANT_USER = 'tenant_user',
}

export enum SubscriptionsStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
  CANCELLED = 'cancelled',
}

export enum SubscriptionsBillingCycle {
  MONTHLY = 'monthly',
  ANNUALLY = 'annually',
}

// Base types
export interface BaseModel {
  id: string
  created_at: string
  updated_at: string
}

// User types
export interface User extends BaseModel {
  email: string
  name: string
  role: Role
}

export interface UserCreateRequest {
  email: string
  name: string
  password: string
  tenant_name: string
}

export interface UserUpdateRequest {
  email?: string
  name?: string
}

// Tenant types
export interface Tenant extends BaseModel {
  name: string
}

export interface TenantCreateRequest {
  name: string
}

export interface TenantUpdateRequest {
  name?: string
}

// UserTenant types
export interface UserTenant {
  user: User
  tenant: Tenant
  created_at: string
  updated_at: string
}

// LimitPolicies types
export interface LimitPolicy extends BaseModel {
  metric: string
  limit: number
  created_by: string
}

export interface LimitPolicyCreateRequest {
  metric: string
  limit: number
}

export interface LimitPolicyUpdateRequest {
  metric?: string
  limit?: number
}

// Plan types
export interface Plan extends BaseModel {
  name: string
  description: string
  billing_cycle: SubscriptionsBillingCycle
  billing_duration: number
  price: number
  associated_policies: Array<LimitPolicy>
}

export interface PlanCreateRequest {
  name: string
  description: string
  billing_cycle: SubscriptionsBillingCycle
  billing_duration: number
  price: number
  policy_ids: Array<string>
}

export interface PlanUpdateRequest {
  name?: string
  description?: string
  billing_cycle?: SubscriptionsBillingCycle
  billing_duration?: number
  price?: number
  policy_ids?: Array<string>
}

// PlanLimitPolicy types
export interface PlanLimitPolicy {
  plan: Plan
  limit_policy: LimitPolicy
  created_at: string
  updated_at: string
}

export interface PlanLimitPolicyCreateRequest {
  plan_id: string
  policy_id: string
}

// Subscription types
export interface Subscription extends BaseModel {
  plan: Plan
  tenant: Tenant
  status: SubscriptionsStatus
  started_at: string
  ended_at: string
  created_by_user_id: string
}

export interface SubscriptionCreateRequest {
  plan_id: string
}

export interface SubscriptionUpdateRequest {
  plan_id?: string
}

// Usage types
export interface Usage extends BaseModel {
  metric: string
  value: number
  subscription_id: string
}

export interface UsageCreateRequest {
  metric: string
  value: number
}

export interface UsageUpdateRequest {
  metric?: string
  value?: number
}

// Authentication types
export interface TokenResponse {
  refresh: string
  access: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenClaims {
  role: Role
  id: string
  exp: number
  iat: number
}

// Registration types
export interface UserRegistrationRequest {
  email: string
  name: string
  password: string
  tenant_name: string
}

export interface TenantRegistrationRequest {
  email: string
  name: string
  password: string
  tenant_name: string
}

export interface AdminRegistrationRequest {
  email: string
  name: string
  password: string
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
  errors?: Record<string, Array<string>>
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: Array<T>
}

// Error types
export interface ValidationError {
  field: string
  messages: Array<string>
}

export interface ApiError {
  detail?: string
  errors?: Array<ValidationError>
  non_field_errors?: Array<string>
}
