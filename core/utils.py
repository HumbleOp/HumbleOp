from datetime import datetime, timedelta
from core.extensions import db, scheduler
from models import Post, Badge, User, Vote, Comment


def award_badge(username, badge_name):
    user = db.session.get(User, username)
    if not user:
        return
    if Badge.query.filter_by(user=username, name=badge_name).first():
        return
    db.session.add(Badge(user=username, name=badge_name))
    db.session.commit()

def award_marathoner(username):
    wins = Post.query.filter_by(winner=username).count()
    if wins >= 100:
        award_badge(username, "The Great Debater")
    db.session.commit()

def evaluate_badges(username):
    # Badge 1: Insightful — almeno 20 voti ricevuti su un post in cui ha commentato
    post_ids = db.session.query(Comment.post_id).filter_by(commenter=username).distinct()
    for (post_id,) in post_ids:
        votes = db.session.query(Vote).filter_by(post_id=post_id, candidate=username).count()
        print(f"[DEBUG] username={username}, post_id={post_id}, votes={votes}")
        if votes >= 20:
            award_badge(username, "Insightful")
            break


    # Badge 2: Serial Voter
    distinct_votes = db.session.query(Vote.post_id).filter_by(voter=username).distinct().count()
    if distinct_votes >= 10:
        award_badge(username, "Serial Voter")

    # Badge 3: Consistent Debater
    participated = Post.query.filter((Post.winner == username) | (Post.second == username)).count()
    if participated >= 10:
        award_badge(username, "Consistent Debater")

def handle_duel_timeout(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return

    if not post.started:
        if not post.postponed:
            post.postponed = True
            db.session.commit()
            scheduler.add_job(
                handle_duel_timeout,
                'date',
                run_date=datetime.now() + timedelta(hours=6),
                args=[post_id]
            )
        else:
            post.winner = post.second
            post.postponed = False
            post.started = False
            db.session.commit()
            scheduler.add_job(
                handle_duel_timeout,
                'date',
                run_date=datetime.now() + timedelta(hours=2),
                args=[post_id]
            )
