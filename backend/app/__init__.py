import os
from flask import Flask, session
from flask_cors import CORS
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import timedelta
from .models import db, User, UserSettings, ApplicationHistory

login_manager = LoginManager()

class SecureModelView(ModelView):
    def is_accessible(self):
        from flask_login import current_user
        return current_user.is_authenticated and current_user.is_admin

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure CORS with credentials support
    CORS(app,
         supports_credentials=True,
         resources={r"/api/*": {
             # Include both port 3000 and port 5001 origins
             "origins": ["http://localhost:3000", "http://127.0.0.1:3000",
                        "http://localhost:5001", "http://127.0.0.1:5001"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
             "expose_headers": ["Content-Type", "Authorization"],
             "max_age": 86400
         }})
    
    # Set session cookie attributes for better security and proper handling
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(app.instance_path, 'ai_job_applier.sqlite')),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # Session configuration
        SESSION_TYPE='filesystem',
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        # Cookie settings for proper authentication
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',  # Prevents CSRF in modern browsers
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',  # HTTPS only in production
    )
    
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize database
    db.init_app(app)
    
    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    # Initialize Flask-Admin
    admin = Admin(app, name='AI Job Applier Admin', template_mode='bootstrap4')
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(UserSettings, db.session))
    admin.add_view(SecureModelView(ApplicationHistory, db.session))
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin_user.set_password('Mascerrano@Cyber2025--')
            db.session.add(admin_user)
            db.session.commit()
    
    # Register blueprints
    from app.api import routes
    app.register_blueprint(routes.bp)
    
    from app.api import auth_routes
    app.register_blueprint(auth_routes.bp)
    
    from app.api import settings_routes
    app.register_blueprint(settings_routes.bp)
    
    # Register old user_routes with a different name to avoid conflicts
    from app.api import user_routes
    app.register_blueprint(user_routes.bp, name='user_api_v1')
    
    # Register admin routes and allow 'admin' name to be overridden
    from app.api import admin_routes
    app.register_blueprint(admin_routes.bp, name='admin_api_v1')
    
    # Register new structured blueprints with unique names using 'name=' parameter
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, name='admin_v2')
    
    from app.routes.user import bp as user_bp
    app.register_blueprint(user_bp, name='user_v2')
    
    # Ensure upload directories exist
    os.makedirs(os.path.join(app.root_path, 'static', 'uploads', 'profile_pictures'), exist_ok=True)
    
    return app