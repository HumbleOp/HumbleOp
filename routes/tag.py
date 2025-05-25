import re
from flask import Blueprint, jsonify, request
from core.extensions import db
from models import Post, Tag

tag_bp = Blueprint("tag", __name__)

TAG_REGEX = re.compile(r"#(\w{2,30})")  # evita #a o #supercalifragilistico

def extract_tags(text):
    """Estrae tag validi da un testo."""
    return list(set(TAG_REGEX.findall(text)))

@tag_bp.route("/tags/<tag_name>", methods=["GET"])
def get_posts_by_tag(tag_name):
    """
    Retrieve posts associated with a specific tag
    ---
    tags:
      - Tags
    parameters:
      - name: tag_name
        in: path
        type: string
        required: true
        description: Name of the tag to search for
    responses:
      200:
        description: List of posts using the tag
        examples:
          application/json:
            tag: "python"
            count: 2
            posts:
              - id: "abc123"
                author: "user1"
                body: "Let's talk about #python"
                media: []
                created_at: "2025-05-25T10:30:00"
      404:
        description: Tag not found
    """
    tag = Tag.query.filter_by(name=tag_name.lower()).first()
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    posts = tag.posts.order_by(Post.created_at.desc()).all()
    return jsonify({
        "tag": tag_name,
        "count": len(posts),
        "posts": [
            {
                "id": p.id,
                "author": p.author,
                "body": p.body,
                "media": p.media_urls,
                "created_at": p.created_at.isoformat()
            }
            for p in posts
        ]
    }), 200


@tag_bp.route("/tags", methods=["GET"])
def list_popular_tags():
    """
    List the most frequently used tags
    ---
    tags:
      - Tags
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        default: 20
        description: Maximum number of tags to return (max 100)
    responses:
      200:
        description: List of tags sorted by usage
        examples:
          application/json:
            - name: "python"
              count: 12
            - name: "flask"
              count: 8
    """
    limit = min(int(request.args.get("limit", 20)), 100)
    tags = (
        db.session.query(Tag.name, db.func.count().label("count"))
        .join(Tag.posts)
        .group_by(Tag.name)
        .order_by(db.func.count().desc())
        .limit(limit)
        .all()
    )
    return jsonify([{"name": name, "count": count} for name, count in tags]), 200

