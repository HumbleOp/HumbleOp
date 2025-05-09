def test_create_post(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    token = login_response.json["token"]

    response = client.post(
        "/posts/create/1",
        json={"body": "This is a test post."},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["status"] == "Post created."

def test_start_duel(client):
    # Setup: Register user, login, create post, add comments and votes
    client.post("/auth/register", json={
        "username": "testuser",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    token = login_response.json["token"]

    client.post(
        "/posts/create/1",
        json={"body": "This is a test post."},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Simulate duel start
    response = client.post(
        "/posts/start_duel/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400  # Not enough comments to start the duel