import uuid
from models import User, Post, Comment, Vote


def test_create_post_without_body(client):
    token = client.post("/register", json={"username": "x1", "password": "p", "email": "x1@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    rv = client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={})
    assert rv.status_code == 400

def test_create_post_duplicate(client):
    token = client.post("/register", json={"username": "x2", "password": "p", "email": "x2@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "ok"})
    rv = client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "ok"})
    assert rv.status_code == 409

def test_comment_on_nonexistent_post(client):
    token = client.post("/register", json={"username": "x3", "password": "p", "email": "x3@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    rv = client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"text": "hi"})
    assert rv.status_code == 404

def test_comment_without_text(client):
    token = client.post("/register", json={"username": "x4", "password": "p", "email": "x4@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "B"})
    rv = client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token}"}, json={})
    assert rv.status_code == 400

def test_comment_twice_same_user(client):
    token = client.post("/register", json={"username": "x5", "password": "p", "email": "x5@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "B"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"text": "C"})
    rv = client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"text": "C"})
    assert rv.status_code == 403

def test_eloquent_speaker_badge(client):
    token = client.post("/register", json={"username": "x6", "password": "p", "email": "x6@example.com"}).get_json()["token"]
    for i in range(20):
        pid = uuid.uuid4().hex
        client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "B"})
        long_text = "x" * 101
        client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"text": long_text})
    profile = client.get("/profile", headers={"Authorization": f"Bearer {token}"}).get_json()
    assert "Eloquent Speaker" in profile["badges"]

def test_vote_invalid_candidate(client):
    token = client.post("/register", json={"username": "x7", "password": "p", "email": "x7@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "B"})
    rv = client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"candidate": "ghost"})
    assert rv.status_code == 400

def test_vote_twice(client):
    token = client.post("/register", json={"username": "x8", "password": "p", "email": "x8@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "B"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"text": "text"})
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"candidate": "x8"})
    rv = client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"candidate": "x8"})
    assert rv.status_code == 403

def test_start_duel_with_no_post(client):
    token = client.post("/register", json={"username": "x9", "password": "p", "email": "x9@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    rv = client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 404

def test_start_duel_with_no_comments(client):
    token = client.post("/register", json={"username": "x10", "password": "p", "email": "x10@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "text"})
    rv = client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 400

def test_start_duel_with_no_votes(client):
    token = client.post("/register", json={"username": "x11", "password": "p", "email": "x11@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "text"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"text": "text"})
    rv = client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 400

def test_get_results_with_no_votes(client):
    token = client.post("/register", json={"username": "x12", "password": "p", "email": "x12@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "text"})
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"text": "text"})
    rv = client.get(f"/results/{pid}")
    data = rv.get_json()
    assert data["winner"] is None
    assert data["second"] is None

def test_start_now_on_missing_post(client):
    token = client.post("/register", json={"username": "x13", "password": "p", "email": "x13@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    rv = client.post(f"/start_now/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 404

def test_flag_post_no_winner(client):
    token = client.post("/register", json={"username": "x14", "password": "p", "email": "x14@example.com"}).get_json()["token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "B"})
    rv = client.post(f"/flag/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 400