"""
Management command to test and verify PostgreSQL Row Level Security (RLS) setup.

This command provides various utilities for testing RLS functionality,
checking RLS status, and debugging RLS issues.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import connection
from server.api.utils.rls_utils import RLSUtils, debug_rls_policies, check_rls_functions
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Test and verify PostgreSQL Row Level Security (RLS) setup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-status',
            action='store_true',
            help='Check RLS status on all tables',
        )
        parser.add_argument(
            '--check-policies',
            action='store_true',
            help='List all RLS policies',
        )
        parser.add_argument(
            '--check-functions',
            action='store_true',
            help='Check if RLS functions exist',
        )
        parser.add_argument(
            '--test-isolation',
            action='store_true',
            help='Test RLS isolation between users',
        )
        parser.add_argument(
            '--get-context',
            action='store_true',
            help='Get current RLS context',
        )
        parser.add_argument(
            '--set-context',
            nargs=2,
            metavar=('USER_ID', 'ROLE'),
            help='Set RLS context for testing (USER_ID ROLE)',
        )
        parser.add_argument(
            '--clear-context',
            action='store_true',
            help='Clear RLS context',
        )
        parser.add_argument(
            '--user1',
            type=str,
            help='Email of first user for isolation testing',
        )
        parser.add_argument(
            '--user2',
            type=str,
            help='Email of second user for isolation testing',
        )
        parser.add_argument(
            '--table',
            type=str,
            default='tenants',
            help='Table to test isolation on (default: tenants)',
        )

    def handle(self, *args, **options):
        """Handle the management command."""
        
        if options['check_status']:
            self.check_rls_status()
        
        if options['check_policies']:
            self.check_rls_policies()
        
        if options['check_functions']:
            self.check_rls_functions()
        
        if options['test_isolation']:
            self.test_rls_isolation(
                options.get('user1'),
                options.get('user2'),
                options.get('table', 'tenants')
            )
        
        if options['get_context']:
            self.get_rls_context()
        
        if options['set_context']:
            user_id, role = options['set_context']
            self.set_rls_context(user_id, role)
        
        if options['clear_context']:
            self.clear_rls_context()

    def check_rls_status(self):
        """Check RLS status on all tables."""
        self.stdout.write(self.style.SUCCESS('Checking RLS status on tables...'))
        
        status = RLSUtils.check_rls_enabled()
        
        for table, enabled in status.items():
            if enabled:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {table}: RLS enabled')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ {table}: RLS disabled or table not found')
                )

    def check_rls_policies(self):
        """List all RLS policies."""
        self.stdout.write(self.style.SUCCESS('Checking RLS policies...'))
        
        policies = debug_rls_policies()
        
        if not policies:
            self.stdout.write(self.style.WARNING('No RLS policies found'))
            return
        
        current_table = None
        for policy in policies:
            if policy['tablename'] != current_table:
                current_table = policy['tablename']
                self.stdout.write(f'\n{self.style.HTTP_INFO}Table: {current_table}')
            
            self.stdout.write(
                f'  • {policy["policyname"]} ({policy["cmd"]}) - '
                f'Roles: {policy["roles"] or "all"}'
            )

    def check_rls_functions(self):
        """Check if RLS functions exist."""
        self.stdout.write(self.style.SUCCESS('Checking RLS functions...'))
        
        functions = check_rls_functions()
        
        for func_name, exists in functions.items():
            if exists:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {func_name}: exists')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ {func_name}: missing')
                )

    def test_rls_isolation(self, user1_email, user2_email, table):
        """Test RLS isolation between two users."""
        self.stdout.write(self.style.SUCCESS('Testing RLS isolation...'))
        
        if not user1_email or not user2_email:
            raise CommandError(
                'Both --user1 and --user2 email addresses are required for isolation testing'
            )
        
        try:
            user1 = User.objects.get(email=user1_email)
            user2 = User.objects.get(email=user2_email)
        except User.DoesNotExist as e:
            raise CommandError(f'User not found: {e}')
        
        self.stdout.write(f'Testing isolation on table: {table}')
        self.stdout.write(f'User 1: {user1.email} (role: {user1.role})')
        self.stdout.write(f'User 2: {user2.email} (role: {user2.role})')
        
        results = RLSUtils.test_rls_isolation(user1, user2, table)
        
        self.stdout.write(f'\nUser 1 can see {len(results["user1_can_see"])} records')
        self.stdout.write(f'User 2 can see {len(results["user2_can_see"])} records')
        
        if results['isolation_working']:
            self.stdout.write(
                self.style.SUCCESS('✓ RLS isolation is working correctly')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠ Users see the same data - check if this is expected')
            )
        
        # Show record IDs if not too many
        if len(results["user1_can_see"]) <= 10:
            self.stdout.write(f'User 1 records: {results["user1_can_see"]}')
        if len(results["user2_can_see"]) <= 10:
            self.stdout.write(f'User 2 records: {results["user2_can_see"]}')

    def get_rls_context(self):
        """Get current RLS context."""
        self.stdout.write(self.style.SUCCESS('Getting current RLS context...'))
        
        context = RLSUtils.get_current_rls_context()
        
        self.stdout.write(f'Current User ID: {context["current_user_id"] or "Not set"}')
        self.stdout.write(f'Current User Role: {context["current_user_role"] or "Not set"}')

    def set_rls_context(self, user_id, role):
        """Set RLS context."""
        self.stdout.write(self.style.SUCCESS(f'Setting RLS context...'))
        
        try:
            RLSUtils.set_rls_context(user_id, role)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Set context: user_id={user_id}, role={role}')
            )
        except Exception as e:
            raise CommandError(f'Error setting RLS context: {e}')

    def clear_rls_context(self):
        """Clear RLS context."""
        self.stdout.write(self.style.SUCCESS('Clearing RLS context...'))
        
        try:
            RLSUtils.clear_rls_context()
            self.stdout.write(self.style.SUCCESS('✓ RLS context cleared'))
        except Exception as e:
            raise CommandError(f'Error clearing RLS context: {e}')
