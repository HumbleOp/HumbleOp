from flask import Blueprint
from app.routes.auth_routes import auth_bp
from app.routes.post_routes import post_bp
from app.routes.comment_routes import comment_bp
from app.routes.vote_routes import vote_bp
from app.routes.interaction_routes import interaction_bp
from app.routes.profile_routes import profile_bp

def register_blueprints(app):
    """Register all route blueprints to the Flask app."""
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(post_bp, url_prefix="/posts")
    app.register_blueprint(comment_bp, url_prefix="/comments")
    app.register_blueprint(vote_bp, url_prefix="/votes")
    app.register_blueprint(interaction_bp, url_prefix="/interactions")
    app.register_blueprint(profile_bp, url_prefix="/profile")