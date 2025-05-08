def test_get_profile(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    token = login_response.json["token"]

    response = client.get(
        "/profile/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["username"] == "testuser"

def test_update_profile(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    token = login_response.json["token"]

    response = client.put(
        "/profile/",
        json={"bio": "This is a test bio."},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["profile"]["bio"] == "This is a test bio."