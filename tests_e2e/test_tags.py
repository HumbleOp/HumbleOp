
def test_get_posts_by_tag(client):
    client.post("/register", json={"username": "t1", "password": "p", "email": "t1@example.com"})
    res = client.post("/login", json={"username": "t1", "password": "p"})
    token = res.json()["access_token"]

    pid = "tagtest001"
    client.post(
        f"/create_post/{pid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"body": "test #python #flask", "voting_hours": 0.01}
    )

    # Utente diverso commenta
    client.post("/register", json={"username": "t2", "password": "p", "email": "t2@example.com"})
    token2 = client.post("/login", json={"username": "t2", "password": "p"}).json()["access_token"]
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token2}"}, json={"text": "Test comment"})

    res = client.get("/tags/python")
    assert res.status_code == 200
    data = res.json()
    assert data["tag"] == "python"
    assert data["count"] >= 1
    assert any(p["id"] == pid for p in data["posts"])


def test_list_popular_tags(client):
    client.post("/register", json={"username": "taguser", "password": "p", "email": "taguser@example.com"})
    res = client.post("/login", json={"username": "taguser", "password": "p"})
    token = res.json()["access_token"]

    pid = "sampletagpost"
    client.post(
        f"/create_post/{pid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"body": "#popular il contenuto con un tag", "voting_hours": 0.01}
    )

    client.post("/register", json={"username": "commenter", "password": "p", "email": "commenter@example.com"})
    token2 = client.post("/login", json={"username": "commenter", "password": "p"}).json()["access_token"]
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token2}"}, json={"text": "Another test comment"})

    res = client.get("/tags?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "name" in data[0]
    assert data[0]["count"] >= 1
