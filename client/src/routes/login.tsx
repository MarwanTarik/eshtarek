import { createFileRoute } from '@tanstack/react-router'
import { LoginForm } from '@/components/auth/login-form'
import { Card, CardContent } from '@/components/ui/card'

export const Route = createFileRoute('/login')({
  component: LoginPage,
})

function LoginPage() {
  return (
    <div className="bg-gray-50 flex justify-center items-center min-h-screen min-w-screen">
      <Card className="w-full max-w-md p-6 shadow-lg">
        <CardContent className="flex-col">
          <h1 className="text-2xl font-bold mb-4 text-purple-500 text-center">
            Eshtarek
          </h1>
          <LoginForm />
        </CardContent>
      </Card>
    </div>
  )
}

export default LoginPage