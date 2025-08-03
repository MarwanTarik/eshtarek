from django.db import migrations

# use postgres to enable RLS
# This migration is intended to enable Row Level Security (RLS) on the users tenants, subscriptions, and usages tables.
class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- Enable Row Level Security for all tables
                ALTER TABLE users ENABLE ROW LEVEL SECURITY;
                ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
                ALTER TABLE user_tenants ENABLE ROW LEVEL SECURITY;
                ALTER TABLE plans ENABLE ROW LEVEL SECURITY;
                ALTER TABLE limit_policies ENABLE ROW LEVEL SECURITY;
                ALTER TABLE plans_limit_policies ENABLE ROW LEVEL SECURITY;
                ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
                ALTER TABLE usages ENABLE ROW LEVEL SECURITY;

                -- Create function to get current user's tenant IDs
                CREATE OR REPLACE FUNCTION get_user_tenant_ids(user_uuid UUID)
                RETURNS UUID[] AS $$
                BEGIN
                    RETURN ARRAY(
                        SELECT tenant_id 
                        FROM user_tenants 
                        WHERE user_id = user_uuid
                    );
                END;
                $$ LANGUAGE plpgsql SECURITY DEFINER;

                -- Create function to get current user's role
                CREATE OR REPLACE FUNCTION get_user_role(user_uuid UUID)
                RETURNS TEXT AS $$
                BEGIN
                    RETURN (SELECT role FROM users WHERE id = user_uuid);
                END;
                $$ LANGUAGE plpgsql SECURITY DEFINER;

                -- USERS table policies
                -- Platform admins can see all users, others can only see users in their tenants
                CREATE POLICY users_select_policy ON users
                FOR SELECT
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    id = current_setting('app.current_user_id', true)::UUID
                    OR
                    EXISTS (
                        SELECT 1 FROM user_tenants ut1, user_tenants ut2
                        WHERE ut1.user_id = current_setting('app.current_user_id', true)::UUID
                        AND ut2.user_id = users.id
                        AND ut1.tenant_id = ut2.tenant_id
                    )
                );

                -- Only platform admins can insert/update/delete users
                CREATE POLICY users_insert_policy ON users
                FOR INSERT
                WITH CHECK (current_setting('app.current_user_role', true) = 'platform_admin');

                CREATE POLICY users_update_policy ON users
                FOR UPDATE
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR id = current_setting('app.current_user_id', true)::UUID
                );

                CREATE POLICY users_delete_policy ON users
                FOR DELETE
                USING (current_setting('app.current_user_role', true) = 'platform_admin');

                -- TENANTS table policies
                -- Platform admins can see all tenants, others can only see their tenants
                CREATE POLICY tenants_select_policy ON tenants
                FOR SELECT
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID))
                );

                -- Only platform admins can manage tenants
                CREATE POLICY tenants_insert_policy ON tenants
                FOR INSERT
                WITH CHECK (current_setting('app.current_user_role', true) = 'platform_admin');

                CREATE POLICY tenants_update_policy ON tenants
                FOR UPDATE
                USING (current_setting('app.current_user_role', true) = 'platform_admin');

                CREATE POLICY tenants_delete_policy ON tenants
                FOR DELETE
                USING (current_setting('app.current_user_role', true) = 'platform_admin');

                -- USER_TENANTS table policies
                -- Users can see their own tenant relationships, platform admins see all
                CREATE POLICY user_tenants_select_policy ON user_tenants
                FOR SELECT
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    user_id = current_setting('app.current_user_id', true)::UUID
                    OR
                    tenant_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID))
                );

                -- Platform admins and tenant admins can manage user-tenant relationships
                CREATE POLICY user_tenants_insert_policy ON user_tenants
                FOR INSERT
                WITH CHECK (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    (current_setting('app.current_user_role', true) = 'tenant_admin' 
                     AND tenant_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID)))
                );

                CREATE POLICY user_tenants_update_policy ON user_tenants
                FOR UPDATE
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    (current_setting('app.current_user_role', true) = 'tenant_admin' 
                     AND tenant_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID)))
                );

                CREATE POLICY user_tenants_delete_policy ON user_tenants
                FOR DELETE
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    (current_setting('app.current_user_role', true) = 'tenant_admin' 
                     AND tenant_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID)))
                );

                -- PLANS table policies
                -- All users can see plans, only platform admins can manage them
                CREATE POLICY plans_select_policy ON plans
                FOR SELECT
                USING (true);

                CREATE POLICY plans_insert_policy ON plans
                FOR INSERT
                WITH CHECK (current_setting('app.current_user_role', true) = 'platform_admin');

                CREATE POLICY plans_update_policy ON plans
                FOR UPDATE
                USING (current_setting('app.current_user_role', true) = 'platform_admin');

                CREATE POLICY plans_delete_policy ON plans
                FOR DELETE
                USING (current_setting('app.current_user_role', true) = 'platform_admin');

                -- LIMIT_POLICIES table policies
                -- All users can see limit policies, only platform admins can manage them
                CREATE POLICY limit_policies_select_policy ON limit_policies
                FOR SELECT
                USING (true);

                CREATE POLICY limit_policies_insert_policy ON limit_policies
                FOR INSERT
                WITH CHECK (current_setting('app.current_user_role', true) = 'platform_admin');

                CREATE POLICY limit_policies_update_policy ON limit_policies
                FOR UPDATE
                USING (current_setting('app.current_user_role', true) = 'platform_admin');

                CREATE POLICY limit_policies_delete_policy ON limit_policies
                FOR DELETE
                USING (current_setting('app.current_user_role', true) = 'platform_admin');

                -- PLANS_LIMIT_POLICIES table policies
                -- All users can see plan limit policies, only platform admins can manage them
                CREATE POLICY plans_limit_policies_select_policy ON plans_limit_policies
                FOR SELECT
                USING (true);

                CREATE POLICY plans_limit_policies_insert_policy ON plans_limit_policies
                FOR INSERT
                WITH CHECK (current_setting('app.current_user_role', true) = 'platform_admin');

                CREATE POLICY plans_limit_policies_update_policy ON plans_limit_policies
                FOR UPDATE
                USING (current_setting('app.current_user_role', true) = 'platform_admin');

                CREATE POLICY plans_limit_policies_delete_policy ON plans_limit_policies
                FOR DELETE
                USING (current_setting('app.current_user_role', true) = 'platform_admin');

                -- SUBSCRIPTIONS table policies
                -- Users can only see subscriptions for their tenants
                CREATE POLICY subscriptions_select_policy ON subscriptions
                FOR SELECT
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    tenant_id_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID))
                );

                -- Tenant admins can create/modify subscriptions for their tenants
                CREATE POLICY subscriptions_insert_policy ON subscriptions
                FOR INSERT
                WITH CHECK (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    (current_setting('app.current_user_role', true) = 'tenant_admin' 
                     AND tenant_id_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID)))
                );

                CREATE POLICY subscriptions_update_policy ON subscriptions
                FOR UPDATE
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    (current_setting('app.current_user_role', true) = 'tenant_admin' 
                     AND tenant_id_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID)))
                );

                CREATE POLICY subscriptions_delete_policy ON subscriptions
                FOR DELETE
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    (current_setting('app.current_user_role', true) = 'tenant_admin' 
                     AND tenant_id_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID)))
                );

                -- USAGES table policies
                -- Users can only see usages for their tenant subscriptions
                CREATE POLICY usages_select_policy ON usages
                FOR SELECT
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    EXISTS (
                        SELECT 1 FROM subscriptions s
                        WHERE s.id = subscription_id_id
                        AND s.tenant_id_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID))
                    )
                );

                -- Users in tenant can insert/update usages, platform admins have full access
                CREATE POLICY usages_insert_policy ON usages
                FOR INSERT
                WITH CHECK (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    EXISTS (
                        SELECT 1 FROM subscriptions s
                        WHERE s.id = subscription_id_id
                        AND s.tenant_id_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID))
                    )
                );

                CREATE POLICY usages_update_policy ON usages
                FOR UPDATE
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    EXISTS (
                        SELECT 1 FROM subscriptions s
                        WHERE s.id = subscription_id_id
                        AND s.tenant_id_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID))
                    )
                );

                CREATE POLICY usages_delete_policy ON usages
                FOR DELETE
                USING (
                    current_setting('app.current_user_role', true) = 'platform_admin'
                    OR 
                    EXISTS (
                        SELECT 1 FROM subscriptions s
                        WHERE s.id = subscription_id_id
                        AND s.tenant_id_id = ANY(get_user_tenant_ids(current_setting('app.current_user_id', true)::UUID))
                    )
                );
            """,
            reverse_sql="""
                -- Drop all policies
                DROP POLICY IF EXISTS users_select_policy ON users;
                DROP POLICY IF EXISTS users_insert_policy ON users;
                DROP POLICY IF EXISTS users_update_policy ON users;
                DROP POLICY IF EXISTS users_delete_policy ON users;
                
                DROP POLICY IF EXISTS tenants_select_policy ON tenants;
                DROP POLICY IF EXISTS tenants_insert_policy ON tenants;
                DROP POLICY IF EXISTS tenants_update_policy ON tenants;
                DROP POLICY IF EXISTS tenants_delete_policy ON tenants;
                
                DROP POLICY IF EXISTS user_tenants_select_policy ON user_tenants;
                DROP POLICY IF EXISTS user_tenants_insert_policy ON user_tenants;
                DROP POLICY IF EXISTS user_tenants_update_policy ON user_tenants;
                DROP POLICY IF EXISTS user_tenants_delete_policy ON user_tenants;
                
                DROP POLICY IF EXISTS plans_select_policy ON plans;
                DROP POLICY IF EXISTS plans_insert_policy ON plans;
                DROP POLICY IF EXISTS plans_update_policy ON plans;
                DROP POLICY IF EXISTS plans_delete_policy ON plans;
                
                DROP POLICY IF EXISTS limit_policies_select_policy ON limit_policies;
                DROP POLICY IF EXISTS limit_policies_insert_policy ON limit_policies;
                DROP POLICY IF EXISTS limit_policies_update_policy ON limit_policies;
                DROP POLICY IF EXISTS limit_policies_delete_policy ON limit_policies;
                
                DROP POLICY IF EXISTS plans_limit_policies_select_policy ON plans_limit_policies;
                DROP POLICY IF EXISTS plans_limit_policies_insert_policy ON plans_limit_policies;
                DROP POLICY IF EXISTS plans_limit_policies_update_policy ON plans_limit_policies;
                DROP POLICY IF EXISTS plans_limit_policies_delete_policy ON plans_limit_policies;
                
                DROP POLICY IF EXISTS subscriptions_select_policy ON subscriptions;
                DROP POLICY IF EXISTS subscriptions_insert_policy ON subscriptions;
                DROP POLICY IF EXISTS subscriptions_update_policy ON subscriptions;
                DROP POLICY IF EXISTS subscriptions_delete_policy ON subscriptions;
                
                DROP POLICY IF EXISTS usages_select_policy ON usages;
                DROP POLICY IF EXISTS usages_insert_policy ON usages;
                DROP POLICY IF EXISTS usages_update_policy ON usages;
                DROP POLICY IF EXISTS usages_delete_policy ON usages;
                
                -- Drop helper functions
                DROP FUNCTION IF EXISTS get_user_tenant_ids(UUID);
                DROP FUNCTION IF EXISTS get_user_role(UUID);
                
                -- Disable Row Level Security
                ALTER TABLE users DISABLE ROW LEVEL SECURITY;
                ALTER TABLE tenants DISABLE ROW LEVEL SECURITY;
                ALTER TABLE user_tenants DISABLE ROW LEVEL SECURITY;
                ALTER TABLE plans DISABLE ROW LEVEL SECURITY;
                ALTER TABLE limit_policies DISABLE ROW LEVEL SECURITY;
                ALTER TABLE plans_limit_policies DISABLE ROW LEVEL SECURITY;
                ALTER TABLE subscriptions DISABLE ROW LEVEL SECURITY;
                ALTER TABLE usages DISABLE ROW LEVEL SECURITY;
            """
        ),
    ]