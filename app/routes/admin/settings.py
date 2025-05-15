"""Admin routes for system settings."""

from flask import request, jsonify, current_app
from flask_login import login_required, current_user
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import anthropic
import openai
from app.models import db, User, UserSettings
from app.routes.admin.decorators import admin_required
from app.routes.admin import bp

# Setup logging
logger = logging.getLogger(__name__)

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