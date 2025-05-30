# tests/test_posts.py
import uuid
from core.utils import evaluate_badges
from datetime import datetime, timedelta
from models import User, Post, Comment, Vote, Badge


def test_vote_assigns_insightful_badge(client):
    # Autore del post
    token_author = client.post("/register", json={"username": "a", "password": "p", "email": "a@example.com"}).get_json()["token"]
    # Commentatore separato
    token_commenter = client.post("/register", json={"username": "commenter", "password": "p", "email": "c@example.com"}).get_json()["token"]

    pid = uuid.uuid4().hex

    # a crea il post
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token_author}"}, json={"body": "Insightful test"})

    # commenter commenta
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token_commenter}"}, json={"text": "well-thought argument"})

    for i in range(25):
        uname = f"voter{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        t = client.post("/login", json={"username": uname, "password": "x"}).get_json()["access_token"]
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"candidate": "commenter"})

    with client.application.app_context():
        evaluate_badges("commenter")

    rv = client.get("/profile", headers={"Authorization": f"Bearer {token_commenter}"})
    assert "Insightful" in rv.get_json()["badges"]

def test_consistent_debater_badge(client):
    from models import Post, Comment
    from core.extensions import db

    # Autore bob, commentatori alice e charlie
    token_bob = client.post("/register", json={"username": "bob", "password": "p", "email": "bob@example.com"}).get_json()["token"]
    token_alice = client.post("/register", json={"username": "alice", "password": "p", "email": "alice@example.com"}).get_json()["token"]
    token_charlie = client.post("/register", json={"username": "charlie", "password": "p", "email": "charlie@example.com"}).get_json()["token"]

    for i in range(10):
        pid = uuid.uuid4().hex
        client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token_bob}"}, json={"body": "Q"})

        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token_alice}"}, json={"text": "argomento da alice"})
        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token_charlie}"}, json={"text": "argomento da charlie"})

        # Registrazione votante terzo
        voter_token = client.post("/register", json={"username": f"judge{i}", "password": "p", "email": f"judge{i}@example.com"}).get_json()["token"]
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {voter_token}"}, json={"candidate": "alice"})

        client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {voter_token}"})

        with client.application.app_context():
            db.session.expire_all()
            post = db.session.get(Post, pid)
            comments = Comment.query.filter_by(post_id=pid).all()
            print(f"[DEBUG POST] {pid}: winner={post.winner}, second={post.second}, started={post.started}")
            print(f"[DEBUG COMMENTS] {pid}: {[c.commenter for c in comments]}")

    with client.application.app_context():
        evaluate_badges("alice")

    rv = client.get("/profile", headers={"Authorization": f"Bearer {token_alice}"})
    assert "Consistent Debater" in rv.get_json()["badges"]


def test_serial_voter_badge(client):
    token = client.post("/register", json={"username": "vuser", "password": "p", "email": "vuser@example.com"}).get_json()["token"]
    client.post("/register", json={"username": "target", "password": "p", "email": "target@example.com"})

    for i in range(10):
        pid = uuid.uuid4().hex

        # crea post
        client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": f"Post {i}"})

        # target commenta
        token_t = client.post("/login", json={"username": "target", "password": "p"}).get_json()["access_token"]
        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token_t}"}, json={"text": "commento"})

        # vuser vota per target
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"candidate": "target"})

    rv = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert "Serial Voter" in rv.get_json()["badges"]



def test_get_comments(client):
    author_token = client.post("/register", json={"username": "aut", "password": "p", "email": "a@a.com"}).get_json()["token"]
    commenter_token = client.post("/register", json={"username": "comm", "password": "p", "email": "c@c.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {author_token}"}, json={"body": "abc"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {commenter_token}"}, json={"text": "commento test"})
    rv = client.get(f"/comments/{pid}", headers={"Authorization": f"Bearer {commenter_token}"})
    assert rv.status_code == 200
    assert len(rv.get_json()["comments"]) == 1


def test_get_status(client):
    token = client.post("/register", json={ "username": "s1", "password": "p", "email": "s1@example.com" }).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "stat post"})
    rv = client.get(f"/status/{pid}")
    data = rv.get_json()
    assert rv.status_code == 200
    assert data["id"] == pid
    assert data["author"] == "s1"
    assert data["started"] is False

def test_get_results(client):
    author_token = client.post("/register", json={"username": "aut", "password": "p", "email": "a@a.com"}).get_json()["token"]
    voter_token = client.post("/register", json={"username": "voter", "password": "p", "email": "v@v.com"}).get_json()["token"]
    client.post("/register", json={"username": "alt", "password": "p", "email": "alt@alt.com"})
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {author_token}"}, json={"body": "abc"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {voter_token}"}, json={"text": "comment by voter"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {voter_token}"}, json={"candidate": "voter"})
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {voter_token}"})
    rv = client.get(f"/results/{pid}")
    assert rv.status_code == 200
    assert rv.get_json()["winner"] == "voter"



def test_start_now(client):
    token = client.post("/register", json={ "username": "z1", "password": "p", "email": "z1@example.com" }).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "text"} )
    rv = client.post(f"/start_now/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    status = client.get(f"/status/{pid}").get_json()
    assert status["started"] is True


def test_like_post(client):
    # autore
    token1 = client.post("/register", json={ "username": "like1", "password": "p", "email": "like1@example.com" }).get_json()["token"]
    # commentatore
    token2 = client.post("/register", json={ "username": "like2", "password": "p", "email": "like2@example.com" }).get_json()["token"]
    # votante
    token3 = client.post("/register", json={ "username": "like3", "password": "p", "email": "like3@example.com" }).get_json()["token"]

    pid = uuid.uuid4().hex

    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token1}"}, json={"body": "like post"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token2}"}, json={"text": "comment"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token3}"}, json={"candidate": "like2"})
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {token3}"})

    rv = client.post(f"/like/{pid}", headers={"Authorization": f"Bearer {token3}"})
    assert rv.status_code == 200
    assert "Like registered" in rv.get_json()["status"]


def test_flag_switches_to_second_if_too_many_flags(client):
    token_1 = client.post("/register", json={"username": "u1", "password": "p", "email": "u1@example.com"}).get_json()["token"]
    token_2 = client.post("/register", json={"username": "u2", "password": "p", "email": "u2@example.com"}).get_json()["token"]

    pid = "flagtest001"
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token_1}"}, json={"body": "post with duel"})

    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token_1}"}, json={"text": "comment from u1"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token_2}"}, json={"text": "comment from u2"})

    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token_1}"}, json={"candidate": "u1"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token_2}"}, json={"candidate": "u2"})  # <- ESSENZIALE

    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {token_1}"})
    client.post(f"/start_now/{pid}", headers={"Authorization": f"Bearer {token_1}"})

    # imposta duel_start_time
    with client.application.app_context():
        from models import Post
        from core.extensions import db
        post = db.session.get(Post, pid)
        post.duel_start_time = datetime.now()
        db.session.commit()

    client.post(f"/like/{pid}", headers={"Authorization": f"Bearer {token_1}"})

    for i in range(31):
        uname = f"fuser{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        tok = client.post("/login", json={"username": uname, "password": "x"}).get_json()["access_token"]
        client.post(f"/flag/{pid}", headers={"Authorization": f"Bearer {tok}"})

    # forza valutazione
    with client.application.app_context():
        from core.utils_flag import evaluate_flags_and_maybe_switch
        from core.extensions import db
        db.session.expire_all()
        post = db.session.get(Post, pid)
        evaluate_flags_and_maybe_switch(post)

    res = client.get(f"/status/{pid}").get_json()
    assert res["winner"] == "u2"


def test_flag_does_not_switch_if_enough_likes(client):
    poster = client.post("/register", json={"username": "x", "password": "p", "email": "x@x.com"}).get_json()["token"]
    c1 = client.post("/register", json={"username": "c1", "password": "p", "email": "c1@c.com"}).get_json()["token"]
    c2 = client.post("/register", json={"username": "c2", "password": "p", "email": "c2@c.com"}).get_json()["token"]
    pid = "flagtest002"
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {poster}"}, json={"body": "another post"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {c1}"}, json={"text": "comment 1"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {c2}"}, json={"text": "comment 2"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {c1}"}, json={"candidate": "c1"})
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {c1}"})
    for i in range(3):
        uname = f"liker{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        tok = client.post("/login", json={"username": uname, "password": "x"}).get_json()["access_token"]
        client.post(f"/like/{pid}", headers={"Authorization": f"Bearer {tok}"})
    for i in range(2):
        uname = f"flagger{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        tok = client.post("/login", json={"username": uname, "password": "x"}).get_json()["access_token"]
        client.post(f"/flag/{pid}", headers={"Authorization": f"Bearer {tok}"})
    res = client.get(f"/status/{pid}").get_json()
    assert res["winner"] == "c1"


def test_flag_ratio_zero_likes_zero_flags_does_not_switch(client):
    poster = client.post("/register", json={"username": "p", "password": "p", "email": "p@p.com"}).get_json()["token"]
    u1 = client.post("/register", json={"username": "u1", "password": "p", "email": "u1@u.com"}).get_json()["token"]
    u2 = client.post("/register", json={"username": "u2", "password": "p", "email": "u2@u.com"}).get_json()["token"]
    pid = "flagtest003"
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {poster}"}, json={"body": "edge case test"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {u1}"}, json={"text": "u1 comment"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {u2}"}, json={"text": "u2 comment"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {u1}"}, json={"candidate": "u1"})
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {u1}"})
    res = client.get(f"/status/{pid}").get_json()
    assert res["winner"] == "u1"



def test_status_includes_media(client):
    token = client.post("/register", json={"username": "statmedia", "password": "p", "email": "s@example.com"}).get_json()["token"]
    pid = "status_media_001"
    body = "Video: https://youtube.com/watch?v=abc"
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": body})
    rv = client.get(f"/status/{pid}")
    data = rv.get_json()
    assert "media" in data
    assert "https://youtube.com/watch?v=abc" in data["media"]
