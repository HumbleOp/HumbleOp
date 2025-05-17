from flask import Blueprint, request, jsonify, g
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from core.extensions import db
from models import User
import uuid

auth_bp = Blueprint('auth', __name__)
ph = PasswordHasher(time_cost=2, memory_cost=51200, parallelism=8)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    u, p = data.get('username'), data.get('password')
    if not u or not p:
        return jsonify(error='username and password required'), 400
    if db.session.get(User, u):
        return jsonify(error='username already exists'), 409
    hashed = ph.hash(p)
    token = uuid.uuid4().hex
    db.session.add(User(username=u, password_hash=hashed, token=token))
    db.session.commit()
    return jsonify(status='user registered', token=token), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    u, p = data.get('username'), data.get('password')
    user = db.session.get(User, u)
    if not user:
        return jsonify(error='invalid credentials'), 401
    try:
        ph.verify(user.password_hash, p)
    except VerifyMismatchError:
        return jsonify(error='invalid credentials'), 401
    if ph.check_needs_rehash(user.password_hash):
        user.password_hash = ph.hash(p)
    user.token = uuid.uuid4().hex
    db.session.commit()
    return jsonify(token=user.token), 200
