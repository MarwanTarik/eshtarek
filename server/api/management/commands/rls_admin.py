from django.core.management.base import BaseCommand
from django.db import connection
from api.models import Users, Tenants, UserTenants
from api.enums.role import Role
from api.middleware import RLSContextManager
import uuid


class Command(BaseCommand):
    help = 'Administration commands for Row Level Security (RLS) setup and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            required=True,
            choices=['create_platform_admin', 'create_tenant_admin', 'create_tenant_user', 
                    'test_rls', 'bypass_rls', 'enable_rls', 'list_policies'],
            help='Action to perform'
        )
        parser.add_argument('--email', type=str, help='User email')
        parser.add_argument('--name', type=str, help='User name')
        parser.add_argument('--tenant_name', type=str, help='Tenant name')
        parser.add_argument('--user_id', type=str, help='User ID for testing')

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'create_platform_admin':
            self.create_platform_admin(options)
        elif action == 'create_tenant_admin':
            self.create_tenant_admin(options)
        elif action == 'create_tenant_user':
            self.create_tenant_user(options)
        elif action == 'test_rls':
            self.test_rls(options)
        elif action == 'bypass_rls':
            self.bypass_rls()
        elif action == 'enable_rls':
            self.enable_rls()
        elif action == 'list_policies':
            self.list_policies()

    def create_platform_admin(self, options):
        """Create a platform admin user who can manage everything"""
        email = options.get('email')
        name = options.get('name')
        
        if not email or not name:
            self.stdout.write(
                self.style.ERROR('Email and name are required for creating platform admin')
            )
            return
        
        # Use RLS context to bypass restrictions during user creation
        with RLSContextManager():
            try:
                user = Users.objects.create(
                    email=email,
                    name=name,
                    role=Role.PLATFORM_ADMIN
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Platform admin created: {user.email} (ID: {user.id})')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating platform admin: {str(e)}')
                )

    def create_tenant_admin(self, options):
        """Create a tenant admin user"""
        email = options.get('email')
        name = options.get('name')
        tenant_name = options.get('tenant_name')
        
        if not email or not name or not tenant_name:
            self.stdout.write(
                self.style.ERROR('Email, name, and tenant_name are required')
            )
            return
        
        with RLSContextManager():
            try:
                # Create or get tenant
                tenant, created = Tenants.objects.get_or_create(name=tenant_name)
                if created:
                    self.stdout.write(f'Created new tenant: {tenant_name}')
                
                # Create user
                user = Users.objects.create(
                    email=email,
                    name=name,
                    role=Role.TENANT_ADMIN
                )
                
                # Associate user with tenant
                UserTenants.objects.create(user=user, tenant=tenant)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Tenant admin created: {user.email} for tenant {tenant_name} (ID: {user.id})'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating tenant admin: {str(e)}')
                )

    def create_tenant_user(self, options):
        """Create a regular tenant user"""
        email = options.get('email')
        name = options.get('name')
        tenant_name = options.get('tenant_name')
        
        if not email or not name or not tenant_name:
            self.stdout.write(
                self.style.ERROR('Email, name, and tenant_name are required')
            )
            return
        
        with RLSContextManager():
            try:
                # Get tenant
                tenant = Tenants.objects.get(name=tenant_name)
                
                # Create user
                user = Users.objects.create(
                    email=email,
                    name=name,
                    role=Role.TENANT_USER
                )
                
                # Associate user with tenant
                UserTenants.objects.create(user=user, tenant=tenant)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Tenant user created: {user.email} for tenant {tenant_name} (ID: {user.id})'
                    )
                )
            except Tenants.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Tenant {tenant_name} does not exist')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating tenant user: {str(e)}')
                )

    def test_rls(self, options):
        """Test RLS policies with a specific user"""
        user_id = options.get('user_id')
        
        if not user_id:
            self.stdout.write(
                self.style.ERROR('User ID is required for testing')
            )
            return
        
        try:
            user = Users.objects.get(id=user_id)
            
            self.stdout.write(f'Testing RLS for user: {user.email} (Role: {user.role})')
            
            # Test with user context
            with RLSContextManager(user_id=user.id, user_role=user.role):
                # Test users visibility
                visible_users = Users.objects.all().count()
                self.stdout.write(f'Visible users: {visible_users}')
                
                # Test tenants visibility
                visible_tenants = Tenants.objects.all().count()
                self.stdout.write(f'Visible tenants: {visible_tenants}')
                
                # Test user-tenant relationships
                visible_user_tenants = UserTenants.objects.all().count()
                self.stdout.write(f'Visible user-tenant relationships: {visible_user_tenants}')
                
        except Users.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with ID {user_id} does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error testing RLS: {str(e)}')
            )

    def bypass_rls(self):
        """Temporarily bypass RLS for all tables (use with caution)"""
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    ALTER TABLE users DISABLE ROW LEVEL SECURITY;
                    ALTER TABLE tenants DISABLE ROW LEVEL SECURITY;
                    ALTER TABLE user_tenants DISABLE ROW LEVEL SECURITY;
                    ALTER TABLE plans DISABLE ROW LEVEL SECURITY;
                    ALTER TABLE limit_policies DISABLE ROW LEVEL SECURITY;
                    ALTER TABLE plans_limit_policies DISABLE ROW LEVEL SECURITY;
                    ALTER TABLE subscriptions DISABLE ROW LEVEL SECURITY;
                    ALTER TABLE usages DISABLE ROW LEVEL SECURITY;
                """)
                self.stdout.write(
                    self.style.WARNING('RLS has been DISABLED for all tables. Remember to re-enable it!')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error disabling RLS: {str(e)}')
                )

    def enable_rls(self):
        """Re-enable RLS for all tables"""
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    ALTER TABLE users ENABLE ROW LEVEL SECURITY;
                    ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
                    ALTER TABLE user_tenants ENABLE ROW LEVEL SECURITY;
                    ALTER TABLE plans ENABLE ROW LEVEL SECURITY;
                    ALTER TABLE limit_policies ENABLE ROW LEVEL SECURITY;
                    ALTER TABLE plans_limit_policies ENABLE ROW LEVEL SECURITY;
                    ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
                    ALTER TABLE usages ENABLE ROW LEVEL SECURITY;
                """)
                self.stdout.write(
                    self.style.SUCCESS('RLS has been ENABLED for all tables')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error enabling RLS: {str(e)}')
                )

    def list_policies(self):
        """List all RLS policies in the database"""
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
                    FROM pg_policies 
                    WHERE schemaname = 'public'
                    ORDER BY tablename, policyname;
                """)
                
                policies = cursor.fetchall()
                
                if not policies:
                    self.stdout.write('No RLS policies found')
                    return
                
                self.stdout.write('\n--- RLS Policies ---')
                current_table = None
                
                for policy in policies:
                    schema, table, name, permissive, roles, cmd, qual, with_check = policy
                    
                    if table != current_table:
                        self.stdout.write(f'\nTable: {table}')
                        current_table = table
                    
                    self.stdout.write(f'  Policy: {name}')
                    self.stdout.write(f'    Command: {cmd}')
                    self.stdout.write(f'    Permissive: {permissive}')
                    if roles:
                        self.stdout.write(f'    Roles: {roles}')
                    if qual:
                        self.stdout.write(f'    Using: {qual[:100]}...' if len(qual) > 100 else f'    Using: {qual}')
                    if with_check:
                        self.stdout.write(f'    With Check: {with_check[:100]}...' if len(with_check) > 100 else f'    With Check: {with_check}')
                    self.stdout.write('')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error listing policies: {str(e)}')
                )