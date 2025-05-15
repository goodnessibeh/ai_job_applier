from flask import Blueprint, request, jsonify, current_app, url_for, session, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import datetime
import os
from ..models import db, User
import secrets
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.modules.auth.linkedin_auth import LinkedInOAuth

bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = logging.getLogger(__name__)

# Initialize OAuth objects
linkedin_auth = LinkedInOAuth()

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409
    
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({'error': 'Email already exists'}), 409
    
    # Create new user
    new_user = User(
        username=username,
        email=email
    )
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Log the user in
        login_user(new_user)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'is_admin': new_user.is_admin
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Log in a regular user"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Find user by username or email
    user = User.query.filter_by(username=username).first()
    if not user:
        # Try by email
        user = User.query.filter_by(email=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Prevent admin users from logging in via the regular login endpoint
    if user.is_admin:
        return jsonify({'error': 'Please use the admin login page'}), 403
    
    # Update last login timestamp
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()
    
    # Log in the user
    login_user(user)
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': False
        }
    }), 200


@bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Log in an admin user"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Find user by username or email
    user = User.query.filter_by(username=username).first()
    if not user:
        # Try by email
        user = User.query.filter_by(email=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Verify this is an admin user
    if not user.is_admin:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    # Update last login timestamp
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()
    
    # Log in the user
    login_user(user)
    
    return jsonify({
        'message': 'Admin login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': True
        }
    }), 200


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Log out a user"""
    logout_user()
    
    # Also clear LinkedIn session if present
    if 'linkedin_access_token' in session:
        del session['linkedin_access_token']
    if 'linkedin_profile' in session:
        del session['linkedin_profile']
    if 'linkedin_auth_state' in session:
        del session['linkedin_auth_state']
    
    return jsonify({'message': 'Logout successful'}), 200


@bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user's profile"""
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'is_admin': current_user.is_admin,
            'created_at': current_user.created_at,
            'last_login': current_user.last_login
        }
    }), 200


@bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'is_admin': current_user.is_admin
            }
        }), 200
    else:
        return jsonify({'authenticated': False}), 200


@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user's password"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify current password
    if not current_user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Set new password
    current_user.set_password(new_password)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Change password error: {str(e)}")
        return jsonify({'error': 'Failed to change password'}), 500


@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't reveal that the user doesn't exist
        return jsonify({'message': 'If an account with this email exists, a reset link has been sent'}), 200
    
    # Generate reset token
    token = secrets.token_urlsafe(32)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=current_app.config.get('TOKEN_EXPIRY_HOURS', 24))
    
    # Save token to user
    user.set_reset_token(token, expiry)
    
    try:
        db.session.commit()
        
        # Send email (in a production app, this would be a separate function or service)
        reset_link = f"{request.host_url.rstrip('/')}/reset-password?token={token}"
        
        # For demo purposes, just log the link
        logger.info(f"Password reset link for {email}: {reset_link}")
        
        return jsonify({'message': 'If an account with this email exists, a reset link has been sent'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'Failed to process request'}), 500


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    token = data.get('token')
    new_password = data.get('newPassword')
    
    if not token or not new_password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Find user by token
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    # Check if token is expired
    if user.reset_token_expiry and user.reset_token_expiry < datetime.datetime.utcnow():
        user.clear_reset_token()
        db.session.commit()
        return jsonify({'error': 'Token has expired'}), 401
    
    # Set new password and clear token
    user.set_password(new_password)
    user.clear_reset_token()
    
    try:
        db.session.commit()
        return jsonify({'message': 'Password reset successful'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Reset password error: {str(e)}")
        return jsonify({'error': 'Failed to reset password'}), 500


# LinkedIn OAuth routes

@bp.route('/linkedin/login', methods=['GET'])
def linkedin_login():
    """Start LinkedIn OAuth process by redirecting to LinkedIn authorization page"""
    auth_url = linkedin_auth.get_auth_url()
    if not auth_url:
        return jsonify({'error': 'LinkedIn OAuth configuration missing'}), 500
    
    return jsonify({'auth_url': auth_url})


@bp.route('/linkedin/callback', methods=['GET'])
def linkedin_callback():
    """Handle LinkedIn OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return jsonify({'error': 'Authorization code missing'}), 400
    
    # Exchange auth code for access token
    token_data = linkedin_auth.get_access_token(code, state)
    if not token_data:
        return jsonify({'error': 'Failed to get access token'}), 400
    
    # Get user profile with access token
    user_profile = linkedin_auth.get_user_profile(token_data.get('access_token'))
    if not user_profile:
        return jsonify({'error': 'Failed to get user profile'}), 400
    
    # Success, redirect to frontend with success param
    frontend_url = request.args.get('redirect_uri', os.environ.get('FRONTEND_URL', 'http://localhost:3000'))
    return redirect(f"{frontend_url}/auth-success?provider=linkedin")


@bp.route('/linkedin/profile', methods=['GET'])
def linkedin_profile():
    """Get LinkedIn user profile if authenticated"""
    if not linkedin_auth.is_authenticated():
        return jsonify({'error': 'Not authenticated with LinkedIn'}), 401
    
    profile = session.get('linkedin_profile')
    return jsonify(profile)


@bp.route('/status', methods=['GET'])
def auth_status():
    """Check authentication status for all providers"""
    status = {
        'user': current_user.is_authenticated,
        'linkedin': linkedin_auth.is_authenticated(),
        # Add other providers here as implemented
        'indeed': False,
        'glassdoor': False
    }
    
    return jsonify(status)