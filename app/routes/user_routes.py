from flask import Blueprint, jsonify, g
from app.models.models import db, User
from ..services.auth_service import login_required

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/<string:username>/follow', methods=['POST'])
@login_required
def follow_user(username):
    current = g.current_user  # alias per chiarezza

    # 1) Prevent users from following themselves
    if current.username == username:
        return jsonify({'error': 'You cannot follow yourself'}), 400

    # 2) Lookup the target user by username
    target = User.query.get(username)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    # 3) Check if already following (dynamic relationship)
    if current.following.filter_by(username=username).first():
        return jsonify({'error': 'Already following'}), 409

    # 4) Append to the relationship and commit
    current.following.append(target)
    db.session.commit()

    return jsonify({'status': f'Now following {username}'}), 200


@user_bp.route('/<string:username>/unfollow', methods=['POST'])
@login_required
def unfollow_user(username):
    current = g.current_user

    # 1) Lookup the target user
    target = User.query.get(username)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    # 2) Check if not following (dynamic relationship)
    if not current.following.filter_by(username=username).first():
        return jsonify({'error': 'Not following'}), 400

    # 3) Remove from the relationship and commit
    current.following.remove(target)
    db.session.commit()

    return jsonify({'status': f'Unfollowed {username}'}), 200
