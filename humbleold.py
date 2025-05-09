import json
import os
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher, exceptions
from apscheduler.schedulers.background import BackgroundScheduler

ph = PasswordHasher(
    time_cost=2,      # iterations
    memory_cost=51200,# in KiB (50 MiB)
    parallelism=8,    # thread
)


# --- Users persistence --------------------------------
USERS_FILE = "users.json"
if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except json.JSONDecodeError:
        users = {}
else:
    users = {}


def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def award_badge(username, badge_name):
    """
    Adds a badge to the user if they don’t already have it.
    """
    user = users.get(username)
    if not user:
        return
    if badge_name not in user["badges"]:
        user["badges"].append(badge_name)
        save_users()


# --- Flask & Scheduler setup --------------------------
app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# --- Flask SQLAlchemy setup --------------------------
BASE_DIR    = os.path.abspath(os.path.dirname(__file__))
DB_PATH     = os.path.join(BASE_DIR, "humbleop.db")
print(f"🔧 SQLite DB path: {DB_PATH}")

app.config['SQLALCHEMY_DATABASE_URI']        = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ----------------------------------------
# --- Association table for self-referential follows ----------------
follows = db.Table(
    'follows',
    db.Column('follower', db.String, db.ForeignKey('users.username'), primary_key=True),
    db.Column('followed', db.String, db.ForeignKey('users.username'), primary_key=True)
)

class User(db.Model):
    __tablename__      = 'users'
    username           = db.Column(db.String, primary_key=True)
    password_hash      = db.Column(db.String, nullable=False)
    token              = db.Column(db.String, unique=True)
    avatar_url         = db.Column(db.String, default='')
    bio                = db.Column(db.String, default='')

    # standard relations
    comments           = db.relationship('Comment', backref='author', lazy=True)
    votes              = db.relationship('Vote',    backref='voter_user',  lazy=True)
    badges             = db.relationship('Badge',   backref='user_owner',   lazy=True)

    # follow/followers many-to-many
    following = db.relationship(
        'User',
        secondary=follows,
        primaryjoin=lambda: follows.c.follower == User.username,
        secondaryjoin=lambda: follows.c.followed == User.username,
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

class Post(db.Model):
    __tablename__ = 'posts'
    id        = db.Column(db.String, primary_key=True)
    author    = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    body      = db.Column(db.Text, nullable=False)
    started   = db.Column(db.Boolean, default=False)
    postponed = db.Column(db.Boolean, default=False)
    winner    = db.Column(db.String, db.ForeignKey('users.username'))
    second    = db.Column(db.String, db.ForeignKey('users.username'))
    comments  = db.relationship('Comment', backref='post', lazy=True)
    votes     = db.relationship('Vote',    backref='post', lazy=True)
    flags     = db.relationship('Flag',    backref='post', lazy=True)
    likes     = db.relationship('Like',    backref='post', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id        = db.Column(db.Integer, primary_key=True)
    post_id   = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    commenter = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    text      = db.Column(db.Text, nullable=False)

class Vote(db.Model):
    __tablename__ = 'votes'
    id        = db.Column(db.Integer, primary_key=True)
    post_id   = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    voter     = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    candidate = db.Column(db.String, nullable=False)  # commenter username

class Flag(db.Model):
    __tablename__ = 'flags'
    id        = db.Column(db.Integer, primary_key=True)
    post_id   = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    flagger   = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)

class Like(db.Model):
    __tablename__ = 'likes'
    id        = db.Column(db.Integer, primary_key=True)
    post_id   = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    liker     = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)

class Badge(db.Model):
    __tablename__ = 'badges'
    id        = db.Column(db.Integer, primary_key=True)
    user      = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    name      = db.Column(db.String, nullable=False)



DATA_FILE = "data.json"
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r") as f:
            posts = json.load(f)
    except json.JSONDecodeError:
        posts = {}
else:
    posts = {}


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(posts, f, indent=2)
    print("[DATA SAVED]")

# --- Auth decorator ----------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        parts = auth.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({"error":"authorization required"}), 401

        token = parts[1]
        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify({"error":"invalid token"}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorated

# --- Duel timeout handler ----------------------------
def handle_duel_timeout(post_id):
    post = posts.get(post_id)
    if not post or post.get("started"):
        return

    if not post.get("postponed"):
        post["postponed"] = True
        scheduler.add_job(
            handle_duel_timeout,
            'date',
            run_date=datetime.now() + timedelta(hours=6),
            args=[post_id]
        )
    else:
        post["winner"] = post.get("second")
        post["postponed"] = False
        post["started"] = False
        scheduler.add_job(
            handle_duel_timeout,
            'date',
            run_date=datetime.now() + timedelta(hours=2),
            args=[post_id]
        )

    save_data()

# --- Auth endpoints with Argon2id --------------------
@app.route("/register", methods=["POST"])
def register():
    data     = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    # already existent?
    if db.session.get(User, username):
        return jsonify({"error": "username already exists"}), 409

    # generate hash and create user
    hashed = ph.hash(password)
    token = uuid.uuid4().hex
    user = User(
        username      = username,
        password_hash = hashed,
        token         = token,
        avatar_url    = "",
        bio           = ""
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"status": "user registered", "token":  token}), 201


@app.route("/profile", methods=["GET"])
@login_required
def get_profile():
    user = g.current_user
    return jsonify({
        "username":   user.username,
        "avatar_url": user.avatar_url,
        "bio":        user.bio,
        "badges":     [b.name for b in user.badges],
        "following":  [u.username for u in user.following],
        "followers":  [u.username for u in user.followers],
    }), 200


@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow_user(username):
    """Current user in g.current_user follows <username>."""
    me = g.current_user
    if username not in users:
        return jsonify({"error": "User not found."}), 404
    if username == me:
        return jsonify({"error": "Cannot follow yourself."}), 400

    # add follow
    if username in users[me]["following"]:
        return jsonify({"error": "Already following."}), 409

    users[me]["following"].append(username)
    users[username]["followers"].append(me)
    save_users()
    return jsonify({"status": f"You are now following {username}"}), 200

@app.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow_user(username):
    """Current user in g.current_user unfollows <username>."""
    me = g.current_user
    if username not in users:
        return jsonify({"error": "User not found."}), 404
    if username == me:
        return jsonify({"error": "Cannot unfollow yourself."}), 400

    if username not in users[me]["following"]:
        return jsonify({"error": "Not following."}), 409

    users[me]["following"].remove(username)
    users[username]["followers"].remove(me)
    save_users()
    return jsonify({"status": f"You have unfollowed {username}"}), 200

@app.route("/following", methods=["GET"])
@login_required
def get_following():
    """List users that current user is following."""
    me = g.current_user
    return jsonify({"following": users[me].get("following", [])}), 200

@app.route("/followers", methods=["GET"])
@login_required
def get_followers():
    """List users that follow current user."""
    me = g.current_user
    return jsonify({"followers": users[me].get("followers", [])}), 200


@app.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    uname = g.current_user
    user = users.get(uname)
    if not user:
        return jsonify({"error":"User not found"}), 404

    data = request.json or {}
    # Only these fields can be updated manually
    if "avatar_url" in data:
        user["avatar_url"] = data["avatar_url"]
    if "bio" in data:
        user["bio"] = data["bio"]

    save_users()
    return jsonify({
        "status": "profile updated",
        "profile": {
            "username":   uname,
            "avatar_url": user["avatar_url"],
            "bio":        user["bio"],
            "badges":     user["badges"]
        }
    }), 200



@app.route("/login", methods=["POST"])
def login():
    data     = request.json or {}
    username = data.get("username")
    password = data.get("password")

    user = db.session.get(User, username)
    if not user:
        return jsonify({"error": "invalid credentials"}), 401

    # verification Argon2
    try:
        ph.verify(user.password_hash, password)
    except exceptions.VerifyMismatchError:
        return jsonify({"error": "invalid credentials"}), 401

    # re-hash if needed
    if ph.check_needs_rehash(user.password_hash):
        user.password_hash = ph.hash(password)
        db.session.commit()

    # create and save a new token
    user.token = uuid.uuid4().hex
    db.session.commit()

    return jsonify({"token": user.token, "token":  user.token}), 200

# --- Post creation & duel endpoints -----------------
@app.route("/create_post/<post_id>", methods=["POST"])
@login_required
def create_post(post_id):
    body = request.json.get("body")
    author = g.current_user
    if not body:
        return jsonify({"error": "Field 'body' is required."}), 400

    posts[post_id] = {
        "author": author,
        "body": body,
        "comments": {},
        "commenters": [],
        "votes": {},
        "voted_users": [],
        "flags": [],
        "likes": []
    }
    save_data()
    return jsonify({"status": "Post created."}), 200

@app.route("/start_duel/<post_id>", methods=["POST"])
@login_required
def start_duel(post_id):
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    if len(post["commenters"]) < 1:
        return jsonify({"error": "Not enough comments to start duel."}), 400

    ranking = sorted(post["votes"].items(), key=lambda x: x[1], reverse=True)
    winner = ranking[0][0]
    second = ranking[1][0] if len(ranking) > 1 else None

    post["winner"]    = winner
    post["second"]    = second
    post["postponed"] = False
    post["started"]   = False

    scheduler.add_job(
        handle_duel_timeout,
        'date',
        run_date=datetime.now() + timedelta(hours=2),
        args=[post_id]
    )

    # award "Baptism of Fire" badge for first duel
    award_badge(winner, "Baptism of Fire")

    # —— CRITIQUE MASTER LOGIC ——   
    votes_for_winner = post["votes"].get(winner, 0)
    total_votes = sum(post["votes"].values())
    if total_votes > 0 and (votes_for_winner / total_votes) >= 0.60:
        # increment their “quality wins” counter
        quality_wins = users[winner].setdefault("quality_duel_wins", 0) + 1
        users[winner]["quality_duel_wins"] = quality_wins
        save_users()

        # award "Great Debater"
        if quality_wins == 5:
            award_badge(winner, "Great Debater")
    save_data()
    return jsonify({
        "status": "Duel started.",
        "winner": winner,
        "second": second
    }), 200


# award "Marathoner"
win_count = sum(1 for p in posts.values() if p.get("winner") == winner)
if win_count >= 100:
    award_badge(winner, "Marathoner Legend")
elif win_count >= 50:
    award_badge(winner, "Marathoner III")
elif win_count >= 10:
    award_badge(winner, "Marathoner II")
elif win_count >= 5:
    award_badge(winner, "Marathoner I")


@app.route("/start_now/<post_id>", methods=["POST"])
@login_required
def user_started(post_id):
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    post["started"] = True
    save_data()
    return jsonify({"status": "Duel started."}), 200

# --- Comment & vote endpoints -----------------------
@app.route("/comment/<post_id>", methods=["POST"])
@login_required
def add_comment(post_id):
    post = posts.get(post_id)
    commenter = g.current_user
    text = request.json.get("text")
    if not post:
        return jsonify({"error": "Post not found."}), 404
    if not text:
        return jsonify({"error": "Field 'text' is required."}), 400
    if commenter in post["commenters"]:
        return jsonify({"error": f"User '{commenter}' has already commented."}), 403

    post["comments"][commenter] = text
    post["commenters"].append(commenter)

    save_data()

    # award "First blood" badge for first commenter on a post
    award_badge(commenter, "First blood")

    long_comments = sum(
        1 for txt in post["comments"].values() 
        if len(txt) >= 100
    )
    total_long_comments = sum(
    1 for p in posts.values() 
      for txt in p["comments"].values() 
      if len(txt) >= 100
    )
    if total_long_comments >= 20:
        award_badge(commenter, "Eloquent Speaker")


    return jsonify({
        "status": "Comment added.",
        "comment": {"commenter": commenter, "text": text}
    }), 200

@app.route("/comments/<post_id>", methods=["GET"])
@login_required
def get_comments(post_id):
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    comments = []
    for c in post["commenters"]:
        comments.append({
            "commenter": c,
            "text": post["comments"][c],
            "votes": post["votes"].get(c, 0)
        })
    return jsonify({"comments": comments}), 200

@app.route("/vote/<post_id>", methods=["POST"])
@login_required
def vote(post_id):
    post = posts.get(post_id)
    voter = g.current_user
    candidate = request.json.get("candidate")
    if not post:
        return jsonify({"error": "Post not found."}), 404
    if candidate not in post["commenters"]:
        return jsonify({"error": f"Candidate '{candidate}' has not commented."}), 400
    if voter in post["voted_users"]:
        return jsonify({"error": f"User '{voter}' has already voted."}), 403

    post["votes"][candidate] = post["votes"].get(candidate, 0) + 1
    post["voted_users"].append(voter)

    sorted_votes = sorted(post["votes"].items(), key=lambda x: x[1], reverse=True)
    post["winner"] = sorted_votes[0][0]
    post["second"] = sorted_votes[1][0] if len(sorted_votes) > 1 else None

    save_data()
    
    # award "First Responder" badge for first voter
    award_badge(voter, "First Responder")
    total_votes_for_candidate = sum(
        p["votes"].get(candidate, 0)
        for p in posts.values()
    )
    if total_votes_for_candidate >= 10:
        award_badge(candidate, "Popular Debater")
   
    return jsonify({
        "message": f"{voter} voted for {candidate}",
        "votes": post["votes"]
    }), 200

# --- Flag & like endpoints -------------------------
@app.route("/flag/<post_id>", methods=["POST"])
@login_required
def flag_post(post_id):
    data = request.json or {}
    flagger = g.current_user
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    winner = post.get("winner")
    if not winner:
        return jsonify({"error": "No winner to flag."}), 400

    post.setdefault("flags", [])
    post.setdefault("likes", [])

    if flagger in post["flags"]:
        return jsonify({"error": f"User '{flagger}' has already flagged the winner."}), 403

    post["flags"].append(flagger)

    winner_votes = post["votes"].get(winner, 0)
    flag_count   = len(post["flags"])
    like_count   = len(post["likes"])
    net_flags    = max(0, flag_count - like_count)
    flag_ratio   = (net_flags / winner_votes) if winner_votes > 0 else 0

    if flag_ratio >= 0.6:
        post["started"] = False
        second = post.get("second")
        if second:
            post["winner"] = second
            result = {
                "status": "Duel interrupted due to net flags on winner.",
                "switched_to": second
            }
            scheduler.add_job(
                handle_duel_timeout,
                'date',
                run_date=datetime.now() + timedelta(hours=2),
                args=[post_id]
            )
        else:
            result = {
                "status": "Duel interrupted but no second user available.",
                "switched_to": None
            }

        post["flags"] = []
        post["likes"] = []
        post["postponed"] = False
        save_data()
        return jsonify(result), 200

    save_data()
    return jsonify({
        "status": f"Flag registered on '{winner}'. Net flags: {net_flags}/{winner_votes}."
    }), 200

@app.route("/like/<post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    data = request.json or {}
    liker = g.current_user
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    winner = post.get("winner")
    if not winner:
        return jsonify({"error": "No winner to like."}), 400

    post.setdefault("likes", [])
    if liker in post["likes"]:
        return jsonify({"error": f"User '{liker}' has already liked the winner."}), 403

    post["likes"].append(liker)
    save_data()
    return jsonify({
        "status": f"Like registered on '{winner}'. Total likes: {len(post['likes'])}"
    }), 200

# --- Read endpoints --------------------------------
@app.route("/status/<post_id>", methods=["GET"])
def get_status(post_id):
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    return jsonify(post), 200

@app.route("/results/<post_id>", methods=["GET"])
def get_results(post_id):
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    ranking = sorted(post["votes"].items(), key=lambda x: x[1], reverse=True)
    return jsonify({
        "body": post["body"],
        "ranking": ranking,
        "winner": post.get("winner"),
        "second": post.get("second")
    }), 200

# --- App runner -----------------------------------
if __name__ == "__main__":
    with app.app_context():
        print("📦 Creating database tables…")
        db.create_all()
    app.run(debug=True, use_reloader=False)
