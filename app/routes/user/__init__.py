"""User routes package for the application."""

from flask import Blueprint

# Create the user blueprint
bp = Blueprint('user_routes', __name__, url_prefix='/api/user_v2')

# Import the routes
from app.routes.user import profile, profile_picture

# Register sub-blueprints if needed
# bp.register_blueprint(some_sub_blueprint)