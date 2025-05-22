from flask import Blueprint, jsonify, request
from models import User, Post

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET"])
def search():
    q = request.args.get("q", "").strip()
    search_type = request.args.get("type", "all")
    author_filter = request.args.get("author")
    limit = min(int(request.args.get("limit", 10)), 100)

    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    results = {"users": [], "posts": []}

    if search_type in ("all", "user"):
        users = User.query.filter(User.username.ilike(f"%{q}%")).limit(limit).all()
        results["users"] = [u.username for u in users]

    if search_type in ("all", "post"):
        query = Post.query.filter(Post.body.ilike(f"%{q}%"))
        if author_filter:
            query = query.filter(Post.author == author_filter)
        sort_order = request.args.get("sort", "desc").lower()
        if sort_order == "asc":
            query = query.order_by(Post.created_at.asc())
        else:
            query = query.order_by(Post.created_at.desc())

        posts = query.limit(limit).all()

        results["posts"] = [
            {"id": p.id, "author": p.author, "body": p.body, "media": p.media_urls}
            for p in posts
        ]

    return jsonify(results), 200

