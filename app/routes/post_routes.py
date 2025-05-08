from flask import Blueprint, request, jsonify, g
from app.utils.data_utils import save_data
from app.scheduler.scheduler import scheduler, handle_duel_timeout
from app.utils.badge_utils import award_badge
from datetime import datetime, timedelta

post_bp = Blueprint("posts", __name__)

posts = {}  # Replace with actual data loading logic

@post_bp.route("/create/<post_id>", methods=["POST"])
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
    save_data(posts, "data.json")
    return jsonify({"status": "Post created."}), 200

@post_bp.route("/start_duel/<post_id>", methods=["POST"])
def start_duel(post_id):
    post = posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    if len(post["commenters"]) < 1:
        return jsonify({"error": "Not enough comments to start duel."}), 400

    ranking = sorted(post["votes"].items(), key=lambda x: x[1], reverse=True)
    winner = ranking[0][0]
    second = ranking[1][0] if len(ranking) > 1 else None

    post["winner"] = winner
    post["second"] = second
    post["postponed"] = False
    post["started"] = False

    scheduler.add_job(handle_duel_timeout, 'date', run_date=datetime.now() + timedelta(hours=2), args=[post_id])

    award_badge(winner, "Baptism of Fire")

    save_data(posts, "data.json")
    return jsonify({"status": "Duel started.", "winner": winner, "second": second}), 200