from flask import Blueprint, request, g
from core.responses import error, success
from core.extensions import db, scheduler
from core.utils import award_badge, award_marathoner, evaluate_badges, handle_duel_timeout, extract_media_urls
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
from models import User, Post, Comment, Vote, Like, Flag, Badge, Tag
from core.utils_flag import evaluate_flags_and_maybe_switch
from config import MIN_INITIAL_VOTES, MAX_INITIAL_VOTES

posts_bp = Blueprint("posts", __name__)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        parts = request.headers.get("Authorization", "").split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return error("authorization required", 401)
        token = parts[1]
        user = User.query.filter_by(token=token).first()
        if not user:
            return error("invalid token", 401)
        g.current_user = user
        return f(*args, **kwargs)
    return wrapper

@posts_bp.route("/create_post/<post_id>", methods=["POST"])
@login_required
def create_post(post_id):
    """
    Create a new post
    ---
    tags:
      - Posts
    security:
      - BearerAuth: []
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: Unique post identifier
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - body
          properties:
            body:
              type: string
              example: "#Debate Should AI moderate online forums?"
    responses:
      200:
        description: Post created successfully
      400:
        description: Missing body field
      409:
        description: Post with given ID already exists
    """
    from routes.tag import extract_tags

    body = request.json.get("body")
    if not body:
        return error("Field 'body' is required.", 400)
    if db.session.get(Post, post_id):
        return error("Post already exists.", 409)

    media_urls = extract_media_urls(body)
    post = Post(id=post_id, author=g.current_user.username, body=body, media_urls=media_urls)
    db.session.add(post)

    tag_names = extract_tags(body)
    for name in tag_names:
        tag = db.session.get(Tag, name.lower())
        if not tag:
            tag = Tag(name=name.lower())
            db.session.add(tag)
        post.tags.append(tag)

    db.session.commit()
    return success({
        "status": "Post created.",
        "tags": tag_names,
        "media": media_urls
    }, 200)


@posts_bp.route("/comment/<post_id>", methods=["POST"])
@login_required
def add_comment(post_id):
    """
    Add a comment to a post
    ---
    tags:
      - Posts
    security:
      - BearerAuth: []
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: ID of the post to comment on
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - text
          properties:
            text:
              type: string
              example: "I think this idea has potential."
    responses:
      200:
        description: Comment added successfully
      400:
        description: Missing or invalid input
      403:
        description: User has already commented
      404:
        description: Post not found
    """
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    commenter = g.current_user.username
    text = request.json.get("text")
    if not text:
        return error("Field 'text' is required.", 400)
    existing = Comment.query.filter_by(post_id=post_id, commenter=commenter).first()
    if existing:
        return error(f"User '{commenter}' has already commented.", 403)
    db.session.add(Comment(post_id=post_id, commenter=commenter, text=text))
    db.session.commit()
    award_badge(commenter, "First blood")
    long_comments = Comment.query.filter(func.length(Comment.text) >= 100).count()
    if long_comments >= 20:
        award_badge(commenter, "Eloquent Speaker")
    return success({"status": "Comment added."}, 200)


@posts_bp.route("/vote/<post_id>", methods=["POST"])
@login_required
def vote(post_id):
    """
    Vote for a comment in a post
    ---
    tags:
      - Posts
    security:
      - BearerAuth: []
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: ID of the post to vote on
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - candidate
          properties:
            candidate:
              type: string
              example: test1
    responses:
      200:
        description: Vote registered
      400:
        description: Candidate has not commented
      403:
        description: User has already voted
      404:
        description: Post not found
    """
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    voter = g.current_user.username
    candidate = request.json.get("candidate")
    if not Comment.query.filter_by(post_id=post_id, commenter=candidate).first():
        return error(f"Candidate '{candidate}' has not commented.", 400)
    if Vote.query.filter_by(post_id=post_id, voter=voter).first():
        return error(f"User '{voter}' has already voted.", 403)
    db.session.add(Vote(post_id=post_id, voter=voter, candidate=candidate))
    db.session.commit()
    award_badge(voter, "First Responder")
    total_votes = Vote.query.filter_by(candidate=candidate).count()
    if total_votes >= 10:
        award_badge(candidate, "Popular Debater")
        db.session.commit()
    evaluate_badges(voter)
    db.session.commit()
    return success({"message": f"{voter} voted for {candidate}"}, 200)


@posts_bp.route("/start_duel/<post_id>", methods=["POST"])
@login_required
def start_duel(post_id):
    """
    Force start a duel manually
    ---
    tags:
      - Posts
    security:
      - BearerAuth: []
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: ID of the post to force-start
    responses:
      200:
        description: Post marked as started
      404:
        description: Post not found
    """
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    commenters = Comment.query.filter_by(post_id=post_id).all()
    if len(commenters) < 1:
        return error("Not enough comments to start duel.", 400)
    votes = Vote.query.filter_by(post_id=post_id).all()
    tally = {}
    for v in votes:
        tally[v.candidate] = tally.get(v.candidate, 0) + 1
    if not tally:
        return error("No votes found.", 400)
    ranking = sorted(tally.items(), key=lambda x: x[1], reverse=True)
    winner, winner_count = ranking[0]
    iv = winner_count
    iv = max(iv, MIN_INITIAL_VOTES)
    iv = min(iv, MAX_INITIAL_VOTES)
    post.initial_votes = iv
    second = next((c.commenter for c in commenters if c.commenter != winner), None)
    post.winner = winner
    post.second = second
    post.started = False
    post.postponed = False
    db.session.commit()
    scheduler.add_job(handle_duel_timeout, 'date', run_date=datetime.now() + timedelta(hours=2), args=[post_id])
    award_badge(winner, "Baptism of Fire")
    award_marathoner(winner)
    evaluate_badges(winner)
    db.session.commit()
    return success({
        "status": "Duel started.",
        "winner": winner,
        "second": second
    }, 200)

@posts_bp.route("/status/<post_id>", methods=["GET"])
def get_status(post_id):
    """
    Get current status of a post
    ---
    tags:
      - Posts
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: ID of the post
    responses:
      200:
        description: Post status returned
      404:
        description: Post not found
    """
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    return success({
        "id": post.id,
        "author": post.author,
        "winner": post.winner,
        "second": post.second,
        "started": post.started,
        "postponed": post.postponed,
        "media": post.media_urls
    }, 200)


@posts_bp.route("/results/<post_id>", methods=["GET"])
def get_results(post_id):
    """
    Get duel results for a post
    ---
    tags:
      - Posts
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: ID of the post
    responses:
      200:
        description: Vote results and winner
      404:
        description: Post not found
    """
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    votes = Vote.query.filter_by(post_id=post_id).all()
    tally = {}
    for v in votes:
        tally[v.candidate] = tally.get(v.candidate, 0) + 1
    return success({
        "ranking": tally,
        "winner": post.winner,
        "second": post.second
    }, 200)

@posts_bp.route("/comments/<post_id>", methods=["GET"])
def get_comments(post_id):
    """
    Get comments for a post with vote counts
    ---
    tags:
      - Posts
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: ID of the post
    responses:
      200:
        description: List of comments with votes
      404:
        description: Post not found
    """
    if not db.session.get(Post, post_id):
        return error("Post not found.", 404)
    comments = Comment.query.filter_by(post_id=post_id).all()
    data = [{
        "commenter": c.commenter,
        "text": c.text,
        "votes": Vote.query.filter_by(post_id=post_id, candidate=c.commenter).count()
    } for c in comments]
    return success({"comments": data}, 200)

@posts_bp.route("/like/<post_id>", methods=["POST"])
@login_required
def like(post_id):
    """
    Like a post
    ---
    tags:
      - Posts
    security:
      - BearerAuth: []
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: ID of the post to like
    responses:
      200:
        description: Like registered
      403:
        description: User has already liked this post
      404:
        description: Post not found
    """
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    liker = g.current_user.username
    if Like.query.filter_by(post_id=post_id, liker=liker).first():
        return error(f"User '{liker}' has already liked this post.", 403)
    db.session.add(Like(post_id=post_id, liker=liker))
    db.session.commit()
    return success({"status": "Like registered"}, 200)

@posts_bp.route("/flag/<post_id>", methods=["POST"])
@login_required
def flag(post_id):
    """
    Flag a post for review
    ---
    tags:
      - Posts
    security:
      - BearerAuth: []
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: ID of the post to flag
    responses:
      200:
        description: Flag registered or winner switched
      400:
        description: Duel has not started
      403:
        description: User has already flagged this post
      404:
        description: Post not found
    """
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    if not post.winner:
        return error("Duel has not started yet.", 400)
    flagger = g.current_user.username
    if Flag.query.filter_by(post_id=post_id, flagger=flagger).first():
        return error(f"User '{flagger}' has already flagged this post.", 403)
    db.session.add(Flag(post_id=post_id, flagger=flagger))
    db.session.commit()
    switched, old, new = evaluate_flags_and_maybe_switch(post)
    if switched:
        return success({"status": "Winner switched.", "old": old, "new": new}, 200)
    return success({"status": "Flag registered."}, 200)

@posts_bp.route("/start_now/<post_id>", methods=["POST"])
@login_required
def start_now(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    post.started = True
    post.postponed = False
    db.session.commit()
    return success({"status": "Post marked as started."}, 200)
