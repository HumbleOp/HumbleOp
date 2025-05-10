import jwt
from functools import wraps
from flask        import request, jsonify, g
from datetime     import datetime, timedelta
from app.models   import User

SECRET_KEY = "your-secret-key"

class AuthService:
    @staticmethod
    def generate_token(username):
        payload = {"username": username, "exp": datetime.utcnow() + timedelta(days=1)}
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token):
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return data["username"]
        except jwt.PyJWTError:
            return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization","").split()
        if len(auth)!=2 or auth[0]!="Bearer":
            return jsonify({"error":"Authorization required"}),401
        usern = AuthService.verify_token(auth[1])
        if not usern:
            return jsonify({"error":"Invalid or expired token"}),401
        g.current_user = User.query.get(usern)
        return f(*args, **kwargs)
    return decorated
