def test_get_posts_by_tag(client):
    res = client.post("/login", json={"username": "t1", "password": "p"})
    if res.status_code == 404:
        client.post("/register", json={"username": "t1", "password": "p", "email": "t1@example.com"})
        res = client.post("/login", json={"username": "t1", "password": "p"})
    assert res.status_code == 200
    token = res.json()["token"]
    pid = "tagtest001"
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"body": "test #python #flask"})
    res = client.get("/tags/python")
    data = res.json()
    assert res.status_code == 200
    assert data["tag"] == "python"
    assert data["count"] == 1
    assert any(p["id"] == pid for p in data["posts"])
    assert any(p["id"] == pid for p in data["posts"])


def test_list_popular_tags(client):
    res = client.get("/tags?limit=5")
    data = res.json()
    assert isinstance(data, list)
    assert data[0]["name"]
    assert data[0]["count"] >= 1
