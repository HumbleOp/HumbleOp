from flask import Blueprint, request, g, jsonify
from collections import Counter
from core.responses import error, success
from core.extensions import db, scheduler
from core.utils import award_badge, award_marathoner, evaluate_badges, handle_duel_timeout, extract_media_urls
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
from models import User, Post, Comment, Vote, Like, Flag, Badge, Tag
from core.utils_flag import evaluate_flags_and_maybe_switch, compute_flag_status
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

def finalize_voting_phase(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return
    commenters = Comment.query.filter_by(post_id=post_id).all()
    if not commenters:
        return
    votes = Vote.query.filter_by(post_id=post_id).all()
    if not votes:
        return
    tally = {}
    for v in votes:
        tally[v.candidate] = tally.get(v.candidate, 0) + 1
    ranking = sorted(tally.items(), key=lambda x: x[1], reverse=True)
    winner, winner_count = ranking[0]
    second = ranking[1][0] if len(ranking) > 1 else None
    iv = max(min(winner_count, MAX_INITIAL_VOTES), MIN_INITIAL_VOTES)

    post.winner = winner
    post.second = second
    post.initial_votes = iv
    db.session.commit()

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
              description: Text content of the post
            voting_hours:
              type: number
              example: 24
              description: How many hours to allow for voting before the duel is evaluated
    responses:
      200:
        description: Post created successfully
        examples:
          application/json:
            status: Post created.
            tags: ["debate"]
            media: []
            voting_deadline: "2025-05-25T10:45:00"
      400:
        description: Missing body field or invalid voting_hours
      409:
        description: Post with given ID already exists
    """
    from routes.tag import extract_tags
    body = request.json.get("body")
    try:
      hours = float(request.json.get("voting_hours", 24))
    except (TypeError, ValueError):
      return error("Invalid 'voting_hours'", 400)

    if not body:
        return error("Field 'body' is required.", 400)
    if db.session.get(Post, post_id):
        return error("Post already exists.", 409)

    media_urls = extract_media_urls(body)
    voting_deadline = datetime.now() + timedelta(hours=hours)

    post = Post(
        id=post_id,
        author=g.current_user.username,
        body=body,
        media_urls=media_urls,
        voting_deadline=voting_deadline
    )
    db.session.add(post)

    tag_names = extract_tags(body)
    for name in tag_names:
        tag = db.session.get(Tag, name.lower())
        if not tag:
            tag = Tag(name=name.lower())
            db.session.add(tag)
        post.tags.append(tag)

    db.session.commit()

    scheduler.add_job(finalize_voting_phase, 'date', run_date=voting_deadline, args=[post_id])

    return success({"status": "Post created.", "tags": tag_names, "media": media_urls, "voting_deadline": voting_deadline.isoformat()}, 200)

@posts_bp.route("/schedule_duel/<post_id>", methods=["POST"])
@login_required
def schedule_duel(post_id):
    """
    Schedule the start of a duel
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
        description: ID of the post whose duel is to be scheduled
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - start_in_hours
          properties:
            start_in_hours:
              type: number
              example: 0.5
              description: Number of hours from now when the duel should start
    responses:
      200:
        description: Duel start scheduled
        examples:
          application/json:
            status: Duel scheduled.
            duel_start_time: "2025-05-25T12:30:00"
      400:
        description: Missing or invalid scheduling time
      403:
        description: Unauthorized (not a duel participant)
      404:
        description: Post not found
    """
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    if g.current_user.username not in (post.winner, post.second):
        return error("Only duel participants can schedule.", 403)

    start_in = request.json.get("start_in_hours")
    if not start_in:
        return error("Missing 'start_in_hours'", 400)

    start_time = datetime.now() + timedelta(hours=start_in)
    post.duel_start_time = start_time
    db.session.commit()

    scheduler.add_job(start_duel_officially, 'date', run_date=start_time, args=[post_id])
    return success({"status": "Duel scheduled.", "duel_start_time": start_time.isoformat()}, 200)


def start_duel_officially(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return
    post.started = True
    post.postponed = False
    db.session.commit()


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

    if post.completed:
        return error("Post is completed. No more comments allowed.", 403)

    commenter = g.current_user.username
    text = request.json.get("text")

    if post.started:
        return jsonify({"error": "The post has started a duel. You can no longer comment."}), 403

    if commenter == post.author:
        return error("Authors cannot comment on their own post.", 403)

    if not text:
        return error("Field 'text' is required.", 400)

    existing = Comment.query.filter_by(post_id=post_id, commenter=commenter, is_duel=False).first()
    if existing:
        return error(f"User '{commenter}' has already commented.", 403)

    comment = Comment(post_id=post_id, commenter=commenter, text=text, is_duel=False)
    db.session.add(comment)
    db.session.commit()
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
    comment = Comment.query.filter_by(post_id=post_id, commenter=candidate).first()
    if not Comment.query.filter_by(post_id=post_id, commenter=candidate).first():
        return error(f"Candidate '{candidate}' has not commented.", 400)
    if Vote.query.filter_by(post_id=post_id, voter=voter).first():
        return error(f"User '{voter}' has already voted.", 400)
    db.session.add(Vote(post_id=post_id, voter=voter, candidate=candidate, comment_id=comment.id))
    db.session.commit()
    award_badge(voter, "First Responder")
    total_votes = Vote.query.filter_by(candidate=candidate).count()
    if total_votes >= 10:
        award_badge(candidate, "Popular Debater")
        db.session.commit()
    evaluate_badges(voter)
    db.session.commit()
    return success({"message": f"{voter} voted for {candidate}"}, 200)

@posts_bp.route("/unvote/<post_id>", methods=["POST"])
@login_required
def unvote(post_id):
    """
    Revoke user's vote on a post
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
    responses:
      200:
        description: Vote revoked
      404:
        description: Post or vote not found
    """
    vote = Vote.query.filter_by(post_id=post_id, voter=g.current_user.username).first()
    if not vote:
        return error("No existing vote to revoke", 404)
    db.session.delete(vote)
    db.session.commit()
    return success({"status": "Vote revoked"}, 200)


@posts_bp.route("/start_duel/<post_id>", methods=["POST"])
@login_required
def start_duel(post_id):
    """
    Force start a duel manually by computing winner and second
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
      400:
        description: Not enough comments or votes
      404:
        description: Post not found
    """
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)

    votes = Vote.query.filter_by(post_id=post_id).all()
    if not votes:
        return error("No votes found.", 400)

    tally = {}
    for v in votes:
        tally[v.candidate] = tally.get(v.candidate, 0) + 1

    ranking = sorted(tally.items(), key=lambda x: x[1], reverse=True)
    winner, winner_count = ranking[0]
    second = ranking[1][0] if len(ranking) > 1 else None

    iv = max(min(winner_count, MAX_INITIAL_VOTES), MIN_INITIAL_VOTES)

    post.winner = winner
    post.second = second
    post.initial_votes = iv
    post.started = True
    post.postponed = False
    post.duel_start_time = datetime.now()
    db.session.commit()

    scheduler.add_job(
        handle_duel_timeout,
        'date',
        run_date=datetime.now() + timedelta(hours=2),
        args=[post_id]
    )

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

    flag_analysis = compute_flag_status(post)
    now = datetime.now()
    countdown = 0
    if post.voting_deadline:
        remaining = (post.voting_deadline - now).total_seconds()
        countdown = max(int(remaining), 0)
    like_users = [l.liker for l in Like.query.filter_by(post_id=post_id).all()]
    flag_users = [f.flagger for f in Flag.query.filter_by(post_id=post_id).all()]
    votes = Vote.query.filter_by(post_id=post_id).all()
    ranking = Counter(v.candidate for v in votes)
    comments = Comment.query.filter_by(post_id=post_id).all()
    comment_list = [
          {
        "commenter": c.commenter,
        "text": c.text,
        "votes": Vote.query.filter_by(post_id=post_id, candidate=c.commenter).count()
          }
      for c in comments
    ]

    return success({
        "id": post.id,
        "author": post.author,
        "body": post.body,
        "winner": post.winner,
        "second": post.second,
        "started": post.started,
        "postponed": post.postponed,
        "media": post.media_urls,
        "voting_deadline": post.voting_deadline.isoformat() if post.voting_deadline else None,
        "voting_ends_in": countdown,
        "likes": len(like_users),
        "flags": len(flag_users),
        "like_users": like_users,
        "flag_users": flag_users,
        "ranking": dict(ranking),
        "comments": comment_list,
        "flag_analysis": flag_analysis,
        "duel_completed_by_author": post.duel_completed_by_author,
        "duel_completed_by_winner": post.duel_completed_by_winner,
        "completed": post.completed


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
    comments = Comment.query.filter_by(post_id=post_id, is_duel=False).all()
    data = [{
        "commenter": c.commenter,
        "text": c.text,
        "votes": Vote.query.filter_by(post_id=post_id, candidate=c.commenter).count(),
        "voters": [v.voter for v in c.votes_rel.all()]
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
    if post.completed:
      return error("Post is completed. No more voting allowed.", 403)

    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    liker = g.current_user.username
    if Like.query.filter_by(post_id=post_id, liker=liker).first():
        return error(f"User '{liker}' has already liked this post.", 403)
    if not post.winner:
        return error("Post has no winner yet.", 400)
    if liker in (post.author, post.winner):
        return error("Authors and winners cannot like.", 403)
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
    if post.completed:
      return error("Post is completed. No more voting allowed.", 403)

    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    
    if not post.started:
        return error("Duel has not started yet.", 400)
    
    flagger = g.current_user.username

    if Flag.query.filter_by(post_id=post_id, flagger=flagger).first():
        return error(f"User '{flagger}' has already flagged this post.", 403)
    
    if not post.winner:
        return error("Post has no winner yet.", 400)
    
    if flagger in (post.author, post.winner):
        return error("Authors and winners cannot flag.", 403)
    
    db.session.add(Flag(post_id=post_id, flagger=flagger))
    db.session.commit()
    
    switched, old, new = evaluate_flags_and_maybe_switch(post)
    if switched:
        return success({"status": "Winner switched.", "old": old, "new": new}, 200)
    
    print("[DEBUG] SWITCH FLAG? winner=", post.winner)
    return success({"status": "Flag registered."}, 200)


@posts_bp.route("/start_now/<post_id>", methods=["POST"])
@login_required
def start_now(post_id):
    """
    Force mark post as started (bypasses scheduling)
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
        description: ID of the post to mark as started
    responses:
      200:
        description: Post marked as started
      404:
        description: Post not found
    """
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    post.started = True
    post.postponed = False
    db.session.commit()
    return success({"status": "Post marked as started."}, 200)

@posts_bp.route("/duel_comment/<post_id>", methods=["POST"])
@login_required
def add_duel_comment(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    if post.completed:
      return error("Post is completed. Duel is over.", 403)
    if not post.started:
        return error("Duel not started", 400)

    commenter = g.current_user.username
    if commenter not in [post.author, post.winner]:
        return error("Only duel participants can comment", 403)

    text = request.json.get("text")
    if not text:
        return error("Text is required", 400)

    # Rimuoviamo il blocco che limita un solo commento per utente nel duello
    # existing = Comment.query.filter_by(post_id=post_id, commenter=commenter, is_duel=True).first()
    # if existing:
    #     return error(f"User '{commenter}' already commented in duel", 403)

    comment = Comment(post_id=post_id, commenter=commenter, text=text)
    comment.is_duel = True
    db.session.add(comment)
    db.session.commit()
    return success({"status": "Duel comment added."}, 200)


@posts_bp.route("/duel_comments/<post_id>", methods=["GET"])
def get_duel_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id, is_duel=True).all()
    return success([{
        "commenter": c.commenter,
        "text": c.text
    } for c in comments], 200)


@posts_bp.route("/complete_duel/<post_id>", methods=["POST"])
@login_required
def complete_duel(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return error("Post not found.", 404)
    if not post.started:
        return error("Duel hasn't started yet.", 400)
    if post.completed:
        return success({"status": "Duel already marked as completed."}, 200)

    user = g.current_user.username

    if user == post.author:
        post.duel_completed_by_author = True
    elif user == post.winner:
        post.duel_completed_by_winner = True
    else:
        return error("Only the author or winner can mark the duel as completed.", 403)

    # Se entrambi hanno confermato
    if post.duel_completed_by_author and post.duel_completed_by_winner:
        post.completed = True

    db.session.commit()
    return success({
        "status": "Completion recorded.",
        "completed": post.completed,
        "by_author": post.duel_completed_by_author,
        "by_winner": post.duel_completed_by_winner
    }, 200)

@posts_bp.route("/posts", methods=["GET"])
def list_posts():
    """
    List posts, optionally filtered by type (e.g. completed)
    """
    post_type = request.args.get("type")

    if post_type == "completed":
        posts = Post.query.filter_by(completed=True).order_by(Post.created_at.desc()).all()
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()

    data = [{
        "id": p.id,
        "author": p.author,
        "body": p.body,
        "winner": p.winner,
        "second": p.second,
        "completed": p.completed
    } for p in posts]

    return success({"posts": data}, 200)
