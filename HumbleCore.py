import json
import os
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler

# --- Users persistence --------------------------------
USERS_FILE = "users.json"
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# --- Flask & Scheduler setup --------------------------
app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

DATA_FILE = "data.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        posts = json.load(f)
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
            return jsonify({"error": "authorization required"}), 401
        token = parts[1]
        for uname, u in users.items():
            if u.get("token") == token:
                g.current_user = uname
                return f(*args, **kwargs)
        return jsonify({"error": "invalid token"}), 401
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

# --- Auth endpoints ---------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    if username in users:
        return jsonify({"error": "username already exists"}), 409

    users[username] = {
        "password_hash": generate_password_hash(password),
        "token": None
    }
    save_users()
    return jsonify({"status": "user registered"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    user = users.get(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "invalid credentials"}), 401

    token = uuid.uuid4().hex
    user["token"] = token
    save_users()
    return jsonify({"token": token}), 200

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
    save_data()
    return jsonify({
        "status": "Duel started.",
        "winner": winner,
        "second": second
    }), 200

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

    if flag_ratio >= 0.4:
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
    print(app.url_map)
    app.run(debug=True)
