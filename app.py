import os
from flask import Flask
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from core.extensions import db, scheduler

if os.getenv("DATABASE_URL", "").startswith("postgresql://"):
    from wait_for_postgres import wait_for_postgres
    wait_for_postgres()

# Factory

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config['SWAGGER'] = {
        'title': 'HumbleOp API',
        'uiversion': 3,
        'securityDefinitions': {
            'BearerAuth': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header'
            }
        },
        'security': [{'BearerAuth': []}]
    }
    Swagger(app)

    db_uri = os.getenv("DATABASE_URL")
    if not db_uri:
        os.makedirs(app.instance_path, exist_ok=True)
        db_uri = f"sqlite:///{os.path.join(app.instance_path, 'humbleop.db')}"

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if config:
        app.config.update(config)

    db.init_app(app)

    with app.app_context():
        from models import User, Post, Comment, Vote, Flag, Like, Badge, Tag, post_tags
        db.create_all()

    from routes.auth import auth_bp
    from routes.posts import posts_bp
    from routes.profile import profile_bp
    from routes.search import search_bp
    from routes.search import search_bp
    from routes.tag import tag_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(tag_bp)
    app.config["UPLOAD_FOLDER"] = "static/avatars"

    @app.route("/")
    def index():
        return "HumbleOp è attivo!"
    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        scheduler.start()
    app.run(debug=True)


