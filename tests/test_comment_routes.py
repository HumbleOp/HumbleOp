def test_add_comment(client):
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

    response = client.post(
        "/comments/1",
        json={"text": "This is a test comment."},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["status"] == "Comment added."

def test_get_comments(client):
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

    client.post(
        "/comments/1",
        json={"text": "This is a test comment."},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.get(
        "/comments/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json["comments"]) == 1