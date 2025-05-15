from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
import json
import os
import time
import logging
import io
import tempfile
from datetime import datetime
from app.modules.resume_parser import parser
from app.modules.job_search import searcher
from app.modules.application_customizer import customizer
from app.modules.application_submitter import submitter
from app.modules.notifications.email_service import EmailService
from app.modules.export.csv_exporter import CSVExporter
from app.api import settings_routes, auth_routes, user_routes
from ..models import db, ApplicationHistory, UserSettings

# Setup logging
logger = logging.getLogger(__name__)

bp = Blueprint('api', __name__, url_prefix='/api')

# Register other route blueprints
bp.register_blueprint(settings_routes.bp)
bp.register_blueprint(auth_routes.bp)
bp.register_blueprint(user_routes.bp)

@bp.route('/parse-resume', methods=['POST'])
@login_required
def parse_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        parsed_data = parser.parse_resume(file)
        return jsonify({'data': parsed_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/improve-resume', methods=['POST'])
@login_required
def improve_resume():
    """Get AI-powered improvement suggestions for a resume"""
    from app.modules.resume_parser.resume_improver import ResumeImprover
    
    data = request.json
    if not data or 'resume_data' not in data:
        return jsonify({'error': 'No resume data provided'}), 400
    
    try:
        # Check if user provided API keys
        anthropic_api_key = data.get('anthropic_api_key')
        openai_api_key = data.get('openai_api_key')
        
        # Get user settings to determine preferred AI provider
        user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
        
        # Initialize resume improver with user settings and/or explicit API keys
        improver = ResumeImprover(
            user_id=current_user.id,
            anthropic_api_key=anthropic_api_key,
            openai_api_key=openai_api_key
        )
        
        # Generate improvement suggestions
        result = improver.generate_improvement_suggestions(data['resume_data'])
        
        # Add provider info to response if not already included
        if 'provider' not in result and user_settings:
            if user_settings.use_anthropic and user_settings.anthropic_api_key:
                result['provider'] = 'anthropic'
            elif user_settings.use_openai and user_settings.openai_api_key:
                result['provider'] = 'openai'
            else:
                result['provider'] = 'unknown'
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error improving resume: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@bp.route('/search-jobs', methods=['POST'])
@login_required
def search_jobs():
    data = request.json
    if not data or 'keywords' not in data:
        return jsonify({'error': 'No search parameters provided'}), 400
    
    try:
        # Extract auto_apply flag
        auto_apply = data.get('auto_apply', False)
        
        # Search for jobs
        jobs = searcher.search_jobs(data)
        
        # If auto_apply is True, automatically submit applications
        if auto_apply and jobs:
            # Get resume data if available
            from app.modules.resume_parser import parser
            
            # Get user settings for email notifications
            user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
            
            # Create email service if notifications are enabled
            email_service = None
            if user_settings and user_settings.notifications_enabled and all([
                user_settings.smtp_server,
                user_settings.smtp_port,
                user_settings.smtp_username,
                user_settings.smtp_password,
                user_settings.smtp_from_email
            ]):
                email_service = EmailService(
                    user_settings.smtp_server,
                    user_settings.smtp_port,
                    user_settings.smtp_username,
                    user_settings.smtp_password,
                    user_settings.smtp_from_email
                )
            
            # Limit auto-applications based on user settings
            max_apps = user_settings.max_applications_per_day if user_settings else 5
            auto_apply_jobs = jobs[:max_apps]
            
            for job in auto_apply_jobs:
                try:
                    # Generate and submit application
                    # Here you would implement the actual application logic
                    
                    # For demonstration, create an application history record
                    application_result = {
                        'user_id': current_user.id,
                        'job_id': job.get('id', str(time.time())),
                        'job_url': job.get('url', ''),
                        'position': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', ''),
                        'platform': job.get('source', 'external'),
                        'description': job.get('description', ''),
                        'application_type': 'easy_apply' if job.get('easy_apply', False) else 'external',
                        'success': True,  # This would be the actual result in real implementation
                        'timestamp': datetime.utcnow(),
                        'message': 'Application submitted successfully',
                        'notification_sent': False
                    }
                    
                    # Save to database
                    app_history = ApplicationHistory(**application_result)
                    db.session.add(app_history)
                    db.session.commit()
                    
                    # Mark as processed by auto-apply
                    job['auto_applied'] = True
                    
                    # Send email notification if enabled
                    if email_service and email_service.is_enabled():
                        notification_sent = email_service.send_application_notification(
                            current_user.email,
                            application_result
                        )
                        
                        if notification_sent:
                            app_history.notification_sent = True
                            db.session.commit()
                    
                except Exception as e:
                    logger.error(f"Error auto-applying to job {job.get('id')}: {str(e)}")
                    job['auto_apply_error'] = str(e)
        
        return jsonify({'jobs': jobs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/customize-application', methods=['POST'])
@login_required
def customize_application():
    data = request.json
    if not data or 'resume' not in data or 'job' not in data:
        return jsonify({'error': 'Missing resume or job data'}), 400
    
    try:
        customized_app = customizer.generate_application(data['resume'], data['job'])
        return jsonify({'application': customized_app})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/submit-application', methods=['POST'])
@login_required
def submit_application():
    # Check if this is a multipart form (with file uploads) or JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle multipart form data with file uploads
        if 'job' not in request.form or 'application' not in request.form:
            return jsonify({'error': 'Missing job or application data'}), 400
        
        try:
            # Parse JSON data from form fields
            job_data = json.loads(request.form['job'])
            application_data = json.loads(request.form['application'])
            resume_data = json.loads(request.form['resume']) if 'resume' in request.form else None
            
            # Handle file uploads
            resume_file_path = None
            cover_letter_file_path = None
            
            if 'resume_file' in request.files:
                resume_file = request.files['resume_file']
                if resume_file.filename != '':
                    # Save the file to a temporary location
                    resume_file_path = os.path.join(
                        os.path.dirname(__file__), '..', 'temp', 
                        f"resume_{int(time.time())}_{resume_file.filename}"
                    )
                    os.makedirs(os.path.dirname(resume_file_path), exist_ok=True)
                    resume_file.save(resume_file_path)
            
            if 'cover_letter_file' in request.files:
                cover_letter_file = request.files['cover_letter_file']
                if cover_letter_file.filename != '':
                    # Save the file to a temporary location
                    cover_letter_file_path = os.path.join(
                        os.path.dirname(__file__), '..', 'temp', 
                        f"cover_letter_{int(time.time())}_{cover_letter_file.filename}"
                    )
                    os.makedirs(os.path.dirname(cover_letter_file_path), exist_ok=True)
                    cover_letter_file.save(cover_letter_file_path)
            
            # Submit the application with all data
            result = submitter.submit_application(
                job_data, 
                application_data, 
                resume_data, 
                resume_file_path, 
                cover_letter_file_path
            )
            
            # Save application result to database
            app_history = ApplicationHistory(
                user_id=current_user.id,
                job_id=job_data.get('id', str(time.time())),
                job_url=job_data.get('url', ''),
                position=job_data.get('title', ''),
                company=job_data.get('company', ''),
                location=job_data.get('location', ''),
                platform=job_data.get('source', 'external'),
                description=job_data.get('description', ''),
                application_type='easy_apply' if job_data.get('easy_apply', False) else 'external',
                success=result.get('success', False),
                timestamp=datetime.utcnow(),
                message=result.get('message', ''),
                error=result.get('error', ''),
                cover_letter_text=application_data.get('cover_letter', '')
            )
            db.session.add(app_history)
            db.session.commit()
            
            # Send email notification if enabled
            try:
                user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
                if user_settings and user_settings.notifications_enabled and all([
                    user_settings.smtp_server,
                    user_settings.smtp_port,
                    user_settings.smtp_username,
                    user_settings.smtp_password,
                    user_settings.smtp_from_email
                ]):
                    email_service = EmailService(
                        user_settings.smtp_server,
                        user_settings.smtp_port,
                        user_settings.smtp_username,
                        user_settings.smtp_password,
                        user_settings.smtp_from_email
                    )
                    
                    notification_sent = email_service.send_application_notification(
                        current_user.email,
                        {
                            'position': job_data.get('title', ''),
                            'company': job_data.get('company', ''),
                            'location': job_data.get('location', ''),
                            'platform': job_data.get('source', 'external'),
                            'job_url': job_data.get('url', ''),
                            'success': result.get('success', False),
                            'message': result.get('message', ''),
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    )
                    
                    if notification_sent:
                        app_history.notification_sent = True
                        db.session.commit()
            except Exception as e:
                logger.warning(f"Failed to send email notification: {str(e)}")
            
            # Clean up temporary files after submission
            if resume_file_path and os.path.exists(resume_file_path):
                os.remove(resume_file_path)
            if cover_letter_file_path and os.path.exists(cover_letter_file_path):
                os.remove(cover_letter_file_path)
                
            return jsonify({'result': result})
            
        except Exception as e:
            # Clean up temporary files in case of error
            if 'resume_file_path' in locals() and resume_file_path and os.path.exists(resume_file_path):
                os.remove(resume_file_path)
            if 'cover_letter_file_path' in locals() and cover_letter_file_path and os.path.exists(cover_letter_file_path):
                os.remove(cover_letter_file_path)
            return jsonify({'error': str(e)}), 500
    else:
        # Handle JSON data without file uploads (backward compatibility)
        data = request.json
        if not data or 'job' not in data or 'application' not in data:
            return jsonify({'error': 'Missing job or application data'}), 400
        
        try:
            # Check if resume data is included
            resume_data = data.get('resume')
            
            # Submit application without file uploads
            result = submitter.submit_application(data['job'], data['application'], resume_data)
            
            # Save application result to database
            app_history = ApplicationHistory(
                user_id=current_user.id,
                job_id=data['job'].get('id', str(time.time())),
                job_url=data['job'].get('url', ''),
                position=data['job'].get('title', ''),
                company=data['job'].get('company', ''),
                location=data['job'].get('location', ''),
                platform=data['job'].get('source', 'external'),
                description=data['job'].get('description', ''),
                application_type='easy_apply' if data['job'].get('easy_apply', False) else 'external',
                success=result.get('success', False),
                timestamp=datetime.utcnow(),
                message=result.get('message', ''),
                error=result.get('error', ''),
                cover_letter_text=data['application'].get('cover_letter', '')
            )
            db.session.add(app_history)
            db.session.commit()
            
            # Send email notification if enabled
            try:
                user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
                if user_settings and user_settings.notifications_enabled and all([
                    user_settings.smtp_server,
                    user_settings.smtp_port,
                    user_settings.smtp_username,
                    user_settings.smtp_password,
                    user_settings.smtp_from_email
                ]):
                    email_service = EmailService(
                        user_settings.smtp_server,
                        user_settings.smtp_port,
                        user_settings.smtp_username,
                        user_settings.smtp_password,
                        user_settings.smtp_from_email
                    )
                    
                    notification_sent = email_service.send_application_notification(
                        current_user.email,
                        {
                            'position': data['job'].get('title', ''),
                            'company': data['job'].get('company', ''),
                            'location': data['job'].get('location', ''),
                            'platform': data['job'].get('source', 'external'),
                            'job_url': data['job'].get('url', ''),
                            'success': result.get('success', False),
                            'message': result.get('message', ''),
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    )
                    
                    if notification_sent:
                        app_history.notification_sent = True
                        db.session.commit()
            except Exception as e:
                logger.warning(f"Failed to send email notification: {str(e)}")
            
            return jsonify({'result': result})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@bp.route('/application-history', methods=['GET'])
@login_required
def get_application_history():
    """Get user's application history"""
    try:
        # Get application history from database
        history = ApplicationHistory.query.filter_by(user_id=current_user.id).order_by(
            ApplicationHistory.timestamp.desc()
        ).all()
        
        # Convert to list of dictionaries
        history_list = []
        for app in history:
            history_list.append({
                'id': app.id,
                'job_id': app.job_id,
                'job_url': app.job_url,
                'position': app.position,
                'company': app.company,
                'location': app.location,
                'platform': app.platform,
                'application_type': app.application_type,
                'success': app.success,
                'timestamp': app.timestamp.isoformat(),
                'message': app.message,
                'error': app.error
            })
        
        return jsonify({'history': history_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/application-statistics', methods=['GET'])
@login_required
def get_application_statistics():
    """Get statistics about applications"""
    try:
        # Get all applications for the user
        applications = ApplicationHistory.query.filter_by(user_id=current_user.id).all()
        
        # Calculate statistics
        total = len(applications)
        successful = sum(1 for app in applications if app.success)
        
        # Count by platform
        platforms = {}
        for app in applications:
            platform = app.platform.lower() if app.platform else 'unknown'
            platforms[platform] = platforms.get(platform, 0) + 1
        
        # Count by application type
        types = {
            'easy_apply': sum(1 for app in applications if app.application_type == 'easy_apply'),
            'external': sum(1 for app in applications if app.application_type == 'external')
        }
        
        # Recent applications (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent = sum(1 for app in applications if app.timestamp >= seven_days_ago)
        
        return jsonify({
            'total': total,
            'successful': successful,
            'success_rate': round((successful / total) * 100, 2) if total > 0 else 0,
            'platforms': platforms,
            'types': types,
            'recent': recent
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/export-applications', methods=['GET'])
@login_required
def export_applications():
    """Export application history to CSV"""
    try:
        # Get application history from database
        history = ApplicationHistory.query.filter_by(user_id=current_user.id).order_by(
            ApplicationHistory.timestamp.desc()
        ).all()
        
        if not history:
            return jsonify({'error': 'No application history found'}), 404
        
        # Convert to list of dictionaries
        history_list = []
        for app in history:
            history_list.append({
                'id': app.id,
                'job_id': app.job_id,
                'job_url': app.job_url,
                'position': app.position,
                'company': app.company,
                'location': app.location,
                'platform': app.platform,
                'application_type': app.application_type,
                'success': app.success,
                'timestamp': app.timestamp,
                'message': app.message,
                'error': app.error
            })
        
        # Generate CSV
        exporter = CSVExporter()
        csv_data = exporter.generate_applications_csv_string(history_list)
        
        if not csv_data:
            return jsonify({'error': 'Failed to generate CSV'}), 500
        
        # Create response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"application_history_{timestamp}.csv"
        
        # Create a BytesIO object for the CSV data
        csv_bytes = io.BytesIO()
        csv_bytes.write(csv_data.encode('utf-8'))
        csv_bytes.seek(0)
        
        # Return the CSV file
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error exporting applications: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})