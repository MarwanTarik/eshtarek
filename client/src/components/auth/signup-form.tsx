import { useState } from 'react'
import { Link, useRouter } from '@tanstack/react-router'
import { useAuth } from '@/hooks/use-auth'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Role } from '@/app/types'

interface FieldConfig {
  name: string
  type: string
  label: string
  placeholder?: string
}

const roleFieldMap: Record<
  Role.TENANT_ADMIN | Role.PLATFORM_ADMIN,
  Array<FieldConfig>
> = {
  [Role.TENANT_ADMIN]: [
    {
      name: 'tenant_name',
      type: 'text',
      label: 'Tenant Name',
      placeholder: 'tenant name',
    },
    {
      name: 'email',
      type: 'email',
      label: 'Email',
      placeholder: 'm@domain.com',
    },
    { name: 'name', type: 'text', label: 'Name', placeholder: 'username' },
    {
      name: 'password',
      type: 'password',
      label: 'Password',
      placeholder: 'password',
    },
  ],
  [Role.PLATFORM_ADMIN]: [
    {
      name: 'email',
      type: 'email',
      label: 'Email',
      placeholder: 'm@domain.com',
    },
    { name: 'name', type: 'text', label: 'Name', placeholder: 'username' },
    {
      name: 'password',
      type: 'password',
      label: 'Password',
      placeholder: 'password',
    },
  ],
}

export function SignupForm({
  className,
  ...props
}: React.ComponentProps<'div'>) {
  const router = useRouter()
  const { signup, isLoading } = useAuth()
  const [role, setRole] = useState<Role.TENANT_ADMIN | Role.PLATFORM_ADMIN>(
    Role.TENANT_ADMIN,
  )
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [signupError, setSignupError] = useState<string | null>(null)

  const fields = roleFieldMap[role]

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }))
    }
  }

  const handleRoleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newRole = e.target.value as Role.TENANT_ADMIN | Role.PLATFORM_ADMIN
    setRole(newRole)
    setFormData({})
    setErrors({})
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    fields.forEach((field) => {
      const value = formData[field.name] || ''

      if (!value.trim()) {
        newErrors[field.name] = `${field.label} is required`
      } else if (field.type === 'email' && !/\S+@\S+\.\S+/.test(value)) {
        newErrors[field.name] = 'Email is invalid'
      } else if (field.name === 'password' && value.length < 6) {
        newErrors[field.name] = 'Password must be at least 6 characters'
      }
    })

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      setSignupError(null)
      await signup(formData, role)
      console.log('Registration successful')
      router.navigate({ to: '/login' })
    } catch (error) {
      console.error('Registration failed:', error)
      setSignupError('Registration failed. Please check your information and try again.')
    }
  }

  return (
    <div className={cn('flex flex-col gap-6', className)} {...props}>
      <Card className="border-none shadow-none">
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-6">
              <div className="grid gap-6">
                <div className="grid gap-3">
                  <Label htmlFor="role">Account Type</Label>
                  <select
                    id="role"
                    value={role}
                    onChange={handleRoleChange}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
                    disabled={isLoading}
                  >
                    <option value={Role.TENANT_ADMIN}>Tenant Admin</option>
                    <option value={Role.PLATFORM_ADMIN}>Platform Admin</option>
                  </select>
                </div>

                {fields.map((field) => (
                  <div key={field.name} className="grid gap-3">
                    <Label htmlFor={field.name}>{field.label}</Label>
                    <Input
                      id={field.name}
                      name={field.name}
                      type={field.type}
                      placeholder={field.placeholder}
                      value={formData[field.name] || ''}
                      onChange={handleChange}
                      required
                      disabled={isLoading}
                    />
                    {errors[field.name] && (
                      <span className="text-sm text-red-500">
                        {errors[field.name]}
                      </span>
                    )}
                  </div>
                ))}

                {signupError && (
                  <div className="text-sm text-red-500">
                    {signupError}
                  </div>
                )}

                <Button
                  type="submit"
                  className="w-full bg-purple-500 hover:bg-purple-400"
                  disabled={isLoading}
                >
                  {isLoading
                    ? 'Creating account...'
                    : 'Create account'}
                </Button>
              </div>
              <div className="text-center text-sm">
                Already have an account?{' '}
                <Link to='/login' className="underline underline-offset-4">
                  Login
                </Link>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
      <div className="text-muted-foreground *:[a]:hover:text-primary text-center text-xs text-balance *:[a]:underline *:[a]:underline-offset-4">
        By clicking continue, you agree to our <a href="#">Terms of Service</a>{' '}
        and <a href="#">Privacy Policy</a>.
      </div>
    </div>
  )
}
