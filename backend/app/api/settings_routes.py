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
        
        # Update settings
        
        # SMTP settings
        if 'smtp' in data:
            smtp_data = data['smtp']
            user_settings.smtp_server = smtp_data.get('server', user_settings.smtp_server)
            user_settings.smtp_port = smtp_data.get('port', user_settings.smtp_port)
            user_settings.smtp_username = smtp_data.get('username', user_settings.smtp_username)
            if 'password' in smtp_data and smtp_data['password']:  # Only update if provided
                user_settings.smtp_password = smtp_data['password']
            user_settings.smtp_from_email = smtp_data.get('from_email', user_settings.smtp_from_email)
            user_settings.notifications_enabled = smtp_data.get('enabled', user_settings.notifications_enabled)
        
        # OpenAI/Anthropic settings
        if 'openai' in data:
            user_settings.openai_api_key = data['openai'].get('api_key', user_settings.openai_api_key)
            user_settings.use_openai = data['openai'].get('enabled', user_settings.use_openai)
        
        if 'anthropic' in data:
            user_settings.anthropic_api_key = data['anthropic'].get('api_key', user_settings.anthropic_api_key)
            user_settings.use_anthropic = data['anthropic'].get('enabled', user_settings.use_anthropic)
        
        # LinkedIn settings
        if 'linkedin' in data:
            user_settings.linkedin_client_id = data['linkedin'].get('client_id', user_settings.linkedin_client_id)
            user_settings.linkedin_client_secret = data['linkedin'].get('client_secret', user_settings.linkedin_client_secret)
            user_settings.use_linkedin = data['linkedin'].get('enabled', user_settings.use_linkedin)
        
        # Indeed settings
        if 'indeed' in data:
            user_settings.indeed_publisher_id = data['indeed'].get('publisher_id', user_settings.indeed_publisher_id)
            user_settings.indeed_api_key = data['indeed'].get('api_key', user_settings.indeed_api_key)
            user_settings.use_indeed = data['indeed'].get('enabled', user_settings.use_indeed)
        
        # Glassdoor settings
        if 'glassdoor' in data:
            user_settings.glassdoor_partner_id = data['glassdoor'].get('partner_id', user_settings.glassdoor_partner_id)
            user_settings.glassdoor_api_key = data['glassdoor'].get('api_key', user_settings.glassdoor_api_key)
            user_settings.use_glassdoor = data['glassdoor'].get('enabled', user_settings.use_glassdoor)
        
        # Application settings
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
        # Return defaults if no settings found
        settings = {
            'smtp': {
                'server': '',
                'port': 587,
                'username': '',
                'password': '',  # Never return actual password
                'from_email': '',
                'enabled': False
            },
            'openai': {
                'enabled': False,
                'api_key': ''  # Masked in production
            },
            'anthropic': {
                'enabled': True,
                'api_key': ''  # Masked in production
            },
            'linkedin': {
                'enabled': False,
                'client_id': '',
                'client_secret': ''  # Masked in production
            },
            'indeed': {
                'enabled': False,
                'publisher_id': '',
                'api_key': ''  # Masked in production
            },
            'glassdoor': {
                'enabled': False,
                'partner_id': '',
                'api_key': ''  # Masked in production
            },
            'application': {
                'max_applications_per_day': 10
            }
        }
    else:
        # In a production app, don't return actual API keys/passwords
        is_debug = current_app.debug
        
        # Helper to mask sensitive data
        def mask_string(s, show_chars=4):
            if not s:
                return ''
            if is_debug:
                return s
            return s[:show_chars] + '*' * (len(s) - show_chars) if s else ''
        
        settings = {
            'smtp': {
                'server': user_settings.smtp_server or '',
                'port': user_settings.smtp_port or 587,
                'username': user_settings.smtp_username or '',
                'password': '********' if user_settings.smtp_password else '',  # Never return actual password
                'from_email': user_settings.smtp_from_email or '',
                'enabled': user_settings.notifications_enabled
            },
            'openai': {
                'enabled': user_settings.use_openai,
                'api_key': mask_string(user_settings.openai_api_key)
            },
            'anthropic': {
                'enabled': user_settings.use_anthropic,
                'api_key': mask_string(user_settings.anthropic_api_key)
            },
            'linkedin': {
                'enabled': user_settings.use_linkedin,
                'client_id': user_settings.linkedin_client_id or '',
                'client_secret': mask_string(user_settings.linkedin_client_secret)
            },
            'indeed': {
                'enabled': user_settings.use_indeed,
                'publisher_id': user_settings.indeed_publisher_id or '',
                'api_key': mask_string(user_settings.indeed_api_key)
            },
            'glassdoor': {
                'enabled': user_settings.use_glassdoor,
                'partner_id': user_settings.glassdoor_partner_id or '',
                'api_key': mask_string(user_settings.glassdoor_api_key)
            },
            'application': {
                'max_applications_per_day': user_settings.max_applications_per_day
            }
        }
    
    return jsonify(settings)


@bp.route('/test-smtp', methods=['POST'])
@login_required
def test_smtp():
    """Test SMTP connection"""
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
    
    settings = {
        'openai': {
            'enabled': bool(Config.OPENAI_API_KEY),
            'api_key': Config.OPENAI_API_KEY if current_app.debug else '********'
        },
        'anthropic': {
            'enabled': Config.USE_ANTHROPIC,
            'api_key': Config.ANTHROPIC_API_KEY if current_app.debug else '********'
        },
        'linkedin': {
            'enabled': bool(Config.LINKEDIN_CLIENT_ID and Config.LINKEDIN_CLIENT_SECRET),
            'client_id': Config.LINKEDIN_CLIENT_ID if current_app.debug else '',
            'client_secret': '' if not current_app.debug else (Config.LINKEDIN_CLIENT_SECRET[:5] + '*****' if Config.LINKEDIN_CLIENT_SECRET else ''),
            'redirect_uri': Config.LINKEDIN_REDIRECT_URI
        },
        'indeed': {
            'enabled': bool(Config.INDEED_PUBLISHER_ID and Config.INDEED_API_KEY),
            'publisher_id': Config.INDEED_PUBLISHER_ID if current_app.debug else '',
            'api_key': '' if not current_app.debug else (Config.INDEED_API_KEY[:5] + '*****' if Config.INDEED_API_KEY else '')
        },
        'glassdoor': {
            'enabled': bool(Config.GLASSDOOR_PARTNER_ID and Config.GLASSDOOR_API_KEY),
            'partner_id': Config.GLASSDOOR_PARTNER_ID if current_app.debug else '',
            'api_key': '' if not current_app.debug else (Config.GLASSDOOR_API_KEY[:5] + '*****' if Config.GLASSDOOR_API_KEY else '')
        },
        'application': {
            'simulation_mode': Config.SIMULATION_MODE,
            'max_applications_per_day': Config.MAX_APPLICATIONS_PER_DAY
        },
        'smtp': {
            'server': Config.SMTP_SERVER,
            'port': Config.SMTP_PORT,
            'username': Config.SMTP_USERNAME,
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
        # In a production environment, these would be securely stored
        # For this demo, we'll write to .env file (not ideal for security)
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.env')
        
        # OpenAI settings
        if 'openai' in data:
            if 'api_key' in data['openai']:
                set_key(env_file, 'OPENAI_API_KEY', data['openai']['api_key'])
        
        # Anthropic settings
        if 'anthropic' in data:
            if 'api_key' in data['anthropic']:
                set_key(env_file, 'ANTHROPIC_API_KEY', data['anthropic']['api_key'])
            if 'enabled' in data['anthropic']:
                set_key(env_file, 'USE_ANTHROPIC', str(data['anthropic']['enabled']))
        
        # LinkedIn settings
        if 'linkedin' in data:
            if 'client_id' in data['linkedin']:
                set_key(env_file, 'LINKEDIN_CLIENT_ID', data['linkedin']['client_id'])
            if 'client_secret' in data['linkedin']:
                set_key(env_file, 'LINKEDIN_CLIENT_SECRET', data['linkedin']['client_secret'])
            if 'redirect_uri' in data['linkedin']:
                set_key(env_file, 'LINKEDIN_REDIRECT_URI', data['linkedin']['redirect_uri'])
        
        # Indeed settings
        if 'indeed' in data:
            if 'publisher_id' in data['indeed']:
                set_key(env_file, 'INDEED_PUBLISHER_ID', data['indeed']['publisher_id'])
            if 'api_key' in data['indeed']:
                set_key(env_file, 'INDEED_API_KEY', data['indeed']['api_key'])
        
        # Glassdoor settings
        if 'glassdoor' in data:
            if 'partner_id' in data['glassdoor']:
                set_key(env_file, 'GLASSDOOR_PARTNER_ID', data['glassdoor']['partner_id'])
            if 'api_key' in data['glassdoor']:
                set_key(env_file, 'GLASSDOOR_API_KEY', data['glassdoor']['api_key'])
        
        # SMTP settings
        if 'smtp' in data:
            smtp_data = data['smtp']
            if 'server' in smtp_data:
                set_key(env_file, 'SMTP_SERVER', smtp_data['server'])
            if 'port' in smtp_data:
                set_key(env_file, 'SMTP_PORT', str(smtp_data['port']))
            if 'username' in smtp_data:
                set_key(env_file, 'SMTP_USERNAME', smtp_data['username'])
            if 'password' in smtp_data and smtp_data['password']:
                set_key(env_file, 'SMTP_PASSWORD', smtp_data['password'])
            if 'from_email' in smtp_data:
                set_key(env_file, 'SMTP_FROM_EMAIL', smtp_data['from_email'])
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