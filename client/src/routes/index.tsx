import { createFileRoute } from '@tanstack/react-router'
import LoginPage from './login'

export const Route = createFileRoute('/')({
  component: App,
})

function App() {
  return (
    <div className="bg-gray-50">
      <LoginPage />
    </div>
  )
}
