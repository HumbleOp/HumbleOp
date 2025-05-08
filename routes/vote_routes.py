from flask import Blueprint, request, jsonify, g
from app.utils.data_utils import save_data
from app.utils.badge_utils import award_badge

vote_bp = Blueprint("votes", __name__)

posts = {}  # Replace with actual data loading logic

@vote_bp.route("/<post_id>", methods=["POST"])
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

    save_data(posts, "data.json")
    award_badge(voter, "First Responder")

    return jsonify({"message": f"{voter} voted for {candidate}", "votes": post["votes"]}), 200