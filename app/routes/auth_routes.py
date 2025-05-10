from flask import Blueprint, request, jsonify
from app.extensions import db
from argon2 import PasswordHasher, exceptions
from app.models import db, User
import uuid

auth_bp = Blueprint("auth", __name__)

ph = PasswordHasher()

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    if User.query.get(username):
        return jsonify({"error": "username already exists"}), 409

    hashed = ph.hash(password)
    user = User(username=username, password_hash=hashed, token=None, avatar_url="", bio="")
    db.session.add(user)
    db.session.commit()

    return jsonify({"status": "user registered"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    user = db.session.get(User, username)
    if not user:
        return jsonify({"error": "invalid credentials"}), 401

    try:
        ph.verify(user.password_hash, password)
    except exceptions.VerifyMismatchError:
        return jsonify({"error": "invalid credentials"}), 401

    user.token = uuid.uuid4().hex
    db.session.commit()
    return jsonify({"token": user.token}), 200
