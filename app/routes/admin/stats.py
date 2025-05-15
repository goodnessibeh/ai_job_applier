"""Admin routes for dashboard statistics."""

from flask import jsonify
from flask_login import login_required, current_user
import logging
from datetime import datetime, timedelta
from app.models import db, User, ApplicationHistory, UserSettings
from app.routes.admin.decorators import admin_required
from app.routes.admin import bp

# Setup logging
logger = logging.getLogger(__name__)

@bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        # Get user count
        user_count = User.query.count()
        
        # Get admin count
        admin_count = User.query.filter_by(is_admin=True).count()
        
        # Get application count
        application_count = ApplicationHistory.query.count()
        
        # Get active users (users who logged in during the last 24 hours)
        active_cutoff = datetime.utcnow() - timedelta(hours=24)
        active_users = User.query.filter(User.last_login >= active_cutoff).count()
        
        # Get recent users
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_user_list = []
        
        for user in recent_users:
            # Get application count for each user
            app_count = ApplicationHistory.query.filter_by(user_id=user.id).count()
            
            recent_user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'applications': app_count
            })
        
        return jsonify({
            'user_count': user_count,
            'admin_count': admin_count,
            'application_count': application_count,
            'active_users': active_users,
            'recent_users': recent_user_list
        })
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return jsonify({'error': str(e)}), 500