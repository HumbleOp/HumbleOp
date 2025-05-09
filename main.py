from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config.config import Config
from app.models.models import db
from app.routes.auth_routes import auth_bp
from app.routes.post_routes import post_bp
from app.routes.interaction_routes import interaction_bp
from app.routes.profile_routes import profile_bp
from app.middleware import authenticate_user

def create_app():
    """Application factory for creating Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Middleware to authenticate user
    @app.before_request
    def before_request():
        authenticate_user()

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(post_bp, url_prefix="/posts")
    app.register_blueprint(interaction_bp, url_prefix="/interactions")
    app.register_blueprint(profile_bp, url_prefix="/profile")  # Added URL prefix

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(e):
        return {"error": "Not Found"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        return {"error": "Internal Server Error"}, 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)