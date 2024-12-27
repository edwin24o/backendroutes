from flask import Flask
from app.models import db
from app.extensions import ma, limiter, cache
from app.blueprints.users import users_bp
from app.blueprints.transactions import transactions_bp
from app.blueprints.listings import listings_bp
from app.blueprints.skills import skills_bp
from app.blueprints.search import search_bp
from flask_cors import CORS


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")


    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    # CORS(app, resources={r"/users/*": {"origins": "http://localhost:5173", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

    

    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(transactions_bp, url_prefix="/transactions")
    app.register_blueprint(listings_bp, url_prefix="/listings")
    app.register_blueprint(skills_bp, url_prefix="/skills")
    app.register_blueprint(search_bp, url_prefix='/api')
 

    return app