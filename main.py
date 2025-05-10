from flask import Flask, g, jsonify, request
from flask_migrate import Migrate
from app.config.config import Config
from app.extensions import db  # Unified db instance
from app.routes.auth_routes import auth_bp
from app.routes.post_routes import post_bp
from app.routes.interaction_routes import interaction_bp
from app.routes.profile_routes import profile_bp
from app.routes.user_routes import user_bp
from app.services.auth_service import AuthService



def authenticate_user():
    """Middleware to authenticate users."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        g.current_user = None
        return jsonify({"error": "Authentication required"}), 401

    token = auth_header.split(" ")[1]
    # Replace with your token validation logic
    username = AuthService.verify_token(token)  # validate_token is a custom function
    if not user_bp:
        g.current_user = None
        return jsonify({"error": "Invalid or expired token"}), 401

    g.current_user = user_bp


def create_app():
    """Factory function to create a Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)  # Use unified db instance
    Migrate(app, db)  # Initialize Flask-Migrate

    # Middleware
    @app.before_request
    def before_request():
        auth_response = authenticate_user()
        if auth_response:  # Return response if authentication fails
            return auth_response

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(post_bp, url_prefix="/posts")
    app.register_blueprint(interaction_bp, url_prefix="/interactions")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(user_bp, url_prefix="/users")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(e):
        return {"error": "Not Found"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        if app.config["DEBUG"]:  # In development mode
            return {"error": "Internal Server Error", "details": str(e)}, 500
        return {"error": "Internal Server Error"}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config.get("DEBUG", False))  # Toggle debug mode via config