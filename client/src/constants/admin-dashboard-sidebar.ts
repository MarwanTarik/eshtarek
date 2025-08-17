import { IconChartBar, IconDashboard, IconListDetails, IconUsers } from "@tabler/icons-react";

export const adminDashboardData = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "/admin/dashboard",
      icon: IconDashboard,
    },
    {
      title: "Plans",
      url: "/admin/plans",
      icon: IconListDetails,
    },
    {
      title: "Usages",
      url: "/admin/usages",
      icon: IconChartBar,
    },
    {
      title: "Subscriptions",
      url: "/admin/subscriptions",
      icon: IconUsers,
    },
  ],
}
