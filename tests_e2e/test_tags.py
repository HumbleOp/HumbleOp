def test_get_posts_by_tag(client):
    # Registra utente nuovo
    client.post("/register", json={"username": "t1", "password": "p", "email": "t1@example.com"})
    res = client.post("/login", json={"username": "t1", "password": "p"})
    assert res.status_code == 200
    token = res.json()["token"]

    # Crea post con tag
    pid = "tagtest001"
    client.post(
        f"/create_post/{pid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"body": "test #python #flask", "voting_hours": 0.01}
    )

    # Verifica tag
    res = client.get("/tags/python")
    assert res.status_code == 200
    data = res.json()
    assert data["tag"] == "python"
    assert data["count"] >= 1
    assert any(p["id"] == pid for p in data["posts"])


def test_list_popular_tags(client):
    # Assicurati che almeno un post con tag esista
    client.post("/register", json={"username": "taguser", "password": "p", "email": "taguser@example.com"})
    res = client.post("/login", json={"username": "taguser", "password": "p"})
    token = res.json()["token"]
    client.post(
        "/create_post/sampletagpost",
        headers={"Authorization": f"Bearer {token}"},
        json={"body": "#popular il contenuto con un tag", "voting_hours": 0.01}
    )

    # Ora prova a ottenere i tag popolari
    res = client.get("/tags?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "name" in data[0]
    assert data[0]["count"] >= 1
