from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from argon2 import PasswordHasher, exceptions
import jwt
import uuid

# --- Configuration ---
SECRET_KEY = "your-secret-key"
DB_PATH = "sqlite:///humbleop.db"

# --- App Initialization ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Job Scheduler ---
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
scheduler = BackgroundScheduler(jobstores=jobstores)

# --- Password Hasher ---
ph = PasswordHasher(time_cost=2, memory_cost=51200, parallelism=8)

# --- Models ---
follows = db.Table(
    'follows',
    db.Column('follower', db.String, db.ForeignKey('users.username'), primary_key=True),
    db.Column('followed', db.String, db.ForeignKey('users.username'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String, primary_key=True)
    password_hash = db.Column(db.String, nullable=False)
    token = db.Column(db.String, unique=True)
    avatar_url = db.Column(db.String, default='')
    bio = db.Column(db.String, default='')

    comments = db.relationship('Comment', backref='author', lazy=True)
    followers = db.relationship(
        'User',
        secondary=follows,
        primaryjoin=lambda: follows.c.followed == User.username,
        secondaryjoin=lambda: follows.c.follower == User.username,
        backref='following',
        lazy='dynamic'
    )

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    voter_id = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    candidate_id = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.String, primary_key=True)
    author_id = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    started = db.Column(db.Boolean, default=False)
    postponed = db.Column(db.Boolean, default=False)
    winner_id = db.Column(db.String, db.ForeignKey('users.username'))
    second_id = db.Column(db.String, db.ForeignKey('users.username'))
    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.Column(db.Integer, default=0)
    flags = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    author_id = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    text = db.Column(db.Text, nullable=False)

class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    name = db.Column(db.String, nullable=False)

# --- Badge Service ---
class BadgeService:
    def __init__(self, db_session):
        self.db_session = db_session

    def award_badge(self, user, badge_name):
        existing_badge = Badge.query.filter_by(user_id=user.username, name=badge_name).first()
        if not existing_badge:
            badge = Badge(user_id=user.username, name=badge_name)
            self.db_session.add(badge)
            self.db_session.commit()
badge_service = BadgeService(db.session)

# --- Auth Service ---
class AuthService:
    @staticmethod
    def generate_token(username):
        payload = {
            "username": username,
            "exp": datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload["username"]
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

# --- Middleware ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        parts = auth.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({"error": "Authorization required"}), 401
        token = parts[1]
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username = payload.get("username")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        user = User.query.get(username)
        if not user or user.token != token:
            return jsonify({"error": "Unauthorized"}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorated

# --- Background Job ---
def check_postponed_duels():
    with app.app_context():
        now = datetime.utcnow()
        postponed_duels = Post.query.filter_by(postponed=True).all()
        for post in postponed_duels:
            if post.updated_at + timedelta(minutes=30) <= now:
                post.postponed = False
                post.started = True
                db.session.commit()
                print(f"Auto-started duel for post: {post.id}")

scheduler.add_job(check_postponed_duels, 'interval', minutes=1)
scheduler.start()

@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    if scheduler.running:  # Check if the scheduler is running
        scheduler.shutdown()

# --- Routes ---
@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already exists"}), 409

    hashed = ph.hash(password)
    token = AuthService.generate_token(username)
    user = User(username=username, password_hash=hashed, token=token)
    db.session.add(user)
    db.session.commit()

    return jsonify({"status": "user registered", "token": token}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    with db.session() as session:  # Use a session
        user = session.get(User, username)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        try:
            ph.verify(user.password_hash, password)
        except exceptions.VerifyMismatchError:
            return jsonify({"error": "Invalid credentials"}), 401

        if ph.check_needs_rehash(user.password_hash):
            user.password_hash = ph.hash(password)
        
        token = AuthService.generate_token(username)
        user.token = token
        session.commit()

        return jsonify({"token": token}), 200

@app.route("/profile", methods=["GET"])
@login_required
def get_profile():
    user = g.current_user
    return jsonify({
        "username": user.username,
        "avatar_url": user.avatar_url,
        "bio": user.bio
    }), 200

@app.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    user = g.current_user
    data = request.json or {}
    if "avatar_url" in data:
        user.avatar_url = data["avatar_url"]
    if "bio" in data:
        user.bio = data["bio"]
    db.session.commit()
    return jsonify({"status": "profile updated"}), 200

@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow_user(username):
    me = g.current_user
    target = User.query.get(username)
    if not target:
        return jsonify({"error": "User not found."}), 404
    if target.username == me.username:
        return jsonify({"error": "Cannot follow yourself."}), 400
    # già seguo?
    if me.following.filter_by(username=target.username).first():
        return jsonify({"error": "Already following."}), 400

    me.following.append(target)
    db.session.commit()
    return jsonify({"status": f"Now following {username}"}), 200


@app.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow_user(username):
    me = g.current_user
    target = User.query.get(username)
    if not target:
        return jsonify({"error": "User not found."}), 404
    if not me.following.filter_by(username=target.username).first():
        return jsonify({"error": "Not following."}), 400

    me.following.remove(target)
    db.session.commit()
    return jsonify({"status": f"Unfollowed {username}"}), 200


@app.route("/<username>/followers", methods=["GET"])
def list_followers(username):
    user = User.query.get(username)
    if not user:
        return jsonify({"error": "User not found."}), 404
    data = [u.username for u in user.followers]
    return jsonify({"followers": data}), 200


@app.route("/<username>/following", methods=["GET"])
def list_following(username):
    user = User.query.get(username)
    if not user:
        return jsonify({"error": "User not found."}), 404
    data = [u.username for u in user.following]
    return jsonify({"following": data}), 200

@app.route("/create_post", methods=["POST"])
@login_required
def create_post():
    user = g.current_user
    data = request.json or {}
    body = data.get("body")
    if not body:
        return jsonify({"error": "Field 'body' is required."}), 400

    post = Post(
        id=str(uuid.uuid4()),
        author_id=user.username,
        body=body
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({"status": "Post created."}), 201

@app.route("/comment/<post_id>", methods=["POST"])
@login_required
def add_comment(post_id):
    user = g.current_user
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    data = request.json or {}
    text = data.get("text")
    if not text:
        return jsonify({"error": "Field 'text' is required."}), 400

    comment = Comment(post_id=post.id, author_id=user.username, text=text)
    BadgeService(db.session).award_badge(g.current_user, "First Blood")
    db.session.add(comment)
    db.session.commit()
    # award "First blood" badge for the first comment on a post
    badge_service.award_badge(user, "First blood")
    # award "Eloquent Speaker"
    from sqlalchemy import func
    total_long_comments = (
    db.session.query(func.count(Comment.id))
    .filter(func.length(Comment.text) >= 100)
    .scalar()
    )
    if total_long_comments >= 20:
        badge_service.award_badge(user, "Eloquent Speaker")
        return jsonify({"status": "Comment added."}), 201

@app.route("/vote/<post_id>", methods=["POST"])
@login_required
def vote(post_id):
    user = g.current_user
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    data = request.json or {}
    candidate_id = data.get("candidate")
    if not candidate_id:
        return jsonify({"error": "Candidate is required."}), 400

    candidate = User.query.filter_by(username=candidate_id).first()
    if not candidate or not Comment.query.filter_by(post_id=post_id, author_id=candidate_id).first():
        return jsonify({"error": f"Candidate '{candidate_id}' has not commented."}), 400

    if Vote.query.filter_by(post_id=post_id, voter_id=user.username).first():
        return jsonify({"error": "You have already voted."}), 403

    new_vote = Vote(post_id=post_id, voter_id=user.username, candidate_id=candidate_id)
    db.session.add(new_vote)
    db.session.commit()
    # award "First Responder" to the first vote to every user
    badge_service.award_badge(user, "First Responder")
    # award "Popular Debater" to the candidate asa soon as it reaches 10 total votes
    total_votes_for_candidate = (
        db.session.query(func.count(Vote.id))
        .filter(Vote.candidate_id == candidate_id)
        .scalar()
    )
    if total_votes_for_candidate >= 10:
        # load candidate
        candidate_user = User.query.get(candidate_id)
        badge_service.award_badge(candidate_user, "Popular Debater")


    return jsonify({"status": f"{user.username} voted for {candidate_id}"}), 200

@app.route("/flag/<post_id>", methods=["POST"])
@login_required
def flag_post(post_id):
    user = g.current_user
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    post.flags += 1
    db.session.commit()
    return jsonify({"status": "Post flagged."}), 200

@app.route("/like/<post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    user = g.current_user
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    post.likes += 1
    db.session.commit()
    return jsonify({"status": "Post liked."}), 200

# --- Duel control endpoints -------------------------

@app.route("/start_duel/<post_id>", methods=["POST"])
@login_required
def start_duel(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    # Ensure there is at least one comment before starting the duel
    if not post.comments:
        return jsonify({"error": "Not enough comments to start duel."}), 400

    # Count votes per candidate
    from sqlalchemy import func
    votes_data = (
        db.session.query(
            Vote.candidate_id,
            func.count(Vote.id).label("vote_count")
        )
        .filter(Vote.post_id == post_id)
        .group_by(Vote.candidate_id)
        .all()
    )
    if not votes_data:
        return jsonify({"error": "No votes cast."}), 400

    # Sort candidates by vote count descending
    votes_sorted = sorted(votes_data, key=lambda x: x.vote_count, reverse=True)
    winner = votes_sorted[0].candidate_id
    second = votes_sorted[1].candidate_id if len(votes_sorted) > 1 else None

    # Update post with duel result
    post.winner_id  = winner
    post.second_id  = second
    post.started    = True
    post.postponed  = False
    db.session.commit()

    # Award a badge to the winner for their first duel
    badge_service.award_badge(User.query.get(winner), "Baptism of Fire")

    return jsonify({
        "status": "Duel started.",
        "winner": winner,
        "second": second
    }), 200


@app.route("/status/<post_id>", methods=["GET"])
@login_required
def get_status(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    # Return the current status of the duel
    return jsonify({
        "post_id":   post.id,
        "started":   post.started,
        "postponed": post.postponed,
        "winner":    post.winner_id,
        "second":    post.second_id,
        "flags":     post.flags,
        "likes":     post.likes
    }), 200


# --- Main ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)