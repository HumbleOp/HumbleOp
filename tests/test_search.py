import uuid
import time

def register_and_post(client, username, body):
    client.post("/register", json={
        "username": username,
        "password": "p",
        "email": f"{username}@example.com"
    })
    token = client.post("/login", json={"username": username, "password": "p"}).get_json()["access_token"]
    pid = uuid.uuid4().hex
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": body})
    return username, pid

def test_search_users_only(client):
    client.post("/register", json={"username": "searchtest", "password": "p", "email": "searchtest@example.com"})
    rv = client.get("/search?q=search&type=user")
    data = rv.get_json()
    assert "searchtest" in data["users"]
    assert data["posts"] == []

def test_search_posts_only(client):
    u, _ = register_and_post(client, "postuser", "This is a test post about Python.")
    rv = client.get("/search?q=python&type=post")
    data = rv.get_json()
    assert data["users"] == []
    assert any("Python" in p["body"] for p in data["posts"])
    assert all(p["author"] == u for p in data["posts"])

def test_search_with_author_filter(client):
    register_and_post(client, "alice", "Post by alice about flowers")
    register_and_post(client, "bob", "Post by bob about flowers")

    rv = client.get("/search?q=flowers&type=post&author=alice")
    data = rv.get_json()
    assert all(p["author"] == "alice" for p in data["posts"])
    assert all("flowers" in p["body"].lower() for p in data["posts"])

def test_search_with_limit(client):
    for i in range(5):
        register_and_post(client, f"user{i}", f"post {i} about flask")

    rv = client.get("/search?q=flask&type=post&limit=3")
    data = rv.get_json()
    assert len(data["posts"]) <= 3

def test_search_missing_q(client):
    rv = client.get("/search")
    assert rv.status_code == 200
    data = rv.get_json()
    assert "users" in data
    assert "posts" in data

def test_search_sort_order(client):
    client.post("/register", json={"username": "chronos", "password": "p", "email": "chronos@example.com"})
    token = client.post("/login", json={"username": "chronos", "password": "p"}).get_json()["access_token"]

    # Post più vecchio
    pid_old = uuid.uuid4().hex
    client.post(f"/create_post/{pid_old}", headers={"Authorization": f"Bearer {token}"}, json={"body": "first"})
    time.sleep(0.5)

    # Post più nuovo
    pid_new = uuid.uuid4().hex
    client.post(f"/create_post/{pid_new}", headers={"Authorization": f"Bearer {token}"}, json={"body": "second"})

    # Ordine ASC
    rv = client.get("/search?q=first&type=post&sort=asc")
    assert rv.get_json()["posts"][0]["body"] == "first"

    # Ordine DESC
    rv = client.get("/search?q=second&type=post&sort=desc")
    assert rv.get_json()["posts"][0]["body"] == "second"

def test_search_returns_media_field(client):
    _, pid = register_and_post(client, "mediauser", "Check this image: https://example.com/cat.jpg")
    rv = client.get("/search?q=cat&type=post")
    data = rv.get_json()
    assert "media" in data["posts"][0]
    assert "https://example.com/cat.jpg" in data["posts"][0]["media"]
