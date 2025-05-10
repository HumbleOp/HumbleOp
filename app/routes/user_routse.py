# app/routes/user_routes.py

from flask import Blueprint, jsonify, g
from ..models import db, User
from ..services.auth_service import login_required  # your decorator

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/<string:username>/follow', methods=['POST'])
@login_required
def follow_user(username):
    # Prevent users from following themselves
    if g.current_user.username == username:
        return jsonify({'error': 'You cannot follow yourself'}), 400

    # Lookup the target user by username
    target = User.query.get(username)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    # Check if already following
    if target in g.current_user.following:
        return jsonify({'error': 'Already following'}), 409

    # Append to the many-to-many relationship and commit
    g.current_user.following.append(target)
    db.session.commit()

    return jsonify({'status': f'Now following {username}'}), 200

@user_bp.route('/<string:username>/unfollow', methods=['POST'])
@login_required
def unfollow_user(username):
    # Lookup the target user by username
    target = User.query.get(username)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    # Check if not following in the first place
    if target not in g.current_user.following:
        return jsonify({'error': 'Not following'}), 400

    # Remove from the relationship and commit
    g.current_user.following.remove(target)
    db.session.commit()

    return jsonify({'status': f'Unfollowed {username}'}), 200
