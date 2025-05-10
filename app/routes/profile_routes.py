from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models.models import db, User

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/", methods=["GET"])
def get_profile():
    """Get the profile of the currently authenticated user."""
    if not g.current_user:
        return jsonify({"error": "Unauthorized"}), 401

    user = db.session.query(User).filter_by(username=g.current_user).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": user.username,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "badges": [badge.name for badge in user.badges],  # Assuming badges is a relationship
        "following": [u.username for u in user.following],  # Assuming self-referential relationship
        "followers": [u.username for u in user.followers]
    }), 200

@profile_bp.route("/", methods=["PUT"])
def update_profile():
    """Update the profile of the currently authenticated user."""
    if not g.current_user:
        return jsonify({"error": "Unauthorized"}), 401

    user = db.session.query(User).filter_by(username=g.current_user).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json or {}
    if "avatar_url" in data:
        user.avatar_url = data["avatar_url"]
    if "bio" in data:
        user.bio = data["bio"]

    db.session.commit()
    return jsonify({
        "status": "Profile updated",
        "profile": {
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio
        }
    }), 200
