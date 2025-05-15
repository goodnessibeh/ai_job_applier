from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Profile picture information
    profile_picture = db.Column(db.String(512), nullable=True)  # Path to the profile picture file
    profile_picture_type = db.Column(db.String(50), nullable=True)  # File type (e.g., 'image/jpeg', 'image/png')
    profile_picture_updated_at = db.Column(db.DateTime, nullable=True)  # When the profile picture was last updated
    
    # Job search preferences
    job_titles = db.Column(db.Text, nullable=True)  # Comma-separated list of job titles
    min_salary = db.Column(db.Integer, nullable=True)  # Minimum salary expectation
    max_commute_distance = db.Column(db.Integer, nullable=True)  # Maximum commute distance in miles
    preferred_locations = db.Column(db.Text, nullable=True)  # Comma-separated list of preferred locations
    remote_only = db.Column(db.Boolean, default=False)  # Whether user wants remote-only jobs
    auto_apply_enabled = db.Column(db.Boolean, default=False)  # Whether to automatically apply to matching jobs
    minimum_match_score = db.Column(db.Integer, default=70)  # Minimum match score (0-100) for auto-apply
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_reset_token(self, token, expiry):
        self.reset_token = token
        self.reset_token_expiry = expiry
    
    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None
    
    def set_profile_picture(self, file_path, file_type):
        """Set or update the user's profile picture"""
        self.profile_picture = file_path
        self.profile_picture_type = file_type
        self.profile_picture_updated_at = datetime.datetime.utcnow()
    
    def get_profile_picture_url(self):
        """Get the profile picture URL or return a default if none is set"""
        if self.profile_picture:
            return f"/api/user/profile-picture/{self.id}"
        return "/static/default-profile.png"
    
    def get_job_titles_list(self):
        """Get job titles as a list"""
        if not self.job_titles:
            return []
        return [title.strip() for title in self.job_titles.split(',')]
    
    def set_job_titles_list(self, titles):
        """Set job titles from a list"""
        if not titles:
            self.job_titles = None
        else:
            self.job_titles = ','.join(titles)
    
    def get_preferred_locations_list(self):
        """Get preferred locations as a list"""
        if not self.preferred_locations:
            return []
        return [location.strip() for location in self.preferred_locations.split(',')]
    
    def set_preferred_locations_list(self, locations):
        """Set preferred locations from a list"""
        if not locations:
            self.preferred_locations = None
        else:
            self.preferred_locations = ','.join(locations)
        
    @property
    def full_name(self):
        """Return display_name if set, otherwise username"""
        return self.display_name or self.username


from cryptography.fernet import Fernet
import base64
import os

def get_encryption_key():
    """Get or generate encryption key for sensitive data"""
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        # Generate a key for testing/development - in production this should be set in env
        key = Fernet.generate_key().decode()
        os.environ['ENCRYPTION_KEY'] = key
    return key.encode()

class UserSettings(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    # SMTP settings - encrypted fields
    _smtp_server = db.Column('smtp_server', db.String(512), nullable=True)
    smtp_port = db.Column(db.Integer, nullable=True)
    _smtp_username = db.Column('smtp_username', db.String(512), nullable=True)
    _smtp_password = db.Column('smtp_password', db.String(512), nullable=True)
    _smtp_from_email = db.Column('smtp_from_email', db.String(512), nullable=True)
    notifications_enabled = db.Column(db.Boolean, default=False)
    
    # API keys - encrypted
    _anthropic_api_key = db.Column('anthropic_api_key', db.String(512), nullable=True)
    _openai_api_key = db.Column('openai_api_key', db.String(512), nullable=True)
    _rapidapi_key = db.Column('rapidapi_key', db.String(512), nullable=True)
    
    # Application settings
    max_applications_per_day = db.Column(db.Integer, default=10)
    
    # Default platform settings
    use_anthropic = db.Column(db.Boolean, default=True)
    use_openai = db.Column(db.Boolean, default=False)
    
    # Job API preferences
    use_indeed = db.Column(db.Boolean, default=True)
    use_upwork = db.Column(db.Boolean, default=True)
    use_google_jobs = db.Column(db.Boolean, default=True)
    use_workday = db.Column(db.Boolean, default=True)
    use_glassdoor = db.Column(db.Boolean, default=True)
    use_startup_jobs = db.Column(db.Boolean, default=True)
    use_job_search = db.Column(db.Boolean, default=True)
    use_internships = db.Column(db.Boolean, default=True)
    use_active_jobs = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Encryption/decryption methods using property decorators
    def _encrypt(self, data):
        if not data:
            return None
        key = get_encryption_key()
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()
    
    def _decrypt(self, data):
        if not data:
            return None
        key = get_encryption_key()
        f = Fernet(key)
        return f.decrypt(data.encode()).decode()
    
    # Property decorators for encrypted fields
    @property
    def smtp_server(self):
        return self._decrypt(self._smtp_server)
        
    @smtp_server.setter
    def smtp_server(self, value):
        self._smtp_server = self._encrypt(value) if value else None
    
    @property
    def smtp_username(self):
        return self._decrypt(self._smtp_username)
        
    @smtp_username.setter
    def smtp_username(self, value):
        self._smtp_username = self._encrypt(value) if value else None
    
    @property
    def smtp_password(self):
        return self._decrypt(self._smtp_password)
        
    @smtp_password.setter
    def smtp_password(self, value):
        self._smtp_password = self._encrypt(value) if value else None
    
    @property
    def smtp_from_email(self):
        return self._decrypt(self._smtp_from_email)
        
    @smtp_from_email.setter
    def smtp_from_email(self, value):
        self._smtp_from_email = self._encrypt(value) if value else None
    
    @property
    def anthropic_api_key(self):
        return self._decrypt(self._anthropic_api_key)
        
    @anthropic_api_key.setter
    def anthropic_api_key(self, value):
        self._anthropic_api_key = self._encrypt(value) if value else None
    
    @property
    def openai_api_key(self):
        return self._decrypt(self._openai_api_key)
        
    @openai_api_key.setter
    def openai_api_key(self, value):
        self._openai_api_key = self._encrypt(value) if value else None
    
    @property
    def rapidapi_key(self):
        return self._decrypt(self._rapidapi_key)
        
    @rapidapi_key.setter
    def rapidapi_key(self, value):
        self._rapidapi_key = self._encrypt(value) if value else None


class ApplicationHistory(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    # Job details
    job_id = db.Column(db.String(100), nullable=True)
    job_url = db.Column(db.String(1024), nullable=False)
    position = db.Column(db.String(256), nullable=False)
    company = db.Column(db.String(256), nullable=False)
    location = db.Column(db.String(256), nullable=True)
    platform = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Match details
    match_score = db.Column(db.Integer, nullable=True)  # 0-100 score indicating match quality
    match_reasons = db.Column(db.Text, nullable=True)  # JSON string containing match reasons
    auto_applied = db.Column(db.Boolean, default=False)  # Whether job was auto-applied for
    
    # Application details
    application_type = db.Column(db.String(100), nullable=False)  # 'easy_apply', 'external', or 'manual'
    success = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    message = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    
    # Submission details
    cover_letter_text = db.Column(db.Text, nullable=True)
    resume_used = db.Column(db.String(256), nullable=True)
    notification_sent = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)