import re
from datetime import datetime, timedelta
from core.extensions import db, scheduler
from models import Post, Badge, User, Vote, Comment
from config import (
    INSIGHTFUL_THRESHOLD,
    SERIAL_VOTER_THRESHOLD,
    CONSISTENT_DEBATER_THRESHOLD,
    DUEL_TIMEOUT_POSTPONE_HOURS,
    DUEL_TIMEOUT_RETRY_HOURS
)

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
    post_ids = db.session.query(Comment.post_id).filter_by(commenter=username).distinct()
    for (post_id,) in post_ids:
        votes = db.session.query(Vote).filter_by(post_id=post_id, candidate=username).count()
        print(f"[DEBUG] username={username}, post_id={post_id}, votes={votes}")
        if votes >= INSIGHTFUL_THRESHOLD:
            award_badge(username, "Insightful")
            break

    distinct_votes = db.session.query(Vote.post_id).filter_by(voter=username).distinct().count()
    if distinct_votes >= SERIAL_VOTER_THRESHOLD:
        award_badge(username, "Serial Voter")

    participated = Post.query.filter((Post.winner == username) | (Post.second == username)).count()
    if participated >= CONSISTENT_DEBATER_THRESHOLD:
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
                run_date=datetime.now() + timedelta(hours=DUEL_TIMEOUT_POSTPONE_HOURS),
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
                run_date=datetime.now() + timedelta(hours=DUEL_TIMEOUT_RETRY_HOURS),
                args=[post_id]
            )

URL_REGEX = re.compile(r'https?://[^\s]+')
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")
VIDEO_HOSTS = ("youtube.com", "youtu.be", "vimeo.com")

def extract_media_urls(text):
    urls = URL_REGEX.findall(text)
    return [
        url for url in urls
        if url.lower().endswith(IMAGE_EXTENSIONS) or any(h in url for h in VIDEO_HOSTS)
    ]
