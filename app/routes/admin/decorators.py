"""Decorators for admin routes."""

from functools import wraps
from flask import jsonify
from flask_login import current_user

def admin_required(f):
    """Decorator to ensure the current user is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function