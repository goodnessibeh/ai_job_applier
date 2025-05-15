"""Admin routes package for the application."""

from flask import Blueprint

# Create the admin blueprint
bp = Blueprint('admin_routes', __name__, url_prefix='/api/admin_v2')

# Import the routes
from app.routes.admin import users, settings, stats

# Register sub-blueprints if needed
# bp.register_blueprint(some_sub_blueprint)