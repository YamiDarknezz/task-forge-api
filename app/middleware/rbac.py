from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTExtendedException
from app.middleware.auth import get_current_user
from app.models.user import RoleType


def role_required(*allowed_roles):
    """
    Decorator that requires user to have one of the specified roles
    Usage: @role_required(RoleType.ADMIN)
           @role_required(RoleType.ADMIN, RoleType.USER)
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except (NoAuthorizationError, JWTExtendedException) as e:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'message': str(e)
                }), 401

            current_user = get_current_user()

            if not current_user:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'message': 'Authentication required'
                }), 401

            # Extract role values from RoleType enums
            allowed_role_values = [role.value if isinstance(role, RoleType) else role for role in allowed_roles]

            if current_user.role.name not in allowed_role_values:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'You do not have permission to access this resource'
                }), 403

            kwargs['current_user'] = current_user
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """
    Decorator that requires user to be an admin
    Shorthand for @role_required(RoleType.ADMIN)
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except (NoAuthorizationError, JWTExtendedException) as e:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': str(e)
            }), 401

        current_user = get_current_user()

        if not current_user:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Authentication required'
            }), 401

        if not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Admin access required'
            }), 403

        kwargs['current_user'] = current_user
        return fn(*args, **kwargs)
    return wrapper


def resource_owner_or_admin(resource_user_id_getter):
    """
    Decorator that requires user to be either the resource owner or an admin

    Args:
        resource_user_id_getter: Function that extracts user_id from the resource
                                Example: lambda: Task.query.get(task_id).user_id
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except (NoAuthorizationError, JWTExtendedException) as e:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'message': str(e)
                }), 401

            current_user = get_current_user()

            if not current_user:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'message': 'Authentication required'
                }), 401

            resource_user_id = resource_user_id_getter(*args, **kwargs)

            if not resource_user_id:
                return jsonify({
                    'success': False,
                    'error': 'Not Found',
                    'message': 'Resource not found'
                }), 404

            is_owner = current_user.id == resource_user_id
            is_admin = current_user.is_admin

            if not (is_owner or is_admin):
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'You can only access your own resources'
                }), 403

            kwargs['current_user'] = current_user
            return fn(*args, **kwargs)
        return wrapper
    return decorator
