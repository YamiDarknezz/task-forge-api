from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.user import User


def jwt_required_custom(fn):
    """
    Custom JWT required decorator that also loads the user
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """
    Get current authenticated user from JWT token
    """
    user_id = get_jwt_identity()
    if user_id:
        # Convert string user_id back to int (JWT identity is stored as string)
        user = User.query.get(int(user_id))
        if user and user.is_active:
            return user
    return None


def current_user_required(fn):
    """
    Decorator that requires valid JWT and active user
    Adds current_user to kwargs
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_current_user()

        if not current_user:
            return jsonify({
                'success': False,
                'error': 'User Not Found',
                'message': 'User account not found or inactive'
            }), 404

        kwargs['current_user'] = current_user
        return fn(*args, **kwargs)
    return wrapper


def optional_jwt(fn):
    """
    Decorator that allows both authenticated and unauthenticated access
    Adds current_user to kwargs if authenticated
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            current_user = get_current_user()
            kwargs['current_user'] = current_user
        except Exception:
            kwargs['current_user'] = None

        return fn(*args, **kwargs)
    return wrapper


def refresh_token_required(fn):
    """
    Decorator that requires a refresh token
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request(refresh=True)
        return fn(*args, **kwargs)
    return wrapper
