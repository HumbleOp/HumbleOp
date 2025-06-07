from flask import Blueprint, jsonify, request
from datetime import datetime
from models import User, Post

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET"])
def search():
    """
    Search for users or posts
    ---
    tags:
      - Search
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Search query string
      - name: type
        in: query
        type: string
        enum: [all, user, post]
        default: all
        description: Filter results by type
      - name: author
        in: query
        type: string
        required: false
        description: Filter posts by author username
      - name: limit
        in: query
        type: integer
        default: 10
        description: Maximum number of results (max 100)
      - name: sort
        in: query
        type: string
        enum: [asc, desc]
        default: desc
        description: Sort order for posts
    responses:
      200:
        description: Search results
        examples:
          application/json:
            users: ["alice", "bob"]
            posts:
              - id: "123"
                author: "bob"
                body: "example post"
                media: []
      400:
        description: Missing query parameter
    """
    q = request.args.get("q", "").strip()
    search_type = request.args.get("type", "all")
    author_filter = request.args.get("author")
    limit = min(int(request.args.get("limit", 10)), 100)

    if not q and search_type == "user":
        return jsonify({"error": "Missing query parameter 'q' for user search"}), 400

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
        {
            "id": p.id,
            "author": p.author,
            "body": p.body,
            "media": p.media_urls,
            "winner": p.winner,
            "second": p.second,
            "voting_ends_in": max(int((p.voting_deadline - datetime.now()).total_seconds()), 0) if p.voting_deadline else None,
            "created_at":    p.created_at.isoformat()
        }
            for p in posts
        ]

    return jsonify(results), 200
