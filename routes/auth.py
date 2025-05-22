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
    u, p, e = data.get('username'), data.get('password'), data.get('email')

    if not u or not p or not e:
        return jsonify(error='username, password and email required'), 400

    if '@' not in e or '.' not in e:
        return jsonify(error='invalid email format'), 400

    if db.session.get(User, u):
        return jsonify(error='username already exists'), 409

    if User.query.filter_by(email=e).first():
        return jsonify(error='email already in use'), 409

    hashed = ph.hash(p)
    token = uuid.uuid4().hex
    verify_token = uuid.uuid4().hex

    # 👇 simulazione invio email
    print(f"[FAKE EMAIL] Verify link: /verify/{verify_token}")

    user = User(
        username=u,
        email=e,
        password_hash=hashed,
        token=token,
        email_verified=False,
        reset_token=None
    )
    db.session.add(user)
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
