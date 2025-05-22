import os   
from flask import Blueprint, jsonify, request, g
from models import User
from core.extensions import db
from functools import wraps
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/avatars"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

profile_bp = Blueprint("profile", __name__)

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        parts = request.headers.get("Authorization", "").split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify(error="authorization required"), 401
        token = parts[1]
        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify(error="invalid token"), 401
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper

@profile_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    user = g.current_user
    return jsonify({
        "username": user.username,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "badges": [b.name for b in user.badges],
        "following": [u.username for u in user.following],
        "followers": [u.username for u in user.followers]
    }), 200

@profile_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    user = db.session.get(User, g.current_user.username)
    data = request.json or {}
    if "avatar_url" in data:
        user.avatar_url = data["avatar_url"]
    if "bio" in data:
        user.bio = data["bio"]
    db.session.commit()
    return jsonify({
        "status": "profile updated",
        "profile": {
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "badges": [b.name for b in user.badges]
        }
    }), 200

@profile_bp.route("/upload_avatar", methods=["POST"])
@login_required
def upload_avatar():
    if "avatar" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["avatar"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Allowed extensions?
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if "." not in file.filename or ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(f"{g.current_user.username}.{ext}")
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    # Create folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # File saving
    file.save(save_path)

    # Update profile
    user = db.session.get(User, g.current_user.username)
    user.avatar_url = f"/{UPLOAD_FOLDER}/{filename}"
    db.session.commit()

    return jsonify({"status": "avatar uploaded", "avatar_url": user.avatar_url}), 200

@profile_bp.route("/follow/<username>", methods=["POST"])
@login_required
def follow_user(username):
    me = g.current_user
    target = db.session.get(User, username)
    if not target:
        return jsonify({"error": "User not found."}), 404
    if target.username == me.username:
        return jsonify({"error": "Cannot follow yourself."}), 400
    if target in me.following:
        return jsonify({"error": "Already following."}), 409
    me.following.append(target)
    db.session.commit()
    return jsonify({"status": f"You are now following {username}"}), 200

@profile_bp.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow_user(username):
    me = g.current_user
    target = db.session.get(User, username)
    if not target:
        return jsonify({"error": "User not found."}), 404
    if target.username == me.username:
        return jsonify({"error": "Cannot unfollow yourself."}), 400
    if target not in me.following:
        return jsonify({"error": "Not following."}), 409
    me.following.remove(target)
    db.session.commit()
    return jsonify({"status": f"You have unfollowed {username}"}), 200

@profile_bp.route("/followers", methods=["GET"])
@login_required
def get_followers():
    return jsonify({"followers": [u.username for u in g.current_user.followers]}), 200

@profile_bp.route("/following", methods=["GET"])
@login_required
def get_following():
    return jsonify({"following": [u.username for u in g.current_user.following]}), 200
