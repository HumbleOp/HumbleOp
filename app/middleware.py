from flask import request, g, jsonify
from app.models.models import db, User  # Import the unified db instance and User model

def authenticate_user():
    """Middleware to authenticate users via token."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # If no valid Authorization header is provided, set user to None
        g.current_user = None
        return

    token = auth_header.split(" ")[1]
    
    # Ensure database operations are within the app context
    with db.session.begin():  # Use the db session to query the database
        user = db.session.query(User).filter_by(token=token).first()
        g.current_user = user.username if user else None

def require_authentication():
    """Utility function to enforce authentication in routes."""
    if not g.current_user:
        return jsonify({"error": "Authentication required"}), 401