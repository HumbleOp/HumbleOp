def test_insightful_badge(client, unique_post_id, alice_token):
    pid = unique_post_id
    client.post(f"/create_post/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"body": "Post badge"})

    # Registriamo nuovo utente per il commento
    client.post("/register", json={"username": "xuser", "password": "p", "email": "x@example.com"})
    token = client.post("/login", json={"username": "xuser", "password": "p"}).json()["token"]
    client.post(f"/comment/{pid}", headers={"Authorization": f"Bearer {token}"}, json={"text": "Insightful comment"})

    for i in range(30):
        uname = f"u{i}"
        client.post("/register", json={"username": uname, "password": "p", "email": f"{uname}@example.com"})
        voter_token = client.post("/login", json={"username": uname, "password": "p"}).json()["token"]
        client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {voter_token}"}, json={"candidate": "xuser"})

    # Alice vota anche per sicurezza
    client.post(f"/vote/{pid}", headers={"Authorization": f"Bearer {alice_token}"}, json={"candidate": "xuser"})

    # Avvio del duello
    client.post(f"/start_duel/{pid}", headers={"Authorization": f"Bearer {alice_token}"})

    # Verifica vincitore
    res_status = client.get(f"/status/{pid}").json()
    print(">> Winner:", res_status["winner"])
    assert res_status["winner"] == "xuser"

    # Verifica badge
    res = client.get("/profile", headers={"Authorization": f"Bearer {token}"}).json()
    assert "Insightful" in res["badges"]
