from tests.test_search import register_and_post

def test_tag_extraction_and_association(client):
    # Step 1: crea utente e ottieni token
    rv = client.post("/register", json={"username": "tagger", "password": "p", "email": "tagger@example.com"})
    token = rv.get_json()["token"]

    # Step 2: crea un post con tag nel testo
    body = "Questo post parla di #scienza e un po' anche di #Filosofia. Ripetiamolo: #scienza."
    pid = "tagged_post_001"
    rv = client.post(
        f"/create_post/{pid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"body": body}
    )
    assert rv.status_code == 200
    tags_used = rv.get_json()["tags"]
    assert sorted(tags_used) == ["Filosofia", "scienza"] or sorted(tags_used) == ["scienza", "Filosofia"]

    # Step 3: verifica che i tag siano accessibili da /tags/<tag>
    rv = client.get("/tags/scienza")
    data = rv.get_json()
    assert rv.status_code == 200
    assert data["tag"] == "scienza"
    assert any(p["id"] == pid for p in data["posts"])

    rv = client.get("/tags/filosofia")
    data = rv.get_json()
    assert rv.status_code == 200
    assert any(p["id"] == pid for p in data["posts"])

    # Step 4: verifica che il tag sia unico anche se ripetuto nel testo
    rv = client.get("/tags")
    all_tags = rv.get_json()
    tag_names = [t["name"] for t in all_tags]
    assert "scienza" in tag_names
    assert "filosofia" in tag_names

def test_search_returns_media_field(client):
    _, pid = register_and_post(client, "mediauser", "Check this image: https://example.com/cat.jpg")
    rv = client.get("/search?q=cat&type=post")
    data = rv.get_json()
    assert "media" in data["posts"][0]
    assert "https://example.com/cat.jpg" in data["posts"][0]["media"]
