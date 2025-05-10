from flask import Blueprint, request, jsonify, g
from app.middleware import require_authentication
from app.utils.data_utils import save_data

interaction_bp = Blueprint("interactions", __name__)

posts = {}  # Replace with actual data loading logic

@interaction_bp.route("/flag/<post_id>", methods=["POST"])
def flag_post(post_id):
    auth_response = require_authentication()
    if auth_response:  # If user is not authenticated, return the response
        return auth_response

    post = posts.get(post_id)
    flagger = g.current_user
    if not post:
        return jsonify({"error": "Post not found."}), 404

    post.setdefault("flags", [])
    if flagger in post["flags"]:
        return jsonify({"error": f"User '{flagger}' has already flagged the post."}), 403

    post["flags"].append(flagger)
    save_data(posts, "data.json")
    return jsonify({"status": f"Flag registered on post '{post_id}'"}), 200

@interaction_bp.route("/like/<post_id>", methods=["POST"])
def like_post(post_id):
    post = posts.get(post_id)
    liker = g.current_user
    if not post:
        return jsonify({"error": "Post not found."}), 404

    post.setdefault("likes", [])
    if liker in post["likes"]:
        return jsonify({"error": f"User '{liker}' has already liked the post."}), 403

    post["likes"].append(liker)
    save_data(posts, "data.json")
    return jsonify({"status": f"Like registered on post '{post_id}'"}), 200