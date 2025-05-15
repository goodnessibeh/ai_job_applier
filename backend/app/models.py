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
    
    # Job portal settings - encrypted
    _linkedin_client_id = db.Column('linkedin_client_id', db.String(512), nullable=True)
    _linkedin_client_secret = db.Column('linkedin_client_secret', db.String(512), nullable=True)
    _indeed_publisher_id = db.Column('indeed_publisher_id', db.String(512), nullable=True)
    _indeed_api_key = db.Column('indeed_api_key', db.String(512), nullable=True)
    _glassdoor_partner_id = db.Column('glassdoor_partner_id', db.String(512), nullable=True)
    _glassdoor_api_key = db.Column('glassdoor_api_key', db.String(512), nullable=True)
    
    # Application settings
    max_applications_per_day = db.Column(db.Integer, default=10)
    
    # Default platform settings
    use_anthropic = db.Column(db.Boolean, default=True)
    use_openai = db.Column(db.Boolean, default=False)
    use_linkedin = db.Column(db.Boolean, default=True)
    use_indeed = db.Column(db.Boolean, default=True)
    use_glassdoor = db.Column(db.Boolean, default=True)
    
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
    def linkedin_client_id(self):
        return self._decrypt(self._linkedin_client_id)
        
    @linkedin_client_id.setter
    def linkedin_client_id(self, value):
        self._linkedin_client_id = self._encrypt(value) if value else None
    
    @property
    def linkedin_client_secret(self):
        return self._decrypt(self._linkedin_client_secret)
        
    @linkedin_client_secret.setter
    def linkedin_client_secret(self, value):
        self._linkedin_client_secret = self._encrypt(value) if value else None
    
    @property
    def indeed_publisher_id(self):
        return self._decrypt(self._indeed_publisher_id)
        
    @indeed_publisher_id.setter
    def indeed_publisher_id(self, value):
        self._indeed_publisher_id = self._encrypt(value) if value else None
    
    @property
    def indeed_api_key(self):
        return self._decrypt(self._indeed_api_key)
        
    @indeed_api_key.setter
    def indeed_api_key(self, value):
        self._indeed_api_key = self._encrypt(value) if value else None
    
    @property
    def glassdoor_partner_id(self):
        return self._decrypt(self._glassdoor_partner_id)
        
    @glassdoor_partner_id.setter
    def glassdoor_partner_id(self, value):
        self._glassdoor_partner_id = self._encrypt(value) if value else None
    
    @property
    def glassdoor_api_key(self):
        return self._decrypt(self._glassdoor_api_key)
        
    @glassdoor_api_key.setter
    def glassdoor_api_key(self, value):
        self._glassdoor_api_key = self._encrypt(value) if value else None


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
    
    # Application details
    application_type = db.Column(db.String(100), nullable=False)  # 'easy_apply' or 'external'
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