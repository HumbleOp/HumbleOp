from flask import Blueprint, request, jsonify, g
from app.utils.data_utils import save_data
from app.utils.badge_utils import award_badge
from app.utils.user_utils import load_users, save_users
from threading import Lock

# Blueprint for comments
comment_bp = Blueprint("comments", __name__)

# In-memory posts storage (replace with actual data loading logic)
posts = {}

# Thread lock for concurrency safety
lock = Lock()

@comment_bp.route("/<post_id>", methods=["POST"])
def add_comment(post_id):
    """Add a comment to a specific post."""
    with lock:  # Ensure thread-safe access to posts
        # Retrieve post details
        post = posts.get(post_id)
        
        if not post:
            return jsonify({"error": "Post not found."}), 404

        # Get current user and comment text
        commenter = g.current_user
        text = request.json.get("text")

        # Validate input
        if not text:
            return jsonify({"error": "Field 'text' is required."}), 400
        if commenter in post["commenters"]:
            return jsonify({"error": f"User '{commenter}' has already commented."}), 403

        # Add comment to the post
        post["comments"][commenter] = text
        post["commenters"].append(commenter)

        # Save updated posts data
        save_data(posts, "data.json")

        # Award badge safely
        users = load_users()
        award_badge(commenter, "First blood", users, save=False)
        save_users(users)

        return jsonify({
            "status": "Comment added.",
            "comment": {"commenter": commenter, "text": text}
        }), 200

<<<<<<< HEAD

=======
>>>>>>> bfa9cd8 (update)
@comment_bp.route("/<post_id>", methods=["GET"])
def get_comments(post_id):
    """Retrieve all comments for a specific post."""
    # Retrieve post details
    post = posts.get(post_id)

    if not post:
        return jsonify({"error": "Post not found."}), 404

    # Prepare comments with their details
    comments = [
        {
            "commenter": c,
            "text": post["comments"][c],
            "votes": post["votes"].get(c, 0)
        }
        for c in post["commenters"]
    ]

<<<<<<< HEAD
    return jsonify({"comments": comments}), 200
=======
    return jsonify({"comments": comments}), 200
>>>>>>> bfa9cd8 (update)
