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


class UserSettings(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    # SMTP settings
    smtp_server = db.Column(db.String(256), nullable=True)
    smtp_port = db.Column(db.Integer, nullable=True)
    smtp_username = db.Column(db.String(256), nullable=True)
    smtp_password = db.Column(db.String(256), nullable=True)
    smtp_from_email = db.Column(db.String(256), nullable=True)
    notifications_enabled = db.Column(db.Boolean, default=False)
    
    # API keys
    anthropic_api_key = db.Column(db.String(256), nullable=True)
    openai_api_key = db.Column(db.String(256), nullable=True)
    
    # Job portal settings
    linkedin_client_id = db.Column(db.String(256), nullable=True)
    linkedin_client_secret = db.Column(db.String(256), nullable=True)
    indeed_publisher_id = db.Column(db.String(256), nullable=True)
    indeed_api_key = db.Column(db.String(256), nullable=True)
    glassdoor_partner_id = db.Column(db.String(256), nullable=True)
    glassdoor_api_key = db.Column(db.String(256), nullable=True)
    
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