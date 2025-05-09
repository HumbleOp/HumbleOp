def test_add_comment(client):
    # Step 1: Register a user
    register_response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "password123"
    })
    assert register_response.status_code == 201, f"Registration failed: {register_response.json}"

    # Step 2: Login to get a token
    login_response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    assert login_response.status_code == 200, f"Login failed: {login_response.json}"
    assert "token" in login_response.json, "Token not found in login response"
    token = login_response.json["token"]

    # Step 3: Create a post
    create_post_response = client.post(
        "/posts/create/1",
        json={"body": "This is a test post."},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_post_response.status_code == 200, f"Post creation failed: {create_post_response.json}"

    # Step 4: Add a comment
    add_comment_response = client.post(
        "/comments/add/1",
        json={"text": "This is a test comment."},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert add_comment_response.status_code == 200, f"Adding comment failed: {add_comment_response.json}"
    assert add_comment_response.json["status"] == "Comment added."


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