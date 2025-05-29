import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from core.extensions import db, scheduler
from models import Post

if os.getenv("DATABASE_URL", "").startswith("postgresql://"):
    from wait_for_postgres import wait_for_postgres
    wait_for_postgres()

# Factory

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(
    app,
    origins=["http://localhost:3000"],
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS"]
)


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
    

    @app.route('/debug/expire_post/<post_id>', methods=['POST'])
    def debug_expire_post(post_id):
        if not app.debug:
            return jsonify(error="Not allowed outside debug mode"), 403

        post = Post.query.get(post_id)
        if not post:
            return jsonify(error="Post not found"), 404

        post.voting_ends_in = 0
        db.session.commit()

        return jsonify(success=True)
    
    @app.route('/debug/force_winner/<post_id>', methods=['POST'])
    def debug_force_winner(post_id):
        if not app.debug:
            return jsonify(error="Not allowed outside debug mode"), 403

        post = Post.query.get(post_id)
        if not post:
            return jsonify(error="Post not found"), 404

        data = request.get_json()
        winner = data.get('winner')
        second = data.get('second')

        if not winner or not second:
            return jsonify(error="Missing winner or second"), 400

        post.winner = winner
        post.second = second
        db.session.commit()

        return jsonify(success=True)

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        scheduler.start()
    app.run(debug=True)


