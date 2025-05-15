"""User routes for profile management."""

from flask import request, jsonify
from flask_login import login_required, current_user
import logging
from app.models import db
from app.routes.user import bp

# Setup logging
logger = logging.getLogger(__name__)

@bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get user profile information"""
    user_data = {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'display_name': current_user.display_name,
        'is_admin': current_user.is_admin,
        'profile_picture_url': current_user.get_profile_picture_url(),
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
        'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
        # Job preferences
        'job_titles': current_user.get_job_titles_list(),
        'min_salary': current_user.min_salary,
        'max_commute_distance': current_user.max_commute_distance,
        'preferred_locations': current_user.get_preferred_locations_list(),
        'remote_only': current_user.remote_only,
        'auto_apply_enabled': current_user.auto_apply_enabled,
        'minimum_match_score': current_user.minimum_match_score
    }
    
    return jsonify(user_data)

@bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile information (excluding profile picture)"""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Update basic profile fields
        if 'display_name' in data:
            current_user.display_name = data['display_name']
        
        # Update job preferences
        if 'job_titles' in data:
            current_user.set_job_titles_list(data['job_titles'])
            
        if 'min_salary' in data:
            current_user.min_salary = data['min_salary']
            
        if 'max_commute_distance' in data:
            current_user.max_commute_distance = data['max_commute_distance']
            
        if 'preferred_locations' in data:
            current_user.set_preferred_locations_list(data['preferred_locations'])
            
        if 'remote_only' in data:
            current_user.remote_only = data['remote_only']
            
        if 'auto_apply_enabled' in data:
            current_user.auto_apply_enabled = data['auto_apply_enabled']
            
        if 'minimum_match_score' in data:
            current_user.minimum_match_score = data['minimum_match_score']
        
        # Save changes to the database
        db.session.commit()
        
        # Return the updated user profile
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'display_name': current_user.display_name,
                'profile_picture_url': current_user.get_profile_picture_url(),
                'job_titles': current_user.get_job_titles_list(),
                'min_salary': current_user.min_salary,
                'max_commute_distance': current_user.max_commute_distance,
                'preferred_locations': current_user.get_preferred_locations_list(),
                'remote_only': current_user.remote_only,
                'auto_apply_enabled': current_user.auto_apply_enabled,
                'minimum_match_score': current_user.minimum_match_score
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500