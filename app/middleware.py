from flask import g, request
from app.models.models import User, db

def authenticate_user():
    """Middleware to authenticate users via token."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        g.current_user = None
        return

    token = auth_header.split(" ")[1]
    user = db.session.query(User).filter_by(token=token).first()
    g.current_user = user.username if user else None