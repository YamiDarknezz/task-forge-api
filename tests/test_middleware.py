import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app.middleware.auth import get_current_user, current_user_required, optional_jwt
from app.middleware.rbac import role_required, admin_required
from app.models.user import User, RoleType


class TestAuthMiddleware:
    """Tests for auth middleware"""

    def test_get_current_user_valid(self, app, regular_user, user_token):
        """Test getting current user with valid token"""
        with app.test_request_context(
            '/',
            headers={'Authorization': f'Bearer {user_token}'}
        ):
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
            user = get_current_user()

            assert user is not None
            assert user.id == regular_user.id

    def test_get_current_user_inactive(self, app, regular_user, user_token):
        """Test getting inactive user"""
        with app.app_context():
            user = User.query.get(regular_user.id)
            user.is_active = False
            from app import db
            db.session.commit()

        with app.test_request_context(
            '/',
            headers={'Authorization': f'Bearer {user_token}'}
        ):
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
            user = get_current_user()

            assert user is None

    def test_current_user_required_success(self, app, regular_user, user_token):
        """Test current_user_required decorator with valid token"""
        @current_user_required
        def test_endpoint(current_user=None):
            return {'user_id': current_user.id}, 200

        with app.test_request_context(
            '/',
            headers={'Authorization': f'Bearer {user_token}'}
        ):
            response, status_code = test_endpoint()
            assert status_code == 200
            assert response['user_id'] == regular_user.id

    def test_current_user_required_no_user(self, app):
        """Test current_user_required decorator with invalid token"""
        @current_user_required
        def test_endpoint(current_user=None):
            return {'success': True}, 200

        # Create invalid token
        invalid_token = create_access_token(identity="99999")

        with app.test_request_context(
            '/',
            headers={'Authorization': f'Bearer {invalid_token}'}
        ):
            response, status_code = test_endpoint()
            assert status_code == 404

    def test_optional_jwt_with_token(self, app, regular_user, user_token):
        """Test optional_jwt with valid token"""
        @optional_jwt
        def test_endpoint(current_user=None):
            if current_user:
                return {'authenticated': True, 'user_id': current_user.id}, 200
            return {'authenticated': False}, 200

        with app.test_request_context(
            '/',
            headers={'Authorization': f'Bearer {user_token}'}
        ):
            response, status_code = test_endpoint()
            assert status_code == 200
            assert response['authenticated'] is True

    def test_optional_jwt_without_token(self, app):
        """Test optional_jwt without token"""
        @optional_jwt
        def test_endpoint(current_user=None):
            if current_user:
                return {'authenticated': True}, 200
            return {'authenticated': False}, 200

        with app.test_request_context('/'):
            response, status_code = test_endpoint()
            assert status_code == 200
            assert response['authenticated'] is False


class TestRBACMiddleware:
    """Tests for RBAC middleware"""

    def test_role_required_success(self, app, regular_user, user_token):
        """Test role_required with correct role"""
        @role_required(RoleType.USER)
        def test_endpoint(current_user=None):
            return {'success': True}, 200

        with app.test_request_context(
            '/',
            headers={'Authorization': f'Bearer {user_token}'}
        ):
            response, status_code = test_endpoint()
            assert status_code == 200
            assert response['success'] is True

    def test_role_required_wrong_role(self, app, regular_user, user_token):
        """Test role_required with wrong role"""
        @role_required(RoleType.ADMIN)
        def test_endpoint(current_user=None):
            return {'success': True}, 200

        with app.test_request_context(
            '/',
            headers={'Authorization': f'Bearer {user_token}'}
        ):
            response, status_code = test_endpoint()
            assert status_code == 403

    def test_role_required_no_token(self, app):
        """Test role_required without token"""
        @role_required(RoleType.USER)
        def test_endpoint(current_user=None):
            return {'success': True}, 200

        with app.test_request_context('/'):
            response, status_code = test_endpoint()
            assert status_code == 401

    def test_admin_required_success(self, app, admin_user, admin_token):
        """Test admin_required with admin user"""
        @admin_required
        def test_endpoint(current_user=None):
            return {'success': True}, 200

        with app.test_request_context(
            '/',
            headers={'Authorization': f'Bearer {admin_token}'}
        ):
            response, status_code = test_endpoint()
            assert status_code == 200
            assert response['success'] is True

    def test_admin_required_non_admin(self, app, regular_user, user_token):
        """Test admin_required with non-admin user"""
        @admin_required
        def test_endpoint(current_user=None):
            return {'success': True}, 200

        with app.test_request_context(
            '/',
            headers={'Authorization': f'Bearer {user_token}'}
        ):
            response, status_code = test_endpoint()
            assert status_code == 403

    def test_admin_required_no_token(self, app):
        """Test admin_required without token"""
        @admin_required
        def test_endpoint(current_user=None):
            return {'success': True}, 200

        with app.test_request_context('/'):
            response, status_code = test_endpoint()
            assert status_code == 401
