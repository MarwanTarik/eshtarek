# Row Level Security (RLS) Implementation Guide

## Overview

This implementation provides comprehensive Row Level Security (RLS) for the application based on **tenant isolation** and **user roles**. The system ensures that users can only access data they are authorized to see and modify based on their role and tenant membership.

## User Roles

### 1. Platform Admin (`platform_admin`)
- **Full system access** - can see and manage all data
- Can create and manage:
  - All users and tenants
  - Plans and limit policies
  - All subscriptions and usages
- Can impersonate other users for testing
- Bypasses most tenant-based restrictions

### 2. Tenant Admin (`tenant_admin`)
- **Tenant-scoped access** - can only see data for their tenant(s)
- Can manage:
  - Users within their tenant(s)
  - Subscriptions for their tenant(s)
  - Change plans for their tenant(s)
- Cannot create plans or limit policies
- Cannot access other tenants' data

### 3. Tenant User (`tenant_user`)
- **Read-only tenant access** - can only view data for their tenant(s)
- Can see:
  - Other users in their tenant(s)
  - Plans (all plans are visible)
  - Subscriptions for their tenant(s)
  - Usage data for their tenant(s)
- Cannot create or modify most data

## RLS Policy Summary

### Users Table
- **Platform admins**: See all users
- **Others**: See only users in their tenant(s) + themselves
- **Modifications**: Only platform admins can create/delete users; users can update themselves

### Tenants Table
- **Platform admins**: See all tenants
- **Others**: See only their tenant(s)
- **Modifications**: Only platform admins can manage tenants

### Plans & Limit Policies Tables
- **All users**: Can view all plans and limit policies
- **Modifications**: Only platform admins can create/modify

### Subscriptions Table
- **Platform admins**: See all subscriptions
- **Others**: See only subscriptions for their tenant(s)
- **Modifications**: Platform admins and tenant admins can manage

### Usages Table
- **Platform admins**: See all usage data
- **Others**: See only usage for their tenant subscriptions
- **Modifications**: Users in tenant can update usage data

## Setup Instructions

### 1. Database Migration

Run the RLS migration to enable policies:

```bash
cd server
python manage.py migrate
```

### 2. Create Initial Users

Use the management command to create your first platform admin:

```bash
# Create a platform admin
python manage.py rls_admin --action create_platform_admin \
    --email "admin@example.com" \
    --name "Platform Administrator"

# Create a tenant and tenant admin
python manage.py rls_admin --action create_tenant_admin \
    --email "tenant1@example.com" \
    --name "Tenant 1 Admin" \
    --tenant_name "Tenant One"

# Create a regular tenant user
python manage.py rls_admin --action create_tenant_user \
    --email "user1@example.com" \
    --name "Tenant 1 User" \
    --tenant_name "Tenant One"
```

### 3. Test RLS

Test that RLS is working correctly:

```bash
# Test what a specific user can see
python manage.py rls_admin --action test_rls --user_id <user_uuid>

# List all RLS policies
python manage.py rls_admin --action list_policies
```

## API Usage

### RLS Test Endpoints

#### Test Current User's Access
```http
GET /api/rls/test/
Authorization: Bearer <token>
```

Returns what the current user can see based on RLS policies.

#### Test with Detailed Data
```http
GET /api/rls/test/?detailed=true
Authorization: Bearer <token>
```

Returns detailed data including actual records.

#### Impersonate Another User (Platform Admin Only)
```http
POST /api/rls/impersonate/
Authorization: Bearer <token>
Content-Type: application/json

{
    "user_id": "user-uuid-here",
    "detailed": true
}
```

#### View RLS Policies (Platform Admin Only)
```http
GET /api/rls/policies/
Authorization: Bearer <token>
```

#### Create Subscription with RLS
```http
POST /api/rls/create-subscription/
Authorization: Bearer <token>
Content-Type: application/json

{
    "plan_id": "plan-uuid-here",
    "tenant_id": "tenant-uuid-here"
}
```

## Programming with RLS

### Using RLS Context Manager

When you need to perform operations as a specific user (e.g., in background tasks):

```python
from api.middleware import RLSContextManager
from api.models import Users, Subscriptions

# Perform operations as a specific user
user = Users.objects.get(email="admin@example.com")
with RLSContextManager(user_id=user.id, user_role=user.role):
    # All database operations in this block will use the user's context
    subscriptions = Subscriptions.objects.all()  # Filtered by RLS
```

### Setting RLS Context Manually

```python
from api.middleware import set_rls_context
from api.models import Users

user = Users.objects.get(email="user@example.com")
set_rls_context(user)
# Now all queries will be filtered for this user
```

### Bypassing RLS (Use with Caution)

```python
from api.middleware import RLSContextManager

# Bypass RLS entirely (use only for admin operations)
with RLSContextManager():  # No user_id/role = bypass RLS
    all_users = Users.objects.all()  # Will see ALL users
```

## Management Commands

### Available Commands

```bash
# Create users
python manage.py rls_admin --action create_platform_admin --email "admin@example.com" --name "Admin"
python manage.py rls_admin --action create_tenant_admin --email "tadmin@example.com" --name "Tenant Admin" --tenant_name "My Tenant"
python manage.py rls_admin --action create_tenant_user --email "user@example.com" --name "User" --tenant_name "My Tenant"

# Test RLS
python manage.py rls_admin --action test_rls --user_id <uuid>

# Manage RLS (emergency only)
python manage.py rls_admin --action bypass_rls  # Disable RLS temporarily
python manage.py rls_admin --action enable_rls  # Re-enable RLS

# View policies
python manage.py rls_admin --action list_policies
```

## Security Considerations

### 1. Database Connection Security
- RLS policies only work when connected as a database user with appropriate permissions
- Ensure your database user has BYPASSRLS permission only for platform admin operations

### 2. Middleware Order
- The RLS middleware **must** come after authentication middleware
- Session variables are set per database connection

### 3. Background Tasks
- Always use `RLSContextManager` or `set_rls_context` in background tasks
- Without proper context, background tasks may not see expected data

### 4. Emergency Access
- Platform admins can temporarily bypass RLS if needed
- Use management commands to disable/enable RLS in emergencies

## Troubleshooting

### Common Issues

1. **No data visible after RLS setup**
   - Check that users are properly associated with tenants via `UserTenants`
   - Verify session variables are being set by middleware

2. **Users can see data they shouldn't**
   - Check if RLS is enabled: `python manage.py rls_admin --action list_policies`
   - Verify user roles are correctly set

3. **Background tasks failing**
   - Ensure you're using `RLSContextManager` in Celery tasks or management commands

4. **Performance issues**
   - RLS policies use subqueries; ensure proper database indexing
   - Consider caching tenant relationships for frequently accessed data

### Debug Commands

```bash
# Check current RLS status
python manage.py dbshell
SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'public';

# Test current session variables
SELECT current_setting('app.current_user_id', true), current_setting('app.current_user_role', true);
```

## Migration Notes

### From Non-RLS System

1. **Backup your database** before applying RLS migration
2. Ensure all users have proper tenant associations
3. Test thoroughly in staging environment
4. Plan for gradual rollout with ability to disable RLS if needed

### Performance Impact

- RLS adds overhead to every query
- Ensure proper indexing on `tenant_id` and user relationship fields
- Monitor query performance after deployment
- Consider read replicas for reporting if needed

## Best Practices

1. **Always test with multiple user roles** when developing features
2. **Use the management commands** for user creation and testing
3. **Keep tenant associations up to date** when users change organizations
4. **Monitor RLS policy performance** in production
5. **Use impersonation feature** for support and debugging
6. **Document any RLS bypasses** and ensure they're temporary

---

For additional help or questions about the RLS implementation, check the test views at `/api/rls/test/` or use the management commands for debugging.
