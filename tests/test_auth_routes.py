def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json["status"] == "user registered"

def test_register_existing_user(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "password": "password123"
    })
    response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 409
    assert response.json["error"] == "username already exists"

def test_login_user(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "password": "password123"
    })
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "token" in response.json