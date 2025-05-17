# tests/test_posts.py
import uuid
from core.utils import evaluate_badges
from models import User, Post, Comment, Vote, Badge


def test_vote_assigns_badges(client):
    t = client.post("/register", json={"username": "a", "password": "p"}).get_json()["token"]
    pid = uuid.uuid4().hex

    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"body": "Test post"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"text": "comment"})

    for i in range(25):
        uname = f"v{i}"
        client.post("/register", json={"username": uname, "password": "x"})
        token = client.post("/login", json={"username": uname, "password": "x"}).get_json()["token"]
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"candidate": "a"})

    # forza la valutazione dopo tutti i voti
    with client.application.app_context():
        evaluate_badges("a")

    rv = client.get("/profile", headers={"Authorization": f"Bearer {t}"})
    print("BADGES:", rv.get_json()["badges"])
    assert "Insightful" in rv.get_json()["badges"]

def test_start_duel_assigns_consistent_debater(client):
    t = client.post("/register", json={"username": "c", "password": "p"}).get_json()["token"]
    client.post("/register", json={"username": "d", "password": "p"})

    for i in range(10):
        pid = uuid.uuid4().hex
        client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"body": "Q"})
        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"text": "A"})
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"candidate": "c"})
        client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {t}"})

    rv = client.get("/profile", headers={"Authorization": f"Bearer {t}"})
    assert "Consistent Debater" in rv.get_json()["badges"]

def test_vote_multiple_posts_serial_voter(client):
    t = client.post("/register", json={"username": "vuser", "password": "p"}).get_json()["token"]
    client.post("/register", json={"username": "target", "password": "p"})

    for i in range(10):
        pid = uuid.uuid4().hex
        client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"body": "X"})
        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"text": "T"})
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"candidate": "vuser"})

    rv = client.get("/profile", headers={"Authorization": f"Bearer {t}"})
    assert "Serial Voter" in rv.get_json()["badges"]

def test_get_comments(client):
    token = client.post("/register", json={"username": "x", "password": "p"}).get_json()["token"]
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
    token = client.post("/register", json={"username": "s1", "password": "p"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "stat post"})
    rv = client.get(f"/status/{pid}")
    data = rv.get_json()
    assert rv.status_code == 200
    assert data["id"] == pid
    assert data["author"] == "s1"
    assert data["started"] is False

def test_get_results(client):
    t = client.post("/register", json={"username": "u1", "password": "p"}).get_json()["token"]
    client.post("/register", json={"username": "u2", "password": "p"})
    pid = uuid.uuid4().hex

    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"body": "body"} )
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"text": "text"} )
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"candidate": "u1"} )

    rv = client.get(f"/results/{pid}")
    data = rv.get_json()
    assert rv.status_code == 200
    assert "ranking" in data
    assert data["winner"] == "u1"


def test_start_now(client):
    token = client.post("/register", json={"username": "z1", "password": "p"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "text"} )
    rv = client.post(f"/start_now/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    status = client.get(f"/status/{pid}").get_json()
    assert status["started"] is True


def test_like_post(client):
    t = client.post("/register", json={"username": "like1", "password": "p"}).get_json()["token"]
    client.post("/register", json={"username": "like2", "password": "p"})

    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"body": "b"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"text": "c"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {t}"}, json={"candidate": "like1"})
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {t}"})

    rv = client.post(f"/like/{pid}", headers={"Authorization": f"Bearer {t}"})
    assert rv.status_code == 200
    assert "Like registered" in rv.get_json()["status"]

def test_flag_post_and_switch_winner(client):
    t1 = client.post("/register", json={"username": "fl1", "password": "p"}).get_json()["token"]
    t2 = client.post("/register", json={"username": "fl2", "password": "p"}).get_json()["token"]

    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {t1}"}, json={"body": "f"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t1}"}, json={"text": "A"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {t2}"}, json={"text": "B"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {t1}"}, json={"candidate": "fl1"})
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {t1}"})

    for i in range(2):
        uname = f"flaguser{i}"
        client.post("/register", json={"username": uname, "password": "x"})
        tok = client.post("/login", json={"username": uname, "password": "x"}).get_json()["token"]
        client.post(f"/flag/{pid}", headers={"Authorization": f"Bearer {tok}"})

    rv = client.post(f"/flag/{pid}", headers={"Authorization": f"Bearer {t1}"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert "status" in data

