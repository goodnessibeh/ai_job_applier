from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
import os
import uuid
import imghdr
from werkzeug.utils import secure_filename
from ..models import db, User

bp = Blueprint('user', __name__, url_prefix='/api/user')

# Configure allowed file extensions and max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(stream):
    """Validate that the file is a real image"""
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

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

@bp.route('/profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    """Upload a new profile picture"""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Validate that the file is a real image
        file_ext = validate_image(file.stream)
        if not file_ext:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Create a secure filename with a random UUID
        filename = secure_filename(str(uuid.uuid4()) + file_ext)
        
        # Ensure the uploads directory exists
        uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pictures')
        os.makedirs(uploads_dir, exist_ok=True)
        
        try:
            # Save the file
            file_path = os.path.join(uploads_dir, filename)
            file.save(file_path)
            
            # Set file permissions
            os.chmod(file_path, 0o644)
            
            # Delete old profile picture if it exists
            if current_user.profile_picture:
                old_file_path = os.path.join(current_app.root_path, current_user.profile_picture)
                if os.path.exists(old_file_path):
                    try:
                        os.remove(old_file_path)
                    except Exception as e:
                        current_app.logger.error(f"Error removing old profile picture: {str(e)}")
            
            # Update the user's profile picture information
            relative_path = os.path.join('static', 'uploads', 'profile_pictures', filename)
            current_user.set_profile_picture(relative_path, file.content_type)
            
            db.session.commit()
            
            # Get the updated URL with timestamp to force refresh
            updated_url = current_user.get_profile_picture_url()
            
            return jsonify({
                'message': 'Profile picture uploaded successfully',
                'profile_picture_url': updated_url
            })
            
        except Exception as e:
            current_app.logger.error(f"Error saving profile picture: {str(e)}")
            db.session.rollback()
            return jsonify({'error': f'Error saving profile picture: {str(e)}'}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@bp.route('/profile-picture/<user_id>', methods=['GET'])
def get_profile_picture(user_id):
    """Get a user's profile picture"""
    user = User.query.get(user_id)
    
    if not user or not user.profile_picture:
        # Return default profile picture
        response = send_file(os.path.join(current_app.root_path, 'static', 'default-profile.png'), mimetype='image/png')
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    # Check if the file actually exists
    file_path = os.path.join(current_app.root_path, user.profile_picture)
    if not os.path.exists(file_path):
        current_app.logger.warning(f"Profile picture file not found: {file_path}")
        # Fall back to default if the file doesn't exist
        response = send_file(os.path.join(current_app.root_path, 'static', 'default-profile.png'), mimetype='image/png')
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    # Return the user's profile picture with cache control headers
    response = send_file(file_path, mimetype=user.profile_picture_type)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@bp.route('/profile-picture', methods=['DELETE'])
@login_required
def delete_profile_picture():
    """Delete the current user's profile picture"""
    if current_user.profile_picture:
        try:
            # Remove the file from the filesystem
            file_path = os.path.join(current_app.root_path, current_user.profile_picture)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Update the user's profile picture information
            current_user.profile_picture = None
            current_user.profile_picture_type = None
            current_user.profile_picture_updated_at = None
            
            db.session.commit()
            
            return jsonify({
                'message': 'Profile picture deleted successfully',
                'profile_picture_url': current_user.get_profile_picture_url()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'message': 'No profile picture to delete'})