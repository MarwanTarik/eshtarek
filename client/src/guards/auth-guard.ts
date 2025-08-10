import { redirect } from "@tanstack/react-router"
import { Role } from "@/app/types"
import { auth } from "@/lib/auth"

export function authGuard (route: string) {
  if (!auth.isAuthenticated()) {
    throw redirect({
      to: '/login',
      search: {
        redirect: route,
      },
    })
  }

  const token = auth.getRefreshToken()
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const userRole = payload.role

      if (userRole !== Role.PLATFORM_ADMIN) {
        throw redirect({
          to: '/',
        })
      }
    } catch (error) {
      auth.logout()
      throw redirect({
        to: '/login',
      })
    }
  }
}