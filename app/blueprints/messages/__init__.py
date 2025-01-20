from flask import Blueprint

# Create the profile blueprint
messages_bp = Blueprint("messages", __name__)

from . import routes  # Import routes to register them with the blueprint
