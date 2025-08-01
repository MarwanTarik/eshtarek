# Business Context:
Eshtarek enables businesses to run subscription services without development overhead. Your mission is to prototype the core engine of our platform — supporting isolated tenant data, plan management, and subscription workflows.

# Functional Requirments
1. JWT-based auth (register/login/logout)
2. Users are stored globally across the system, but each user must be assigned to a specific tenant
3. Admin can define subscription plans (Free, Pro, etc.)
4. Tenants can subscribe to/change plans
5. Basic usage limits based on plan (e.g., max users)
6. Admin manage plans, tenants, and usage policies
7. Admin track subscriptions and active tenants
8. Simulate Stripe or billing logic (mock is fine)
9. Trigger a “subscribe now” action with plan switch
