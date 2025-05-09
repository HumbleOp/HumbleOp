from flask import request, g
from app.models.models import User
from app import db

def authenticate_user():
    """Middleware to authenticate user and set g.current_user."""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        user = db.session.query(User).filter_by(token=token).first()
        if user:
            g.current_user = user.username
        else:
            g.current_user = None
    else:
        g.current_user = None