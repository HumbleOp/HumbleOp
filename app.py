from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from core.extensions import db, scheduler

# Factory

def create_app(config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='sqlite:///humbleop.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if config:
        app.config.update(config)

    db.init_app(app)

    with app.app_context():
        from models import User, Post, Comment, Vote, Flag, Like, Badge
        db.create_all()

    from routes.auth import auth_bp
    from routes.posts import posts_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(profile_bp)
    app.config["UPLOAD_FOLDER"] = "static/avatars"

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        scheduler.start()
    app.run(debug=True)
