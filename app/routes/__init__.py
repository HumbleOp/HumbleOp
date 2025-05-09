import logging
from flask import Flask, Blueprint

# Import all blueprints (manually or dynamically)
from app.routes.auth_routes import auth_bp
from app.routes.post_routes import post_bp
from app.routes.comment_routes import comment_bp
from app.routes.vote_routes import vote_bp
from app.routes.interaction_routes import interaction_bp
from app.routes.profile_routes import profile_bp

# Set up logging for blueprint registration
logging.basicConfig(level=logging.INFO)

# Blueprint configurations as (blueprint, prefix)
BLUEPRINTS: list[tuple[Blueprint, str]] = [
    (auth_bp, "/auth"),
    (post_bp, "/posts"),
    (comment_bp, "/comments"),
    (vote_bp, "/votes"),
    (interaction_bp, "/interactions"),
    (profile_bp, "/profile"),
]

def register_blueprints(app: Flask) -> None:
    """
    Register all route blueprints to the Flask app.

    Args:
        app (Flask): The Flask application instance.
    """
    for bp, prefix in BLUEPRINTS:
        try:
            app.register_blueprint(bp, url_prefix=prefix)
            logging.info(f"Registered blueprint: {bp.name} with prefix {prefix}")
        except Exception as e:
<<<<<<< HEAD
            logging.error(f"Failed to register blueprint: {bp.name} with prefix {prefix}. Error: {e}")
=======
            logging.error(f"Failed to register blueprint: {bp.name} with prefix {prefix}. Error: {e}")
>>>>>>> bfa9cd8 (update)
