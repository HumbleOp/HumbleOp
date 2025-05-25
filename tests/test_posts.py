# tests/test_posts.py
import uuid
from core.utils import evaluate_badges
from datetime import datetime, timedelta
from models import User, Post, Comment, Vote, Badge


def test_vote_assigns_badges(client):
    t = client.post("/register", json={ "username": "a", "password": "p", "email": "a@example.com" }).get_json()["token"]
    pid = uuid.uuid4().hex

    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"body": "Test post"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"text": "comment"})

    for i in range(25):
        uname = f"v{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        token = client.post("/login", json={"username": uname, "password": "x"}).get_json()["token"]
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"candidate": "a"})


    # forza la valutazione dopo tutti i voti
    with client.application.app_context():
        evaluate_badges("a")

    rv = client.get("/profile", headers={"Authorization": f"Bearer {t}"})
    print("BADGES:", rv.get_json()["badges"])
    assert "Insightful" in rv.get_json()["badges"]

def test_start_duel_assigns_consistent_debater(client):
    t = client.post("/register", json={ "username": "c", "password": "p", "email": "c@example.com" }).get_json()["token"]
    client.post("/register", json={ "username": "d", "password": "p", "email": "d@example.com" })

    for i in range(10):
        pid = uuid.uuid4().hex
        client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"body": "Q"})
        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"text": "A"})
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"candidate": "c"})
        client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {t}"})

    rv = client.get("/profile", headers={"Authorization": f"Bearer {t}"})
    assert "Consistent Debater" in rv.get_json()["badges"]

def test_vote_multiple_posts_serial_voter(client):
    t = client.post("/register", json={ "username": "vuser", "password": "p", "email": "vuser@example.com" }).get_json()["token"]
    client.post("/register", json={ "username": "target", "password": "p", "email": "target@example.com" })

    for i in range(10):
        pid = uuid.uuid4().hex
        client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"body": "X"})
        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"text": "T"})
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"candidate": "vuser"})

    rv = client.get("/profile", headers={"Authorization": f"Bearer {t}"})
    assert "Serial Voter" in rv.get_json()["badges"]

def test_get_comments(client):
    token = client.post("/register", json={ "username": "x", "password": "p", "email": "x@example.com" }).get_json()["token"]
    pid = uuid.uuid4().hex

    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "abc"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"text": "commento test"})

    rv = client.get(f"/comments/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    comments = rv.get_json()["comments"]
    assert len(comments) == 1
    assert comments[0]["commenter"] == "x"
    assert comments[0]["text"] == "commento test"
    assert isinstance(comments[0]["votes"], int)

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
    t = client.post("/register", json={ "username": "u1", "password": "p", "email": "u1@example.com" }).get_json()["token"]
    client.post("/register", json={ "username": "u2", "password": "p", "email": "u2@example.com" })
    pid = uuid.uuid4().hex

    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"body": "body"} )
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"text": "text"} )
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"candidate": "u1"} )
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {t}"})
    rv = client.get(f"/results/{pid}")
    data = rv.get_json()
    assert rv.status_code == 200
    assert "ranking" in data
    assert data["winner"] == "u1"


def test_start_now(client):
    token = client.post("/register", json={ "username": "z1", "password": "p", "email": "z1@example.com" }).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "text"} )
    rv = client.post(f"/start_now/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    status = client.get(f"/status/{pid}").get_json()
    assert status["started"] is True


def test_like_post(client):
    t = client.post("/register", json={ "username": "like1", "password": "p", "email": "like1@example.com" }).get_json()["token"]
    client.post("/register", json={ "username": "like2", "password": "p", "email": "like2@example.com" })

    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"body": "b"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"text": "c"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"candidate": "like1"})
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {t}"})

    rv = client.post(f"/like/{pid}", headers={"Authorization": f"Bearer {t}"})
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
        tok = client.post("/login", json={"username": uname, "password": "x"}).get_json()["token"]
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
    # Registrazione utenti
    token_1 = client.post("/register", json={"username": "alice", "password": "p", "email": "alice@example.com"}).get_json()["token"]
    token_2 = client.post("/register", json={"username": "bob", "password": "p", "email": "bob@example.com"}).get_json()["token"]

    pid = "flagtest002"
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token_1}"}, json={"body": "another post"})

    # Entrambi commentano
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token_1}"}, json={"text": "alice comment"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token_2}"}, json={"text": "bob comment"})

    # alice vota per se stessa, vince
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token_1}"}, json={"candidate": "alice"})
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {token_1}"})

    # 3 like → like = 3
    for i in range(3):
        uname = f"liker{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        tok = client.post("/login", json={"username": uname, "password": "x"}).get_json()["token"]
        client.post(f"/like/{pid}", headers={"Authorization": f"Bearer {tok}"})

    # 2 flag → like/(like+flag) = 3/5 = 0.6 → non si cambia
    for i in range(2):
        uname = f"flagger{i}"
        client.post("/register", json={"username": uname, "password": "x", "email": f"{uname}@example.com"})
        tok = client.post("/login", json={"username": uname, "password": "x"}).get_json()["token"]
        client.post(f"/flag/{pid}", headers={"Authorization": f"Bearer {tok}"})

    res = client.get(f"/status/{pid}").get_json()
    assert res["winner"] == "alice"  # il vincitore NON cambia

def test_flag_ratio_zero_likes_zero_flags_does_not_switch(client):
    # Registra due utenti
    token_1 = client.post("/register", json={"username": "zero1", "password": "p", "email": "zero1@example.com"}).get_json()["token"]
    token_2 = client.post("/register", json={"username": "zero2", "password": "p", "email": "zero2@example.com"}).get_json()["token"]

    pid = "flagtest003"
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token_1}"}, json={"body": "edge case test"})

    # Entrambi commentano
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token_1}"}, json={"text": "comment from zero1"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token_2}"}, json={"text": "comment from zero2"})

    # zero1 vota per sé → vince
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token_1}"}, json={"candidate": "zero1"})
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {token_1}"})

    # Nessun like, nessun flag

    res = client.get(f"/status/{pid}").get_json()
    assert res["winner"] == "zero1"  # vincitore invariato


def test_status_includes_media(client):
    token = client.post("/register", json={"username": "statmedia", "password": "p", "email": "s@example.com"}).get_json()["token"]
    pid = "status_media_001"
    body = "Video: https://youtube.com/watch?v=abc"
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": body})
    rv = client.get(f"/status/{pid}")
    data = rv.get_json()
    assert "media" in data
    assert "https://youtube.com/watch?v=abc" in data["media"]
