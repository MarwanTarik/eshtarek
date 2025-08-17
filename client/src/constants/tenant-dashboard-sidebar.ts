import { IconChartBar, IconCreditCard, IconDashboard, IconUsers } from "@tabler/icons-react";

export const tenantSideBarData = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "/tenant/dashboard",
      icon: IconDashboard,
    },
    {
      title: "Billing",
      url: "/tenant/billing",
      icon: IconCreditCard,
    },
    {
      title: "Usages",
      url: "/tenant/usages",
      icon: IconChartBar,
    },
    {
      title: "Users",
      url: "/tenant/users",
      icon: IconUsers,
    },
  ],
}

