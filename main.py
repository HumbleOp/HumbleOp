from flask import Flask
from app.config.config import Config
from app.models.models import db
from app.routes.auth_routes import auth_bp
from app.routes.post_routes import post_bp
from app.routes.interaction_routes import interaction_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(post_bp, url_prefix="/posts")
    app.register_blueprint(interaction_bp, url_prefix="/interactions")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)