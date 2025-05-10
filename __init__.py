# app/__init__.py
import os
from flask import Flask
from app.models    import db
from app.scheduler import init_scheduler
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.post_routes import post_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # config
    db_path = os.path.join(app.instance_path, "humbleop.db")
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI     = f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
    )
    if test_config:
        app.config.update(test_config)

    # init extensions
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(post_bp, url_prefix="/posts")

    # start scheduler
    init_scheduler(app)

    return app

# Export per i test e per WSGI
app = create_app()
