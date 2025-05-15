"""Admin routes for user management."""

from flask import request, jsonify
from flask_login import login_required, current_user
import logging
from app.models import db, User, UserSettings, ApplicationHistory
from app.routes.admin.decorators import admin_required
from app.routes.admin import bp

# Setup logging
logger = logging.getLogger(__name__)

@bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """Get all users for admin"""
    try:
        users = User.query.all()
        
        user_list = []
        for user in users:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'display_name': user.display_name,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'profile_picture_url': user.get_profile_picture_url(),
                'profile_picture_updated_at': user.profile_picture_updated_at.isoformat() if user.profile_picture_updated_at else None
            }
            user_list.append(user_dict)
        
        return jsonify({'users': user_list})
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    """Get a specific user for admin"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Get user settings
        user_settings = UserSettings.query.filter_by(user_id=user.id).first()
        
        # Get application count
        application_count = ApplicationHistory.query.filter_by(user_id=user.id).count()
        
        user_dict = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'display_name': user.display_name,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'profile_picture_url': user.get_profile_picture_url(),
            'profile_picture_updated_at': user.profile_picture_updated_at.isoformat() if user.profile_picture_updated_at else None,
            'application_count': application_count,
            'settings': {
                'notifications_enabled': user_settings.notifications_enabled if user_settings else False,
                'max_applications_per_day': user_settings.max_applications_per_day if user_settings else 10
            }
        }
        
        return jsonify({'user': user_dict})
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    """Create a new user as admin"""
    data = request.json
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    try:
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
            
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            display_name=data.get('display_name', data['username']),
            is_admin=data.get('is_admin', False)
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create user settings if needed
        if 'settings' in data:
            user_settings = UserSettings(
                user_id=new_user.id,
                notifications_enabled=data['settings'].get('notifications_enabled', False),
                max_applications_per_day=data['settings'].get('max_applications_per_day', 10)
            )
            db.session.add(user_settings)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user_id': new_user.id
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    """Update a user as admin"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update user fields
        if 'username' in data:
            # Check if username already exists (for a different user)
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Username already exists'}), 400
            user.username = data['username']
            
        if 'email' in data:
            # Check if email already exists (for a different user)
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']
            
        if 'display_name' in data:
            user.display_name = data['display_name']
            
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
            
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        
        # Update user settings if needed
        if 'settings' in data:
            user_settings = UserSettings.query.filter_by(user_id=user.id).first()
            
            if not user_settings:
                user_settings = UserSettings(user_id=user.id)
                db.session.add(user_settings)
            
            if 'notifications_enabled' in data['settings']:
                user_settings.notifications_enabled = data['settings']['notifications_enabled']
                
            if 'max_applications_per_day' in data['settings']:
                user_settings.max_applications_per_day = data['settings']['max_applications_per_day']
            
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user as admin"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete your own admin account'}), 400
        
        # Delete user settings
        user_settings = UserSettings.query.filter_by(user_id=user.id).first()
        if user_settings:
            db.session.delete(user_settings)
        
        # Delete user's application history
        ApplicationHistory.query.filter_by(user_id=user.id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': str(e)}), 500