from flask import Blueprint, request, jsonify, g
from app.utils.data_utils import save_data
from app.utils.badge_utils import award_badge, load_users, save_users
from app.scheduler.scheduler import scheduler, handle_duel_timeout
from datetime import datetime, timedelta
import logging
from threading import Lock

# Blueprint for posts
post_bp = Blueprint("posts", __name__)

# In-memory storage for posts (should be replaced with a database in production)
posts = {}  # Load posts at application startup

# Thread lock for concurrency safety
lock = Lock()

# Constants for badge names
BAPTISM_OF_FIRE = "Baptism of Fire"
GREAT_DEBATER = "Great Debater"
MARATHONER_LEGEND = "Marathoner Legend"
MARATHONER_III = "Marathoner III"
MARATHONER_II = "Marathoner II"
MARATHONER_I = "Marathoner I"

# Constants for thresholds
GREAT_DEBATER_THRESHOLD = 0.60
MARATHONER_THRESHOLDS = {
    MARATHONER_LEGEND: 100,
    MARATHONER_III: 50,
    MARATHONER_II: 10,
    MARATHONER_I: 5,
}

<<<<<<< HEAD
=======
@post_bp.route("/create/<post_id>", methods=["POST"])
def create_post(post_id):
    if post_id in posts:
        return jsonify({"error": "Post already exists."}), 400

    data = request.json or {}
    body = data.get("body")
    if not body:
        return jsonify({"error": "Post body is required."}), 400

    posts[post_id] = {
        "body": body,
        "author": g.current_user,
        "comments": []
    }
    return jsonify({"status": "Post created.", "post": posts[post_id]}), 200

>>>>>>> bfa9cd8 (update)
@post_bp.route("/start_duel/<post_id>", methods=["POST"])
def start_duel(post_id):
    with lock:  # Ensure thread-safe access to `posts`
        # Retrieve post and validate
        post = posts.get(post_id)
        if not post:
            return jsonify({"error": "Post not found."}), 404

        if not post.get("commenters"):
            return jsonify({"error": "Not enough comments to start duel."}), 400

        if not post.get("votes"):
            return jsonify({"error": "No votes available for this post."}), 400

        # Rank votes to determine winner and second place
        try:
            ranking = sorted(post["votes"].items(), key=lambda x: x[1], reverse=True)
            winner = ranking[0][0]
            second = ranking[1][0] if len(ranking) > 1 else None
        except IndexError:
            return jsonify({"error": "Not enough votes to rank participants."}), 400

        # Update post details
        post["winner"] = winner
        post["second"] = second
        post["postponed"] = False
        post["started"] = False

        # Schedule duel timeout
        try:
            run_date = datetime.now() + timedelta(hours=2)
            scheduler.add_job(
                handle_duel_timeout, 'date', run_date=run_date, args=[post_id]
            )
        except Exception as e:
            logging.error(f"Failed to schedule timeout for duel {post_id}: {e}")
            return jsonify({"error": "Failed to schedule duel timeout."}), 500

        # Load users once for efficiency
        users = load_users()

        # Award badges
        _award_baptism_of_fire(winner, users)
        _award_great_debater(winner, post["votes"], users)
        _award_marathoner(winner, users)

        # Save all user changes once
        save_users(users)

        # Save updated posts
        save_data(posts, "data.json")

        # Log duel start
        logging.info(f"Duel started for post {post_id}. Winner: {winner}, Second: {second}")

        return jsonify({
            "status": "Duel started.",
            "winner": winner,
            "second": second
        }), 200

def _award_baptism_of_fire(winner, users):
    """Award the 'Baptism of Fire' badge to the winner."""
    award_badge(winner, BAPTISM_OF_FIRE, users, save=False)

def _award_great_debater(winner, votes, users):
    """Award the 'Great Debater' badge if the winner meets the criteria."""
    total_votes = sum(votes.values())
    if total_votes > 0:
        votes_for_winner = votes.get(winner, 0)
        if (votes_for_winner / total_votes) >= GREAT_DEBATER_THRESHOLD:
            quality_wins = users[winner].get("quality_duel_wins", 0) + 1
            users[winner]["quality_duel_wins"] = quality_wins
            if quality_wins == 5:
                award_badge(winner, GREAT_DEBATER, users, save=False)

def _award_marathoner(winner, users):
    """Award the appropriate 'Marathoner' badge based on the winner's total wins."""
    win_count = sum(1 for p in posts.values() if p.get("winner") == winner)
    for badge, threshold in MARATHONER_THRESHOLDS.items():
        if win_count >= threshold:
            award_badge(winner, badge, users, save=False)
<<<<<<< HEAD
            break
=======
            break
>>>>>>> bfa9cd8 (update)
