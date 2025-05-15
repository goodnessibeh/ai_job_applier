from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import anthropic
import openai
from ..models import db, User, UserSettings

# Setup logging
logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Admin Routes
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
        from ..models import ApplicationHistory
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
        from ..models import ApplicationHistory
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

@bp.route('/settings', methods=['GET'])
@login_required
@admin_required
def get_admin_settings():
    """Get admin settings"""
    try:
        # Get global user settings with all config parameters
        global_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
        
        if not global_settings:
            # Create default settings if they don't exist
            global_settings = UserSettings(user_id=current_user.id)
            db.session.add(global_settings)
            db.session.commit()
        
        # Prepare settings response
        settings = {
            'smtp_server': global_settings.smtp_server,
            'smtp_port': global_settings.smtp_port,
            'smtp_username': global_settings.smtp_username,
            'smtp_password': global_settings.smtp_password,
            'smtp_from_email': global_settings.smtp_from_email,
            'notifications_enabled': global_settings.notifications_enabled,
            'anthropic_api_key': global_settings.anthropic_api_key,
            'openai_api_key': global_settings.openai_api_key,
            'use_anthropic': global_settings.use_anthropic,
            'use_openai': global_settings.use_openai,
            'max_applications_per_day': global_settings.max_applications_per_day
        }
        
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        logger.error(f"Error getting admin settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/settings', methods=['POST'])
@login_required
@admin_required
def update_admin_settings():
    """Update admin settings"""
    data = request.json
    
    if not data or 'settings' not in data:
        return jsonify({'error': 'No settings provided'}), 400
    
    try:
        # Get admin settings
        admin_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
        
        if not admin_settings:
            # Create settings if they don't exist
            admin_settings = UserSettings(user_id=current_user.id)
            db.session.add(admin_settings)
        
        settings_data = data['settings']
        
        # Update SMTP settings
        if 'smtp_server' in settings_data:
            admin_settings.smtp_server = settings_data['smtp_server']
        if 'smtp_port' in settings_data:
            admin_settings.smtp_port = settings_data['smtp_port']
        if 'smtp_username' in settings_data:
            admin_settings.smtp_username = settings_data['smtp_username']
        if 'smtp_password' in settings_data:
            admin_settings.smtp_password = settings_data['smtp_password']
        if 'smtp_from_email' in settings_data:
            admin_settings.smtp_from_email = settings_data['smtp_from_email']
        if 'notifications_enabled' in settings_data:
            admin_settings.notifications_enabled = settings_data['notifications_enabled']
        
        # Update API keys
        if 'anthropic_api_key' in settings_data:
            admin_settings.anthropic_api_key = settings_data['anthropic_api_key']
        if 'openai_api_key' in settings_data:
            admin_settings.openai_api_key = settings_data['openai_api_key']
        
        # Update preferences
        if 'use_anthropic' in settings_data:
            admin_settings.use_anthropic = settings_data['use_anthropic']
        if 'use_openai' in settings_data:
            admin_settings.use_openai = settings_data['use_openai']
        
        # Update application settings
        if 'max_applications_per_day' in settings_data:
            admin_settings.max_applications_per_day = settings_data['max_applications_per_day']
        
        # Update timestamps
        admin_settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating admin settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/test-smtp', methods=['POST'])
@login_required
@admin_required
def test_smtp_connection():
    """Test SMTP connection"""
    data = request.json
    
    if not data or 'smtp_settings' not in data:
        return jsonify({'error': 'No SMTP settings provided'}), 400
    
    smtp_settings = data['smtp_settings']
    
    if not all(k in smtp_settings for k in ('server', 'port', 'username', 'password', 'from_email')):
        return jsonify({'error': 'Incomplete SMTP settings'}), 400
    
    try:
        # Create test message
        message = MIMEMultipart('alternative')
        message['Subject'] = 'AI Job Applier - SMTP Test'
        message['From'] = smtp_settings['from_email']
        message['To'] = current_user.email
        
        text = "This is a test email from AI Job Applier to verify SMTP settings."
        html = f"""
        <html>
          <head></head>
          <body>
            <p>This is a test email from AI Job Applier to verify SMTP settings.</p>
            <p>Your SMTP settings are working correctly!</p>
            <p>Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
          </body>
        </html>
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        message.attach(part1)
        message.attach(part2)
        
        # Connect to SMTP server
        port = int(smtp_settings['port'])
        
        if port == 465:  # SSL
            server = smtplib.SMTP_SSL(smtp_settings['server'], port)
        else:  # TLS
            server = smtplib.SMTP(smtp_settings['server'], port)
            server.ehlo()
            server.starttls()
            server.ehlo()
        
        server.login(smtp_settings['username'], smtp_settings['password'])
        server.sendmail(smtp_settings['from_email'], current_user.email, message.as_string())
        server.close()
        
        return jsonify({
            'success': True,
            'message': 'SMTP test successful'
        })
    except Exception as e:
        logger.error(f"SMTP test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/test-api-key', methods=['POST'])
@login_required
@admin_required
def test_api_key():
    """Test API key for Anthropic or OpenAI"""
    data = request.json
    
    if not data or not all(k in data for k in ('provider', 'api_key')):
        return jsonify({'error': 'Provider and API key are required'}), 400
    
    provider = data['provider']
    api_key = data['api_key']
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    try:
        if provider == 'anthropic':
            # Test Anthropic API key
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Say hello for API key validation"}
                ]
            )
            
            if response and hasattr(response, 'content'):
                return jsonify({
                    'success': True,
                    'message': 'Anthropic API key validation successful'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Invalid response from Anthropic API'
                }), 400
                
        elif provider == 'openai':
            # Test OpenAI API key
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello for API key validation"}
                ],
                max_tokens=10
            )
            
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                return jsonify({
                    'success': True,
                    'message': 'OpenAI API key validation successful'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Invalid response from OpenAI API'
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown provider: {provider}'
            }), 400
    except Exception as e:
        logger.error(f"API key test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/dashboard/stats', methods=['GET'])
@login_required
@admin_required
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        # Get user count
        user_count = User.query.count()
        
        # Get application count
        from ..models import ApplicationHistory
        application_count = ApplicationHistory.query.count()
        
        # Get active users (users who logged in during the last 24 hours)
        from datetime import timedelta
        active_cutoff = datetime.utcnow() - timedelta(hours=24)
        active_users = User.query.filter(User.last_login >= active_cutoff).count()
        
        return jsonify({
            'stats': {
                'totalUsers': user_count,
                'totalApplications': application_count,
                'activeUsers': active_users
            }
        })
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/users/recent', methods=['GET'])
@login_required
@admin_required
def get_recent_users():
    """Get recent users for admin dashboard"""
    try:
        # Get recent users with last login
        recent_users = User.query.order_by(User.last_login.desc().nullslast()).limit(5).all()
        users_list = []
        
        for user in recent_users:
            # Get application count for each user
            from ..models import ApplicationHistory
            app_count = ApplicationHistory.query.filter_by(user_id=user.id).count()
            
            users_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'lastLogin': user.last_login.isoformat() if user.last_login else None,
                'applications': app_count
            })
        
        return jsonify({
            'users': users_list
        })
    except Exception as e:
        logger.error(f"Error getting recent users: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
        from ..models import ApplicationHistory
        application_count = ApplicationHistory.query.count()
        
        # Get active users (users who logged in during the last 24 hours)
        from datetime import timedelta
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