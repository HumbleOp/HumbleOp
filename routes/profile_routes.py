from flask import Blueprint, request, jsonify, g
from app.utils.data_utils import save_data

profile_bp = Blueprint("profile", __name__)

users = {}  # Replace with actual data loading logic

@profile_bp.route("/", methods=["GET"])
def get_profile():
    uname = g.current_user
    user = users.get(uname, {})
    return jsonify({
        "username": uname,
        "avatar_url": user.get("avatar_url", ""),
        "bio": user.get("bio", ""),
        "badges": user.get("badges", []),
        "following": user.get("following", []),
        "followers": user.get("followers", [])
    }), 200

@profile_bp.route("/", methods=["PUT"])
def update_profile():
    uname = g.current_user
    user = users.get(uname)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json or {}
    if "avatar_url" in data:
        user["avatar_url"] = data["avatar_url"]
    if "bio" in data:
        user["bio"] = data["bio"]

    save_data(users, "users.json")
    return jsonify({"status": "Profile updated", "profile": user}), 200