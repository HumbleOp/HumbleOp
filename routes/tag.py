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
