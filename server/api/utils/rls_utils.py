"""
Utility functions for PostgreSQL Row Level Security (RLS) operations.

This module provides helper functions for working with RLS in the application,
including functions to check RLS status, validate policies, and test RLS behavior.
"""

import logging
from django.db import connection
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class RLSUtils:
    """Utility class for RLS operations."""
    
    @staticmethod
    def get_current_rls_context():
        """
        Get the current RLS context (user ID and role) from PostgreSQL session variables.
        
        Returns:
            dict: Dictionary containing current_user_id and current_user_role
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_setting('app.current_user_id', true)")
                user_id = cursor.fetchone()[0]
                
                cursor.execute("SELECT current_setting('app.current_user_role', true)")
                user_role = cursor.fetchone()[0]
                
                return {
                    'current_user_id': user_id if user_id else None,
                    'current_user_role': user_role if user_role else None
                }
        except Exception as e:
            logger.error(f"Error getting RLS context: {str(e)}")
            return {
                'current_user_id': None,
                'current_user_role': None
            }
    
    @staticmethod
    def set_rls_context(user_id=None, user_role=None):
        """
        Manually set RLS context for testing or special operations.
        
        Args:
            user_id (str, optional): User ID to set
            user_role (str, optional): User role to set
            
        Warning:
            This function should only be used for testing or special administrative
            operations. Normal request processing should rely on the middleware.
        """
        try:
            with connection.cursor() as cursor:
                if user_id:
                    cursor.execute(
                        "SELECT set_config('app.current_user_id', %s, false)",
                        [str(user_id)]
                    )
                
                if user_role:
                    cursor.execute(
                        "SELECT set_config('app.current_user_role', %s, false)",
                        [user_role]
                    )
                    
                logger.debug(f"Manually set RLS context: user_id={user_id}, role={user_role}")
                
        except Exception as e:
            logger.error(f"Error setting RLS context: {str(e)}")
            raise
    
    @staticmethod
    def clear_rls_context():
        """
        Clear RLS context by resetting session variables.
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT set_config('app.current_user_id', '', false)")
                cursor.execute("SELECT set_config('app.current_user_role', '', false)")
                
                logger.debug("Cleared RLS context")
                
        except Exception as e:
            logger.error(f"Error clearing RLS context: {str(e)}")
    
    @staticmethod
    def check_rls_enabled():
        """
        Check if RLS is enabled on all expected tables.
        
        Returns:
            dict: Dictionary mapping table names to their RLS status
        """
        tables = [
            'users', 'tenants', 'user_tenants', 'plans', 
            'limit_policies', 'plans_limit_policies', 
            'subscriptions', 'usages'
        ]
        
        try:
            with connection.cursor() as cursor:
                result = {}
                for table in tables:
                    cursor.execute("""
                        SELECT relrowsecurity 
                        FROM pg_class 
                        WHERE relname = %s AND relnamespace = (
                            SELECT oid FROM pg_namespace WHERE nspname = 'public'
                        )
                    """, [table])
                    
                    row = cursor.fetchone()
                    result[table] = row[0] if row else False
                
                return result
                
        except Exception as e:
            logger.error(f"Error checking RLS status: {str(e)}")
            return {}
    
    @staticmethod
    def get_user_tenant_ids(user_id):
        """
        Get all tenant IDs associated with a user.
        This replicates the PostgreSQL function used in RLS policies.
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of tenant IDs
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT tenant_id 
                    FROM user_tenants 
                    WHERE user_id = %s
                """, [user_id])
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting user tenant IDs: {str(e)}")
            return []
    
    @staticmethod
    def test_rls_isolation(user1, user2, test_table='tenants'):
        """
        Test RLS isolation between two users.
        
        Args:
            user1: First user instance
            user2: Second user instance
            test_table (str): Table to test isolation on
            
        Returns:
            dict: Test results
        """
        results = {
            'user1_can_see': [],
            'user2_can_see': [],
            'isolation_working': False
        }
        
        try:
            RLSUtils.set_rls_context(user1.id, user1.role)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT id FROM {test_table}")
                results['user1_can_see'] = [row[0] for row in cursor.fetchall()]
            
            RLSUtils.set_rls_context(user2.id, user2.role)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT id FROM {test_table}")
                results['user2_can_see'] = [row[0] for row in cursor.fetchall()]
            
            # Check if isolation is working
            # For most tables, different users should see different data sets
            # unless they share tenants or one is a platform admin
            if user1.role == 'platform_admin' or user2.role == 'platform_admin':
                results['isolation_working'] = True  # Admin sees everything
            else:
                results['isolation_working'] = (
                    set(results['user1_can_see']) != set(results['user2_can_see'])
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing RLS isolation: {str(e)}")
            return results
        finally:
            # Clean up
            RLSUtils.clear_rls_context()


def debug_rls_policies():
    """
    Debug function to check all RLS policies in the database.
    
    Returns:
        list: List of dictionaries containing policy information
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    policyname,
                    permissive,
                    roles,
                    cmd,
                    qual,
                    with_check
                FROM pg_policies 
                WHERE schemaname = 'public'
                ORDER BY tablename, policyname
            """)
            
            columns = [desc[0] for desc in cursor.description]
            policies = []
            
            for row in cursor.fetchall():
                policy = dict(zip(columns, row))
                policies.append(policy)
            
            return policies
            
    except Exception as e:
        logger.error(f"Error getting RLS policies: {str(e)}")
        return []


def check_rls_functions():
    """
    Check if the custom RLS functions exist in the database.
    
    Returns:
        dict: Dictionary of function existence status
    """
    functions = [
        'get_user_tenant_ids',
        'get_user_role'
    ]
    
    try:
        with connection.cursor() as cursor:
            result = {}
            for func in functions:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_proc p
                        JOIN pg_namespace n ON p.pronamespace = n.oid
                        WHERE n.nspname = 'public' AND p.proname = %s
                    )
                """, [func])
                
                result[func] = cursor.fetchone()[0]
            
            return result
            
    except Exception as e:
        logger.error(f"Error checking RLS functions: {str(e)}")
        return {func: False for func in functions}
