from flask import Blueprint, request, jsonify, g
from app.utils.data_utils import save_data
from app.utils.badge_utils import award_badge

comment_bp = Blueprint("comments", __name__)

posts = {}  # Replace with actual data loading logic

@comment_bp.route("/<post_id>", methods=["POST"])
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

    save_data(posts, "data.json")

    award_badge(commenter, "First blood")
    return jsonify({"status": "Comment added.", "comment": {"commenter": commenter, "text": text}}), 200

@comment_bp.route("/<post_id>", methods=["GET"])
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