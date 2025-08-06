"""
Tests for PostgreSQL RLS middleware functionality.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import connection
from unittest.mock import patch, MagicMock
import uuid

from api.serializers import UserSerializer
from api.middleware import PostgreSQLRLSMiddleware, RLSDebugMiddleware
from api.utils.rls_utils import RLSUtils
from api.enums.role import Role



class TestPostgreSQLRLSMiddleware(TestCase):
    """Test cases for PostgreSQL RLS middleware."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.middleware = PostgreSQLRLSMiddleware(get_response=lambda r: None)
        
        # Create test user
        serializer = UserSerializer()
        self.test_user = serializer.create({
            'email': 'test@example.com',
            'name': 'Test User',
            'role': Role.TENANT_ADMIN
        })

    def tearDown(self):
        """Clean up after tests."""
        # Clear RLS context
        try:
            RLSUtils.clear_rls_context()
        except:
            pass
    
    def test_middleware_sets_session_variables_for_authenticated_user(self):
        """Test that middleware sets session variables for authenticated users."""
        request = self.factory.get('/')
        request.user = self.test_user
        
        # Process request
        self.middleware.process_request(request)
        
        # Check that session variables are set
        context = RLSUtils.get_current_rls_context()
        self.assertEqual(context['current_user_id'], str(self.test_user.id))
        self.assertEqual(context['current_user_role'], self.test_user.role)
    
    def test_middleware_clears_session_variables_for_anonymous_user(self):
        """Test that middleware clears session variables for anonymous users."""
        # First, set some context
        RLSUtils.set_rls_context(str(uuid.uuid4()), Role.PLATFORM_ADMIN)
        
        # Create anonymous request
        request = self.factory.get('/')
        request.user = MagicMock()
        request.user.is_authenticated = False
        
        # Process request
        self.middleware.process_request(request)
        
        # Check that session variables are cleared
        context = RLSUtils.get_current_rls_context()
        self.assertIn(context['current_user_id'], [None, ''])
        self.assertIn(context['current_user_role'], [None, ''])
    
    def test_middleware_resets_session_variables_on_each_request(self):
        """Test that middleware resets session variables on each request."""
        # Set some initial context
        RLSUtils.set_rls_context('old-user-id', 'old-role')
        
        # Create request with different user
        request = self.factory.get('/')
        request.user = self.test_user
        
        # Process request
        self.middleware.process_request(request)
        
        # Check that session variables are updated
        context = RLSUtils.get_current_rls_context()
        self.assertEqual(context['current_user_id'], str(self.test_user.id))
        self.assertEqual(context['current_user_role'], self.test_user.role)
        self.assertNotEqual(context['current_user_id'], 'old-user-id')
        self.assertNotEqual(context['current_user_role'], 'old-role')
    
    def test_middleware_handles_database_errors_gracefully(self):
        """Test that middleware handles database errors gracefully."""
        request = self.factory.get('/')
        request.user = self.test_user
        
        # Mock database error and suppress logging during test
        with patch('api.middleware.connection') as mock_connection, \
             patch('api.middleware.logger') as mock_logger:
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = Exception("Database error")
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
            
            # Should not raise exception
            result = self.middleware.process_request(request)
            self.assertIsNone(result)  # Request should continue processing
            
            # Verify that errors were logged (but suppressed from output)
            self.assertTrue(mock_logger.error.called)
    
    def test_process_response_returns_response(self):
        """Test that process_response returns the response unchanged."""
        request = self.factory.get('/')
        response = MagicMock()
        
        result = self.middleware.process_response(request, response)
        self.assertEqual(result, response)


class TestRLSUtils(TestCase):
    """Test cases for RLS utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        serializer = UserSerializer()
        self.test_user = serializer.create({
            'email': 'utils_test@example.com',
            'name': 'Utils Test User',
            'role': Role.TENANT_USER,
        })
    
    def tearDown(self):
        """Clean up after tests."""
        try:
            RLSUtils.clear_rls_context()
        except:
            pass
    
    def test_set_and_get_rls_context(self):
        """Test setting and getting RLS context."""
        user_id = str(self.test_user.id)
        role = self.test_user.role
        
        # Set context
        RLSUtils.set_rls_context(user_id, role)
        
        # Get context
        context = RLSUtils.get_current_rls_context()
        self.assertEqual(context['current_user_id'], user_id)
        self.assertEqual(context['current_user_role'], role)
    
    def test_clear_rls_context(self):
        """Test clearing RLS context."""
        # Set some context first
        RLSUtils.set_rls_context(str(self.test_user.id), self.test_user.role)
        
        # Clear context
        RLSUtils.clear_rls_context()
        
        # Check that context is cleared
        context = RLSUtils.get_current_rls_context()
        self.assertIn(context['current_user_id'], [None, ''])
        self.assertIn(context['current_user_role'], [None, ''])
    
    def test_check_rls_enabled(self):
        """Test checking RLS status."""
        status = RLSUtils.check_rls_enabled()
        
        # Should return a dictionary
        self.assertIsInstance(status, dict)
        
        # Should include expected tables
        expected_tables = [
            'users', 'tenants', 'user_tenants', 'plans',
            'limit_policies', 'plans_limit_policies',
            'subscriptions', 'usages'
        ]
        
        for table in expected_tables:
            self.assertIn(table, status)
    
    def test_get_user_tenant_ids_empty_for_new_user(self):
        """Test getting tenant IDs for user with no tenants."""
        tenant_ids = RLSUtils.get_user_tenant_ids(str(self.test_user.id))
        self.assertEqual(tenant_ids, [])


class TestRLSDebugMiddleware(TestCase):
    """Test cases for RLS debug middleware."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.middleware = RLSDebugMiddleware(get_response=lambda r: None)
    
    def test_debug_middleware_does_not_raise_exceptions(self):
        """Test that debug middleware handles errors gracefully."""
        request = self.factory.get('/test-path')
        
        # Should not raise any exceptions
        result = self.middleware.process_request(request)
        self.assertIsNone(result)
    
    @patch('api.middleware.logger')
    def test_debug_middleware_logs_context(self, mock_logger):
        """Test that debug middleware logs RLS context when debug is enabled."""
        mock_logger.isEnabledFor.return_value = True
        
        request = self.factory.get('/test-path')
        
        # Set some context first
        RLSUtils.set_rls_context('test-user-id', 'test-role')
        
        # Process request
        self.middleware.process_request(request)
        
        # Check that debug was called
        mock_logger.isEnabledFor.assert_called()
        mock_logger.debug.assert_called()


class TestMiddlewareIntegration(TestCase):
    """Integration tests for middleware with Django request processing."""
    
    def setUp(self):
        """Set up test fixtures."""
        serializer = UserSerializer()
        self.test_user = serializer.create({
            'email': 'integration_test@example.com',
            'name': 'Integration Test User',
            'role': Role.PLATFORM_ADMIN
        })
    
    
    def test_middleware_integration_with_django_client(self):
        """Test middleware integration using Django test client."""
        # Login user
        self.client.force_login(self.test_user)
        
        # Make a request (this should trigger the middleware)
        response = self.client.get('/api/') 
  
        context = RLSUtils.get_current_rls_context()
        
        # Context might be cleared after request, so we just check this doesn't error
        self.assertIsInstance(context, dict)
        self.assertIn('current_user_id', context)
        self.assertIn('current_user_role', context)
