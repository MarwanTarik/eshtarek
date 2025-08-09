import { createFileRoute } from '@tanstack/react-router'
import { Card, CardContent } from '@/components/ui/card'
import { SignupForm } from '@/components/signup-form'

export const Route = createFileRoute('/signup')({
  component: SignupPage,
})

function SignupPage() {
  return (
    <div className="bg-gray-50 flex justify-center items-center min-h-screen min-w-screen">
      <Card className="w-full max-w-md p-6 shadow-lg">
        <CardContent className="flex-col">
          <h1 className="text-2xl font-bold mb-4 text-purple-500 text-center">
            Eshtarek
          </h1>
          <SignupForm />
        </CardContent>
      </Card>
    </div>
  )
}
