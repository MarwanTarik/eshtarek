import logging
from django.db import connection
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

User = get_user_model()

class PostgreSQLRLSMiddleware(MiddlewareMixin):
    """
    Middleware to enable PostgreSQL Row Level Security (RLS) by setting
    session variables for the current user ID and role.
    
    This middleware sets the following PostgreSQL session variables:
    - app.current_user_id: UUID of the authenticated user
    - app.current_user_role: Role of the authenticated user (platform_admin, tenant_admin, tenant_user)
    
    These variables are used by the RLS policies defined in the database
    to control access to data based on user permissions and tenant relationships.
    """
    
    def process_request(self, request):
        """
        Process incoming request and set PostgreSQL session variables for RLS.
        
        Args:
            request: The Django HttpRequest object
            
        Returns:
            None if processing should continue, or HttpResponse if an error occurs
        """
        try:
            self._reset_session_variables()
            
            if hasattr(request, 'user') and request.user.is_authenticated:
                self._set_user_session_variables(request.user)
                
        except Exception as e:
            logger.error(f"Error in PostgreSQLRLSMiddleware: {str(e)}")
            return None
    
    def process_response(self, request, response):
        """
        Process the response and optionally clean up session variables.
        
        Args:
            request: The Django HttpRequest object
            response: The Django HttpResponse object
            
        Returns:
            The response object
        """
        return response
    
    def _reset_session_variables(self):
        """
        Reset PostgreSQL session variables to ensure clean state.
        This prevents data leakage between requests.
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT set_config('app.current_user_id', '', false)")
                cursor.execute("SELECT set_config('app.current_user_role', '', false)")
                
        except Exception as e:
            logger.error(f"Error resetting session variables: {str(e)}")
    
    def _set_user_session_variables(self, user):
        """
        Set PostgreSQL session variables for the authenticated user.
        
        Args:
            user: The authenticated User instance
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT set_config('app.current_user_id', %s, false)",
                    [str(user.id)]
                )
                
                cursor.execute(
                    "SELECT set_config('app.current_user_role', %s, false)",
                    [user.role]
                )
                
                logger.debug(f"Set RLS variables for user {user.id} with role {user.role}")
                
        except Exception as e:
            logger.error(f"Error setting session variables for user {user.id}: {str(e)}")

class RLSDebugMiddleware(MiddlewareMixin):
    """
    Debug middleware to log RLS session variables.
    Only use this in development environments.
    """
    
    def process_request(self, request):
        """Log current RLS session variables for debugging."""
        if logger.isEnabledFor(logging.DEBUG):
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT current_setting('app.current_user_id', true)")
                    user_id = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT current_setting('app.current_user_role', true)")
                    user_role = cursor.fetchone()[0]
                    
                    logger.debug(f"RLS Debug - User ID: {user_id}, Role: {user_role}, Path: {request.path}")
                    
            except Exception as e:
                logger.debug(f"Error in RLS debug middleware: {str(e)}")


class RLSConnectionMiddleware(MiddlewareMixin):
    """
    Middleware to ensure database connection settings are appropriate for RLS.
    This middleware can be used to set additional connection-level settings
    if needed for RLS functionality.
    """
    
    def process_request(self, request):
        """
        Ensure database connection is properly configured for RLS.
        """
        try:
            if connection.connection is not None:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT relrowsecurity 
                        FROM pg_class 
                        WHERE relname = 'users' AND relnamespace = (
                            SELECT oid FROM pg_namespace WHERE nspname = 'public'
                        )
                    """)
                    result = cursor.fetchone()
                    if result and not result[0]:
                        logger.warning("RLS is not enabled on users table")
                        
        except Exception as e:
            logger.error(f"Error in RLS connection middleware: {str(e)}")
            pass
