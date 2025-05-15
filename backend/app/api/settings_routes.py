from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import os
import json
from dotenv import set_key
from app.config import Config
from ..models import db, UserSettings

bp = Blueprint('settings', __name__, url_prefix='/api/settings')

@bp.route('/save', methods=['POST'])
@login_required
def save_settings():
    """Save user settings"""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Find or create user settings
        user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
        if not user_settings:
            user_settings = UserSettings(user_id=current_user.id)
            db.session.add(user_settings)
        
        # Update settings - ONLY user-specific settings are allowed
        
        # User can change their display name if provided
        if 'user' in data and 'display_name' in data['user']:
            # This would need to be added to the User model
            user = current_user
            user.display_name = data['user']['display_name']
        
        # Allow users to change their password
        if 'user' in data and 'current_password' in data['user'] and 'new_password' in data['user']:
            user = current_user
            if user.check_password(data['user']['current_password']):
                user.set_password(data['user']['new_password'])
            else:
                return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Application settings (only max_applications_per_day is accessible to regular users)
        if 'application' in data:
            user_settings.max_applications_per_day = data['application'].get('max_applications_per_day', user_settings.max_applications_per_day)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Settings saved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/get', methods=['GET'])
@login_required
def get_settings():
    """Get user settings"""
    # Find user settings
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    
    if not user_settings:
        # Return defaults if no settings found - only for user settings, not API keys
        settings = {
            'user': {
                'username': current_user.username,
                'email': current_user.email,
                'display_name': getattr(current_user, 'display_name', current_user.username),
            },
            'application': {
                'max_applications_per_day': 10
            },
            'system': {
                'ai_enabled': True,  # Just indicate if AI features are enabled
                'job_portals_enabled': True  # Just indicate if job portal integrations are available
            }
        }
    else:
        settings = {
            'user': {
                'username': current_user.username,
                'email': current_user.email,
                'display_name': getattr(current_user, 'display_name', current_user.username),
            },
            'application': {
                'max_applications_per_day': user_settings.max_applications_per_day
            },
            'system': {
                'ai_enabled': user_settings.use_anthropic or user_settings.use_openai,
                'job_portals_enabled': user_settings.use_linkedin or user_settings.use_indeed or user_settings.use_glassdoor
            }
        }
    
    return jsonify(settings)


@bp.route('/test-smtp', methods=['POST'])
@login_required
def test_smtp():
    """Test SMTP connection (admin only)"""
    # Only allow admins to test SMTP
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized. Only admins can test SMTP settings'}), 403
        
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    import smtplib
    from email.mime.text import MIMEText
    
    smtp_server = data.get('server')
    smtp_port = data.get('port')
    username = data.get('username')
    password = data.get('password')
    from_email = data.get('from_email')
    test_recipient = data.get('test_recipient', current_user.email)
    
    if not all([smtp_server, smtp_port, username, password, from_email, test_recipient]):
        return jsonify({'error': 'Missing required SMTP parameters'}), 400
    
    try:
        # Create message
        msg = MIMEText("This is a test email from AI Job Applier to verify your SMTP settings.")
        msg['Subject'] = "AI Job Applier - SMTP Test"
        msg['From'] = from_email
        msg['To'] = test_recipient
        
        # Connect to server and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        
        return jsonify({'success': True, 'message': f'Test email sent to {test_recipient}'})
    except Exception as e:
        return jsonify({'error': f'SMTP test failed: {str(e)}'}), 500


@bp.route('/system', methods=['GET'])
@login_required
def get_system_settings():
    """Get system settings (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Helper to safely mask API keys
    def mask_api_key(key, visible_chars=4):
        if not key:
            return ''
        if len(key) <= visible_chars * 2:
            return '*' * len(key)  # If key is too short, mask all
        return key[:visible_chars] + '*' * (len(key) - visible_chars * 2) + key[-visible_chars:]
    
    settings = {
        'openai': {
            'enabled': bool(Config.OPENAI_API_KEY),
            'api_key': mask_api_key(Config.OPENAI_API_KEY),
            'has_key': bool(Config.OPENAI_API_KEY),
            'key_placeholder': '(API key set)'
        },
        'anthropic': {
            'enabled': Config.USE_ANTHROPIC,
            'api_key': mask_api_key(Config.ANTHROPIC_API_KEY),
            'has_key': bool(Config.ANTHROPIC_API_KEY),
            'key_placeholder': '(API key set)'
        },
        'linkedin': {
            'enabled': bool(Config.LINKEDIN_CLIENT_ID and Config.LINKEDIN_CLIENT_SECRET),
            'client_id': Config.LINKEDIN_CLIENT_ID,
            'client_secret': mask_api_key(Config.LINKEDIN_CLIENT_SECRET),
            'has_secret': bool(Config.LINKEDIN_CLIENT_SECRET),
            'secret_placeholder': '(Client secret set)',
            'redirect_uri': Config.LINKEDIN_REDIRECT_URI
        },
        'indeed': {
            'enabled': bool(Config.INDEED_PUBLISHER_ID and Config.INDEED_API_KEY),
            'publisher_id': Config.INDEED_PUBLISHER_ID,
            'api_key': mask_api_key(Config.INDEED_API_KEY),
            'has_key': bool(Config.INDEED_API_KEY),
            'key_placeholder': '(API key set)'
        },
        'glassdoor': {
            'enabled': bool(Config.GLASSDOOR_PARTNER_ID and Config.GLASSDOOR_API_KEY),
            'partner_id': Config.GLASSDOOR_PARTNER_ID,
            'api_key': mask_api_key(Config.GLASSDOOR_API_KEY),
            'has_key': bool(Config.GLASSDOOR_API_KEY),
            'key_placeholder': '(API key set)'
        },
        'application': {
            'simulation_mode': Config.SIMULATION_MODE,
            'max_applications_per_day': Config.MAX_APPLICATIONS_PER_DAY
        },
        'smtp': {
            'server': Config.SMTP_SERVER,
            'port': Config.SMTP_PORT,
            'username': Config.SMTP_USERNAME,
            'password': '********' if Config.SMTP_PASSWORD else '',
            'has_password': bool(Config.SMTP_PASSWORD),
            'password_placeholder': '(Password set)',
            'from_email': Config.SMTP_FROM_EMAIL,
            'enabled': Config.NOTIFICATIONS_ENABLED
        }
    }
    
    return jsonify(settings)


@bp.route('/system/save', methods=['POST'])
@login_required
def save_system_settings():
    """Save system settings (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # In a production environment, sensitive data would be encrypted before storing
        # For this demo, we'll write to .env file (not ideal for security)
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.env')
        
        # OpenAI settings
        if 'openai' in data:
            # Don't overwrite existing API key if blank or placeholder value is sent
            if 'api_key' in data['openai']:
                api_key = data['openai']['api_key']
                # Only save if it's a new key, not a placeholder or blank value
                if api_key and not api_key.startswith('(') and not api_key.startswith('*'):
                    set_key(env_file, 'OPENAI_API_KEY', api_key)
            if 'enabled' in data['openai']:
                set_key(env_file, 'USE_OPENAI', str(data['openai']['enabled']))
        
        # Anthropic settings
        if 'anthropic' in data:
            # Don't overwrite existing API key if blank or placeholder value is sent
            if 'api_key' in data['anthropic']:
                api_key = data['anthropic']['api_key']
                # Only save if it's a new key, not a placeholder or blank value
                if api_key and not api_key.startswith('(') and not api_key.startswith('*'):
                    set_key(env_file, 'ANTHROPIC_API_KEY', api_key)
            if 'enabled' in data['anthropic']:
                set_key(env_file, 'USE_ANTHROPIC', str(data['anthropic']['enabled']))
        
        # LinkedIn settings
        if 'linkedin' in data:
            if 'client_id' in data['linkedin']:
                client_id = data['linkedin']['client_id']
                if client_id:  # Allow clearing client_id
                    set_key(env_file, 'LINKEDIN_CLIENT_ID', client_id)
                
            if 'client_secret' in data['linkedin']:
                client_secret = data['linkedin']['client_secret']
                # Only save if it's a new secret, not a placeholder or blank value
                if client_secret and not client_secret.startswith('(') and not client_secret.startswith('*'):
                    set_key(env_file, 'LINKEDIN_CLIENT_SECRET', client_secret)
                    
            if 'redirect_uri' in data['linkedin']:
                redirect_uri = data['linkedin']['redirect_uri']
                if redirect_uri:  # Allow clearing redirect_uri
                    set_key(env_file, 'LINKEDIN_REDIRECT_URI', redirect_uri)
        
        # Indeed settings
        if 'indeed' in data:
            if 'publisher_id' in data['indeed']:
                publisher_id = data['indeed']['publisher_id']
                if publisher_id:  # Allow clearing publisher_id
                    set_key(env_file, 'INDEED_PUBLISHER_ID', publisher_id)
                
            if 'api_key' in data['indeed']:
                api_key = data['indeed']['api_key']
                # Only save if it's a new key, not a placeholder or blank value
                if api_key and not api_key.startswith('(') and not api_key.startswith('*'):
                    set_key(env_file, 'INDEED_API_KEY', api_key)
        
        # Glassdoor settings
        if 'glassdoor' in data:
            if 'partner_id' in data['glassdoor']:
                partner_id = data['glassdoor']['partner_id']
                if partner_id:  # Allow clearing partner_id
                    set_key(env_file, 'GLASSDOOR_PARTNER_ID', partner_id)
                
            if 'api_key' in data['glassdoor']:
                api_key = data['glassdoor']['api_key']
                # Only save if it's a new key, not a placeholder or blank value
                if api_key and not api_key.startswith('(') and not api_key.startswith('*'):
                    set_key(env_file, 'GLASSDOOR_API_KEY', api_key)
        
        # SMTP settings
        if 'smtp' in data:
            smtp_data = data['smtp']
            if 'server' in smtp_data:
                server = smtp_data['server']
                if server:  # Allow clearing server
                    set_key(env_file, 'SMTP_SERVER', server)
                
            if 'port' in smtp_data:
                set_key(env_file, 'SMTP_PORT', str(smtp_data['port']))
                
            if 'username' in smtp_data:
                username = smtp_data['username']
                if username:  # Allow clearing username
                    set_key(env_file, 'SMTP_USERNAME', username)
                
            if 'password' in smtp_data:
                password = smtp_data['password']
                # Only save if it's a new password, not a placeholder or blank value
                if password and not password.startswith('(') and not password.startswith('*'):
                    set_key(env_file, 'SMTP_PASSWORD', password)
                
            if 'from_email' in smtp_data:
                from_email = smtp_data['from_email']
                if from_email:  # Allow clearing from_email
                    set_key(env_file, 'SMTP_FROM_EMAIL', from_email)
                
            if 'enabled' in smtp_data:
                set_key(env_file, 'NOTIFICATIONS_ENABLED', str(smtp_data['enabled']))
        
        # Application settings
        if 'application' in data:
            if 'simulation_mode' in data['application']:
                set_key(env_file, 'SIMULATION_MODE', str(data['application']['simulation_mode']))
                
            if 'max_applications_per_day' in data['application']:
                set_key(env_file, 'MAX_APPLICATIONS_PER_DAY', str(data['application']['max_applications_per_day']))
        
        return jsonify({'success': True, 'message': 'System settings saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/change-password', methods=['POST'])
@login_required
def admin_change_password():
    """Change password for admin (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new password are required'}), 400
        
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Set new password
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500