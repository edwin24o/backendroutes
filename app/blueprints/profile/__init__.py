from flask import Blueprint

# Create the profile blueprint
profile_bp = Blueprint("profile", __name__)

from . import routes  # Import routes to register them with the blueprint
