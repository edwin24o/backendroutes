from flask import Blueprint


skills_bp = Blueprint('skills_bp', __name__)

from . import routes