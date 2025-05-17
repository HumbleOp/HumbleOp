from flask import Blueprint, request, jsonify, g
from core.extensions import db, scheduler
from core.utils import award_badge, award_marathoner, evaluate_badges, handle_duel_timeout
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
from models import User, Post, Comment, Vote, Like, Flag, Badge


posts_bp = Blueprint("posts", __name__)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        parts = request.headers.get("Authorization", "").split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({"error": "authorization required"}), 401
        token = parts[1]
        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify({"error": "invalid token"}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return wrapper

@posts_bp.route("/create_post/<post_id>", methods=["POST"])
@login_required
def create_post(post_id):
    body = request.json.get("body")
    if not body:
        return jsonify(error="Field 'body' is required."), 400
    if db.session.get(Post, post_id):
        return jsonify(error="Post already exists."), 409
    post = Post(id=post_id, author=g.current_user.username, body=body)
    db.session.add(post)
    db.session.commit()
    return jsonify(status="Post created."), 200

@posts_bp.route("/comment/<post_id>", methods=["POST"])
@login_required
def add_comment(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    commenter = g.current_user.username
    text = request.json.get("text")
    if not text:
        return jsonify({"error": "Field 'text' is required."}), 400
    existing = Comment.query.filter_by(post_id=post_id, commenter=commenter).first()
    if existing:
        return jsonify({"error": f"User '{commenter}' has already commented."}), 403
    db.session.add(Comment(post_id=post_id, commenter=commenter, text=text))
    db.session.commit()
    award_badge(commenter, "First blood")
    long_comments = Comment.query.filter(func.length(Comment.text) >= 100).count()
    if long_comments >= 20:
        award_badge(commenter, "Eloquent Speaker")
    return jsonify({"status": "Comment added."}), 200

@posts_bp.route("/comments/<post_id>", methods=["GET"])
@login_required
def get_comments(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    comments = Comment.query.filter_by(post_id=post_id).all()
    data = []
    for c in comments:
        votes = Vote.query.filter_by(post_id=post_id, candidate=c.commenter).count()
        data.append({"commenter": c.commenter, "text": c.text, "votes": votes})
    return jsonify({"comments": data}), 200

@posts_bp.route("/vote/<post_id>", methods=["POST"])
@login_required
def vote(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    voter = g.current_user.username
    candidate = request.json.get("candidate")
    if not Comment.query.filter_by(post_id=post_id, commenter=candidate).first():
        return jsonify({"error": f"Candidate '{candidate}' has not commented."}), 400
    if Vote.query.filter_by(post_id=post_id, voter=voter).first():
        return jsonify({"error": f"User '{voter}' has already voted."}), 403
    db.session.add(Vote(post_id=post_id, voter=voter, candidate=candidate))
    db.session.commit()
    award_badge(voter, "First Responder")
    total_votes = Vote.query.filter_by(candidate=candidate).count()
    if total_votes >= 10:
        award_badge(candidate, "Popular Debater")
        db.session.commit()
    evaluate_badges(voter)
    db.session.commit()
    return jsonify({"message": f"{voter} voted for {candidate}"}), 200


@posts_bp.route("/start_duel/<post_id>", methods=["POST"])
@login_required
def start_duel(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    commenters = Comment.query.filter_by(post_id=post_id).all()
    if len(commenters) < 1:
        return jsonify({"error": "Not enough comments to start duel."}), 400
    votes = Vote.query.filter_by(post_id=post_id).all()
    tally = {}
    for v in votes:
        tally[v.candidate] = tally.get(v.candidate, 0) + 1
    if not tally:
        return jsonify({"error": "No votes found."}), 400
    ranking = sorted(tally.items(), key=lambda x: x[1], reverse=True)
    winner = ranking[0][0]
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
    return jsonify({"status": "Duel started.", "winner": winner, "second": second}), 200

@posts_bp.route("/status/<post_id>", methods=["GET"])
def get_status(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    return jsonify({
        "id": post.id,
        "author": post.author,
        "body": post.body,
        "started": post.started,
        "postponed": post.postponed,
        "winner": post.winner,
        "second": post.second
    }), 200

@posts_bp.route("/results/<post_id>", methods=["GET"])
def get_results(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    votes = Vote.query.filter_by(post_id=post_id).all()
    tally = {}
    for v in votes:
        tally[v.candidate] = tally.get(v.candidate, 0) + 1
    ranking = sorted(tally.items(), key=lambda x: x[1], reverse=True)
    winner = ranking[0][0] if ranking else None
    second = ranking[1][0] if len(ranking) > 1 else None
    return jsonify({
        "body": post.body,
        "ranking": ranking,
        "winner": winner,
        "second": second
    }), 200

@posts_bp.route("/start_now/<post_id>", methods=["POST"])
@login_required
def start_now(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    post.started = True
    db.session.commit()
    return jsonify({"status": "Duel started."}), 200

@posts_bp.route("/like/<post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    winner = post.winner
    if not winner:
        return jsonify({"error": "No winner to like."}), 400
    liker = g.current_user.username
    if Like.query.filter_by(post_id=post_id, liker=liker).first():
        return jsonify({"error": f"User '{liker}' has already liked the winner."}), 403
    db.session.add(Like(post_id=post_id, liker=liker))
    db.session.commit()
    total_likes = Like.query.filter_by(post_id=post_id).count()
    return jsonify({"status": f"Like registered on '{winner}'. Total likes: {total_likes}"}), 200

@posts_bp.route("/flag/<post_id>", methods=["POST"])
@login_required
def flag_post(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404
    winner = post.winner
    if not winner:
        return jsonify({"error": "No winner to flag."}), 400
    flagger = g.current_user.username
    if Flag.query.filter_by(post_id=post_id, flagger=flagger).first():
        return jsonify({"error": f"User '{flagger}' has already flagged the winner."}), 403
    db.session.add(Flag(post_id=post_id, flagger=flagger))
    db.session.commit()

    total_flags = Flag.query.filter_by(post_id=post_id).count()
    total_likes = Like.query.filter_by(post_id=post_id).count()
    votes_for_winner = Vote.query.filter_by(post_id=post_id, candidate=winner).count()

    net = max(0, total_flags - total_likes)
    ratio = (net / votes_for_winner) if votes_for_winner > 0 else 0

    if ratio >= 0.6:
        post.started = False
        post.postponed = False
        if post.second:
            post.winner = post.second
            result = {
                "status": "Duel interrupted due to net flags on winner.",
                "switched_to": post.second
            }
        else:
            post.winner = None
            result = {
                "status": "Duel interrupted but no second user available.",
                "switched_to": None
            }
        Flag.query.filter_by(post_id=post_id).delete()
        Like.query.filter_by(post_id=post_id).delete()
        scheduler.add_job(handle_duel_timeout, 'date', run_date=datetime.now() + timedelta(hours=2), args=[post_id])
        db.session.commit()
        return jsonify(result), 200

    return jsonify({
        "status": f"Flag registered on '{winner}'. Net flags: {net}/{votes_for_winner}."
    }), 200
