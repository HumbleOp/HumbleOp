# tests/test_utils.py
import uuid
from app import create_app
from core.extensions import db
from core.utils import award_badge, award_marathoner, evaluate_badges, handle_duel_timeout
from sqlalchemy import text
from models import User, Post, Comment, Vote, Badge


app = create_app()

def test_award_badge_skips_for_invalid_user():
    with app.app_context():
        award_badge("ghost", "Ghost Badge")
        assert Badge.query.filter_by(user="ghost").count() == 0

def test_award_badge_skips_if_already_awarded(client):
    token = client.post("/register", json={"username": "z", "password": "p"}).get_json()["token"]
    with client.application.app_context():
        award_badge("z", "Repeat Badge")
        award_badge("z", "Repeat Badge")
        assert Badge.query.filter_by(user="z", name="Repeat Badge").count() == 1

def test_award_marathoner_only_top_level(client):
    client.post("/register", json={"username": "m", "password": "p"})
    with client.application.app_context():
        for i in range(100):
            db.session.add(Post(id=f"marathon_{i}", author="m", body="b", winner="m"))
        db.session.commit()

        award_marathoner("m")

        raw = db.session.execute(text("SELECT * FROM badges")).fetchall()
        print("🎯 RAW BADGES:", raw)

        badges = Badge.query.all()
        names = [b.name for b in badges if b.user == "m"]
        print("🧪 BADGE NAMES:", names)

        assert names == ["The Great Debater"]

def test_handle_duel_timeout_sets_postponed(client):
    token = client.post("/register", json={"username": "x1", "password": "p"}).get_json()["token"]
    pid = uuid.uuid4().hex
    with app.app_context():
        post = Post(id=pid, author="x1", body="q", started=False, postponed=False, second="alt")
        db.session.add(post)
        db.session.commit()
        handle_duel_timeout(pid)
        assert db.session.get(Post, pid).postponed is True

def test_handle_duel_timeout_switches_winner(client):
    token = client.post("/register", json={"username": "x2", "password": "p"}).get_json()["token"]
    pid = uuid.uuid4().hex
    with app.app_context():
        post = Post(id=pid, author="x2", body="q", started=False, postponed=True, second="alt")
        db.session.add(post)
        db.session.commit()
        handle_duel_timeout(pid)
        p = db.session.get(Post, pid)
        assert p.winner == "alt"
        assert p.postponed is False

def test_evaluate_badges_all_three(client):
    # Insightful, Serial Voter, Consistent Debater
    t = client.post("/register", json={"username": "b1", "password": "p"}).get_json()["token"]

    with client.application.app_context():
        for i in range(10):
            pid = f"p{i}"
            db.session.add(Post(id=pid, author="b1", body="X", winner="b1", second="alt"))
            db.session.add(Comment(post_id=pid, commenter="b1", text="T"))
            db.session.add(Vote(post_id=pid, voter="b1", candidate="b1"))
            for j in range(20):
                db.session.add(Vote(post_id=pid, voter=f"voter{j}", candidate="b1"))
        db.session.commit()
        evaluate_badges("b1")
        badges = [b.name for b in Badge.query.filter_by(user="b1")]
        assert "Insightful" in badges
        assert "Serial Voter" in badges
        assert "Consistent Debater" in badges
